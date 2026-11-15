# Test Casy: US-18 Zobrazení a aktualizace uživatelského profilu

**Zdrojová User Story:** US-18  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + QA Tester  

---

### [TC-US18-01] Předvyplnění existujících údajů a úspěšná aktualizace profilu
- **Pokrývá kritérium:** AC-1, AC-3, AC-6
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - Přihlášen uživatel s existujícím profilem.
  - Otevřena stránka profilu `/profile`.
- **Testovací data:**
  - Původní hodnoty: Jméno *Jan Novák*, E-mail `jan.novak@example.com`.
  - Nové platné hodnoty:
    - Jméno: `Jan Novák St.`
    - Telefon: `+420777123456`
    - IČO: `27082440` (platný kontrolní součet modulo 11)
- **Kroky:**
  1. Otevři stránku `/profile`.
  2. Zkontroluj, zda jsou v polích formuláře předvyplněna aktuální data uživatele (jméno a e-mail, případně stávající IČO a telefon).
  3. Změň jméno na `Jan Novák St.`.
  4. Vyplň doplňkové fakturační údaje: platný telefon `+420777123456` a platné IČO `27082440`.
  5. Klikni na tlačítko "Uložit" / "Aktualizovat profil".
- **Očekávaný výsledek:**
  - Formulář se úspěšně odešle a data se uloží.
  - Uživatel je přesměrován na domovskou stránku (`/home`).
  - V rozhraní se zobrazí zpráva o úspěšné aktualizaci údajů profilu.

---

### [TC-US18-02] Validace povinných polí jména a e-mailu a kontrola formátu e-mailu
- **Pokrývá kritérium:** AC-2
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Přihlášen uživatel na stránce `/profile`.
- **Testovací data:**
  - Test A: prázdné pole pro jméno.
  - Test B: neplatný formát e-mailu `email-bez-zavinace`.
- **Kroky:**
  1. Na stránce profilu smaž obsah pole Jméno a klikni na "Uložit".
  2. Zkontroluj zobrazenou validační chybu o povinnosti pole Jméno.
  3. Obnov jméno a do pole E-mail zadej neplatný formát `email-bez-zavinace` a klikni na "Uložit".
  4. Zkontroluj validační reakci pro pole E-mail.
- **Očekávaný výsledek:**
  - Formulář se neuloží a uživatel zůstává na stránce `/profile`.
  - Systém vyžaduje neprázdné jméno i e-mail a ověřuje platný formát e-mailové adresy.

---

### [TC-US18-03] Zamezení změny e-mailu na adresu již obsazenou jiným uživatelem
- **Pokrývá kritérium:** AC-2
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - V systému existují dva různí uživatelé: Uživatel A a Uživatel B (`obsazeny.email@example.com`).
  - Přihlášen je Uživatel A na stránce `/profile`.
- **Testovací data:**
  - E-mail Uživatele B: `obsazeny.email@example.com`.
- **Kroky:**
  1. V profilu Uživatele A přepiš pole E-mail na již existující e-mail Uživatele B.
  2. Klikni na tlačítko "Uložit".
- **Očekávaný výsledek:**
  - Systém změnu odmítne z důvodu kolize unikátnosti e-mailových adres.
  - Zobrazí se validační chyba (např. *Zadaný e-mail je již v systému používán*).
  - Původní e-mail Uživatele A zůstává zachován.

---

### [TC-US18-04] Validace formální platnosti IČO pomocí kontrolního součtu na profilu
- **Pokrývá kritérium:** AC-4
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Přihlášen uživatel na stránce `/profile`.
- **Testovací data:**
  - Neplatné IČO: `12345678` (nevyhovující modulo 11 kontrolní součet).
- **Kroky:**
  1. Do pole IČO vlož neplatné 8místné číslo `12345678`.
  2. Klikni na tlačítko "Uložit".
- **Očekávaný výsledek:**
  - Formulář se neuloží.
  - Zobrazí se validační chybová hláška *Neplatné IČO*.

---

### [TC-US18-05] Validace formátu telefonního čísla na profilu
- **Pokrývá kritérium:** AC-5
- **Typ testu:** Negativní
- **Priorita:** Medium
- **Předpoklady:**
  - Přihlášen uživatel na stránce `/profile`.
- **Testovací data:**
  - Neplatný telefon: `12` (příliš krátké číslo).
- **Kroky:**
  1. Do pole pro telefon vlož neplatnou hodnotu `12`.
  2. Klikni na tlačítko "Uložit".
- **Očekávaný výsledek:**
  - Formulář se neodešle.
  - Zobrazí se validační chyba *Neplatné telefonní číslo*.

---

### [TC-US18-06] Úspěšné uložení profilu s vymazáním nepovinných údajů (IČO a telefon)
- **Pokrývá kritérium:** AC-1, AC-3, AC-6
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Uživatel měl na profilu dříve uložené IČO i telefon a přeje si je odstranit.
- **Testovací data:**
  - Prázdné pole IČO a prázdné pole telefon.
- **Kroky:**
  1. Na stránce `/profile` vymaž stávající hodnoty z polí IČO a Telefon.
  2. Ponech vyplněné platné jméno a e-mail.
  3. Klikni na tlačítko "Uložit".
- **Očekávaný výsledek:**
  - Systém povolí smazání doplňkových fakturačních údajů (IČO a telefon nejsou povinné).
  - Profil se úspěšně aktualizuje a uživatel je přesměrován na `/home`.
