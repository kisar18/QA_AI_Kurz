# Plán: Skill pro reportování chyb (`bug-reporting`) a vynucení DoD hookem `Stop`

## 1. Goal Description
Cílem je vytvořit nový projektový skill v `.agents/skills/bug-reporting/` a odpovídající validační hook typu `Stop` v `.agents/hooks.json`, které společně zajistí:
1. Spuštění celé sady automatizovaných E2E testů (Playwright + pytest).
2. Identifikaci všech padajících testů a zachycení důkazních materiálů (screenshot obrazovky, případně Playwright trace).
3. Vytvoření podrobného a standardizovaného bug reportu pro každý padající test s povinnými náležitostmi:
   - Kroky k reprodukci (Steps to reproduce),
   - Očekávaný výsledek (Expected result),
   - Skutečný výsledek (Actual result),
   - Testovací prostředí (Environment: OS, prohlížeč, URL, verze/commit),
   - Odkaz na důkaz (Evidence: platná cesta k existujícímu screenshotu či trace souboru).
4. Vygenerování souhrnného interaktivního HTML přehledu chyb (`reports/bug_overview.html`).
5. **Vynucení Definice hotovo (DoD) pomocí hooku `Stop`**:
   - Hook zablokuje ukončení agenta (`decision: "continue"`), dokud není přehled hotový a kompletní.
   - **Pravidla z kapitoly 5 kurzu**: Hook zasahuje **pouze tehdy, když běžel tento skill** (neblokuje jiné úkoly) a **kontroluje reálný obsah** reportů, nikoliv pouhou existenci souboru na disku.

---

## 2. Architektura řešení a souborová struktura

```text
.agents/
├── hooks.json                                      # Konfigurace lifecycle hooků (Stop hook)
├── scripts/
│   └── check_bug_reporting_dod.py                 # Validační skript pro Stop hook (DoD kontrola obsahu a scope)
└── skills/
    └── bug-reporting/
        ├── SKILL.md                                # Instrukce pro agenta (proces, povinné sekce, pravidla)
        └── scripts/
            ├── run_tests_with_evidence.py          # Runner pytestu s ukládáním důkazů a JSON metadat
            ├── generate_bug_overview.py            # Generátor výsledného HTML přehledu chyb
            └── verify_bug_reports.py               # Samostatný CLI validátor DoD (využívaný i v hooku)
```

---

## 3. Detailní návrh komponent

### Komponenta A: Skripty pro běh testů a sběr důkazů
1. **`run_tests_with_evidence.py`**:
   - Spustí `pytest` s parametry pro sběr metadat a ukládání screenshotů/trace při chybě do `reports/evidence/`.
   - Vytvoří strukturovaný meziprodukt `reports/test_run_data.json`, který obsahuje:
     - Celkový počet testů, počet prošlých (`passed`), selhaných (`failed`) a přeskočených (`skipped`).
     - Seznam padajících testů: ID testu, název funkce, soubor, chybová hláška, traceback, čas pádu a vygenerovaný soubor screenshotu/trace.

