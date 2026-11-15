# Test Casy: US-05 Žádost o obnovu zapomenutého hesla

**Zdrojová User Story:** US-05  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + QA Tester  

---

### [TC-US05-01] Úspěšné odeslání žádosti o reset hesla pro registrovaný e-mail
- **Pokrývá kritérium:** AC-1, AC-4
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - V systému existuje aktivní uživatelský účet.
  - Otevřena stránka obnovy hesla `/forgot-password`.
- **Testovací data:**
  - Platný registrovaný e-mail: `jan.novak@example.com`.
- **Kroky:**
  1. Otevři v prohlížeči stránku `/forgot-password`.
  2. Zkontroluj přítomnost pole pro e-mail a odesílacího tlačítka ("Odeslat odkaz pro obnovu hesla").
  3. Do pole pro e-mail zadej platný registrovaný e-mail.
  4. Klikni na odesílací tlačítko.
- **Očekávaný výsledek:**
  - Formulář se úspěšně odešle na server.
  - Systém vygeneruje bezpečný, časově omezený resetovací odkaz s kryptografickým tokenem.
  - V uživatelském rozhraní se zobrazí zřetelná potvrzovací zpráva (např. *Odkaz pro nastavení nového hesla byl odeslán na váš e-mail*).

---

### [TC-US05-02] Validace povinného pole při odeslání prázdného formuláře
- **Pokrývá kritérium:** AC-1, AC-2, AC-3
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Otevřena stránka `/forgot-password`.
- **Testovací data:**
  - Prázdná hodnota pole e-mailu.
- **Kroky:**
  1. Otevři stránku `/forgot-password`.
  2. Ponech pole pro e-mail prázdné.
  3. Klikni na odesílací tlačítko.
- **Očekávaný výsledek:**
  - Formulář se neodešle a stránka zůstává na `/forgot-password`.
  - Prohlížeč nebo server zobrazí validační chybu upozorňující, že e-mailové pole je povinné.
  - Žádný resetovací e-mail není vygenerován.

---

### [TC-US05-03] Validace neplatného formátu e-mailové adresy
- **Pokrývá kritérium:** AC-2, AC-3
- **Typ testu:** Negativní
- **Priorita:** Medium
- **Předpoklady:**
  - Otevřena stránka `/forgot-password`.
- **Testovací data:**
  - Neplatné formáty e-mailu: `neplatny-email-bez-zavinace`, `chybi_domena@`, `@chybi_jmeno.cz`.
- **Kroky:**
  1. Do pole pro e-mail vlož syntakticky chybnou adresu `neplatny-email-bez-zavinace`.
  2. Klikni na odesílací tlačítko.
  3. Zkontroluj reakci formuláře.
- **Očekávaný výsledek:**
  - Formulář se neodešle.
  - Zobrazí se validační chybové hlášení vyžadující platný formát e-mailové adresy.

---

### [TC-US05-04] Odeslání žádosti pro neexistující e-mail a prevence odhadování účtů
- **Pokrývá kritérium:** AC-3, AC-4
- **Typ testu:** Hraniční
- **Priorita:** High
- **Předpoklady:**
  - Otevřena stránka `/forgot-password`.
- **Testovací data:**
  - Neexistující e-mailová adresa (např. `zcela.neexistujici.konto999@example.com`).
- **Kroky:**
  1. Do pole pro e-mail zadej neexistující e-mailovou adresu v platném formátu.
  2. Klikni na odesílací tlačítko.
  3. Zkontroluj zobrazené hlášení v uživatelském rozhraní.
- **Očekávaný výsledek:**
  - Aplikace nesmí prozradit, zda e-mail v databázi existuje či nikoliv (prevence User Enumeration).
  - V rozhraní se zobrazí neutrální potvrzovací hlášení o odeslání odkazu, pokud účet existuje.
  - Na neexistující adresu se žádný resetovací token nevygeneruje.
