"""Skript pro ověření Definice hotovo (DoD) bug reportingu.

Kontroluje:
1. Existenci a aktuálnost reports/test_run_data.json a reports/bug_overview.html.
2. Shodu počtu padajících testů s počtem nahlášených chyb v HTML přehledu.
3. Přítomnost všech povinných polí v každém bug reportu:
   - Kroky k reprodukci (steps_to_reproduce)
   - Očekávaný výsledek (expected_result)
   - Skutečný výsledek (actual_result)
   - Prostředí (environment)
   - Důkaz (evidence) – ověření fyzické existence souboru na disku!
4. Zákaz placeholderů a prázdných hodnot.

Návratové kódy:
  0 = HOTOVO (všechny podmínky splněny)
  1 = NENÍ HOTOVO (seznam nalezených nedostatků)
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
REPORTS_DIR = PROJECT_ROOT / "reports"
RUN_DATA_FILE = REPORTS_DIR / "test_run_data.json"
BUG_REPORTS_FILE = REPORTS_DIR / "bug_reports.json"
HTML_OUTPUT_FILE = REPORTS_DIR / "bug_overview.html"

PLACEHOLDER_PATTERN = re.compile(
    r"\b(todo|tbd|doplnit|vyplnit|n/a|placeholder|none|unknown|chyba)\b",
    re.IGNORECASE,
)


def validate_bug_reporting_dod() -> tuple[bool, list[str]]:
    """Zkontroluje všechna kritéria Definice hotovo."""
    errors = []

    # 1. Kontrola existence souboru z běhu testů
    if not RUN_DATA_FILE.exists():
        errors.append(f"Chybí záznam o běhu testů: '{RUN_DATA_FILE}'. Spusťte nejprve run_tests_with_evidence.py.")
        return False, errors

    try:
        run_data = json.loads(RUN_DATA_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"Nelze přečíst '{RUN_DATA_FILE}': {e}")
        return False, errors

    failed_tests = run_data.get("failed_tests", [])

    # 2. Kontrola existence HTML přehledu
    if not HTML_OUTPUT_FILE.exists():
        errors.append(f"Chybí výsledný HTML přehled chyb: '{HTML_OUTPUT_FILE}'. Spusťte generate_bug_overview.py.")
        return False, errors

    html_content = HTML_OUTPUT_FILE.read_text(encoding="utf-8")
    if not html_content.strip():
        errors.append(f"HTML přehled '{HTML_OUTPUT_FILE}' je prázdný.")
        return False, errors

    # Pokud žádný test neselhal a v run_data je 0 pádů
    if len(failed_tests) == 0:
        if "Všechny testy prošly" not in html_content and "Úspěšné testy" not in html_content:
            errors.append("Testy prošly, ale HTML přehled neobsahuje potvrzení o úspěšném běhu.")
            return False, errors
        return True, []

    # 3. Kontrola načtení bug reportů (ze souboru nebo z embedded JSON v HTML)
    bug_reports = []
    if BUG_REPORTS_FILE.exists():
        try:
            bug_reports = json.loads(BUG_REPORTS_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"Nelze přečíst '{BUG_REPORTS_FILE}': {e}")

    # Fallback: pokus o extrakci z embedded JSON v HTML
    if not bug_reports:
        match = re.search(r'<script type="application/json" id="bug-reports-metadata">\s*(\{.*?\})\s*</script>', html_content, re.DOTALL)
        if match:
            try:
                meta = json.loads(match.group(1))
                bug_reports = meta.get("bug_reports", [])
            except Exception:
                pass

    # 4. Kontrola počtu reportů vs. počtu padajících testů
    if len(bug_reports) < len(failed_tests):
        errors.append(
            f"Počet bug reportů ({len(bug_reports)}) neodpovídá počtu padajících testů ({len(failed_tests)}). "
            f"Každý padající test musí mít svůj report!"
        )

    # Mapa testů z run_data
    failed_test_names = {t["name"] for t in failed_tests}
    reported_test_names = {b.get("test_name") for b in bug_reports if b.get("test_name")}

    missing_tests = failed_test_names - reported_test_names
    if missing_tests:
        errors.append(f"Následující padající testy nemají odpovídající bug report: {', '.join(sorted(missing_tests))}")

    # 5. Kontrola povinných polí u každého bug reportu
    for idx, bug in enumerate(bug_reports, 1):
        bug_id = bug.get("id", f"Report #{idx}")
        test_ref = bug.get("test_name", "neznámý test")

        # a) Kroky k reprodukci
        steps = bug.get("steps_to_reproduce")
        if not steps:
            errors.append(f"[{bug_id} / {test_ref}] Chybí pole 'Kroky k reprodukci' (steps_to_reproduce).")
        elif isinstance(steps, list):
            valid_steps = [s for s in steps if str(s).strip() and not PLACEHOLDER_PATTERN.search(str(s).strip())]
            if not valid_steps:
                errors.append(f"[{bug_id} / {test_ref}] Kroky k reprodukci jsou prázdné nebo obsahují pouze placeholdery.")
        elif isinstance(steps, str):
            if len(steps.strip()) < 10 or PLACEHOLDER_PATTERN.search(steps.strip()):
                errors.append(f"[{bug_id} / {test_ref}] Kroky k reprodukci jsou příliš krátké nebo obsahují placeholdery.")

        # b) Očekávaný výsledek
        expected = str(bug.get("expected_result", "")).strip()
        if not expected or len(expected) < 8 or PLACEHOLDER_PATTERN.fullmatch(expected.lower()):
            errors.append(f"[{bug_id} / {test_ref}] Chybí nebo je neplatný 'Očekávaný výsledek' (expected_result).")

        # c) Skutečný výsledek
        actual = str(bug.get("actual_result", "")).strip()
        if not actual or len(actual) < 8 or PLACEHOLDER_PATTERN.fullmatch(actual.lower()):
            errors.append(f"[{bug_id} / {test_ref}] Chybí nebo je neplatný 'Skutečný výsledek' (actual_result).")

        # d) Prostředí
        env = str(bug.get("environment", "")).strip()
        if not env or len(env) < 5 or PLACEHOLDER_PATTERN.fullmatch(env.lower()):
            errors.append(f"[{bug_id} / {test_ref}] Chybí nebo je neplatné 'Prostředí' (environment).")

        # e) Odkaz na důkaz a ověření existence souboru
        evidence = str(bug.get("evidence", "")).strip()
        if not evidence or PLACEHOLDER_PATTERN.fullmatch(evidence.lower()):
            errors.append(f"[{bug_id} / {test_ref}] Chybí 'Odkaz na důkaz' (evidence - screenshot nebo trace).")
        else:
            evidence_path = PROJECT_ROOT / evidence
            if not evidence_path.exists():
                errors.append(f"[{bug_id} / {test_ref}] Soubor důkazu '{evidence}' neexistuje na disku!")

        # f) Ověření, že text reportu je přítomen v samotném HTML
        if bug.get("id") and bug.get("id") not in html_content:
            errors.append(f"[{bug_id}] ID reportu nebylo nalezeno v HTML přehledu '{HTML_OUTPUT_FILE.name}'.")

    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    print("=" * 60)
    print("🔍 Kontrola Definice hotovo (DoD): Reportování chyb")
    print("=" * 60)

    is_valid, errors = validate_bug_reporting_dod()

    if is_valid:
        print("\n✅ HOTOVO: Všechny podmínky Definice hotovo byly splněny.")
        print(f"📄 HTML přehled: {HTML_OUTPUT_FILE}")
        sys.exit(0)
    else:
        print("\n❌ NENÍ HOTOVO: Nalezeny následující nedostatky:")
        for err in errors:
            print(f"  - {err}")
        print("\nOpravte výše uvedené chyby před dokončením úkolu.")
        sys.exit(1)


if __name__ == "__main__":
    main()
