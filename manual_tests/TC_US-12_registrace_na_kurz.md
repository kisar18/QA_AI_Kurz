# Test Casy: US-12 Nezávazná registrace na běh kurzu s validací IČO a telefonu

**Zdrojová User Story:** US-12  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + QA Tester  

---

### [TC-US12-01] Úspěšná nezávazná registrace na běh kurzu s platným IČO a telefonem
- **Pokrývá kritérium:** AC-1, AC-2, AC-3, AC-5, AC-6, AC-7
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - Přihlášen uživatel v roli zákazníka.
  - Otevřen detail kurzu s volným termínem běhu.
- **Testovací data:**
  - Platný telefon: `+420777123456` (12 znaků / 9+ číslic).
  - Platné IČO s kontrolním součtem modulo 11: `27082440` (Alza.cz a.s.).
- **Kroky:**
  1. Na detailu kurzu klikni na tlačítko "Nezávazná registrace" u vybraného běhu.
  2. Zkontroluj přítomnost formulářových polí pro IČO, telefon a potvrzovacího tlačítka.
  3. Vyplň platné IČO `27082440`.
  4. Vyplň platný telefon `+420777123456`.
  5. Klikni na potvrzovací tlačítko pro odeslání registrace.
- **Očekávaný výsledek:**
  - Formulář projde validací a odešle se.
  - Zákazník obdrží potvrzení o registraci (např. systémový dialog nebo potvrzovací hlášku).
  - Zadané IČO a telefon se automaticky uloží do profilu uživatele.
  - Vytvoří se vazba studenta na daný běh kurzu a zákazník je přesměrován do sekce "Moje kurzy" (`/my-courses`), kde je kurz ihned viditelný.

---

### [TC-US12-02] Validace povinného pole a minimální délky telefonního čísla
- **Pokrývá kritérium:** AC-1, AC-2, AC-4
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Přihlášen zákazník na stránce registrace běhu kurzu.
- **Testovací data:**
  - Test A: prázdné pole telefonu.
  - Test B: příliš krátké telefonní číslo `12345` (5 číslic).
  - Platné IČO: `27082440`.
- **Kroky:**
  1. Ponech pole pro telefon prázdné a klikni na odeslání registrace.
  2. Zkontroluj zobrazenou validační chybu o povinnosti pole.
  3. Do pole pro telefon zadej krátké číslo `12345` a klikni na odeslání.
  4. Zkontroluj novou validační zprávu.
- **Očekávaný výsledek:**
  - Formulář se v ani jednom případě neodešle.
  - V Testu A systém upozorní, že telefonní číslo je povinné.
  - V Testu B systém zobrazí chybu: *Telefonní číslo musí obsahovat alespoň 9 číslic.*

---

### [TC-US12-03] Validace formální platnosti IČO pomocí váženého kontrolního součtu modulo 11
- **Pokrývá kritérium:** AC-3, AC-4
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Přihlášen zákazník na stránce registrace běhu kurzu.
- **Testovací data:**
  - Platný telefon: `+420777123456`.
  - Neplatné IČO s chybným kontrolním součtem: `12345678`.
- **Kroky:**
  1. Do pole pro telefon zadej platné číslo `+420777123456`.
  2. Do pole IČO zadej 8místné číslo s neplatným kontrolním součtem `12345678`.
  3. Klikni na potvrzovací tlačítko.
- **Očekávaný výsledek:**
  - Formulář se neodešle.
  - U pole IČO se zobrazí validační chyba *Neplatné IČO*.
  - Zápis na kurz se nevytvoří.

---

### [TC-US12-04] Zamezení zápisu na kurz pro nepovolané role (Lektor a nepřihlášený host)
- **Pokrývá kritérium:** AC-5
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Přihlášen uživatel v roli Lektor, nebo je relace nepřihlášená.
- **Testovací data:**
  - URL registrace běhu: `/courses/1/register`.
- **Kroky:**
  1. Jako nepřihlášený návštěvník zadej do adresního řádku URL `/courses/1/register` a stiskni Enter.
  2. Přihlas se jako Lektor a otevři detail kurzu i přímou URL `/courses/1/register`.
- **Očekávaný výsledek:**
  - Zápis na kurz je umožněn výhradně uživatelům v roli zákazníka.
  - Nepřihlášený uživatel je přesměrován na přihlášení nebo do katalogu.
  - Lektorovi se tlačítko pro registraci nezobrazuje a pokus o odeslání přihlášky je systémem zamítnut.

---

### [TC-US12-05] Úspěšný zápis na kurz bez vyplnění nepovinného pole IČO
- **Pokrývá kritérium:** AC-1, AC-2, AC-6, AC-7
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Přihlášen zákazník na formuláři registrace běhu kurzu.
- **Testovací data:**
  - Platný telefon: `+420777999888`.
  - Pole IČO: prázdné (fyzická osoba nepodnikající).
- **Kroky:**
  1. Vyplň platné telefonní číslo `+420777999888`.
  2. Pole IČO ponech zcela prázdné.
  3. Klikni na potvrzovací tlačítko registrace.
- **Očekávaný výsledek:**
  - Formulář je úspěšně přijat (IČO je doplňkový nepovinný údaj).
  - Vytvoří se vazba studenta na daný běh kurzu a zákazník je přesměrován do "Moje kurzy".
