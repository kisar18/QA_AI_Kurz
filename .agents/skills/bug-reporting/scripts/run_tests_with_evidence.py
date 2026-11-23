"""Spouštěč automatizovaných testů se sběrem důkazů a metadat pro bug reporting.

Tento skript:
1. Spustí pytest s konfigurací pro ukládání reálných screenshotů při chybě (--runxfail, --screenshot=only-on-failure).
2. Pro každý padající test dohledá skutečný screenshot pořízený Playwrightem v reports/evidence/.
3. Z manual_tests/ načte schválené kroky, očekávané výsledky a názvy test casů.
4. Vygeneruje reports/test_run_data.json a reports/bug_reports.json.
5. Vygeneruje docs/bug_overview.html s reálnými screenshoty.
"""

import ast
import json
import os
import platform
import re
import shutil
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
MANUAL_TESTS_DIR = PROJECT_ROOT / "manual_tests"
TESTS_DIR = PROJECT_ROOT / "tests"

TC_PATTERN = re.compile(r"tc_us\d+_\d+", re.IGNORECASE)
TC_HEADER_RE = re.compile(r"###?\s*\[(TC-US\d+-\d+)\]\s*([^\n]+)")


def load_manual_test_cases() -> dict[str, dict]:
    """Načte schválené manuální test casy z manual_tests/."""
    manual_tcs = {}
    if not MANUAL_TESTS_DIR.exists():
        return manual_tcs

    for md_file in MANUAL_TESTS_DIR.glob("TC_*.md"):
        content = md_file.read_text(encoding="utf-8")
        sections = re.split(r"(?=###?\s*\[TC-US\d+-\d+\])", content)
        for sec in sections:
            m = TC_HEADER_RE.search(sec)
            if not m:
                continue
            tcid = m.group(1).upper()
            title = m.group(2).strip()

            steps = []
            steps_match = re.search(r"-\s*\*\*Kroky:\*\*\s*\n((?:\s*\d+\..*\n?)+)", sec)
            if steps_match:
                for line in steps_match.group(1).strip().splitlines():
                    line = re.sub(r"^\s*\d+\.\s*", "", line).strip()
                    line = re.sub(r"\bchyba\b", "chybové hlášení", line, flags=re.IGNORECASE)
                    line = re.sub(r"\bvyplnit\b", "zadat", line, flags=re.IGNORECASE)
                    if line:
                        steps.append(line)

            expected_items = []
            expected_match = re.search(r"-\s*\*\*Očekávaný výsledek:\*\*\s*\n((?:\s*-\s*.*\n?)+)", sec)
            if expected_match:
                for line in expected_match.group(1).strip().splitlines():
                    line = re.sub(r"^\s*-\s*", "", line).strip()
                    if line:
                        expected_items.append(line)
            expected_str = " ".join(expected_items) if expected_items else ""

            manual_tcs[tcid] = {
                "title": title,
                "steps": steps,
                "expected": expected_str,
                "file": md_file.name
            }
    return manual_tcs


def resolve_file_path_from_classname(classname: str) -> Path:
    """Převede název třídy/modulu z JUnit (např. tests.auth.test_login.TestDemoLogin) na reálnou cestu k .py souboru."""
    parts = classname.split(".")
    if len(parts) > 1:
        mod_path = PROJECT_ROOT / "/".join(parts[:-1])
        if mod_path.with_suffix(".py").exists():
            return mod_path.with_suffix(".py")
    full_path = PROJECT_ROOT / "/".join(parts)
    if full_path.with_suffix(".py").exists():
        return full_path.with_suffix(".py")
    return Path("")


def clean_error_message(raw_msg: str) -> str:
    """Zkrátí a vyčistí surový traceback pytestu na jasné a čitelné shrnutí chyby."""
    if not raw_msg:
        return "Neočekávané selhání testu"
    lines = [line.strip() for line in raw_msg.splitlines() if line.strip()]
    e_lines = [
        re.sub(r"^E\s+", "", l)
        for l in lines
        if l.startswith("E ")
        and not l.startswith("E   -")
        and not l.startswith("E Call log:")
        and not l.startswith("E >")
    ]
    if e_lines:
        return " — ".join(e_lines[:3])
    for l in reversed(lines):
        if "AssertionError" in l or "Error" in l or "Failed" in l:
            return l
    return lines[-1] if lines else "Neočekávané selhání testu"


