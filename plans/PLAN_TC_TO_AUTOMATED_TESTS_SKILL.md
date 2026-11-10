# Plán: Skill `tc-to-automated-tests` (Pracovní postup Schválené Test Casy -> Automatizované Testy)

## 1. Goal Description
Cílem je vytvořit nový projektový skill v `.agents/skills/tc-to-automated-tests/`, který agentovi definuje přesný, udržitelný a spolehlivý postup převodu schválených manuálních test casů (např. z `manual_tests/TC_*.md`) do automatizovaných E2E testů v Playwright + pytest.

Postup integruje **6 pojistek proti falešnému hotovo a reward hackingu**:
1. **Hotovo definuje skript, ne agent** – o převzetí rozhoduje deterministický exit code skriptu, nikoli tvrzení LLM.
2. **Povolení říct "nejde to" (status `BLOKOVÁNO`)** – třetí možný výstup, pokud chybí selektory v UI, data nebo padá prostředí. Zákaz obcházení či mockování překážek.
3. **Validační skript a TC jsou pro agenta striktně READ-ONLY** – agent nesmí upravit kontrolní skript ani zdrojové TC, aby prošel.
4. **Nezávislá kontrola v čistém kontextu** – kontrolor dostane pouze zadání a kód s otázkou *"Co chybí a kde jsou chyby?"*, nikoli historii chatu.
5. **Rozhoduje stroj, AI jen hledá** – posloupnost: skript -> nezávislý AI audit nálezů -> finální schválení člověkem.
6. **Ochrana proti flakiness** – testy musí projít minimálně 3× po sobě.

---

## 2. Navržená struktura skillu

```text
.agents/skills/tc-to-automated-tests/
├── SKILL.md                          # Návod: trigger, role, tabulka workflow s pojistkami, pravidla
└── scripts/
    └── verify_automated_tests.py     # Skript "Definice hotovo" (pokrytí TC, statický audit, 3x pytest)
```

Propojení s existujícími skilly a pravidly:
- **`locator-strategy`** – Zero-Inline-Locators v testech, priorita `data-testid`.
- **`assertion-quality-review`** – hloubka ověření, zákaz oslabování assertů, web-first `expect()`.

---

## 3. Pracovní postup v krocích (Workflow s pojistkami)

| Krok | Název kroku | Kdo dělá | Vstup | Výstup | Popis činnosti & Pojistka |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Příprava vstupů & Analýza** | **Uživatel + Agent** | Schválené TC (např. `manual_tests/TC_US-02_registrace.md`) + `AGENTS.md` | Analytický checklist & mapování TC na testy (nebo `BLOKOVÁNO`) | Uživatel zadá schválené TC. Agent zmapuje potřebné POM třídy a data. Pokud narazí na neřešitelnou překážku (chybějící aplikace/prostředí), ohlásí **`BLOKOVÁNO`**. |
| **2** | **Příprava / úprava Page Objectů** | **Agent** | Chybějící prvky z analýzy | Aktualizované Page Objecty v `pages/` (nebo `BLOKOVÁNO`) | Agent doplní lokátory a metody do POM. **Pojistka:** Pokud na UI chybí prvek nebo nelze jednoznačně zacílit bez křehkých selektorů, agent nevymýšlí složité XPathy, ale ohlásí stav `BLOKOVÁNO (chybí data-testid)`. |
| **3** | **Generování automatizovaných testů** | **Agent** | Schválené TC + POM + `tests/AGENTS.md` | Soubor `tests/<oblast>/test_<tema>.py` | Agent naimplementuje testy (mapování 1:1 pro každý TC). Testy obsahují ID v docstringu, logování kroků (`step()`) a plnohodnotné web-first `expect()` asserty. |
| **4** | **Nezávislý audit lokátorů a assertů** | **Nezávislý AI Kontrolor (Čistý kontext)** | Kód v `pages/` a `tests/` + původní TC | Seznam nálezů (co chybí, slabá místa) | **Pojistka čistého kontextu:** Kontrola neprobíhá ve stejném chatu. Kontrolor dostane pouze kód a zadání s otázkou *"Co v testech chybí, které post-conditions nejsou ověřeny a kde jsou rizika?"*. |
| **5** | **Spuštění skriptu "Definice hotovo"** | **Agent** | Soubor TC + testovací soubor | Protokol DoD skriptu (Exit code 0/1) | **Pojistka deterministického stroje:** Agent spustí skript `verify_automated_tests.py`. Skript ověří: 1) 100% TC pokryto, 2) statická pravidla projektu, 3) test projde **3× po sobě** v pytestu. |
| **6** | **Review & Akceptace uživatelem** | **Uživatel (QA Lead)** | Výstup DoD (PASS) + report nálezů + kód testů | Schválení k začlenění | Uživatel zkontroluje reálné chování a potvrdí způsobilost k commitu. |
| **7** | **Merge & Commit** | **Agent + Uživatel** | Schválený kód | Git commit do větve | Agent připraví commit podle pravidel repozitáře (nikdy necommitovat `.env` ani `reports/`). Uživatel potvrdí finální push. |

