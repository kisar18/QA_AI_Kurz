#!/usr/bin/env python3
"""
Skript 'Definice hotovo' pro manuální test casy (DoD Validator).

Ověřuje:
1. Integritu specifikace User Story (zákaz neoprávněných úprav zdrojové US v gitu – Anti-Reward Hacking).
2. Existenci a kompletní strukturu souboru s test casy (ID, Název, AC, Typ, Předpoklady, Kroky, Očekávaný výsledek).
3. Žádné nevyplněné placeholdery (TODO, TBD, DOPLNIT, PLACEHOLDER).
4. Přítomnost pozitivních i negativních/hraničních scénářů.
5. 100% pokrytí akceptačních kritérií (AC) z příslušné User Story.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class TestCase:
    def __init__(self, tc_id: str, title: str):
        self.tc_id = tc_id
        self.title = title
        self.covered_ac: List[str] = []
        self.test_type: str = ""
        self.preconditions: List[str] = []
        self.test_data: List[str] = []
        self.steps: List[str] = []
        self.expected_result: List[str] = []
        self.raw_lines: List[str] = []


def check_story_integrity(story_file: Path) -> Optional[str]:
    """Zkontroluje, zda zdrojový soubor s User Stories nebyl lokálně modifikován (ochrana proti reward hackingu)."""
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain", str(story_file)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if res.returncode == 0 and res.stdout.strip():
            return (
                f"Zdrojový soubor '{story_file}' vykazuje necommitované změny v gitu! "
                "Agent nesmí upravovat specifikaci User Stories za účelem usnadnění průchodu testů."
            )
    except Exception:
        # Pokud git není dostupný, kontrola tiše projde
        pass
    return None


def parse_test_cases(file_path: Path) -> Tuple[List[TestCase], Optional[str]]:
    """Parsuje markdown soubor a vrací seznam TestCase objektů a detekované US-ID."""
    if not file_path.exists():
        raise FileNotFoundError(f"Soubor s test casy nebyl nalezen: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    detected_us_id: Optional[str] = None
    # Pokus o detekci US-ID z hlavičky (např. **Zdrojová User Story:** US-02)
    us_header_match = re.search(r"Zdrojová User Story:\*{0,2}\s*(US-\d+)", content, re.IGNORECASE)
    if us_header_match:
        detected_us_id = us_header_match.group(1).upper()
    else:
        # Pokus o detekci ze jména souboru (např. TC_US-02.md nebo TC_US-02_registrace.md)
        fn_match = re.search(r"(US-\d+)", file_path.name, re.IGNORECASE)
        if fn_match:
            detected_us_id = fn_match.group(1).upper()

    test_cases: List[TestCase] = []
    current_tc: Optional[TestCase] = None
    current_section: Optional[str] = None

    tc_header_re = re.compile(r"^###\s*\[?([A-Za-z0-9_-]+)\]?\s*[:-]?\s*(.*)$")

    for line in lines:
        stripped = line.strip()

        # Detekce začátku nového test case
        header_match = tc_header_re.match(stripped)
        if header_match and (header_match.group(1).upper().startswith("TC") or "TC-" in header_match.group(1).upper()):
            tc_id = header_match.group(1).strip()
            title = header_match.group(2).strip()
            current_tc = TestCase(tc_id, title)
            test_cases.append(current_tc)
            current_section = None
            continue

        if current_tc is None:
            continue

        current_tc.raw_lines.append(line)

        # Detekce sekcí uvnitř test case
        ac_match = re.search(r"\*\*Pokrývá kritérium:\*\*\s*(.*)$", stripped, re.IGNORECASE)
        if not ac_match:
            ac_match = re.search(r"\*\*(?:Kritérium|AC):\*\*\s*(.*)$", stripped, re.IGNORECASE)
        if ac_match:
            ac_text = ac_match.group(1).strip()
            # Extrakce AC kódů (např. AC-1, AC-02, AC 1)
            found_acs = re.findall(r"AC[- ]?(\d+)", ac_text, re.IGNORECASE)
            for num in found_acs:
                current_tc.covered_ac.append(f"AC-{int(num)}")
            current_section = None
            continue

        type_match = re.search(r"\*\*Typ testu:\*\*\s*(.*)$", stripped, re.IGNORECASE)
        if type_match:
            current_tc.test_type = type_match.group(1).strip()
            current_section = None
            continue

        if re.search(r"\*\*Předpoklady:\*\*", stripped, re.IGNORECASE):
            current_section = "preconditions"
            continue
        elif re.search(r"\*\*Testovací data:\*\*", stripped, re.IGNORECASE):
            current_section = "test_data"
            continue
        elif re.search(r"\*\*Kroky:\*\*", stripped, re.IGNORECASE):
            current_section = "steps"
            continue
        elif re.search(r"\*\*Očekávaný výsledek:\*\*", stripped, re.IGNORECASE):
            current_section = "expected_result"
            continue

        # Přidání obsahu do aktuální sekce
        if current_section and stripped:
            if current_section == "preconditions":
                current_tc.preconditions.append(stripped)
            elif current_section == "test_data":
                current_tc.test_data.append(stripped)
            elif current_section == "steps":
                current_tc.steps.append(stripped)
            elif current_section == "expected_result":
                current_tc.expected_result.append(stripped)

    return test_cases, detected_us_id


def extract_acceptance_criteria_from_story(story_file: Path, us_id: str) -> List[Tuple[int, str]]:
    """Extrahuje akceptační kritéria pro danou US ze souboru specifikace."""
    if not story_file.exists():
        return []

    content = story_file.read_text(encoding="utf-8")

    # Hledáme blok dané User Story (např. #### US-02: Registrace ... až po další #### nebo konec)
    us_pattern = rf"####\s*{re.escape(us_id)}[:\s](.*?)(?=####\s*US-|\Z)"
    match = re.search(us_pattern, content, re.DOTALL | re.IGNORECASE)
    if not match:
        return []

    us_block = match.group(1)

    # V bloku hledáme sekci Akceptační kritéria
    ac_match = re.search(r"- \*\*Akceptační kritéria:\*\*(.*?)(?=- \*\*|\Z)", us_block, re.DOTALL | re.IGNORECASE)
    if not ac_match:
        return []

    ac_text = ac_match.group(1)
    criteria: List[Tuple[int, str]] = []
    idx = 1
    for line in ac_text.splitlines():
        line_clean = line.strip()
        if line_clean.startswith("- ") or line_clean.startswith("* "):
            criterion = line_clean[2:].strip()
            if criterion:
                criteria.append((idx, criterion))
                idx += 1

    return criteria


def validate_dod(
    tc_file: Path,
    story_file: Optional[Path] = None,
    us_id: Optional[str] = None
) -> Tuple[bool, List[str], List[str], Dict[str, any]]:
    """
    Provede kontrolu Definition of Done.
    Vrací: (is_passed, errors, warnings, metrics)
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 0. Kontrola integrity User Story (Anti-Reward Hacking)
    if story_file and story_file.exists():
        integrity_error = check_story_integrity(story_file)
        if integrity_error:
            errors.append(integrity_error)

    test_cases, detected_us_id = parse_test_cases(tc_file)
    effective_us_id = us_id or detected_us_id

    metrics = {
        "us_id": effective_us_id or "Neznámé",
        "tc_count": len(test_cases),
        "ac_count": 0,
        "covered_ac_count": 0,
        "positive_count": 0,
        "negative_count": 0,
        "boundary_count": 0,
    }

    if not test_cases:
        errors.append("V souboru nebyly nalezeny žádné test casy ve formátu '### [TC-ID] Název'.")
        return False, errors, warnings, metrics

    # 1. Kontrola unikátnosti ID test casů
    seen_ids: Set[str] = set()
    for tc in test_cases:
        if tc.tc_id in seen_ids:
            errors.append(f"Duplicitní ID test case: '{tc.tc_id}'. Každý test case musí mít unikátní ID.")
        seen_ids.add(tc.tc_id)

    # 2. Kontrola povinné struktury jednotlivých TC
    all_covered_ac: Set[str] = set()
    placeholder_pattern = re.compile(r"\b(TODO|TBD|DOPLNIT|PLACEHOLDER)\b", re.IGNORECASE)

    for tc in test_cases:
        prefix = f"Test case '{tc.tc_id}'"

        # Název
        if not tc.title:
            errors.append(f"{prefix}: Chybí název / cíl test case.")
        elif placeholder_pattern.search(tc.title):
            errors.append(f"{prefix}: Název obsahuje nevyplněný placeholder ({tc.title}).")

        # Pokrývá kritérium
        if not tc.covered_ac:
            errors.append(f"{prefix}: Není uvedeno pokrývané akceptační kritérium (**Pokrývá kritérium:** AC-X).")
        else:
            all_covered_ac.update(tc.covered_ac)

        # Typ testu
        if not tc.test_type:
            errors.append(f"{prefix}: Není vyplněn typ testu (**Typ testu:** Pozitivní / Negativní / Hraniční).")
        else:
            t_lower = tc.test_type.lower()
            if "pozitivní" in t_lower or "positive" in t_lower:
                metrics["positive_count"] += 1
            elif "negativní" in t_lower or "negative" in t_lower:
                metrics["negative_count"] += 1
            elif "hraniční" in t_lower or "boundary" in t_lower:
                metrics["boundary_count"] += 1

        # Předpoklady
        if not tc.preconditions:
            errors.append(f"{prefix}: Chybí sekce **Předpoklady:**.")
        else:
            for p in tc.preconditions:
                if placeholder_pattern.search(p):
                    errors.append(f"{prefix}: V sekci Předpoklady se nachází placeholder ({p}).")

        # Kroky
        if not tc.steps:
            errors.append(f"{prefix}: Chybí testovací kroky (**Kroky:**).")
        else:
            has_numbered_step = any(re.match(r"^\d+\.", s) for s in tc.steps)
            if not has_numbered_step:
                errors.append(f"{prefix}: Kroky musí obsahovat alespoň jeden očíslovaný krok (např. '1. Otevři...').")
            for s in tc.steps:
                if placeholder_pattern.search(s):
                    errors.append(f"{prefix}: V krocích se nachází placeholder ({s}).")

        # Očekávaný výsledek
        if not tc.expected_result:
            errors.append(f"{prefix}: Chybí **Očekávaný výsledek:**.")
        else:
            for er in tc.expected_result:
                if placeholder_pattern.search(er):
                    errors.append(f"{prefix}: V očekávaném výsledku se nachází placeholder ({er}).")

    # 3. Kontrola diverzity typů testů
    if metrics["positive_count"] == 0:
        errors.append("Sada neobsahuje žádný pozitivní test (Happy Path).")
    if (metrics["negative_count"] + metrics["boundary_count"]) == 0:
        errors.append("Sada neobsahuje žádný negativní ani hraniční scénář (nutné pro robustní testování).")

    # 4. Kontrola 100% pokrytí akceptačních kritérií
    if story_file and effective_us_id:
        ac_list = extract_acceptance_criteria_from_story(story_file, effective_us_id)
        metrics["ac_count"] = len(ac_list)

        if ac_list:
            missing_ac: List[str] = []
            for ac_idx, ac_desc in ac_list:
                ac_code = f"AC-{ac_idx}"
                if ac_code in all_covered_ac:
                    metrics["covered_ac_count"] += 1
                else:
                    short_desc = (ac_desc[:60] + "...") if len(ac_desc) > 60 else ac_desc
                    missing_ac.append(f"{ac_code} (\"{short_desc}\")")

            if missing_ac:
                errors.append(
                    f"Nejsou pokryta všechna akceptační kritéria pro {effective_us_id}! "
                    f"Chybí test case pro: {', '.join(missing_ac)}"
                )
        else:
            warnings.append(
                f"Pro {effective_us_id} v souboru {story_file.name} nebyla nalezena žádná akceptační kritéria k ověření."
            )

    is_passed = (len(errors) == 0)
    return is_passed, errors, warnings, metrics


