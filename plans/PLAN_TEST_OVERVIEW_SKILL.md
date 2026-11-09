# Plán: Skill `test-overview-generator` (Katalog a přehled automatizovaných testů)

## Goal Description
Vytvořit krátký a přímočarý projektový skill v `.agents/skills/test-overview-generator/`, který umožní agentovi i uživateli z příkazové řádky jedním příkazem analyzovat všechny automatizované testy v repozitáři (`tests/`) a vygenerovat přehledný Markdown soubor (`TEST_OVERVIEW.md`).

Samotný soubor `SKILL.md` bude **krátký a věcný – proces v několika odrážkách**, nikoliv zdlouhavý teoretický text.

---

## User Review Required

> [!IMPORTANT]
> **Stručnost skillu (`SKILL.md`):**
> Podle požadavku uživatele bude instrukční soubor `SKILL.md` velmi stručný – proces popsaný v cca 4–5 jasných odrážkách:
> 1. Kdy proces spustit (žádost o přehled testů, po přidání/úpravě testů).
> 2. Jak spustit skript generátoru.
> 3. Co skript extrahuje (názvy testů, docstringy, kroky testu a kontroly/asserty).
> 4. Kde zkontrolovat vygenerovaný Markdown (`TEST_OVERVIEW.md`).
> 5. Jak odpovědět uživateli (stručné shrnutí a odkaz na vygenerovaný soubor).

---

## Proposed Changes

### 1. Nový skill `test-overview-generator`

#### [NEW] `.agents/skills/test-overview-generator/SKILL.md`
Krátký procesní soubor (cca 25–35 řádků):
- **YAML Frontmatter**: `name: test-overview-generator`, `description`.
- **Proces generování v odrážkách:**
  - **Krok 1 (Spuštění):** Spusť skript `python .agents/skills/test-overview-generator/scripts/generate_test_overview.py`.
  - **Krok 2 (Analýza):** Skript staticky projde `tests/` pomocí `ast` a extrahuje:
    - Název testu, třídu a soubor.
    - Cíl testu (docstring / User Story kód).
    - Kroky (volání Page Object metod, navigace, vstupy).
    - Kontroly (Playwright `expect`, `assert` a popisy ze `step(...)`).
  - **Krok 3 (Rozhodnutí zda je hotovo):** Spuštění `check_done.py` pro validaci kompletnosti a aktuálnosti.
  - **Krok 4 (Prezentace):** Odkaz na vygenerovaný soubor předej uživateli se souhrnnou statistikou (počet testů a kontrol).

#### [NEW] `.agents/skills/test-overview-generator/scripts/generate_test_overview.py`
Samostatný a robustní Python skript:
- Prochází `tests/**/test_*.py`.
- Parsuje AST (`ast.parse`) a zdrojový kód.
- Pro každý test extrahuje chronologicky:
  - Název testu + docstring.
  - Volání akcí (Page Object metody, navigace).
  - Kontroly (`expect(...)`, `assert ...`, `step(...)`).
- Formátuje přehledný Markdown soubor `TEST_OVERVIEW.md` se souhrnnou statistikou a rozpadem podle modulů.

#### [NEW] `.agents/skills/test-overview-generator/scripts/generate_coverage_report.py`
Skript pro generování matice pokrytí User Stories v HTML (`reports/coverage_overview.html`):
- Prochází specifikaci v `user stories/` (US-01 až US-20) a extrahuje akceptační kritéria (test casy).
- Prochází `tests/` a mapuje automatizované testy (AT) na konkrétní User Stories.
- Počítá metriky (počet test casů, počet AT, stav pokrytí: 🟢 Plně pokryto, 🟡 Částečně, 🔴 Nepokryto).
- Generuje samostatný interaktivní HTML soubor s KPI kartami, filtry a rozbalovacími detaily testů a kritérií.

#### [NEW] `.agents/skills/test-overview-generator/scripts/check_done.py`
Skript pro rozhodnutí zda je přehled testů hotov (Definition of Done):
- Kontroluje existenci a neprázdnost `TEST_OVERVIEW.md`.
- Kontroluje časovou aktuálnost (žádný test nesmí být modifikován po generování).
- Kontroluje 100% pokrytí testů (žádné chybějící ani osiřelé testy).
- Kontroluje konzistenci statistik.
- Kontroluje kvalitu (žádné testy bez kontrol).
- Vrací exit code 0 (`HOTOVO`) nebo 1 (`NENÍ HOTOVO`). Podporuje `--fix`, `--strict` a `--json`.

---

### 2. Projektové plány a dokumentace

#### [MODIFY] `plans/PLAN_TEST_OVERVIEW_SKILL.md`
Zaznamenání aktualizovaného plánu do adresáře `plans/`.

---

## Verification Plan

### Automatizované ověření
1. Spuštění generátoru:
   ```powershell
   python .agents/skills/test-overview-generator/scripts/generate_test_overview.py
   ```
2. Ověření existence a obsahu `TEST_OVERVIEW.md`:
   - Musí obsahovat všechny moduly (`auth`, `courses`, `navigation`, `portal`, `profile`, `security`).
   - U každého testu musí být uvedeny jeho konkrétní kroky a kontroly.
3. Ověření, že stávající testy běží bez problémů:
   ```powershell
   pytest tests/auth/test_login.py -v
   ```

### Manuální ověření
- Otevřít `TEST_OVERVIEW.md` a ověřit vizuální přehlednost a srozumitelnost vygenerovaného katalogu.
