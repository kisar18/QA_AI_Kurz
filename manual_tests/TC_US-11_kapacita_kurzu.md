# Test Casy: US-11 Vizuální indikace a zamezení zápisu při naplněné kapacitě

**Zdrojová User Story:** US-11  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + QA Tester  

---

### [TC-US11-01] Zobrazení tlačítka registrace u běhu s volnou kapacitou a přesměrování
- **Pokrývá kritérium:** AC-1, AC-2
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - Přihlášen uživatel v roli zákazníka.
  - Kurz má vypsaný termín s volnou kapacitou (např. obsazenost 2/10).
- **Testovací data:**
  - Detail kurzu: `/courses/1`.
- **Kroky:**
  1. Otevři detail kurzu `/courses/1` jako přihlášený zákazník.
  2. Vyhledej kartu termínu, který má volná místa (např. 2/10).
  3. Zkontroluj přítomnost tlačítka pro nezávaznou registraci.
  4. Klikni na tlačítko "Nezávazná registrace".
- **Očekávaný výsledek:**
  - Tlačítko pro nezávaznou registraci je u termínu s volnou kapacitou aktivní a viditelné.
  - Kliknutí přesměruje zákazníka do objednávkového formuláře zápisu daného běhu (URL `/courses/<iteration_id>/register`).

---

### [TC-US11-02] Skrytí registrace a indikace plné obsazenosti u vyčerpané kapacity
- **Pokrývá kritérium:** AC-1, AC-3
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Přihlášen uživatel v roli zákazníka.
  - U kurzu existuje termín, jehož kapacita je zcela naplněna (např. obsazenost 10/10).
- **Testovací data:**
  - Běh kurzu s plnou kapacitou.
- **Kroky:**
  1. Otevři detail kurzu `/courses/1`.
  2. Vyhledej kartu plně obsazeného běhu.
  3. Zkontroluj přítomnost tlačítka pro registraci.
  4. Zkontroluj vizuální indikaci stavu termínu.
- **Očekávaný výsledek:**
  - U plně obsazeného běhu se tlačítko pro nezávaznou registraci vůbec nenabízí (je skryto nebo neaktivní).
  - Termín je zřetelně označen jako plně obsazený / vyprodaný (např. textem *Plně obsazeno* nebo červeným štítkem kapacity 10/10).

---

### [TC-US11-03] Zamezení přímého zápisu na plně obsazený běh přes přímou URL
- **Pokrývá kritérium:** AC-2, AC-3
- **Typ testu:** Hraniční
- **Priorita:** High
- **Předpoklady:**
  - Přihlášen zákazník.
  - Je známo ID plně obsazeného běhu (např. běh s ID 5).
- **Testovací data:**
  - URL registrace plného běhu: `/courses/5/register`.
- **Kroky:**
  1. Zadej do adresního řádku URL pro registraci plně obsazeného běhu a stiskni Enter.
  2. Pokud se formulář načte, zkus vyplnit povinné údaje (IČO, telefon) a odeslat jej.
- **Očekávaný výsledek:**
  - Systém nepovolí přihlášení nad rámec maximální kapacity.
  - Přímý přístup na formulář je buď zablokován, nebo odeslání skončí chybovou zprávou o vyčerpané kapacitě běhu.
  - Kapacita kurzu není překročena.
