#!/usr/bin/env python3
"""
Test Overview Generator
-----------------------
Staticky analyzuje automatizované testy v projektu (Playwright + pytest)
a generuje souhrnný Markdown soubor s přehledem všech testů, jejich kroků a kontrol.

Použití:
    python generate_test_overview.py [--tests-dir tests] [--output TEST_OVERVIEW.md]
"""

import ast
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def extract_string_or_unparse(node: ast.AST) -> str:
    """Extrahuje čistý řetězec z Constant nebo složeného JoinedStr (f-string)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts = []
        for part in node.values:
            if isinstance(part, ast.Constant):
                parts.append(str(part.value))
            elif isinstance(part, ast.FormattedValue):
                parts.append("{" + ast.unparse(part.value) + "}")
            else:
                parts.append(ast.unparse(part))
        return "".join(parts)
    return ast.unparse(node)


class TestItemVisitor:
    """Extrahuje akce a kontroly z těla testovací funkce."""

    def __init__(self):
        self.items: List[Dict[str, Any]] = []

    def parse_body(self, statements: List[ast.stmt]):
        for stmt in statements:
            self._process_statement(stmt)

    def _process_statement(self, stmt: ast.stmt):
        # 1. Kontrola přes assert
        if isinstance(stmt, ast.Assert):
            test_repr = ast.unparse(stmt.test)
            msg = extract_string_or_unparse(stmt.msg) if stmt.msg else ""
            self.items.append({
                "type": "check",
                "kind": "assert",
                "code": f"assert {test_repr}",
                "description": msg,
                "line": stmt.lineno
            })
            return

        # 2. Výrazy (volání funkcí, metod, expect, step)
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            call_code = ast.unparse(call)

            # Volání helperu step("...")
            if isinstance(call.func, ast.Name) and call.func.id == "step":
                msg = extract_string_or_unparse(call.args[0]) if call.args else ""
                
                # Pokud předchozí položka byla kontrola bez popisu, spárujeme ji
                if self.items and self.items[-1]["type"] == "check" and not self.items[-1].get("description"):
                    self.items[-1]["description"] = msg
                else:
                    self.items.append({
                        "type": "check",
                        "kind": "step",
                        "code": call_code,
                        "description": msg,
                        "line": stmt.lineno
                    })
                return

            # Volání expect(...)
            if "expect(" in call_code:
                self.items.append({
                    "type": "check",
                    "kind": "expect",
                    "code": call_code,
                    "description": "",
                    "line": stmt.lineno
                })
                return

            # Ostatní volání = akce / krok testu
            self.items.append({
                "type": "action",
                "kind": "call",
                "code": call_code,
                "description": "",
                "line": stmt.lineno
            })
            return

        # 3. Přiřazení (příprava dat nebo vyčtení stavu pro kontrolu)
        if isinstance(stmt, ast.Assign):
            assign_code = ast.unparse(stmt)
            # Pokud přiřazení volá count(), inner_text(), cookies apod., je to často mezikrok kontroly
            if any(term in assign_code for term in [".count()", ".inner_text()", "cookies()", "status", "request."]):
                self.items.append({
                    "type": "action",
                    "kind": "data_extract",
                    "code": assign_code,
                    "description": "Získání hodnoty/stavu z aplikace",
                    "line": stmt.lineno
                })
            else:
                self.items.append({
                    "type": "action",
                    "kind": "assign",
                    "code": assign_code,
                    "description": "Příprava testovacích dat",
                    "line": stmt.lineno
                })
            return

        # 4. Složené příkazy (with, for, if)
        if isinstance(stmt, (ast.With, ast.For, ast.If)):
            header = "with" if isinstance(stmt, ast.With) else ("for" if isinstance(stmt, ast.For) else "if")
            condition = ""
            if isinstance(stmt, ast.If):
                condition = f" {ast.unparse(stmt.test)}"
            self.items.append({
                "type": "action",
                "kind": "control_flow",
                "code": f"{header}{condition}:",
                "description": f"Řídicí blok ({header})",
                "line": stmt.lineno
            })
            for sub_stmt in stmt.body:
                self._process_statement(sub_stmt)
            if isinstance(stmt, ast.If) and stmt.orelse:
                for sub_stmt in stmt.orelse:
                    self._process_statement(sub_stmt)


class TestAnalyzer:
    """Analyzuje testovací soubory v zadané složce."""

    def __init__(self, tests_dir: Path, project_root: Path):
        self.tests_dir = tests_dir
        self.project_root = project_root

    def discover_and_analyze(self) -> List[Dict[str, Any]]:
        test_files = sorted(self.tests_dir.rglob("test_*.py"))
        results = []

        for file_path in test_files:
            file_info = self._analyze_file(file_path)
            if file_info and file_info["tests"]:
                results.append(file_info)

        return results

    def _analyze_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
        except Exception as e:
            print(f"[VAROVÁNÍ] Nelze zpracovat {file_path}: {e}", file=sys.stderr)
            return None

        rel_path = file_path.relative_to(self.project_root).as_posix()
        module_name = file_path.parent.name if file_path.parent != self.tests_dir else "general"

        file_data = {
            "path": rel_path,
            "filename": file_path.name,
            "module": module_name,
            "module_doc": ast.get_docstring(tree) or "",
            "tests": []
        }

        # Procházení uzlů v souboru
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                class_doc = ast.get_docstring(node) or ""
                for member in node.body:
                    if isinstance(member, ast.FunctionDef) and member.name.startswith("test_"):
                        test_info = self._analyze_test_function(member, class_name=class_name, class_doc=class_doc)
                        file_data["tests"].append(test_info)

            elif isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                test_info = self._analyze_test_function(node, class_name=None, class_doc=None)
                file_data["tests"].append(test_info)

        return file_data

    def _analyze_test_function(self, func_node: ast.FunctionDef, class_name: Optional[str], class_doc: Optional[str]) -> Dict[str, Any]:
        docstring = ast.get_docstring(func_node) or ""
        
        # Markery
        markers = []
        for decorator in func_node.decorator_list:
            dec_repr = ast.unparse(decorator)
            if "pytest.mark" in dec_repr:
                markers.append(dec_repr.replace("pytest.mark.", ""))

        visitor = TestItemVisitor()
        visitor.parse_body(func_node.body)

        actions_count = sum(1 for item in visitor.items if item["type"] == "action")
        checks_count = sum(1 for item in visitor.items if item["type"] == "check")

        return {
            "name": func_node.name,
            "line": func_node.lineno,
            "class_name": class_name,
            "class_doc": class_doc,
            "docstring": docstring.strip(),
            "markers": markers,
            "items": visitor.items,
            "actions_count": actions_count,
            "checks_count": checks_count
        }


class MarkdownReportGenerator:
    """Generuje přehledný Markdown soubor ze zjištěných dat testů."""

    @staticmethod
    def generate(test_data: List[Dict[str, Any]], output_path: Path):
        total_files = len(test_data)
        total_tests = sum(len(f["tests"]) for f in test_data)
        total_checks = sum(sum(t["checks_count"] for t in f["tests"]) for f in test_data)
        total_actions = sum(sum(t["actions_count"] for t in f["tests"]) for f in test_data)

        # Seskupení dle modulů
        modules: Dict[str, List[Dict[str, Any]]] = {}
        for file_info in test_data:
            mod = file_info["module"]
            if mod not in modules:
                modules[mod] = []
            modules[mod].append(file_info)

        lines: List[str] = []

        # Hlavička
        lines.append("# Přehled automatizovaných testů (Test Catalog)")
        lines.append("")
        lines.append(f"> Automaticky vygenerovaný přehled všech testů, kroků a kontrol v projektu.")
        lines.append(f"> Datum vygenerování: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
        lines.append("")

        # Souhrnná statistika
        lines.append("## Souhrnná statistika")
        lines.append("")
        lines.append(f"| Metrika | Hodnota |")
        lines.append(f"| :--- | :--- |")
        lines.append(f"| **Celkem testovacích souborů** | {total_files} |")
        lines.append(f"| **Celkem automatizovaných testů** | {total_tests} |")
        lines.append(f"| **Celkem akčních kroků** | {total_actions} |")
        lines.append(f"| **Celkem ověření a kontrol** | {total_checks} |")
        lines.append(f"| **Oblasti / moduly** | {len(modules)} (`{', '.join(sorted(modules.keys()))}`) |")
        lines.append("")

        # Rychlý rozcestník modulů
        lines.append("## Rychlá navigace podle oblastí")
        lines.append("")
        for mod in sorted(modules.keys()):
            mod_tests_count = sum(len(f["tests"]) for f in modules[mod])
            lines.append(f"- [{mod.capitalize()} ({mod_tests_count} testů)](#oblast-{mod.lower()})")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Jednotlivé oblasti
        for mod in sorted(modules.keys()):
            files_in_mod = modules[mod]
            mod_tests_count = sum(len(f["tests"]) for f in files_in_mod)
            lines.append(f'<a id="oblast-{mod.lower()}"></a>')
            lines.append(f"## Oblast: {mod.capitalize()}")
            lines.append(f"*Počet testů v oblasti: **{mod_tests_count}***")
            lines.append("")

            for file_info in files_in_mod:
                rel_path = file_info["path"]
                lines.append(f"### Soubor: `{rel_path}`")
                if file_info["module_doc"]:
                    lines.append(f"> *{file_info['module_doc']}*")
                    lines.append("")

                for test in file_info["tests"]:
                    test_name = test["name"]
                    class_prefix = f"`{test['class_name']}` -> " if test["class_name"] else ""
                    markers_str = f" `[{', '.join(test['markers'])}]`" if test["markers"] else ""
                    
                    lines.append(f"#### {class_prefix}`{test_name}` (řádek {test['line']}){markers_str}")
                    lines.append("")
                    
                    if test["docstring"]:
                        lines.append(f"**Popis:** {test['docstring']}")
                        lines.append("")

                    lines.append(f"**Souhrn:** `{test['actions_count']}` akcí, `{test['checks_count']}` kontrol")
                    lines.append("")

                    # Seznam kroků a kontrol
                    if test["items"]:
                        lines.append("**Postup kroků a kontrol testu:**")
                        lines.append("")
                        step_num = 1
                        for item in test["items"]:
                            if item["type"] == "action":
                                desc = f" – *{item['description']}*" if item['description'] else ""
                                lines.append(f"{step_num}. ⚙️ **Krok:** `{item['code']}`{desc}")
                                step_num += 1
                            elif item["type"] == "check":
                                kind_icon = "🔍"
                                if item.get("description"):
                                    lines.append(f"{step_num}. {kind_icon} **Kontrola:** {item['description']}")
                                    lines.append(f"   - Technicky: `{item['code']}`")
                                else:
                                    lines.append(f"{step_num}. {kind_icon} **Kontrola:** `{item['code']}`")
                                step_num += 1
                        lines.append("")
                    else:
                        lines.append("*V těle testu nebyly detekovány explicitní akce ani kontroly.*")
                        lines.append("")

            lines.append("---")
            lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"[OK] Přehled testů byl úspěšně vygenerován do: {output_path}")
        print(f"     Nalezeno {total_tests} testů ve {total_files} souborech s {total_checks} kontrolami.")


def main():
    parser = argparse.ArgumentParser(description="Vygeneruje přehled automatizovaných testů včetně kroků a kontrol.")
    parser.add_argument("--tests-dir", default="tests", help="Cesta ke složce s testy (výchozí: tests)")
    parser.add_argument("--output", default="TEST_OVERVIEW.md", help="Cesta k výstupnímu MD souboru (výchozí: TEST_OVERVIEW.md)")
    parser.add_argument("--project-root", default=".", help="Kořenový adresář projektu (výchozí: .)")
    parser.add_argument(
        "--html",
        action="store_true",
        help="Vygeneruje také HTML přehled pokrytí User Stories (do reports/coverage_overview.html)",
    )
    parser.add_argument(
        "--html-output",
        default="reports/coverage_overview.html",
        help="Cesta k výstupnímu HTML přehledu (výchozí: reports/coverage_overview.html)",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not (project_root / args.tests_dir).exists():
        repo_candidate = Path(__file__).resolve().parents[4]
        if (repo_candidate / args.tests_dir).exists():
            project_root = repo_candidate

    tests_dir = (project_root / args.tests_dir).resolve()
    output_path = (project_root / args.output).resolve()

    if not tests_dir.exists():
        print(f"[CHYBA] Složka s testy neexistuje: {tests_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Analyzuji testy v: {tests_dir}")
    analyzer = TestAnalyzer(tests_dir=tests_dir, project_root=project_root)
    test_data = analyzer.discover_and_analyze()

    MarkdownReportGenerator.generate(test_data, output_path)

    if args.html:
        coverage_script = Path(__file__).resolve().parent / "generate_coverage_report.py"
        if coverage_script.exists():
            import importlib.util

            spec = importlib.util.spec_from_file_location("generate_coverage_report", coverage_script)
            if spec and spec.loader:
                cov_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(cov_mod)
                html_out = (project_root / args.html_output).resolve()
                cov_mod.generate_coverage_html(project_root=project_root, output_path=html_out)


if __name__ == "__main__":
    main()
