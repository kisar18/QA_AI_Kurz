# Test Casy: US-07 Ověření e-mailové adresy (Email Verification)

**Zdrojová User Story:** US-07  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + QA Tester  

---

### [TC-US07-01] Úspěšné ověření e-mailu pomocí platného podepsaného odkazu
- **Pokrývá kritérium:** AC-1, AC-2
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - Vytvořen nový uživatelský účet, který dosud nemá ověřenou e-mailovou adresu.
- **Testovací data:**
  - Platný ověřovací odkaz odeslaný na e-mail nového uživatele (např. `/email/verify/<id>/<hash>?expires=...&signature=...`).
- **Kroky:**
  1. Po dokončení registrace otevři platný ověřovací odkaz vygenerovaný systémem.
  2. Zkontroluj reakci aplikace a zobrazenou notifikaci.
  3. Zkontroluj stav účtu v uživatelském profilu nebo databázi (příznak `email_verified_at`).
- **Očekávaný výsledek:**
  - Otevření platného odkazu označí e-mail uživatele za úspěšně ověřený.
  - V uživatelském rozhraní se zobrazí zpráva o úspěšném dokončení ověření e-mailu.
  - Uživatel má plný přístup ke všem autorizovaným funkcím.

---

### [TC-US07-02] Odmítnutí pozměněného nebo vypršeného ověřovacího odkazu
- **Pokrývá kritérium:** AC-3
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - K dispozici je ověřovací odkaz, u kterého byl manuálně upraven parametr podpisu (`signature`) nebo ID uživatele.
- **Testovací data:**
  - Odkaz s poškozeným kryptografickým podpisem: `/email/verify/1/fake_hash?signature=neplatny_podpis`.
- **Kroky:**
  1. Zadej do adresního řádku prohlížeče ověřovací odkaz s pozměněným podpisem nebo vypršeným časovým razítkem.
  2. Stiskni Enter.
  3. Zkontroluj reakci systému.
- **Očekávaný výsledek:**
  - Systém detekuje neplatný či manipulovaný podpis (Invalid Signature / 403 Forbidden).
  - E-mail uživatele není označen jako ověřený.
  - Uživatel je informován o neplatnosti nebo expiraci ověřovacího odkazu.

---

### [TC-US07-03] Opětovné vyžádání nového ověřovacího odkazu z rozhraní aplikace
- **Pokrývá kritérium:** AC-4
- **Typ testu:** Pozitivní
- **Priorita:** Medium
- **Předpoklady:**
  - Uživatel je přihlášen na účet s dosud neověřeným e-mailem.
  - Otevřena stránka výzvy k ověření e-mailu `/email/verify`.
- **Testovací data:**
  - Přihlášený účet s neověřeným e-mailem.
- **Kroky:**
  1. Na stránce `/email/verify` klikni na tlačítko "Znovu odeslat ověřovací e-mail".
  2. Zkontroluj zobrazenou zprávu.
- **Očekávaný výsledek:**
  - Systém vygeneruje nový časově omezený ověřovací odkaz a odešle jej do schránky uživatele.
  - V rozhraní se zobrazí potvrzení: *Na vaši e-mailovou adresu byl odeslán nový ověřovací odkaz.*

---

### [TC-US07-04] Ochrana proti zahlcení (Rate Limiting) při opakovaném vyžádání ověření
- **Pokrývá kritérium:** AC-5
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Uživatel je na stránce `/email/verify` a právě odeslal požadavek na znovuzaslání ověření (podle TC-US07-03).
- **Testovací data:**
  - Opakované kliknutí bez časové prodlevy.
- **Kroky:**
  1. Okamžitě (do několika sekund) po prvním odeslání znovu klikni na tlačítko "Znovu odeslat ověřovací e-mail" opakovaně několikrát za sebou.
  2. Zkontroluj reakci aplikace.
- **Očekávaný výsledek:**
  - Systém aktivuje ochranu proti zahlcení a spamování (časový limit, např. 1 e-mail za minutu).
  - Požadavek je dočasně zablokován a uživatel je upozorněn, aby před dalším odesláním vyčkal.
