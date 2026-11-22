"""Validační skript pro Stop hook (DoD pro skill bug-reporting a testování).

Pravidlo projektu:
Testování musí VŽDY proběhnout s plným bug reportingem a důkazy.
Hook zabezpečuje, že jakýkoliv běh testů nebo požadavek na testování (i při pokusu vynechat report)
nesmí skončit bez vygenerovaného HTML přehledu chyb (reports/bug_overview.html) a kompletních reportů.

Principy z kapitoly 5 kurzu:
1. Zasahuje při jakémkoliv požadavku na testování nebo běhu testů (analyzuje transcript relace,
   uživatelský vstup i aktivní marker reports/.bug_reporting_active).
2. Nekontroluje jen existenci souboru, ale HLOUBKOVÝ OBSAH:
   - Zda existuje reports/bug_overview.html i reports/test_run_data.json.
   - Zda běh proběhl přes runner se sběrem důkazů (run_tests_with_evidence.py).
   - Zda je v HTML reportován KAŽDÝ padající test.
   - Zda každý report obsahuje VŠECHNA povinná pole:
     * Kroky k reprodukci (steps_to_reproduce)
     * Očekávaný výsledek (expected_result)
     * Skutečný výsledek (actual_result)
     * Prostředí (environment)
     * Důkaz (evidence) – soubor musí fyzicky existovat na disku!
3. Ochrana proti zacyklení a chybám:
   - Na výstup VŽDY vrátí validní JSON, nikdy nespadne neošetřenou výjimkou.
   - Sleduje continuationActive a executionNum pro bezpečné uvolnění po opakovaných pokusech.
"""

import json
import os
import re
import sys
from pathlib import Path

def find_project_root(payload: dict | None = None) -> Path:
    """Dynamicky a spolehlivě určí kořenový adresář projektu."""
    if payload:
        workspace_paths = payload.get("workspacePaths")
        if workspace_paths and os.path.exists(workspace_paths[0]):
            return Path(workspace_paths[0])
    curr = Path(__file__).resolve().parent
    for _ in range(5):
        if (curr / "pyproject.toml").exists() or (curr / "tests").exists():
            return curr
        curr = curr.parent
    return Path(__file__).resolve().parents[2]


# Cesta k projektu
PROJECT_ROOT = find_project_root()
REPORTS_DIR = PROJECT_ROOT / "reports"
MARKER_FILE = REPORTS_DIR / ".bug_reporting_active"
RUN_DATA_FILE = REPORTS_DIR / "test_run_data.json"
HTML_OUTPUT_FILE = REPORTS_DIR / "bug_overview.html"
BUG_REPORTS_FILE = REPORTS_DIR / "bug_reports.json"

PLACEHOLDER_PATTERN = re.compile(
    r"\b(todo|tbd|doplnit|vyplnit|n/a|placeholder|none|unknown|chyba)\b",
    re.IGNORECASE,
)


def respond(decision: str, reason: str | None = None) -> None:
    """Vypíše validní JSON odpověď pro Antigravity hook a ukončí proces."""
    out = {"decision": decision}
    if reason:
        out["reason"] = reason
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)