---

## 4. Tři stavy výsledku (Výstupy procesu)

Proces generování smí skončit pouze jedním ze 3 stavů:
1. **`HOTOVO`** (Exit code 0): Skript `verify_automated_tests.py` skončil s kódem 0 (všechny testy naimplementovány, audit čistý, 3x úspěšný běh v pytestu) a uživatel schválil kód.
2. **`NENÍ HOTOVO`** (Exit code 1): Skript nalezl chyby v syntaxi, nepokrytá TC ID, zakázané inline lokátory nebo pád v některém ze 3 běhů. Agent musí chyby opravit a skript spustit znovu.
3. **`BLOKOVÁNO`**: Agent narazil na reálnou překážku (např. chybějící `data-testid` v aplikaci, nedostupný backend, chybějící testovací data). Agent nesmí předstírat funkčnost ani oslabovat testy – zastaví práci a přesně popíše blokaci člověku.

---

## 5. Specifikace skriptu "Definice hotovo" (`verify_automated_tests.py`)

Skript bude spouštěn agentem z příkazové řádky:
```powershell
python .agents/skills/tc-to-automated-tests/scripts/verify_automated_tests.py --tc-file manual_tests/TC_US-02_registrace.md --test-file tests/auth/test_register.py --runs 3
```

### Co skript automaticky kontroluje:
1. **Integrita vstupů (Anti-Reward Hacking):**
   - Ověří, že soubor se schválenými TC nebyl neoprávněně vyprázdněn ani upraven (obsahuje validní TC ID).
2. **100% mapování Test Casů:**
   - Načte všechna ID test casů ze zadaného markdownu (např. `TC-US02-01`, `TC-US02-02`, ...).
   - Zkontroluje, zda v testovacím souboru existuje test pro každé zadané TC ID.
3. **Statická čistota a dodržení standardů projektu:**
   - **Zero Inline Locators:** Žádné `.locator(`, `.get_by_*` ani `xpath=` v testu (musí být v POM).
   - **Zákaz pevných čekání:** Žádné `time.sleep()` ani `wait_for_timeout()`.
   - **Zákaz slabých kontrol:** Žádné `assert locator.is_visible()`.
4. **Flakiness & stabilita (3x opakovaný běh):**
   - Automaticky spustí cílový testovací soubor přes pytest **3× po sobě** (`sys.executable -m pytest <test-file>`).
   - Jakýkoli pád = okamžité selhání DoD skriptu.
5. **Návratové kódy:**
   - Exit code `0` = **HOTOVO**.
   - Exit code `1` = **NENÍ HOTOVO** (detailní výpis chyb).

---

## 6. Realizační kroky (Verification & Execution Plan)

1. **Vytvoření struktury skillu:**
   - Vytvořit `.agents/skills/tc-to-automated-tests/` a `scripts/`.
   - Vytvořit `SKILL.md` (stručný, akční, s tabulkou workflow, 3 stavy výstupu a zákazem obcházení).

2. **Implementace skriptu `verify_automated_tests.py`:**
   - Implementovat parsování TC ID z markdownu.
   - Implementovat statický audit kódu testů (AST + regex kontroly).
   - Implementovat opakovaný běh pytestu (3x) s měřením stability.
   - Implementovat barevný/přehledný reporting do konzole.

3. **Praktické ověření:**
   - Spustit skript na reálném souboru `manual_tests/TC_US-02_registrace.md` a `tests/auth/test_register.py`.
   - Ověřit funkčnost při úspěchu i při simulované chybě (např. chybějící TC nebo pád testu).
