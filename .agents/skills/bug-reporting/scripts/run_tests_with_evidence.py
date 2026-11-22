"""Spouštěč automatizovaných testů se sběrem důkazů a metadat pro bug reporting.

Tento skript:
1. Nastaví příznak aktivního bug reportingu v session (reports/.bug_reporting_active).
2. Spustí pytest s konfigurací pro ukládání screenshotů a trace při chybě.
3. Zpracuje výsledky běhu a vygeneruje strukturovaný soubor reports/test_run_data.json.
4. Připraví šablonu reports/bug_reports.json pro každý nalezený pád testu.
"""

import ast
import json
import os
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Cesty projektu
PROJECT_ROOT = Path(__file__).resolve().parents[4]
REPORTS_DIR = PROJECT_ROOT / "reports"
EVIDENCE_DIR = REPORTS_DIR / "evidence"
MARKER_FILE = REPORTS_DIR / ".bug_reporting_active"
RUN_DATA_FILE = REPORTS_DIR / "test_run_data.json"
BUG_REPORTS_FILE = REPORTS_DIR / "bug_reports.json"


def extract_docstring_and_steps_from_file(file_path: Path, test_func_name: str) -> tuple[str, list[str]]:
    """Extrahuje docstring a volané kroky z testovací funkce pomocí AST."""
    if not file_path.exists():
        return "", []

    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except Exception:
        return "", []

    docstring = ""
    steps = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == test_func_name:
            docstring = ast.get_docstring(node) or ""
            # Pokus o extrakci kroků z volání step(...) nebo komentářů
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name) and child.func.id == "step":
                        if child.args and isinstance(child.args[0], ast.Constant):
                            steps.append(str(child.args[0].value))
                    elif isinstance(child.func, ast.Attribute) and child.func.attr == "step":
                        if child.args and isinstance(child.args[0], ast.Constant):
                            steps.append(str(child.args[0].value))
            break

    return docstring, steps


def get_base_url() -> str:
    """Získá BASE_URL z config.settings nebo vrátí výchozí hodnotu."""
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from config.settings import BASE_URL
        return BASE_URL
    except Exception:
        return os.environ.get("BASE_URL", "http://testovani.kitner.cz")


