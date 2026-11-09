#!/usr/bin/env python3
"""
Check Done - Rozhodnutí o dokončení Test Overview
-------------------------------------------------
Provádí ověření a rozhodnutí, zda je přehled automatizovaných testů (TEST_OVERVIEW.md)
kompletní, aktuální a zda je celá úloha generování přehledu HOTOVA (Definition of Done).

Kritéria pro rozhodnutí "HOTOVO":
1. Soubor s přehledem existuje a není prázdný.
2. Soubor je aktuální – žádný testovací soubor nebyl změněn po vygenerování přehledu.
3. Všechny existující testy v projektu jsou v přehledu zaznamenány (100% pokrytí).
4. V přehledu nejsou žádné neplatné / osiřelé testy, které již v kódu neexistují.
5. Statistické údaje v přehledu přesně odpovídají aktuálnímu kódu.
6. Kvalita testů: žádný test není "slepý" (každý test obsahuje alespoň 1 kontrolu/assert).

Návratový kód:
- 0: Všechna kritéria splněna -> HOTOVO.
- 1: Alespoň jedno kritérium selhalo -> NENÍ HOTOVO.

Použití:
    python check_done.py [--tests-dir tests] [--overview TEST_OVERVIEW.md] [--strict] [--fix]
"""

import argparse
import importlib.util
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Zajištění správného kódování výstupu na Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SCRIPTS_DIR = Path(__file__).resolve().parent


def _load_generator_components():
    """Dynamicky načte TestAnalyzer a MarkdownReportGenerator ze sousedního skriptu
    bez spoléhání na statické import cesty (zabraňuje missing-import chybám v IDE/lintech).
    """
    generator_script = SCRIPTS_DIR / "generate_test_overview.py"
    if not generator_script.exists():
        print(f"[CHYBA] Skript generátoru nebyl nalezen: {generator_script}", file=sys.stderr)
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("generate_test_overview", generator_script)
    if spec is None or spec.loader is None:
        print(f"[CHYBA] Nelze načíst specifikaci pro: {generator_script}", file=sys.stderr)
        sys.exit(1)

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as err:
        print(f"[CHYBA] Chyba při načítání generátoru {generator_script}: {err}", file=sys.stderr)
        sys.exit(1)

    test_analyzer_cls = getattr(module, "TestAnalyzer")
    markdown_generator_cls = getattr(module, "MarkdownReportGenerator")
    return test_analyzer_cls, markdown_generator_cls


TestAnalyzer, MarkdownReportGenerator = _load_generator_components()