### Komponenta B: Tvorba a struktura bug reportů & HTML přehledu
1. **Struktura bug reportu (povinná pole dle zadání):**
   - `id`: Jednoznačný identifikátor vady (např. `BUG-AUTH-01`).
   - `test_name`: Identifikace padajícího testu (např. `test_login_invalid_password`).
   - `steps_to_reproduce`: Číslovaný seznam konkrétních kroků k reprodukci.
   - `expected_result`: Popis očekávaného chování dle specifikace/TC.
   - `actual_result`: Reálný výsledek chování (chybová hláška, neočekávaný element, timeout).
   - `environment`: Specifikace prostředí (OS: Windows/Linux, Browser: Chromium, URL: http://testovani.kitner.cz, datum a čas běhu).
   - `evidence`: Odkaz na existující screenshot nebo Playwright trace soubor v `reports/evidence/`.

2. **`generate_bug_overview.py`**:
   - Vytvoří moderní, responzivní `reports/bug_overview.html`.
   - Obsahuje:
     - Souhrnné statistiky (KPI karty: Total Failed, Critical/Major, prostředí).
     - Seznam chyb s rozbalovacími detaily, formátovanými kroky a lightboxem/náhledem screenshotu.
     - Pokud žádný test neselhal: čisté zobrazení *"Všechny testy prošly (0 chyb)"*.
     - Strojově čitelná metadata (data atributy nebo `<script type="application/json">`) pro přesnou a rychlou validaci obsahem.

### Komponenta C: Instrukční soubor `SKILL.md`
- Definuje přesný a stručný postup pro agenta:
  - **Krok 1 (Spuštění testů):** Spustit testovací sadu přes `run_tests_with_evidence.py` nebo standardní `pytest`.
  - **Krok 2 (Analýza selhání):** Zanalyzovat chybový stack trace a identifikovat root cause pro každý padající test.
  - **Krok 3 (Tvorba reportů):** Sestavit detailní reporty se všemi 5 povinnými poli.
  - **Krok 4 (Generování HTML):** Vytvořit soubor `reports/bug_overview.html`.
  - **Krok 5 (Ověření DoD):** Spustit `verify_bug_reports.py` pro ověření před ukončením.
  - **Krok 6 (Předání výstupu):** Předat uživateli souhrn a klikací odkaz na vygenerovaný HTML přehled.

### Komponenta D: Vynucení Definice hotovo přes hook `Stop`
1. **Konfigurace v `.agents/hooks.json`**:
   ```json
   {
     "bug-reporting-dod": {
       "Stop": [
         {
           "type": "command",
           "command": "python .agents/scripts/check_bug_reporting_dod.py",
           "timeout": 30
         }
       ]
     }
   }
   ```

2. **Implementace skriptu `check_bug_reporting_dod.py` (Zásady kapitoly 5):**
   - **Podmíněné spuštění (Scoping):**
     - Přečte `transcriptPath` z payloadu na `stdin`.
     - Zkontroluje, zda v aktuální konverzaci agent aktivoval skill `bug-reporting` (vyhledání zmínky o `bug-reporting` v transcriptu) nebo zda v session vznikl marker/běh testů z tohoto skillu.
     - **Pokud skill neběžel:** Hook okamžitě vrátí `{"decision": "allow"}` a nezdržuje agenta při jiných úlohách.
   - **Kontrola obsahu (Content Validation):**
     - Pokud skill běžel, hook prověří:
       1. **Existence souboru:** Zda existuje soubor `reports/bug_overview.html` a `reports/test_run_data.json` a jsou časově aktuální (vytvořeny v této session).
       2. **Pokrytí všech pádů:** Zda počet reportovaných chyb v HTML přesně odpovídá počtu identifikovaných padajících testů.
       3. **Kontrola povinných polí v každém reportu:**
          - Kroky k reprodukci (neprázdný seznam, minimálně 1 smysluplný krok).
          - Očekávaný výsledek (text > 5 znaků, ne placeholder).
          - Skutečný výsledek (text > 5 znaků, ne placeholder).
          - Prostředí (obsahuje OS, browser, URL).
          - Odkaz na důkaz (relativní cesta k souboru screenshotu/trace a ověření `os.path.exists` na disku).
       4. **Zákaz placeholderů:** Zakázány texty jako `TODO`, `TBD`, `DOPLNIT`, `Chyba`, `N/A`.
   - **Ochrana proti zacyklení (Anti-Infinite Loop):**
     - Sleduje pole `continuationActive` a interní počítadlo v payloadu. Pokud by agent opakovaně selhával i po instrukcích (více než 3 vynucená pokračování), umožní nouzové předání s varováním, aby nedošlo k vyčerpání tokenů.
   - **Výstupy:**
     - Splněno -> `{"decision": "allow"}`.
     - Nesplněno -> `{"decision": "continue", "reason": "Definice hotovo pro bug-reporting nebyla splněna:\n- [výčet konkrétních chybějících polí či reportů]\nDokončete chybějící části před ukončením."}`.

---

## 4. Fáze implementace

1. **Fáze 1: Pomocné skripty a HTML generátor v rámci skillu**
   - Vytvořit adresářovou strukturu `.agents/skills/bug-reporting/scripts/`.
   - Vytvořit `run_tests_with_evidence.py` pro řízený běh pytestu a extrakci padajících testů a screenshotů.
   - Vytvořit `generate_bug_overview.py` pro tvorbu interaktivního HTML reportu.
   - Vytvořit `verify_bug_reports.py` pro deterministickou kontrolu obsahu a povinných polí.

2. **Fáze 2: Návrh instrukcí skillu `SKILL.md`**
   - Vytvořit `.agents/skills/bug-reporting/SKILL.md` se stručným procesem v odrážkách, popisem kroků, povinných polí a odkazem na DoD.

3. **Fáze 3: Implementace Stop hooku a konfigurace**
   - Vytvořit `.agents/scripts/check_bug_reporting_dod.py` s parsováním `transcriptPath`, scoped detekcí spuštění skillu a hloubkovou kontrolou HTML obsahu.
   - Vytvořit nebo aktualizovat `.agents/hooks.json`.

4. **Fáze 4: Verifikace a testování funkčnosti**
   - **Pozitivní test:** Spuštění testu se simulovaným pádem, vygenerování kompletního reportu se všemi poli a ověření, že hook povolí ukončení (`decision: allow`).
   - **Negativní test (Chybějící pole):** Odstranění odkazu na screenshot nebo kroků k reprodukci a ověření, že hook zablokuje ukončení (`decision: continue`).
   - **Test nezávislosti (Scope test):** Simulace ukončení agenta při jiné činnosti (kdy skill neběžel) a ověření, že hook do běhu nezasahuje.

---

## 5. User Review & Akceptační kritéria
- Je navržený formát HTML reportu v souladu s očekáváním (moderní přehled s lightbox náhledem důkazů)?
- Jsou povinná pole bug reportu vyčerpávající a odpovídají standardu testování?
- Vyhovuje navržená strategie detekce běhu skillu v hooku (parsování transcriptu relace)?
