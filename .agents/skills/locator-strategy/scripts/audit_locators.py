"""Audit lokátorů: hledá porušení pravidel skillu locator-strategy.

Použití:
    python audit_locators.py pages tests

Skript pouze čte soubory a vypisuje nálezy ve formátu ``soubor:řádek: [LEVEL] pravidlo``.
Exit code 1 při jakémkoli ERROR, jinak 0. WARN a TODO exit code neovlivňují.
"""

import re
import sys
from pathlib import Path

# (regex, level, popis) – pro soubory v pages/
PAGES_RULES = [
    (re.compile(r"xpath\s*=|locator\(\s*[\"']\s*//"), "ERROR", "XPath selektor"),
    (re.compile(r"nth-child|nth\s*="), "ERROR", ":nth-child / nth= selektor"),
    (re.compile(r"locator\(\s*[\"'][^\"']*(?<![\w\]])\.[A-Za-z_-]"), "ERROR", "CSS třída v selektoru"),
    (re.compile(r"time\.sleep|wait_for_timeout"), "ERROR", "pevné čekání (sleep)"),
    (re.compile(r"\.locator\("), "WARN", "CSS/atributový selektor, preferuj get_by_test_id"),
    (re.compile(r"get_by_text\("), "WARN", "get_by_text je křehké, preferuj testid / role"),
]

FIRST_NTH = re.compile(r"\.first\b|\.last\b|\.nth\(")
TODO_TESTID = re.compile(r"TODO\(testid\)")

# Pro soubory v tests/ – jakýkoli lokátor je ERROR (Zero-Inline-Locators)
TESTS_RULE = re.compile(r"\.locator\(|\.get_by_\w+\(|xpath\s*=")


def audit_file(path: Path, is_test: bool) -> list[tuple[int, str, str]]:
    findings = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            if TODO_TESTID.search(stripped):
                findings.append((number, "TODO", stripped))
            continue
        if is_test:
            if TESTS_RULE.search(line):
                findings.append((number, "ERROR", "lokátor v testu (Zero-Inline-Locators)"))
            continue
        for regex, level, message in PAGES_RULES:
            if regex.search(line):
                findings.append((number, level, message))
        if FIRST_NTH.search(line) and "#" not in line:
            findings.append((number, "WARN", ".first/.last/.nth() bez komentáře s důvodem"))
        if TODO_TESTID.search(line):
            findings.append((number, "TODO", "fallback čeká na data-testid"))
    return findings


def main(argv: list[str]) -> int:
    roots = [Path(arg) for arg in argv] or [Path("pages"), Path("tests")]
    errors = 0
    for root in roots:
        if not root.exists():
            print(f"Složka {root} neexistuje, přeskočeno.")
            continue
        is_test = root.name == "tests"
        for path in sorted(root.rglob("*.py")):
            for number, level, message in audit_file(path, is_test):
                print(f"{path.as_posix()}:{number}: [{level}] {message}")
                errors += level == "ERROR"
    print(f"\nHotovo. Počet ERROR nálezů: {errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

