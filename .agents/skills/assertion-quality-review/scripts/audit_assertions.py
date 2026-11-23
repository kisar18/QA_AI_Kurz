#!/usr/bin/env python3
"""Audit kvality asercí v Playwright + pytest testech.

Staticky analyzuje testovací soubory pomocí AST (Abstract Syntax Tree) a odhaluje:
1. Podmíněné aserce (assert nebo expect uvnitř bloků if / elif / else).
2. Statické / slabé kontroly typu assert locator.is_visible().
3. Zakázaná umělá čekání (time.sleep, wait_for_timeout).

Použití:
    python audit_assertions.py [cesta_k_testum_nebo_souboru ...]

Návratový kód:
    0 = Vše v pořádku (žádné nekvalitní nebo podmíněné aserce).
    1 = Nalezeno porušení pravidel kvality asercí.
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import List, Tuple

# Zajištění správného kódování výstupu na Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


class AssertionVisitor(ast.NodeVisitor):
    """AST návštěvník detekující nekvalitní a podmíněné aserce."""

    def __init__(self, filepath: Path, lines: List[str]):
        self.filepath = filepath
        self.lines = lines
        self.findings: List[Tuple[int, str, str]] = []  # (line, code_snippet, reason)
        self.if_depth = 0

    def visit_If(self, node: ast.If):
        self.if_depth += 1
        # Procházíme tělo podmínky
        for item in node.body:
            self.visit(item)
        # Procházíme orelse větev (elif / else)
        for item in node.orelse:
            self.visit(item)
        self.if_depth -= 1

    def visit_Assert(self, node: ast.Assert):
        line_idx = max(0, node.lineno - 1)
        code_snippet = self.lines[line_idx].strip() if line_idx < len(self.lines) else ""

        # 1. Kontrola podmíněného assertu
        if self.if_depth > 0:
            self.findings.append((
                node.lineno,
                code_snippet,
                "ZÁKAZ: Podmíněný assert uvnitř bloku if/else. Asserty musí běžet bezpodmínečně (eliminace falešné pozitivity)."
            ))

        # 2. Kontrola statického is_visible() v assertu
        if self._is_is_visible_call(node.test):
            self.findings.append((
                node.lineno,
                code_snippet,
                "ZÁKAZ: Statický assert locator.is_visible(). Použij web-first auto-retrying expect(locator).to_be_visible()."
            ))

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        line_idx = max(0, node.lineno - 1)
        code_snippet = self.lines[line_idx].strip() if line_idx < len(self.lines) else ""

        # Detekce expect(...) volání
        if self._is_expect_call(node):
            if self.if_depth > 0:
                self.findings.append((
                    node.lineno,
                    code_snippet,
                    "ZÁKAZ: Podmíněný expect(...) uvnitř bloku if/else. Kontrola se tiše přeskočí, pokud podmínka neplatí!"
                ))

        # Detekce time.sleep a wait_for_timeout
        if self._is_sleep_call(node):
            self.findings.append((
                node.lineno,
                code_snippet,
                "ZÁKAZ: Pevné čekání (time.sleep / wait_for_timeout). Použij web-first expect(...) s auto-retry."
            ))

        self.generic_visit(node)

    def _is_expect_call(self, node: ast.Call) -> bool:
        """Zjistí, zda se jedná o volání expect(...) z Playwrightu."""
        curr = node
        while isinstance(curr, ast.Call):
            if isinstance(curr.func, ast.Name) and curr.func.id == "expect":
                return True
            if isinstance(curr.func, ast.Attribute):
                curr = curr.func.value
            else:
                break
        return False

    def _is_is_visible_call(self, node: ast.AST) -> bool:
        """Zjistí, zda výraz obsahuje .is_visible()."""
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                if sub.func.attr == "is_visible":
                    return True
        return False

    def _is_sleep_call(self, node: ast.Call) -> bool:
        """Zjistí, zda se jedná o time.sleep() nebo page.wait_for_timeout()."""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "sleep" and isinstance(node.func.value, ast.Name) and node.func.value.id == "time":
                return True
            if node.func.attr == "wait_for_timeout":
                return True
        return False


def audit_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """Provede audit jednoho souboru."""
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.splitlines()
        tree = ast.parse(content, filename=str(filepath))
    except Exception as err:
        return [(0, "", f"Chyba při parsování souboru {filepath}: {err}")]

    visitor = AssertionVisitor(filepath, lines)
    visitor.visit(tree)
    # Odstraníme případné duplicity na stejném řádku (např. zřetězený expect)
    unique_findings = []
    seen = set()
    for line, snippet, reason in visitor.findings:
        key = (line, reason)
        if key not in seen:
            seen.add(key)
            unique_findings.append((line, snippet, reason))
    return sorted(unique_findings, key=lambda x: x[0])


def main():
    parser = argparse.ArgumentParser(description="Audit kvality a bezpodmínečnosti asercí.")
    parser.add_argument("paths", nargs="*", default=["tests"], help="Soubory nebo složky k auditu (výchozí: tests)")
    args = parser.parse_args()

    files_to_check: List[Path] = []
    for p_str in args.paths:
        p = Path(p_str)
        if p.is_file() and p.suffix == ".py":
            files_to_check.append(p)
        elif p.is_dir():
            files_to_check.extend(sorted(p.rglob("test_*.py")))

    if not files_to_check:
        print("[VAROVÁNÍ] Nebyly nalezeny žádné testovací soubory k auditu.")
        sys.exit(0)

    total_findings = 0
    print("=" * 70)
    print("   AUDIT KVALITY A BEZPODMÍNEČNOSTI ASERCÍ (AST KONTROLA)")
    print("=" * 70)

    for filepath in files_to_check:
        findings = audit_file(filepath)
        if findings:
            total_findings += len(findings)
            print(f"\n[CHYBA] {filepath} ({len(findings)} nálezů):")
            for lineno, snippet, reason in findings:
                print(f"  Řádek {lineno}: {reason}")
                if snippet:
                    print(f"    Kód: {snippet}")

    print("\n" + "=" * 70)
    if total_findings == 0:
        print(f"VÝSLEDEK: [ ČISTÝ ] Zkontrolováno {len(files_to_check)} souborů, 0 chyb v asercích.")
        print("=" * 70)
        sys.exit(0)
    else:
        print(f"VÝSLEDEK: [ CHYBA ] Nalezeno celkem {total_findings} porušení pravidel kvality asercí!")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
