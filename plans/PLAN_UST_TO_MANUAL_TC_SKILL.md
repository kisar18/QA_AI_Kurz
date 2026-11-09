# Plán: Skill `ust-to-manual-tc` (Pracovní postup User Story -> Manuální TC)

## 1. Goal Description
Cílem je vytvořit nový projektový skill v `.agents/skills/ust-to-manual-tc/`, který agentovi definuje přesný a efektivní postup tvorby manuálních test casů (TC) ze zadané User Story (UST).

Postup je rozdělen do jasných kroků na principu **Human-in-the-loop** (spolupráce člověk + AI), kde je u každého kroku jednoznačně definován **vstup**, **výstup** a **role (kdo krok provádí)**. 

Součástí skillu je validační skript **Definice hotovo (Definition of Done)**, který automaticky ověří formální i obsahovou kvalitu navržených test casů před jejich finálním schválením.

---

## 2. Navržená struktura skillu

```text
.agents/skills/ust-to-manual-tc/
├── SKILL.md                          # Hlavní návod: popis triggeru, role a tabulka kroků workflow
├── templates/
│   └── test_case_template.md         # Jednotná šablona pro generování test casů
└── scripts/
    └── verify_test_cases.py          # Skript "Definice hotovo" (kontrola struktury a pokrytí AC)
```

Kam se ukládají vygenerované test casy:
- `manual_tests/TC_<US_ID>.md` (např. `manual_tests/TC_US-02_registrace.md`)

---

## 3. Popis pracovního postupu (Kroky workflow)

| Krok | Název kroku | Kdo dělá | Vstup | Výstup | Popis činnosti |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Review User Story** | **Agent + Uživatel** | Text US / odkaz na US (např. z `user stories/požadavky_ust_podle_src.md`) | Potvrzená US s očíslovanými akceptačními kritérii (AC-1, AC-2, ...) | Agent zanalyzuje US, zkontroluje jednoznačnost a testovatelnost. Pokud najde nejasnosti či chybějící hraniční podmínky, zeptá se uživatele. Uživatel potvrdí zadání. |
| **2** | **Návrh test casů agentem** | **Agent** | Potvrzená US + šablona `test_case_template.md` | Soubor `manual_tests/TC_<US_ID>.md` | Agent navrhne kompletní sadu manuálních test casů pokrývajících všechna AC (pozitivní, negativní i hraniční scénáře). Každý TC obsahuje ID, vazbu na AC, předpoklady, kroky a očekávaný výsledek. |
| **3** | **Review test casů uživatelem** | **Uživatel (Tester/QA)** | Navržený soubor `manual_tests/TC_<US_ID>.md` | Připomínky / schválený draft | Uživatel zkontroluje byznys logiku, pokrytí a proveditelnost. Agent zapracuje případné úpravy či doplnění dle instrukcí uživatele. |
| **4** | **Spuštění skriptu "Definice hotovo"** | **Agent** | Soubor s test casy + zdrojová US | Výpis validátoru (PASS/FAIL) | Agent spustí validační skript `verify_test_cases.py`, který zkontroluje dodržení všech pravidel (100% pokrytí AC, povinné sekce, přítomnost negativních testů). V případě chyb agent nedostatky opraví. |
| **5** | **Finální schválení** | **Uživatel** | Výsledek skriptu (PASS) + finální soubor TC | Finální schválené test casy | Uživatel potvrdí převzetí hotových test casů. |

---

## 4. Skript "Definice hotovo" (`verify_test_cases.py`)

Skript bude spouštěn agentem z příkazové řádky:
```powershell
python .agents/skills/ust-to-manual-tc/scripts/verify_test_cases.py manual_tests/TC_US-02.md --story "user stories/požadavky_ust_podle_src.md" --us-id "US-02"
```

### Co skript automaticky kontroluje:
1. **100% pokrytí Akceptačních kritérií (AC):**
   - Načte AC dané User Story a ověří, že každé AC je pokryto alespoň jedním test casem (`Akceptační kritérium: AC-x`).
2. **Povinná struktura každého Test Casu:**
   - Unikátní identifikátor (např. `TC-US02-01`).
   - Název / Cíl testu.
   - Typ testu (Pozitivní / Negativní / Hraniční).
   - Předpoklady (Preconditions).
   - Očíslované testovací kroky (min. 1 krok, jasná akce).
   - Očekávaný výsledek (Expected Result) u každého kroku nebo souhrnně.
3. **Kvalita sady (Rozšíření):**
   - Sada nesmí obsahovat pouze "happy path" (musí obsahovat alespoň 1 negativní nebo chybový scénář).
   - Žádné prázdné placeholdery typu "TODO", "TBD" apod.
4. **Návratové kódy:**
   - Exit code `0` = Vše splněno (**HOTOVO**).
   - Exit code `1` = Nalezeny chyby nebo nepokrytá kritéria (**NENÍ HOTOVO** – agent musí opravit).

---

## 5. Šablona Test Casu (`templates/test_case_template.md`)

Jednotný a čitelný formát v Markdownu:
```markdown
### [TC-ID] Název test case
- **Pokrývá kritérium:** AC-X (nebo kód kritéria)
- **Typ testu:** Pozitivní / Negativní / Hraniční
- **Předpoklady:**
  - Výchozí stav systému a oprávnění uživatele
- **Testovací data:**
  - Vstupní hodnoty, testovací účet
- **Kroky:**
  1. Krok 1 (akce)
  2. Krok 2 (akce)
- **Očekávaný výsledek:**
  - Co přesně systém zobrazí nebo jak se zachová
```

---

## 6. Ověření plánu (Verification Plan) – DOKONČENO

1. **Vytvoření souborů skillu:**
   - [x] `.agents/skills/ust-to-manual-tc/SKILL.md` (stručný přehled rolí a postupu).
   - [x] `.agents/skills/ust-to-manual-tc/templates/test_case_template.md` (šablona test casu).
   - [x] `.agents/skills/ust-to-manual-tc/scripts/verify_test_cases.py` (DoD validační skript).
2. **Pilotní ověření na reálné User Story z projektu:**
   - [x] Vytvořen ukázkový výstup `manual_tests/TC_US-02_registrace.md` pro User Story `US-02`.
   - [x] Spuštěn validační skript `verify_test_cases.py`:
     ```powershell
     python .agents/skills/ust-to-manual-tc/scripts/verify_test_cases.py manual_tests/TC_US-02_registrace.md
     ```
   - [x] Výsledek ověření: Všech 8 akceptačních kritérií (AC-1 až AC-8) je 100% pokryto, sada obsahuje pozitivní (2), negativní (3) i hraniční (1) scénáře, návratový kód `0` (HOTOVO).

