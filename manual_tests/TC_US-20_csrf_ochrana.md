# Test Casy: US-20 Ochrana proti podvržení požadavků (CSRF) a integrita sezení

**Zdrojová User Story:** US-20  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + QA Tester  

---

### [TC-US20-01] Přítomnost platného bezpečnostního CSRF tokenu ve formulářích
- **Pokrývá kritérium:** AC-1
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - Otevřeny formulářové stránky aplikace (`/login`, `/register`, `/courses/create`, `/profile`).
- **Testovací data:**
  - Formuláře pro odesílání POST požadavků.
- **Kroky:**
  1. Otevři v prohlížeči přihlašovací formulář `/login`.
  2. Otevři vývojářské nástroje (F12) a zkontroluj HTML kód formuláře `<form>`.
  3. Vyhledej skryté pole pro CSRF token (`<input type="hidden" name="_token" ...>` nebo meta tag `csrf-token`).
  4. Zkontroluj přítomnost tokenu i na stránce registrace `/register` a v profilu `/profile`.
- **Očekávaný výsledek:**
  - Každý formulář v aplikaci odesílající změnové požadavky obsahuje platný, kryptograficky náhodný CSRF token.
  - Token je součástí každého odesílaného požadavku chránícího uživatele proti útokům typu Cross-Site Request Forgery.

---

### [TC-US20-02] Odmítnutí formulářového požadavku s chybějícím nebo neplatným CSRF tokenem
- **Pokrývá kritérium:** AC-1, AC-2
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Otevřena stránka s formulářem (např. `/login`).
- **Testovací data:**
  - Požadavek s pozměněným nebo vymazaným CSRF tokenem.
- **Kroky:**
  1. Ve vývojářských nástrojích (F12 -> Elements) najdi skrytý element `_token` a smaž jeho hodnotu (nebo změň na `neplatny_podvrzeny_token_123`).
  2. Vyplň formulář a klikni na odesílací tlačítko.
  3. Zkontroluj HTTP odpověď serveru a chování aplikace.
- **Očekávaný výsledek:**
  - Požadavek bez platného tokenu je serverem neprodleně odmítnut.
  - Server vrací stavový kód 419 Page Expired (nebo 403 Forbidden).
  - Žádná změnová operace ani přihlášení se neprovede.

---

### [TC-US20-03] Regenerace identifikátoru sezení při přihlášení a odhlášení (Session Fixation ochrana)
- **Pokrývá kritérium:** AC-3
- **Typ testu:** Hraniční
- **Priorita:** High
- **Předpoklady:**
  - K dispozici je platný uživatelský účet.
- **Testovací data:**
  - Hodnota session cookie před a po změnách stavu autentizace.
- **Kroky:**
  1. V anonymním okně načti stránku `/login` a ve vývojářských nástrojích (F12 -> Application -> Cookies) zaznamenej hodnotu session cookie nepřihlášeného návštěvníka.
  2. Proveď úspěšné přihlášení do aplikace.
  3. Zkontroluj novou hodnotu session cookie po přihlášení a porovnej ji s původní anonymní hodnotou.
  4. V horní navigaci klikni na "Odhlásit se".
  5. Zkontroluj hodnotu session cookie po odhlášení a porovnej ji s hodnotou přihlášeného sezení.
- **Očekávaný výsledek:**
  - Při přihlášení dojde k automatické regeneraci ID sezení (hodnota cookie se změní na nový náhodný řetězec).
  - Při odhlášení je sezení zneplatněno a identifikátor je opět regenerován.
  - Systém spolehlivě zabraňuje útokům typu únos sezení (Session Fixation).
