# Test Casy: US-06 Dokončení změny hesla pomocí tokenu

**Zdrojová User Story:** US-06  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + QA Tester  

---

### [TC-US06-01] Úspěšné nastavení nového hesla s platným tokenem
- **Pokrývá kritérium:** AC-1, AC-2, AC-3, AC-4
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - V systému byl vygenerován platný a dosud nevypršený resetovací odkaz pro existujícího uživatele (např. `/reset-password/<token>?email=user@example.com`).
- **Testovací data:**
  - Nové platné heslo: `NoveSilneHeslo2026!`
  - Potvrzení hesla: `NoveSilneHeslo2026!`
- **Kroky:**
  1. Otevři v prohlížeči platný resetovací odkaz z e-mailu.
  2. Zkontroluj přítomnost polí pro zadání nového hesla a potvrzení hesla.
  3. Zadej nové bezpečné heslo do pole Nové heslo.
  4. Zadej shodné heslo do pole Potvrzení hesla.
  5. Klikni na tlačítko "Uložit nové heslo" / "Resetovat heslo".
- **Očekávaný výsledek:**
  - Systém ověří platnost tokenu a uloží nové heslo uživatele.
  - Zobrazí se potvrzovací zpráva o úspěšné změně hesla.
  - V rozhraní je nabídnut přímý odkaz pro přihlášení a uživatel se může úspěšně přihlásit s novým heslem.

---

### [TC-US06-02] Validace neshody nového hesla a kontrolního potvrzení
- **Pokrývá kritérium:** AC-2, AC-3
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Otevřen formulář resetu hesla s platným tokenem.
- **Testovací data:**
  - Nové heslo: `HesloABC123!`
  - Neshodné potvrzení: `HesloXYZ789!`
- **Kroky:**
  1. Vyplň pole Nové heslo hodnotou `HesloABC123!`.
  2. Vyplň pole Potvrzení hesla odlišnou hodnotou `HesloXYZ789!`.
  3. Klikni na tlačítko pro uložení hesla.
- **Očekávaný výsledek:**
  - Formulář se neuloží a heslo se nezmění.
  - Systém zobrazí validační chybu upozorňující, že zadaná hesla se neshodují.

---

### [TC-US06-03] Pokus o nastavení hesla s neplatným nebo pozměněným tokenem
- **Pokrývá kritérium:** AC-1, AC-5
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Uživatel má odkaz s neplatným nebo ručně pozměněným tokenem (např. `/reset-password/neplatny_token_12345`).
- **Testovací data:**
  - Neplatný kryptografický token.
  - Libovolné platné nové heslo.
- **Kroky:**
  1. Zadej do adresního řádku URL resetu hesla s pozměněným/neplatným tokenem.
  2. Zkus odeslat formulář s novým heslem.
- **Očekávaný výsledek:**
  - Systém rozpozná neplatnost tokenu a operaci odmítne.
  - Zobrazí se chybová zpráva o neplatném požadavku na obnovu hesla.
  - Heslo uživatele zůstává beze změny.

---

### [TC-US06-04] Pokus o použití vypršeného nebo již jednou použitého tokenu
- **Pokrývá kritérium:** AC-1, AC-5
- **Typ testu:** Hraniční
- **Priorita:** High
- **Předpoklady:**
  - Uživatel již úspěšně dokončil reset hesla pomocí tokenu (nebo vypršela časová platnost odkazu, např. 60 minut).
- **Testovací data:**
  - Expirovaný nebo již dříve konzumovaný resetovací odkaz.
- **Kroky:**
  1. V historii prohlížeče znovu otevři odkaz s již jednou použitým resetovacím tokenem.
  2. Zkus zadat další nové heslo a odeslat formulář.
- **Očekávaný výsledek:**
  - Systém jednorázový token neakceptuje podruhé.
  - Uživatel je informován o vypršení platnosti nebo neplatnosti odkazu.

---

### [TC-US06-05] Kontrola bezpečnostních pravidel pro minimální sílu hesla
- **Pokrývá kritérium:** AC-2, AC-3
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Otevřen formulář s platným tokenem.
- **Testovací data:**
  - Příliš krátké heslo (např. `123`).
- **Kroky:**
  1. Do polí Nové heslo i Potvrzení hesla zadej příliš krátké heslo `123`.
  2. Klikni na tlačítko pro uložení hesla.
- **Očekávaný výsledek:**
  - Systém odmítne slabé heslo.
  - Zobrazí se validační chyba vyžadující splnění minimální délky a bezpečnostních pravidel.
