# Test Casy: US-02 Registrace zákaznického účtu s automatickým přihlášením

**Zdrojová User Story:** US-02  
**Datum vytvoření:** 2026-11-09  
**Autor návrhu:** AI Agent + QA Tester  

---

### [TC-US02-01] Úspěšná registrace nového uživatele a automatické přihlášení
- **Pokrývá kritérium:** AC-1, AC-7
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí.
  - Uživatel není přihlášen.
  - Otevřena stránka registrace (`/register`).
- **Testovací data:**
  - Jméno: `Jan Novák`
  - E-mail: unikátní nová adresa (např. `jan.novak.test@example.com`)
  - Heslo: `BezpecneHeslo123`
  - Potvrzení hesla: `BezpecneHeslo123`
- **Kroky:**
  1. Otevři v prohlížeči stránku registrace `/register`.
  2. Zkontroluj přítomnost všech formulářových polí: Jméno, E-mail, Heslo a Potvrzení hesla.
  3. Vyplň platné jméno do pole Jméno.
  4. Vyplň nový unikátní e-mail do pole E-mail.
  5. Vyplň heslo do obou polí (Heslo i Potvrzení hesla).
  6. Klikni na tlačítko "Zaregistrovat".
- **Očekávaný výsledek:**
  - Uživatel je úspěšně zaregistrován a automaticky přihlášen do systému.
  - Dochází k přesměrování na domovskou stránku `/home`.
  - V pravém horním rohu je zobrazena uvítací zpráva se jménem uživatele a role zákazníka.

---

### [TC-US02-02] Validace povinných polí při odeslání prázdného formuláře
- **Pokrývá kritérium:** AC-2, AC-6
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Otevřena stránka registrace `/register`.
- **Testovací data:**
  - Všechna pole ponechána prázdná.
- **Kroky:**
  1. Otevři stránku registrace.
  2. Bez vyplnění jakéhokoliv pole klikni na tlačítko "Zaregistrovat".
- **Očekávaný výsledek:**
  - Formulář se neodešle a uživatel zůstává na stránce `/register`.
  - U všech povinných polí (Jméno, E-mail, Heslo, Potvrzení hesla) se zobrazí validační chybová hlášení upozorňující na nutnost jejich vyplnění.

---

### [TC-US02-03] Pokus o registraci s již existujícím e-mailem
- **Pokrývá kritérium:** AC-3
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - V systému již existuje registrovaný účet s e-mailem `user@example.com`.
  - Otevřena stránka registrace `/register`.
- **Testovací data:**
  - Jméno: `Petr Pokusný`
  - E-mail: `user@example.com`
  - Heslo: `BezpecneHeslo123`
  - Potvrzení hesla: `BezpecneHeslo123`
- **Kroky:**
  1. Vyplň registrační formulář s e-mailem, který již v databázi existuje.
  2. Klikni na tlačítko "Zaregistrovat".
- **Očekávaný výsledek:**
  - Registrace je zamítnuta.
  - Uživatel zůstává na formuláři registrace.
  - U pole E-mail se zobrazí chybová zpráva informující, že účet s tímto e-mailem již existuje.

---

### [TC-US02-04] Normalizace e-mailu a case-insensitivity unikátnosti
- **Pokrývá kritérium:** AC-4
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - V systému již existuje účet `user@example.com`.
  - Otevřena stránka registrace `/register`.
- **Testovací data:**
  - Jméno: `Test Case`
  - E-mail: `  USER@EXAMPLE.COM  ` (velká písmena + úvodní a koncové mezery)
  - Heslo: `BezpecneHeslo123`
  - Potvrzení hesla: `BezpecneHeslo123`
- **Kroky:**
  1. Zadej do pole E-mail adresu `  USER@EXAMPLE.COM  `.
  2. Vyplň ostatní pole platnými hodnotami a odešli formulář.
- **Očekávaný výsledek:**
  - Systém ořeže bílé znaky, převede e-mail na malá písmena a detekuje konflikt s existujícím `user@example.com`.
  - Registrace je zamítnuta s chybou duplicity e-mailu.

---

### [TC-US02-05] Neshoda hesla a potvrzení hesla
- **Pokrývá kritérium:** AC-5, AC-6
- **Typ testu:** Negativní
- **Priorita:** Medium
- **Předpoklady:**
  - Otevřena stránka registrace `/register`.
- **Testovací data:**
  - Jméno: `Karel Nový`
  - E-mail: unikátní e-mail
  - Heslo: `BezpecneHeslo123`
  - Potvrzení hesla: `JineHeslo456`
- **Kroky:**
  1. Vyplň jméno a unikátní e-mail.
  2. Zadej do pole Heslo hodnotu `BezpecneHeslo123`.
  3. Zadej do pole Potvrzení hesla hodnotu `JineHeslo456`.
  4. Klikni na "Zaregistrovat".
- **Očekávaný výsledek:**
  - Formulář se neodešle.
  - U pole potvrzení hesla se zobrazí chybová hláška (např. "Hesla se neshodují").

---

### [TC-US02-06] Ověření navigačních odkazů na stránce registrace
- **Pokrývá kritérium:** AC-8
- **Typ testu:** Pozitivní
- **Priorita:** Low
- **Předpoklady:**
  - Otevřena stránka registrace `/register`.
- **Testovací data:**
  - Žádná.
- **Kroky:**
  1. Ověř přítomnost odkazu "Již máte účet? Přihlaste se" a klikni na něj.
  2. Zkontroluj přesměrování na `/login`.
  3. Vrať se na `/register`.
  4. Ověř přítomnost odkazu pro obnovu hesla "Zapomněli jste heslo?" a klikni na něj.
- **Očekávaný výsledek:**
  - Odkaz pro přihlášení přesměruje uživatele na stránku `/login`.
  - Odkaz pro obnovu hesla přesměruje uživatele na stránku `/forgot-password`.