def run_tests(target: str = "tests", extra_args: list[str] | None = None) -> int:
    """Spustí pytest a shromáždí důkazy a statistiky."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Zápis markeru, že skill bug-reporting běžel
    marker_data = {
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "target": target,
    }
    MARKER_FILE.write_text(json.dumps(marker_data, indent=2), encoding="utf-8")

    junit_path = REPORTS_DIR / "junit_report.xml"

    # Sestavení příkazu pro pytest
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        target,
        f"--junitxml={junit_path}",
        "--screenshot=only-on-failure",
        "--tracing=retain-on-failure",
        f"--output={EVIDENCE_DIR}",
    ]
    if extra_args:
        cmd.extend(extra_args)

    print(f"[BugReporter] Spouštím testy: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    exit_code = result.returncode

    # 2. Parsování výsledků z JUnit XML
    failed_tests = []
    total_tests = 0
    passed_tests = 0
    skipped_tests = 0

    if junit_path.exists():
        try:
            tree = ET.parse(junit_path)
            root = tree.getroot()

            # Kořenový prvek může být <testsuites> nebo přímo <testsuite>
            suites = root.findall("testsuite") if root.tag == "testsuites" else [root]
            for suite in suites:
                total_tests += int(suite.attrib.get("tests", 0))
                failures_cnt = int(suite.attrib.get("failures", 0))
                errors_cnt = int(suite.attrib.get("errors", 0))
                skipped_cnt = int(suite.attrib.get("skipped", 0))
                skipped_tests += skipped_cnt

                for case in suite.findall("testcase"):
                    failure_el = case.find("failure")
                    error_el = case.find("error")
                    err_node = failure_el if failure_el is not None else error_el

                    if err_node is not None:
                        test_name = case.attrib.get("name", "unknown_test")
                        file_attr = case.attrib.get("file", "")
                        classname = case.attrib.get("classname", "")
                        file_path = PROJECT_ROOT / file_attr if file_attr else PROJECT_ROOT / (classname.replace(".", "/") + ".py")

                        docstring, steps = extract_docstring_and_steps_from_file(file_path, test_name)
                        err_message = err_node.attrib.get("message", "")
                        traceback_text = err_node.text or ""

                        # Hledání vygenerovaného screenshotu nebo trace v evidence adresáři
                        evidence_file = ""
                        # Hledáme soubor odpovídající názvu testu
                        matching_evidence = list(EVIDENCE_DIR.glob(f"*{test_name}*"))
                        if matching_evidence:
                            # Preferujeme screenshot (.png), případně trace (.zip)
                            pngs = [p for p in matching_evidence if p.suffix.lower() == ".png"]
                            evidence_file = str(pngs[0].relative_to(PROJECT_ROOT)) if pngs else str(matching_evidence[0].relative_to(PROJECT_ROOT))
                        else:
                            # Pokud playwright uložil do podsložky
                            all_evidence = list(EVIDENCE_DIR.rglob(f"*{test_name}*"))
                            if all_evidence:
                                evidence_file = str(all_evidence[0].relative_to(PROJECT_ROOT))

                        failed_tests.append({
                            "id": f"{file_attr}::{test_name}" if file_attr else test_name,
                            "name": test_name,
                            "file": str(file_attr),
                            "docstring": docstring,
                            "extracted_steps": steps,
                            "error_message": err_message,
                            "traceback": traceback_text,
                            "evidence": evidence_file.replace("\\", "/"),
                        })

            passed_tests = max(0, total_tests - len(failed_tests) - skipped_tests)
        except Exception as e:
            print(f"[BugReporter] Varování při parsování JUnit XML: {e}")

    # 3. Získání informací o prostředí
    env_info = {
        "os": f"{platform.system()} {platform.release()}",
        "python_version": platform.python_version(),
        "browser": "Chromium",
        "base_url": get_base_url(),
        "run_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # 4. Sestavení a uložení run data
    run_data = {
        "timestamp": datetime.now().isoformat(),
        "exit_code": exit_code,
        "total": total_tests,
        "passed": passed_tests,
        "failed": len(failed_tests),
        "skipped": skipped_tests,
        "environment": env_info,
        "failed_tests": failed_tests,
    }

    RUN_DATA_FILE.write_text(json.dumps(run_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[BugReporter] Výsledky uloženy do {RUN_DATA_FILE}")
    print(f"[BugReporter] Celkem testů: {total_tests}, Prošlo: {passed_tests}, Selhalo: {len(failed_tests)}")

    # 5. Inicializace návrhu bug reportů (pokud existují pády)
    if failed_tests:
        draft_reports = []
        for idx, ft in enumerate(failed_tests, 1):
            # Pokud nebyl nalezen screenshot na disku, vytvoříme zástupný důkaz nebo odkaz na report
            evidence_path = ft["evidence"]
            if not evidence_path:
                placeholder_shot = EVIDENCE_DIR / f"{ft['name']}_failure.png"
                if not placeholder_shot.exists():
                    placeholder_shot.write_bytes(b"")  # Bude doplněno nebo vytvořeno
                evidence_path = str(placeholder_shot.relative_to(PROJECT_ROOT)).replace("\\", "/")

            steps_list = ft["extracted_steps"]
            if not steps_list:
                steps_list = [
                    f"Otevřít aplikaci na adrese {env_info['base_url']}",
                    f"Provést kroky testovacího scénáře '{ft['name']}'",
                    "Ověřit výsledný stav a očekávané zobrazení"
                ]

            draft_reports.append({
                "id": f"BUG-{idx:03d}",
                "test_name": ft["name"],
                "test_file": ft["file"],
                "title": f"Chyba v testu: {ft['name']}",
                "steps_to_reproduce": steps_list,
                "expected_result": f"Testovací krok proběhne úspěšně a aplikace odpovídá specifikaci {ft['docstring'][:80]}." if ft["docstring"] else "Aplikace splní specifikované chování bez chyb a výjimek.",
                "actual_result": f"Test selhal s chybou: {ft['error_message'] or 'AssertionError / Timeout'}",
                "environment": f"{env_info['os']}, {env_info['browser']}, URL: {env_info['base_url']}",
                "evidence": evidence_path,
                "stacktrace": ft["traceback"][:1000] if ft["traceback"] else "",
            })

        BUG_REPORTS_FILE.write_text(json.dumps(draft_reports, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[BugReporter] Připraven výchozí soubor reportů: {BUG_REPORTS_FILE}")

    return exit_code


if __name__ == "__main__":
    target_arg = sys.argv[1] if len(sys.argv) > 1 else "tests"
    extra = sys.argv[2:] if len(sys.argv) > 2 else []
    sys.exit(run_tests(target_arg, extra))