class OverviewChecker:
    """Kontroluje aktuálnost, konzistenci a kompletnost vygenerovaného přehledu testů."""

    def __init__(self, project_root: Path, tests_dir: Path, overview_path: Path, strict: bool = False):
        self.project_root = project_root
        self.tests_dir = tests_dir
        self.overview_path = overview_path
        self.strict = strict
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed_checks: List[str] = []

    def run_all_checks(self) -> Dict[str, Any]:
        """Spustí všechna kontrolní kritéria a vrátí strukturovaný výsledek."""
        # 1. Existence výstupního souboru
        if not self._check_file_exists():
            return self._build_result(is_done=False)

        # 2. Aktuální stav kódu (ground truth z AST)
        test_files_data = self._analyze_codebase()
        if test_files_data is None:
            return self._build_result(is_done=False)

        # 3. Časová aktuálnost (mtime)
        self._check_freshness()

        # 4. Parsování obsahu přehledu a kontrola shody
        overview_text = self.overview_path.read_text(encoding="utf-8")
        self._check_metrics_consistency(test_files_data, overview_text)
        self._check_tests_coverage(test_files_data, overview_text)
        self._check_tests_quality(test_files_data)
        self._check_html_coverage_report()

        # Vyhodnocení výsledku:
        # V režimu strict se i varování počítají jako chyba
        has_critical_errors = len(self.errors) > 0
        has_warnings = len(self.warnings) > 0
        is_done = not has_critical_errors and (not self.strict or not has_warnings)

        return self._build_result(is_done=is_done)

    def _check_file_exists(self) -> bool:
        """Kritérium 1: Existence a neprázdnost přehledu."""
        if not self.overview_path.exists():
            self.errors.append(f"Soubor s přehledem neexistuje: '{self.overview_path.name}'")
            return False

        if self.overview_path.stat().st_size == 0:
            self.errors.append(f"Soubor s přehledem '{self.overview_path.name}' je prázdný.")
            return False

        self.passed_checks.append(f"Soubor přehledu existuje ({self.overview_path.name}, velikost {self.overview_path.stat().st_size} B)")
        return True

    def _analyze_codebase(self) -> List[Dict[str, Any]]:
        """Získá aktuální stav všech testů v projektu pomocí AST."""
        if not self.tests_dir.exists():
            self.errors.append(f"Složka s testy neexistuje: '{self.tests_dir}'")
            return None

        analyzer = TestAnalyzer(tests_dir=self.tests_dir, project_root=self.project_root)
        data = analyzer.discover_and_analyze()
        return data

    def _check_freshness(self):
        """Kritérium 2: Žádný testovací soubor nebyl změněn po generování přehledu."""
        overview_mtime = self.overview_path.stat().st_mtime
        newer_files = []

        for test_file in self.tests_dir.rglob("test_*.py"):
            if test_file.stat().st_mtime > overview_mtime:
                rel = test_file.relative_to(self.project_root).as_posix()
                newer_files.append(rel)

        if newer_files:
            self.errors.append(
                f"Přehled je neaktuální. Následující testovací soubory byly změněny po vygenerování přehledu:\n"
                + "\n".join(f"    - {f}" for f in newer_files)
            )
        else:
            self.passed_checks.append("Časová aktuálnost přehledu (žádný testovací soubor není novější než přehled)")

    def _check_metrics_consistency(self, test_data: List[Dict[str, Any]], overview_text: str):
        """Kritérium 3: Shoda souhrnných statistik."""
        actual_files = len(test_data)
        actual_tests = sum(len(f["tests"]) for f in test_data)
        actual_checks = sum(sum(t["checks_count"] for t in f["tests"]) for f in test_data)
        actual_actions = sum(sum(t["actions_count"] for t in f["tests"]) for f in test_data)

        # Hledání metrik v tabulce přehledu pomocí regexu
        files_match = re.search(r"\*\*Celkem testovacích souborů\*\*\s*\|\s*(\d+)", overview_text)
        tests_match = re.search(r"\*\*Celkem automatizovaných testů\*\*\s*\|\s*(\d+)", overview_text)
        actions_match = re.search(r"\*\*Celkem akčních kroků\*\*\s*\|\s*(\d+)", overview_text)
        checks_match = re.search(r"\*\*Celkem ověření a kontrol\*\*\s*\|\s*(\d+)", overview_text)

        mismatches = []
        if files_match and int(files_match.group(1)) != actual_files:
            mismatches.append(f"soubory: v přehledu {files_match.group(1)} vs kód {actual_files}")
        if tests_match and int(tests_match.group(1)) != actual_tests:
            mismatches.append(f"testy: v přehledu {tests_match.group(1)} vs kód {actual_tests}")
        if actions_match and int(actions_match.group(1)) != actual_actions:
            mismatches.append(f"akce: v přehledu {actions_match.group(1)} vs kód {actual_actions}")
        if checks_match and int(checks_match.group(1)) != actual_checks:
            mismatches.append(f"kontroly: v přehledu {checks_match.group(1)} vs kód {actual_checks}")

        if not (files_match and tests_match):
            self.errors.append("V přehledu chybí tabulka se souhrnnou statistikou.")
        elif mismatches:
            self.errors.append("Statistiky v přehledu neodpovídají kódu: " + ", ".join(mismatches))
        else:
            self.passed_checks.append(
                f"Statistiky v přehledu odpovídají kódu ({actual_tests} testů v {actual_files} souborech, "
                f"{actual_checks} kontrol, {actual_actions} akcí)"
            )

    def _check_tests_coverage(self, test_data: List[Dict[str, Any]], overview_text: str):
        """Kritérium 4: 100% pokrytí testů bez chybějících i osiřelých položek."""
        codebase_tests: Set[str] = set()
        for file_info in test_data:
            for test in file_info["tests"]:
                codebase_tests.add(test["name"])

        # Extrakce názvů testů z Markdown nadpisů: #### [`ClassName` -> ]`test_name`
        overview_tests: Set[str] = set()
        for line in overview_text.splitlines():
            if line.startswith("####"):
                match = re.search(r"`(test_[a-zA-Z0-9_]+)`", line)
                if match:
                    overview_tests.add(match.group(1))

        missing_in_overview = codebase_tests - overview_tests
        orphans_in_overview = overview_tests - codebase_tests

        if missing_in_overview:
            self.errors.append(
                f"V přehledu chybí {len(missing_in_overview)} testů:\n"
                + "\n".join(f"    - {t}" for t in sorted(missing_in_overview))
            )
        else:
            self.passed_checks.append(f"Všechny testy z kódu jsou v přehledu ({len(codebase_tests)}/{len(codebase_tests)})")

        if orphans_in_overview:
            self.errors.append(
                f"V přehledu jsou záznamy o {len(orphans_in_overview)} testech, které v kódu neexistují:\n"
                + "\n".join(f"    - {t}" for t in sorted(orphans_in_overview))
            )
        else:
            self.passed_checks.append("Žádné osiřelé záznamy smazaných testů")

    def _check_tests_quality(self, test_data: List[Dict[str, Any]]):
        """Kritérium 5: Kontrola kvality testů (testy bez kontrol a testy bez docstringů)."""
        zero_checks: List[str] = []
        missing_docstrings: List[str] = []

        for file_info in test_data:
            rel = file_info["path"]
            for test in file_info["tests"]:
                test_ref = f"{rel}::{test['name']}"
                if test["checks_count"] == 0:
                    zero_checks.append(test_ref)
                if not test["docstring"]:
                    missing_docstrings.append(test_ref)

        if zero_checks:
            self.errors.append(
                f"Nalezeno {len(zero_checks)} testů bez jediné kontroly/assertu (nedokončené testy!):\n"
                + "\n".join(f"    - {t}" for t in zero_checks)
            )
        else:
            self.passed_checks.append("Všechny testy obsahují alespoň jednu kontrolu (žádný test není slepý)")

        if missing_docstrings:
            self.warnings.append(
                f"Nalezeno {len(missing_docstrings)} testů bez docstringu/popisu:\n"
                + "\n".join(f"    - {t}" for t in missing_docstrings)
            )
        else:
            self.passed_checks.append("Všechny testy mají vyplněný popis v docstringu")

    def _check_html_coverage_report(self):
        """Kritérium: HTML přehled pokrytí User Stories existuje a je aktuální."""
        html_path = self.project_root / "reports" / "coverage_overview.html"
        if not html_path.exists():
            self.warnings.append("HTML přehled pokrytí (reports/coverage_overview.html) neexistuje. Spusť generátor s --html.")
            return

        if html_path.stat().st_size == 0:
            self.errors.append("HTML přehled pokrytí (reports/coverage_overview.html) je prázdný.")
            return

        overview_mtime = html_path.stat().st_mtime
        newer_files = [
            f.relative_to(self.project_root).as_posix()
            for f in self.tests_dir.rglob("test_*.py")
            if f.stat().st_mtime > overview_mtime
        ]
        if newer_files:
            self.warnings.append(
                f"HTML přehled pokrytí může být neaktuální ({len(newer_files)} testovacích souborů je novějších než report)."
            )
        else:
            self.passed_checks.append("HTML přehled pokrytí User Stories existuje a je aktuální (reports/coverage_overview.html)")

    def _build_result(self, is_done: bool) -> Dict[str, Any]:
        return {
            "is_done": is_done,
            "decision": "HOTOVO" if is_done else "NENÍ HOTOVO",
            "overview_file": str(self.overview_path),
            "timestamp": datetime.now().isoformat(),
            "passed_checks": self.passed_checks,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def format_report_text(result: Dict[str, Any]) -> str:
    """Zformátuje výsledek kontroly do přehledného konzolového výstupu."""
    lines: List[str] = []
    lines.append("=" * 70)
    lines.append("   ROZHODNUTÍ O STAVU TEST OVERVIEW (DEFINITION OF DONE)")
    lines.append("=" * 70)
    lines.append(f"Soubor: {result['overview_file']}")
    lines.append("")

    lines.append("--- Splněná kritéria ---")
    if result["passed_checks"]:
        for check in result["passed_checks"]:
            lines.append(f"  [OK] {check}")
    else:
        lines.append("  (žádná kritéria nebyla splněna)")
    lines.append("")

    if result["warnings"]:
        lines.append("--- Varování ---")
        for warning in result["warnings"]:
            lines.append(f"  [VAROVÁNÍ] {warning}")
        lines.append("")

    if result["errors"]:
        lines.append("--- Nesplněná kritéria / Chyby ---")
        for error in result["errors"]:
            lines.append(f"  [CHYBA] {error}")
        lines.append("")

    lines.append("=" * 70)
    if result["is_done"]:
        lines.append("   VÝSLEDNÉ ROZHODNUTÍ: [ HOTOVO ]")
        lines.append("   Všechna kritéria pro Test Overview byla úspěšně splněna.")
    else:
        lines.append("   VÝSLEDNÉ ROZHODNUTÍ: [ NENÍ HOTOVO ]")
        lines.append("   Přehled testů nesplňuje všechna kritéria. Spusť generátor znovu.")
    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Rozhodne, zda je generování přehledu testů HOTOVO (ověří existenci, aktuálnost, pokrytí a kvalitu)."
    )
    parser.add_argument("--tests-dir", default="tests", help="Složka s testy (výchozí: tests)")
    parser.add_argument(
        "--overview",
        "--output",
        dest="overview",
        default="TEST_OVERVIEW.md",
        help="Cesta k přehledu (výchozí: TEST_OVERVIEW.md)",
    )
    parser.add_argument("--project-root", default=".", help="Kořen projektu (výchozí: .)")
    parser.add_argument("--strict", action="store_true", help="Přísný režim: i varování (chybějící docstring) znamenají NENÍ HOTOVO.")
    parser.add_argument("--fix", action="store_true", help="Při zjištění neaktuálnosti automaticky přegeneruje přehled.")
    parser.add_argument("--json", action="store_true", help="Vypíše výsledek ve formátu JSON.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    # Pokud v aktuální složce tests neexistuje, zkusíme automaticky detekovat kořen projektu
    if not (project_root / args.tests_dir).exists():
        repo_candidate = Path(__file__).resolve().parents[4]
        if (repo_candidate / args.tests_dir).exists():
            project_root = repo_candidate

    tests_dir = (project_root / args.tests_dir).resolve()
    overview_path = (project_root / args.overview).resolve()

    checker = OverviewChecker(
        project_root=project_root,
        tests_dir=tests_dir,
        overview_path=overview_path,
        strict=args.strict
    )

    result = checker.run_all_checks()

    # Pokud není hotovo a byl zadán přepínač --fix, přegenerujeme přehled a zkontrolujeme znovu
    if not result["is_done"] and args.fix:
        print("[INFO] Zjištěn nehotový nebo neaktuální přehled. Spouštím automatické generování (--fix)...")
        test_data = TestAnalyzer(tests_dir=tests_dir, project_root=project_root).discover_and_analyze()
        MarkdownReportGenerator.generate(test_data, overview_path)

        cov_script = SCRIPTS_DIR / "generate_coverage_report.py"
        if cov_script.exists():
            spec = importlib.util.spec_from_file_location("generate_coverage_report", cov_script)
            if spec and spec.loader:
                cov_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(cov_mod)
                cov_mod.generate_coverage_html(project_root=project_root)
        
        # Opakovaná kontrola po opravě
        checker = OverviewChecker(
            project_root=project_root,
            tests_dir=tests_dir,
            overview_path=overview_path,
            strict=args.strict
        )
        result = checker.run_all_checks()

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_report_text(result))

    sys.exit(0 if result["is_done"] else 1)


if __name__ == "__main__":
    main()