def is_testing_or_reporting_active(payload: dict) -> tuple[bool, str]:
    """Zkontroluje, zda v aktuální relaci proběhlo testování nebo byl spuštěn/vyžádán test run / bug reporting.

    Pravidlo projektu: Testování musí VŽDY proběhnout s plným bug reportingem a důkazy.
    """
    # 1. Aktivní marker běhu runneru run_tests_with_evidence.py
    if MARKER_FILE.exists():
        return True, "Aktivní marker testování (reports/.bug_reporting_active)"

    last_user_input = (payload.get("lastUserInput") or "").strip()

    # Kontrola meta-dotazů / editací hooku samotného (pokud uživatel řeší samotný hook a nespouští testy)
    is_meta_check = False
    if last_user_input:
        text_lower = last_user_input.lower()
        if any(w in text_lower for w in ["zkontroluj to a případně", "zkontroluj hook", "ověř hook", "uprav hook", "oprav hook"]):
            is_meta_check = True

    # 2. Kontrola transcriptu relace (zda v aktuálním tahu agent spustil testy)
    transcript_path_str = payload.get("transcriptPath")
    if transcript_path_str:
        tp = Path(transcript_path_str)
        if tp.exists():
            try:
                size = tp.stat().st_size
                with open(tp, "r", encoding="utf-8", errors="ignore") as f:
                    if size > 300_000:
                        f.seek(size - 300_000)
                    lines = f.readlines()

                # Zaměření na aktuální tah (od posledního vstupu uživatele)
                last_user_idx = -1
                for idx, line in enumerate(lines):
                    if '"type":"USER_INPUT"' in line or '"type": "USER_INPUT"' in line or '"source":"USER' in line or '"source": "USER' in line:
                        last_user_idx = idx

                current_turn_lines = lines[last_user_idx:] if last_user_idx != -1 else lines

                for line in current_turn_lines:
                    # Detekce spuštění pytestu nebo skriptů bug-reportingu v příkazech
                    if any(t in line for t in [
                        "pytest",
                        "run_tests_with_evidence",
                        "generate_bug_overview",
                        "verify_bug_reports",
                        "bug-reporting",
                        "test_*.py",
                    ]):
                        return True, "V aktuálním tahu bylo detekováno spuštění testů nebo nástrojů bug reportingu"

                    # Detekce výstupu pytestu
                    if any(out in line for out in ["test session starts", "rootdir:", "collected "]):
                        return True, "V aktuálním tahu byl detekován výstup běhu testů (pytest)"
            except Exception:
                pass

    if is_meta_check:
        return False, ""

    # 3. Kontrola posledního uživatelského vstupu
    if last_user_input:
        text_lower = last_user_input.lower()

        # Explicitní bug-reporting
        if any(k in text_lower for k in [
            "bug-reporting", "reportování chyb", "chybový report", "reportovat chyby",
            "bug reporting", "bug report", "bug-report", "přehled chyb", "výsledky testů"
        ]):
            return True, f"Uživatelský požadavek na bug reporting ('{last_user_input}')"

        # Přímá zmínka pytestu
        if re.search(r"\bpytest\b", text_lower):
            return True, f"Uživatelský požadavek na spuštění pytest ('{last_user_input}')"

        # Požadavek na spuštění testů v češtině i angličtině (i s negací typu 'negeneruj report')
        test_verbs = r"(spus[tť]\w*|prov[eé][dď]\w*|běh\w*|proběh\w*|otest\w*|test\w*|přetest\w*|run\w*|exec\w*|uděl\w*)"
        test_nouns = r"(test\w*|suite\w*|sadu|sady|sadě)"
        if re.search(rf"\b{test_verbs}\b.*\b{test_nouns}\b", text_lower) or re.search(rf"\b{test_nouns}\b.*\b{test_verbs}\b", text_lower):
            return True, f"Uživatelský požadavek na testování ('{last_user_input}')"

        # Jednoslovné příkazy k testování: "otestuj to", "testuj"
        if re.search(r"\b(otestuj|otestujte|otestovat|přetestuj|přetestovat)\b", text_lower):
            return True, f"Uživatelský požadavek na testování ('{last_user_input}')"

        # Pokus o vynechání nebo neúplný report ("skonči bez reportu", "skonči s neúplným reportem", "negeneruj report", "bez reportu")
        if re.search(r"\b(bez|neúpln\w*|vynech\w*|negeneruj\w*|přeskoč\w*)\b.*\b(report\w*|přehled\w*|chyb\w*|bug\w*)\b", text_lower) or \
           re.search(r"\b(skonč\w*|ukonč\w*|konči\w*)\b.*\b(bez|neúpln\w*)\b", text_lower):
            return True, f"Detekován pokus o vynechání nebo neúplný bug report ('{last_user_input}')"

    return False, ""