def main():
    parser = argparse.ArgumentParser(
        description="Ověření Definition of Done (DoD) pro manuální test casy."
    )
    parser.add_argument("tc_file", type=Path, help="Cesta k markdown souboru s test casy (např. manual_tests/TC_US-02.md)")
    parser.add_argument("--story", type=Path, default=Path("user stories/požadavky_ust_podle_src.md"), help="Cesta k souboru s User Stories")
    parser.add_argument("--us-id", type=str, default=None, help="Identifikátor User Story (např. US-02)")
    parser.add_argument("--quiet", action="store_true", help="Potlačí detailní výpis, vrátí pouze exit code")

    args = parser.parse_args()

    if not args.tc_file.exists():
        print(f"❌ CHYBA: Zadaný soubor s test casy neexistuje: {args.tc_file}")
        sys.exit(1)

    story_file = args.story if args.story.exists() else None

    is_passed, errors, warnings, metrics = validate_dod(
        tc_file=args.tc_file,
        story_file=story_file,
        us_id=args.us_id
    )

    if args.quiet:
        sys.exit(0 if is_passed else 1)

    # Výpis přehledu do konzole
    print("=" * 70)
    print("📋 VALIDACE DEFINICE HOTOVO (DoD) – MANUÁLNÍ TEST CASY")
    print("=" * 70)
    print(f"Soubor test casů:     {args.tc_file}")
    print(f"User Story:           {metrics['us_id']}")
    print(f"Počet test casů:      {metrics['tc_count']}")
    print(f"Typy testů:           Pozitivní: {metrics['positive_count']} | Negativní: {metrics['negative_count']} | Hraniční: {metrics['boundary_count']}")

    if metrics["ac_count"] > 0:
        coverage_pct = (metrics["covered_ac_count"] / metrics["ac_count"]) * 100
        print(f"Pokrytí kritérií AC:  {metrics['covered_ac_count']}/{metrics['ac_count']} ({coverage_pct:.0f} %)")

    print("-" * 70)

    if warnings:
        print("⚠️  VAROVÁNÍ:")
        for w in warnings:
            print(f"   • {w}")
        print("-" * 70)

    if errors:
        print("❌ NALEZENÉ NEDOSTATKY (NENÍ HOTOVO):")
        for e in errors:
            print(f"   • {e}")
        print("=" * 70)
        print("💥 VÝSLEDEK: NENÍ HOTOVO – Agent musí opravit výše uvedené chyby.")
        print("ℹ️  Pokud je chyba způsobena nejednoznačnou či neúplnou User Story, ohlaste stav BLOKOVÁNO.")
        print("=" * 70)
        sys.exit(1)
    else:
        print("✅ VŠECHNA KRITÉRIA DEFINICE HOTOVO JSOU SPLNĚNA!")
        print("=" * 70)
        print("🎉 VÝSLEDEK: HOTOVO – Test casy jsou připraveny k finálnímu schválení uživatelem.")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
