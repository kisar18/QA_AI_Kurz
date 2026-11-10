"""Skript "Definice hotovo" (Definition of Done) pro automatizované testy.

Ověřuje splnění všech požadavků před schválením a začleněním:
1. 100% mapování schválených Test Casů (všechna TC ID ze souboru .md mají test).
2. Statická čistota a pravidla projektu (Zero-Inline-Locators v testech, zákaz time.sleep a wait_for_timeout, zákaz slabých assertů).
3. Test stability a odolnosti proti flakiness (opakované spuštění v pytestu 3x po sobě).

Použití:
    python verify_automated_tests.py --tc-file manual_tests/TC_US-02.md --test-file tests/auth/test_register.py [--runs 3]

Návratový kód:
    0 = HOTOVO (všechna kritéria splněna)
    1 = NENÍ HOTOVO (nalezeny chyby nebo pád v některém z běhů)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


# Regex pro detekci TC identifikátorů (např. [TC-US02-01] nebo TC-US02-01)
TC_ID_PATTERN = re.compile(r"\b(TC-[A-Za-z0-9_-]+)\b")

# Zakázané vzory v testovacích souborech (tests/)
TEST_FORBIDDEN_PATTERNS = [
    (re.compile(r"\.locator\("), "Inline locator v testu (.locator) – lokátory patří výhradně do Page Objectů"),
    (re.compile(r"\.get_by_\w+\("), "Inline locator v testu (.get_by_*) – lokátory patří výhradně do Page Objectů"),
    (re.compile(r"xpath\s*="), "Použití XPath selektoru v testu"),
    (re.compile(r"time\.sleep\("), "Pevné čekání time.sleep() – použij web-first expect() s auto-retry"),
    (re.compile(r"wait_for_timeout\("), "Pevné čekání wait_for_timeout() – použij web-first expect() s auto-retry"),
    (re.compile(r"assert\s+.*\.is_visible\(\)"), "Slabý assert locator.is_visible() – použij expect(locator).to_be_visible()"),
]

# Zakázané vzory v Page Objectech (pages/)
PAGE_FORBIDDEN_PATTERNS = [
    (re.compile(r"xpath\s*=|locator\(\s*[\"']\s*//"), "XPath selektor"),
    (re.compile(r"nth-child|nth\s*="), ":nth-child / nth= selektor"),
    (re.compile(r"locator\(\s*[\"'][^\"']*(?<![\w\]])\.[A-Za-z_-]"), "CSS třída v selektoru"),
    (re.compile(r"time\.sleep\("), "Pevné čekání time.sleep()"),
    (re.compile(r"wait_for_timeout\("), "Pevné čekání wait_for_timeout()"),
]


def extract_tc_ids(tc_file: Path) -> list[str]:
    """Extrahuje unikátní ID test casů ze souboru specifikace TC."""
    if not tc_file.exists():
        raise FileNotFoundError(f"Soubor s test casy nebyl nalezen: {tc_file}")

    content = tc_file.read_text(encoding="utf-8")
    matches = TC_ID_PATTERN.findall(content)

    # Zachováme unikátní pořadí výskytu
    unique_ids: list[str] = []
    for item in matches:
        if item not in unique_ids:
            unique_ids.append(item)

    return unique_ids


def check_tc_coverage(tc_ids: list[str], test_file: Path) -> tuple[list[str], list[str]]:
    """Zkontroluje přítomnost jednotlivých TC ID v testovacím souboru."""
    if not test_file.exists():
        raise FileNotFoundError(f"Testovací soubor nebyl nalezen: {test_file}")

    content = test_file.read_text(encoding="utf-8")
    covered: list[str] = []
    missing: list[str] = []

    for tc_id in tc_ids:
        if tc_id in content:
            covered.append(tc_id)
        else:
            missing.append(tc_id)

    return covered, missing


def audit_test_file(test_file: Path) -> list[tuple[int, str]]:
    """Provede statický audit testovacího souboru na zakázané vzory."""
    findings: list[tuple[int, str]] = []
    lines = test_file.read_text(encoding="utf-8").splitlines()

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue

        for pattern, description in TEST_FORBIDDEN_PATTERNS:
            if pattern.search(line):
                findings.append((line_num, description))

    return findings


def audit_page_files(pages_dir: Path) -> list[tuple[Path, int, str]]:
    """Provede audit Page Objectů v zadané složce."""
    findings: list[tuple[Path, int, str]] = []
    if not pages_dir.exists():
        return findings

    for page_path in pages_dir.rglob("*.py"):
        lines = page_path.read_text(encoding="utf-8").splitlines()
        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue

            for pattern, description in PAGE_FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    findings.append((page_path, line_num, description))

    return findings


def run_pytest_stability(test_file: Path, runs: int) -> tuple[bool, list[str]]:
    """Spustí testy opakovaně v pytestu pro ověření stability (anti-flakiness)."""
    logs: list[str] = []

    for run_idx in range(1, runs + 1):
        cmd = [sys.executable, "-m", "pytest", str(test_file), "-v"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode != 0:
            error_preview = (result.stdout or "") + "\n" + (result.stderr or "")
            # Zkrátíme výpis na relevantních max 20 řádků
            preview_lines = [l for l in error_preview.splitlines() if l.strip()][-20:]
            logs.append(f"Běh {run_idx}/{runs} SELHAL (exit code {result.returncode}):\n" + "\n".join(preview_lines))
            return False, logs

        logs.append(f"Běh {run_idx}/{runs}: ÚSPĚCH (PASS)")

    return True, logs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Skript 'Definice hotovo' pro automatizované testy (kontrola pokrytí, pravidel a stability)."
    )
    parser.add_argument("--tc-file", required=True, type=Path, help="Cesta k souboru se schválenými Test Casy (.md)")
    parser.add_argument("--test-file", required=True, type=Path, help="Cesta k implementovanému testovacímu souboru (.py)")
    parser.add_argument("--runs", type=int, default=3, help="Počet opakovaných běhů v pytestu (default: 3)")
    parser.add_argument("--pages-dir", type=Path, default=Path("pages"), help="Složka s Page Objecty pro audit (default: pages)")
    parser.add_argument("--skip-runs", action="store_true", help="Přeskočit spouštění pytestu (pouze statická kontrola)")

    args = parser.parse_args()

    print("=" * 75)
    print(" SKRIPT DEFINICE HOTOVO (DoD) - AUTOMATIZOVANÉ TESTY")
    print("=" * 75)
    print(f"Zdrojové Test Casy:   {args.tc_file}")
    print(f"Testovací soubor:     {args.test_file}")
    print(f"Požadováno běhů:      {args.runs}x")
    print("-" * 75)

    errors: list[str] = []

    # 1. Extrakce a kontrola TC ID
    try:
        tc_ids = extract_tc_ids(args.tc_file)
        if not tc_ids:
            errors.append(f"V souboru {args.tc_file} nebyla nalezena žádná ID test casů (např. [TC-US02-01]).")
        else:
            print(f" [OK] Nalezeno {len(tc_ids)} schválených Test Casů: {', '.join(tc_ids)}")
    except Exception as e:
        errors.append(f"Chyba při čtení souboru TC: {e}")
        tc_ids = []

    # 2. Kontrola pokrytí v testovacím kódu
    if tc_ids:
        try:
            covered, missing = check_tc_coverage(tc_ids, args.test_file)
            print(f" [INFO] Pokrytí: {len(covered)}/{len(tc_ids)} ({len(covered)/len(tc_ids)*100:.1f} %)")
            if missing:
                errors.append(f"Chybí implementace pro následující Test Casy: {', '.join(missing)}")
            else:
                print(" [OK] 100% pokrytí: Každý schválený Test Case má svůj implementovaný test.")
        except Exception as e:
            errors.append(f"Chyba při kontrole testovacího souboru: {e}")

    # 3. Statický audit testovacího souboru
    try:
        test_findings = audit_test_file(args.test_file)
        if test_findings:
            for line_no, desc in test_findings:
                errors.append(f"Statická chyba v {args.test_file}:{line_no}: {desc}")
        else:
            print(" [OK] Statický audit testů: Zero inline locators, žádná pevná čekání ani slabé asserty.")
    except Exception as e:
        errors.append(f"Chyba při statickém auditu testu: {e}")

    # 4. Statický audit Page Objectů
    try:
        page_findings = audit_page_files(args.pages_dir)
        if page_findings:
            for page_path, line_no, desc in page_findings:
                errors.append(f"Statická chyba v POM {page_path}:{line_no}: {desc}")
        else:
            print(" [OK] Statický audit Page Objectů: Žádný XPath, :nth-child ani CSS třídy.")
    except Exception as e:
        errors.append(f"Chyba při auditu Page Objectů: {e}")

    # 5. Stabilita testů (anti-flakiness běhy)
    if not errors and not args.skip_runs:
        print(f" [INFO] Spouštím stabilitní test ({args.runs}x opakovaný běh v pytestu)...")
        passed, run_logs = run_pytest_stability(args.test_file, args.runs)
        for log in run_logs:
            print(f"   {log}")
        if not passed:
            errors.append(f"Test selhal během stabilitního ověření ({args.runs}x po sobě).")
    elif args.skip_runs:
        print(" [INFO] Spouštění pytestu přeskočeno (--skip-runs).")

    # Vyhodnocení celkového výsledku
    print("-" * 75)
    if errors:
        print(" VÝSLEDEK DEFINICE HOTOVO: [NENÍ HOTOVO] (Exit code 1)")
        print("-" * 75)
        print("Nalezené nedostatky:")
        for idx, err in enumerate(errors, start=1):
            print(f" {idx}. {err}")
        print("\nAgent musí chyby opravit a spustit kontrolu znovu.")
        print("Pokud je chyba způsobena blokací v aplikaci, ohlaste stav BLOKOVÁNO.")
        return 1

    print(" VÝSLEDEK DEFINICE HOTOVO: [HOTOVO] (Exit code 0)")
    print("-" * 75)
    print("Všechny požadavky Definice hotovo byly úspěšně splněny.")
    print("Výstup je připraven k review a začlenění (merge).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