def validate_content() -> list[str]:
    """Hloubkově ověří obsah HTML přehledu a bug reportů."""
    errors = []

    # 1. Kontrola, zda testy proběhly se sběrem dat
    if not RUN_DATA_FILE.exists():
        errors.append(
            "Chybí soubor 'reports/test_run_data.json' z běhu testů. "
            "Každé testování v projektu musí být spuštěno se sběrem důkazů a metadat: "
            "python .agents/skills/bug-reporting/scripts/run_tests_with_evidence.py"
        )
        return errors

    # Pokud testy běžely, ale chybí marker z run_tests_with_evidence.py (testy běžely např. přímo přes holý pytest)
    if not MARKER_FILE.exists():
        errors.append(
            "Testy v aktuální relaci nebyly spuštěny přes runner 'run_tests_with_evidence.py' (chybí aktivní marker). "
            "Spusťte testy pomocí: python .agents/skills/bug-reporting/scripts/run_tests_with_evidence.py"
        )
        return errors

    try:
        run_data = json.loads(RUN_DATA_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"Chyba při čtení run_data ('{RUN_DATA_FILE}'): {e}")
        return errors

    failed_tests = run_data.get("failed_tests", [])

    # 2. Kontrola existence HTML reportu
    if not HTML_OUTPUT_FILE.exists():
        errors.append(
            "Chybí výsledný přehled chyb 'reports/bug_overview.html'. "
            "Vygenerujte jej pomocí: python .agents/skills/bug-reporting/scripts/generate_bug_overview.py"
        )
        return errors

    try:
        html_content = HTML_OUTPUT_FILE.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(f"Nelze přečíst 'reports/bug_overview.html': {e}")
        return errors

    if not html_content.strip():
        errors.append("Soubor 'reports/bug_overview.html' je prázdný!")
        return errors

    # Pokud žádné testy neselhaly
    if len(failed_tests) == 0:
        if "Všechny testy prošly" not in html_content and "Úspěšné testy" not in html_content:
            errors.append("Všechny testy prošly, ale 'reports/bug_overview.html' neobsahuje potvrzení o úspěchu.")
        return errors

    # Načtení reportů
    bug_reports = []
    if BUG_REPORTS_FILE.exists():
        try:
            bug_reports = json.loads(BUG_REPORTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    if not bug_reports:
        # Fallback z HTML
        m = re.search(r'<script type="application/json" id="bug-reports-metadata">\s*(\{.*?\})\s*</script>', html_content, re.DOTALL)
        if m:
            try:
                meta = json.loads(m.group(1))
                bug_reports = meta.get("bug_reports", [])
            except Exception:
                pass

    if len(bug_reports) < len(failed_tests):
        errors.append(
            f"HTML přehled obsahuje pouze {len(bug_reports)} reportů, ale v testech selhalo {len(failed_tests)} testů! "
            f"Každý padající test musí mít svůj report."
        )

    failed_names = {t["name"] for t in failed_tests}
    reported_names = {b.get("test_name") for b in bug_reports if b.get("test_name")}
    missing_tests = failed_names - reported_names
    if missing_tests:
        errors.append(f"Chybí reporty pro tyto padající testy: {', '.join(sorted(missing_tests))}")

    # Kontrola povinných polí
    for bug in bug_reports:
        bug_id = bug.get("id", "Neznámý BUG")
        test_name = bug.get("test_name", "neznámý test")

        # 1. Kroky k reprodukci
        steps = bug.get("steps_to_reproduce")
        if not steps:
            errors.append(f"[{bug_id} ({test_name})] Chybí kroky k reprodukci (steps_to_reproduce).")
        elif isinstance(steps, list):
            valid_steps = [s for s in steps if str(s).strip() and not PLACEHOLDER_PATTERN.search(str(s).strip())]
            if not valid_steps:
                errors.append(f"[{bug_id} ({test_name})] Kroky k reprodukci jsou prázdné nebo obsahují zakázané zástupné texty (TODO/TBD).")

        # 2. Očekávaný výsledek
        expected = str(bug.get("expected_result", "")).strip()
        if len(expected) < 8 or PLACEHOLDER_PATTERN.fullmatch(expected.lower()):
            errors.append(f"[{bug_id} ({test_name})] Chybí nebo je příliš stručný/zástupný očekávaný výsledek (expected_result).")

        # 3. Skutečný výsledek
        actual = str(bug.get("actual_result", "")).strip()
        if len(actual) < 8 or PLACEHOLDER_PATTERN.fullmatch(actual.lower()):
            errors.append(f"[{bug_id} ({test_name})] Chybí nebo je příliš stručný/zástupný skutečný výsledek (actual_result).")

        # 4. Prostředí
        env = str(bug.get("environment", "")).strip()
        if len(env) < 5 or PLACEHOLDER_PATTERN.fullmatch(env.lower()):
            errors.append(f"[{bug_id} ({test_name})] Chybí platné specifikace prostředí (environment: OS, prohlížeč, URL).")

        # 5. Důkaz (evidence) a existence na disku
        evidence = str(bug.get("evidence", "")).strip()
        if not evidence or PLACEHOLDER_PATTERN.fullmatch(evidence.lower()):
            errors.append(f"[{bug_id} ({test_name})] Chybí odkaz na důkaz (evidence: screenshot nebo trace).")
        else:
            evidence_path = PROJECT_ROOT / evidence
            if not evidence_path.exists():
                errors.append(f"[{bug_id} ({test_name})] Soubor důkazu '{evidence}' na disku neexistuje!")

    return errors


def main():
    global PROJECT_ROOT, REPORTS_DIR, MARKER_FILE, RUN_DATA_FILE, HTML_OUTPUT_FILE, BUG_REPORTS_FILE
    from datetime import datetime
    payload = {}
    try:
        raw = sys.stdin.buffer.read()
        if raw:
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("cp1250", errors="replace")
            payload = json.loads(text) if text.strip() else {}
    except Exception:
        pass

    try:
        if payload:
            new_root = find_project_root(payload)
            if new_root != PROJECT_ROOT:
                PROJECT_ROOT = new_root
                REPORTS_DIR = PROJECT_ROOT / "reports"
                MARKER_FILE = REPORTS_DIR / ".bug_reporting_active"
                RUN_DATA_FILE = REPORTS_DIR / "test_run_data.json"
                HTML_OUTPUT_FILE = REPORTS_DIR / "bug_overview.html"
                BUG_REPORTS_FILE = REPORTS_DIR / "bug_reports.json"

        # KROK 1: Scoping – kontrola, zda proběhlo testování nebo byl vznesen požadavek na testování/bug-reporting
        active, trigger_reason = is_testing_or_reporting_active(payload)
        if not active:
            respond("allow")

        # KROK 2: Ochrana proti zacyklení (Anti-Infinite Loop)
        # Pokud Stop hook již opakovaně vynutil pokračování a agent je v úzkých,
        # po 4 pokusech umožníme předání, aby nedošlo k vyčerpání tokenů.
        execution_num = payload.get("executionNum", 0)
        continuation_active = payload.get("continuationActive", False)
        if continuation_active and execution_num >= 4:
            respond("allow")

        # KROK 3: Hloubková kontrola obsahu (DoD testování a bug reportingu)
        errors = validate_content()

        if errors:
            reason_msg = (
                f"🛑 Definice hotovo (DoD): Testování v projektu musí být vždy zakončeno bug reportingem!\n"
                f"Důvod aktivace kontroly: {trigger_reason}\n\n"
                "Nalezené nedostatky:\n"
                + "\n".join(f"- {e}" for e in errors)
                + "\n\nPostup pro splnění Definice hotovo:\n"
                + "1. Spusťte testy se sběrem důkazů: python .agents/skills/bug-reporting/scripts/run_tests_with_evidence.py\n"
                + "2. Zkontrolujte reports/bug_reports.json a doplňte povinná pole pro padající testy\n"
                + "3. Vygenerujte HTML přehled: python .agents/skills/bug-reporting/scripts/generate_bug_overview.py\n"
                + "4. Ověřte stav pomocí: python .agents/skills/bug-reporting/scripts/verify_bug_reports.py"
            )
            respond("continue", reason_msg)

        # Všechny podmínky splněny -> povolení ukončení
        respond("allow")

    except Exception:
        # Bezpečnostní zásada: při neočekávané chybě hooku nezablokovat agenta
        respond("allow")


if __name__ == "__main__":
    main()