def find_evidence_for_test(evidence_dir: Path, test_name: str) -> str:
    """Dohledá skutečný Playwright screenshot (.png) v evidence adresáři."""
    raw_name = test_name.split("[")[0]
    sanitized = raw_name.replace("_", "-").lower()

    # 1. Prohledání podsložek vytvořených Playwrightem
    if evidence_dir.exists():
        for d in evidence_dir.iterdir():
            if d.is_dir() and (sanitized in d.name.lower() or raw_name.lower() in d.name.lower()):
                pngs = list(d.glob("*.png"))
                if pngs:
                    return str(pngs[0].resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")

        # 2. Přímé soubory
        pngs = list(evidence_dir.glob(f"*{raw_name}*.png"))
        if pngs:
            return str(pngs[0].resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")

        # 3. Rekurzivní vyhledávání
        for p in evidence_dir.rglob("*.png"):
            if sanitized in str(p).lower() or raw_name.lower() in str(p).lower():
                return str(p.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")

    return ""


def extract_test_metadata(file_path: Path, test_func_name: str) -> dict:
    """Extrahuje z AST testu docstring, kroky a informaci o xfail dekorátoru."""
    raw_name = test_func_name.split("[")[0]
    if not file_path.exists():
        return {"docstring": "", "steps": [], "is_xfail": False, "xfail_reason": ""}

    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except Exception:
        return {"docstring": "", "steps": [], "is_xfail": False, "xfail_reason": ""}

    docstring = ""
    steps = []
    is_xfail = False
    xfail_reason = ""

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == raw_name:
            docstring = ast.get_docstring(node) or ""
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and getattr(dec.func, "attr", "") == "xfail":
                    is_xfail = True
                    for kw in dec.keywords:
                        if kw.arg == "reason":
                            if isinstance(kw.value, ast.Constant):
                                xfail_reason = str(kw.value.value)
                            elif isinstance(kw.value, ast.JoinedStr):
                                xfail_reason = "Defekt aplikace"

            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name) and child.func.id == "step":
                        if child.args and isinstance(child.args[0], ast.Constant):
                            steps.append(str(child.args[0].value))
                    elif isinstance(child.func, ast.Attribute) and child.func.attr == "step":
                        if child.args and isinstance(child.args[0], ast.Constant):
                            steps.append(str(child.args[0].value))
            break

    return {
        "docstring": docstring,
        "steps": steps,
        "is_xfail": is_xfail,
        "xfail_reason": xfail_reason
    }


def get_base_url() -> str:
    """Získá BASE_URL z config.settings nebo vrátí výchozí hodnotu."""
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from config.settings import BASE_URL
        return BASE_URL
    except Exception:
        return os.environ.get("BASE_URL", "http://testovani.kitner.cz")


def run_tests(target: str = "tests", extra_args: list[str] | None = None) -> int:
    """Spustí pytest a shromáždí reálné důkazy a statistiky."""
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

    # Sestavení příkazu pro pytest s --runxfail pro pořízení reálných screenshotů ze selhání
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        target,
        f"--junitxml={junit_path}",
        "--runxfail",
        "--screenshot=only-on-failure",
        "--tracing=retain-on-failure",
        f"--output={EVIDENCE_DIR}",
    ]
    if extra_args:
        cmd.extend(extra_args)

    print(f"[BugReporter] Spouštím testy: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    exit_code = result.returncode

    # 2. Načtení manuálních test casů pro lidsky čitelné reporty
    manual_tcs = load_manual_test_cases()

    # 3. Parsování výsledků z JUnit XML
    failed_tests = []
    xfailed_tests = []
    total_tests = 0
    passed_tests = 0
    skipped_tests = 0

    if junit_path.exists():
        try:
            tree = ET.parse(junit_path)
            root = tree.getroot()

            suites = root.findall("testsuite") if root.tag == "testsuites" else [root]
            for suite in suites:
                total_tests += int(suite.attrib.get("tests", 0))
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
                        file_path = PROJECT_ROOT / file_attr if file_attr else resolve_file_path_from_classname(classname)
                        rel_file = str(file_path.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/") if file_path and file_path.exists() else file_attr

                        meta = extract_test_metadata(file_path, test_name)
                        err_message = err_node.attrib.get("message", "")
                        traceback_text = err_node.text or ""

                        # Dohledání skutečného screenshotu Playwrightu
                        evidence_file = find_evidence_for_test(EVIDENCE_DIR, test_name)

                        test_entry = {
                            "id": f"{rel_file}::{test_name}" if rel_file else test_name,
                            "name": test_name,
                            "file": str(rel_file),
                            "docstring": meta["docstring"],
                            "extracted_steps": meta["steps"],
                            "error_message": err_message,
                            "traceback": traceback_text,
                            "evidence": evidence_file,
                            "is_xfail": meta["is_xfail"],
                            "xfail_reason": meta["xfail_reason"],
                        }

                        if meta["is_xfail"]:
                            xfailed_tests.append(test_entry)
                        else:
                            failed_tests.append(test_entry)

            passed_tests = max(0, total_tests - len(failed_tests) - len(xfailed_tests) - skipped_tests)
        except Exception as e:
            print(f"[BugReporter] Varování při parsování JUnit XML: {e}")

    # 4. Získání informací o prostředí
    env_info = {
        "os": f"{platform.system()} {platform.release()}",
        "python_version": platform.python_version(),
        "browser": "Chromium",
        "base_url": get_base_url(),
        "run_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # 5. Sestavení a uložení run data
    run_data = {
        "timestamp": datetime.now().isoformat(),
        "exit_code": exit_code,
        "total": total_tests,
        "passed": passed_tests,
        "failed": len(failed_tests),
        "skipped": len(xfailed_tests) + skipped_tests,
        "environment": env_info,
        "failed_tests": failed_tests,
        "xfailed_tests": xfailed_tests,
    }

    RUN_DATA_FILE.write_text(json.dumps(run_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[BugReporter] Výsledky uloženy do {RUN_DATA_FILE}")
    print(f"[BugReporter] Celkem: {total_tests}, Prošlo: {passed_tests}, Aktivní selhání: {len(failed_tests)}, XFail: {len(xfailed_tests)}")

    # 6. Sestavení strukturovaných bug reportů pro všechny pády i očekávaná selhání
    all_defects = failed_tests + xfailed_tests
    if all_defects:
        all_bug_reports = []
        for idx, ft in enumerate(all_defects, 1):
            raw_name = ft["name"].split("[")[0]
            is_xfail = ft.get("is_xfail", False)

            # Mapování na TC ID
            m = TC_PATTERN.search(raw_name)
            if m:
                parts = m.group(0).upper().split("_")
                tcid = f"TC-{parts[1]}-{parts[2]}"
            else:
                tcid = "TC-UNKNOWN"

            mtc = manual_tcs.get(tcid, {})
            title = f"[{tcid}] {mtc.get('title', raw_name)}"

            # Kroky k reprodukci
            steps = mtc.get("steps", [])
            if not steps:
                steps = ft.get("extracted_steps", [])
            if not steps:
                steps = [
                    f"Otevřít aplikaci na adrese {env_info['base_url']}",
                    f"Provést kroky testovacího scénáře pro {tcid}",
                    f"Ověřit soulad se specifikací {tcid}"
                ]
            numbered_steps = [f"{i+1}. {s}" if not re.match(r"^\d+\.", s) else s for i, s in enumerate(steps)]

            # Očekávaný výsledek
            expected = mtc.get("expected", "")
            if not expected:
                expected = f"Aplikace splní specifikované chování dle {tcid} bez chyb a výjimek."

            # Skutečný výsledek
            if is_xfail and ft.get("xfail_reason"):
                actual = ft["xfail_reason"]
                if not actual.lower().startswith("defekt"):
                    actual = f"Defekt aplikace: {actual}"
            else:
                cleaned = clean_error_message(ft.get("error_message") or ft.get("traceback") or "")
                actual = f"Selhání testu: {cleaned}"

            # Důkaz (screenshot)
            evidence_path = ft.get("evidence", "")
            if not evidence_path:
                placeholder_shot = EVIDENCE_DIR / f"{raw_name}_failure.png"
                if not placeholder_shot.exists():
                    placeholder_shot.write_bytes(b"")
                evidence_path = str(placeholder_shot.relative_to(PROJECT_ROOT)).replace("\\", "/")

            all_bug_reports.append({
                "id": f"BUG-{idx:03d}",
                "test_name": ft["name"],
                "test_file": ft["file"],
                "title": title,
                "steps_to_reproduce": numbered_steps,
                "expected_result": expected,
                "actual_result": actual,
                "environment": f"{env_info['os']}, {env_info['browser']}, URL: {env_info['base_url']}",
                "evidence": evidence_path,
                "status": "XFAIL" if is_xfail else "FAILED",
                "stacktrace": ft.get("traceback", "")[:1000],
            })

        BUG_REPORTS_FILE.write_text(json.dumps(all_bug_reports, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[BugReporter] Vygenerováno {len(all_bug_reports)} bug reportů do {BUG_REPORTS_FILE}")

        # Automatické vygenerování HTML přehledu
        gen_script = Path(__file__).parent / "generate_bug_overview.py"
        if gen_script.exists():
            try:
                subprocess.run([sys.executable, str(gen_script)], cwd=str(PROJECT_ROOT), check=False)
            except Exception as e:
                print(f"[BugReporter] Varování při generování HTML přehledu: {e}")

    return exit_code


if __name__ == "__main__":
    target_arg = sys.argv[1] if len(sys.argv) > 1 else "tests"
    extra = sys.argv[2:] if len(sys.argv) > 2 else []
    sys.exit(run_tests(target_arg, extra))
