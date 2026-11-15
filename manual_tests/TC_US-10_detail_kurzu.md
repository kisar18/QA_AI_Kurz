# Test Casy: US-10 Zobrazení detailu kurzu a vypsaných termínů

**Zdrojová User Story:** US-10  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + QA Tester  

---

### [TC-US10-01] Zobrazení kompletních informací o kurzu a seznamu vypsaných běhů
- **Pokrývá kritérium:** AC-1, AC-2, AC-3
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - V systému existuje kurz s přiřazenými vypsanými termíny.
- **Testovací data:**
  - URL detailu kurzu: `/courses/1`.
- **Kroky:**
  1. Otevři v prohlížeči detail kurzu `/courses/1`.
  2. Zkontroluj přítomnost a správnost:
     - Kompletní název kurzu
     - Podrobný obsahový popis kurzu
     - Náhledový obrázek kurzu
     - Cena kurzu v Kč
  3. Zkontroluj sekci vypsaných termínů (běhů).
  4. U jednotlivých termínů ověř zobrazení data zahájení, data ukončení a kapacity.
- **Očekávaný výsledek:**
  - Všechny detailní informace o kurzu (název, popis, cena, obrázek) jsou přehledně zobrazeny.
  - Stránka obsahuje sekci se všemi vypsanými běhy daného kurzu.
  - U každého termínu je uvedeno přesné datum začátku a konce i aktuální stav obsazenosti.

---

### [TC-US10-02] Ověření formátu a výpočtu poměru obsazenosti termínu (např. 3/12)
- **Pokrývá kritérium:** AC-3
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Otevřen detail kurzu `/courses/1`.
- **Testovací data:**
  - Běh kurzu s kapacitou např. 12 účastníků a 3 zapsanými studenty.
- **Kroky:**
  1. Vyhledej kartu běhu kurzu s existujícími zápisy.
  2. Zkontroluj textový formát poměru obsazenosti.
- **Očekávaný výsledek:**
  - Obsazenost je zformátována přesně podle vzoru *počet přihlášených / celková kapacita* (např. `3/12` nebo `0/12`).
  - Údaje přesně reflektují skutečný počet zapsaných studentů.

---

### [TC-US10-03] Zobrazení výzvy k vytvoření účtu pro nepřihlášeného návštěvníka na detailu kurzu
- **Pokrývá kritérium:** AC-4
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Uživatel si prohlíží detail kurzu v anonymním (nepřihlášeném) stavu.
- **Testovací data:**
  - URL detailu kurzu: `/courses/1`.
- **Kroky:**
  1. Otevři detail kurzu bez přihlášení.
  2. Přejdi na konec stránky pod seznam termínů.
  3. Zkontroluj přítomnost textové výzvy k registraci a odkazu na vytvoření účtu.
  4. Klikni na nabízený odkaz k registraci.
- **Očekávaný výsledek:**
  - Na konci stránky se nepřihlášenému návštěvníkovi zobrazuje zřetelná výzva k vytvoření účtu.
  - Kliknutí na odkaz přesměruje uživatele přímo do registračního formuláře `/register`.

---

### [TC-US10-04] Zpracování požadavku na neexistující ID kurzu
- **Pokrývá kritérium:** AC-1
- **Typ testu:** Negativní
- **Priorita:** Low
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí.
- **Testovací data:**
  - Neexistující ID kurzu (např. `/courses/999999`).
- **Kroky:**
  1. Zadej do adresního řádku URL s neexistujícím ID kurzu `/courses/999999` a stiskni Enter.
  2. Zkontroluj odpověď serveru.
- **Očekávaný výsledek:**
  - Systém vrátí chybový kód 404 Not Found a zobrazí chybovou stránku o nenalezení kurzu.
  - Aplikace neselže neošetřenou chybou 500.
