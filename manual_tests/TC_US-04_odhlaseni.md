# Test Casy: US-04 Bezpečné odhlášení ze systému

**Zdrojová User Story:** US-04  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + Nezávislý QA Kontrolor  

---

### [TC-US04-01] Úspěšné odhlášení přihlášeného uživatele přes horní navigaci
- **Pokrývá kritérium:** AC-1, AC-3
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - Uživatel (zákazník nebo lektor) je úspěšně přihlášen do systému.
  - Uživatel se nachází na úvodní/katalogové stránce (`/courses`).
- **Testovací data:**
  - Platný uživatelský účet (např. `jan.novak@example.com` / `Heslo123`).
- **Kroky:**
  1. Zkontroluj přítomnost tlačítka pro odhlášení v horní navigační liště.
  2. Klikni na tlačítko "Odhlásit se" v horní navigaci.
- **Očekávaný výsledek:**
  - Uživatel je úspěšně odhlášen ze systému.
  - Dojde k přesměrování na výchozí veřejnou stránku (katalog kurzů nebo přihlašovací formulář).
  - V horní navigaci již není zobrazeno tlačítko pro odhlášení ani odkaz na profil.
  - V horní navigaci je opět viditelný odkaz "Přihlásit se" pro nepřihlášené návštěvníky.

---

### [TC-US04-02] Okamžité zneplatnění uživatelského sezení a smazání klientského úložiště
- **Pokrývá kritérium:** AC-2
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Uživatel je přihlášen v prohlížeči.
  - V úložišti prohlížeče (DevTools -> Application -> Cookies a Web Storage) existuje aktivní autentizační session cookie (např. s názvem obsahujícím `session`) a případná lokální data relace.
- **Testovací data:**
  - Přihlášený uživatel se zavedenou platnou session cookie.
- **Kroky:**
  1. Otevři vývojářské nástroje prohlížeče (F12) v záložce Application / Úložiště a zkontroluj hodnotu autentizační session cookie a obsah `localStorage` / `sessionStorage` před odhlášením.
  2. V horní navigaci klikni na tlačítko "Odhlásit se".
  3. Zkontroluj stav cookies a webového úložiště v prohlížeči bezprostředně po odhlášení.
  4. Odešli HTTP požadavek na server s původní (předchozí) session cookie hodnotou.
- **Očekávaný výsledek:**
  - Původní session cookie je v prohlížeči smazána nebo nahrazena novou anonymní hodnotou s odlišným identifikátorem sezení.
  - V `localStorage` ani `sessionStorage` nezůstávají uloženy žádné citlivé autentizační tokeny či identifikační data uživatele.
  - Server odmítne starou session cookie a označí sezení za neplatné (vrací přesměrování na přihlášení nebo stav 401/302).
  - Uživatelské sezení je na straně serveru nevratně ukončeno.

---

### [TC-US04-03] Zamezení přístupu k privátním funkcím a profilu po odhlášení přes přímou URL
- **Pokrývá kritérium:** AC-4
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Uživatel byl přihlášen a následně se z aplikace úspěšně odhlásil.
  - Prohlížeč je ve stavu odhlášeného anonymního návštěvníka.
- **Testovací data:**
  - URL privátních sekcí: `/profile` (Uživatelský profil) a `/my-courses` (Moje kurzy).
- **Kroky:**
  1. Po dokončeném odhlášení zadej do adresního řádku prohlížeče URL adresu uživatelského profilu `/profile` a stiskni Enter.
  2. Zkontroluj reakci systému a viditelnost formuláře/údajů profilu.
  3. Do adresního řádku zadej privátní URL `/my-courses` a stiskni Enter.
  4. Zkontroluj reakci systému a viditelnost seznamu zapsaných kurzů.
- **Očekávaný výsledek:**
  - Anonymnímu uživateli není umožněn přístup k údajům profilu ani k seznamu zapsaných kurzů.
  - Vstupní pole profilu (např. editace jména, e-mailu) i privátní tabulky kurzů zůstávají skryté.
  - Uživatel je přesměrován na přihlašovací stránku `/login` nebo informován o nutnosti přihlášení.

---

### [TC-US04-04] Zabezpečení proti neoprávněnému návratu pomocí tlačítka Zpět v prohlížeči
- **Pokrývá kritérium:** AC-2, AC-4
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Uživatel je přihlášen a otevře privátní stránku svého profilu (`/profile`).
- **Testovací data:**
  - Přihlášený uživatelský profil.
- **Kroky:**
  1. Na stránce profilu klikni v horní navigaci na tlačítko "Odhlásit se".
  2. Vyčkej na přesměrování na veřejnou stránku a ověř odhlášený stav.
  3. Klikni v panelu prohlížeče na tlačítko "Zpět" (Back) pro návrat v historii na předchozí URL `/profile`.
  4. Zkontroluj, zda nedošlo k obnovení aktivního sezení, a stiskni tlačítko Obnovit stránku (F5 / Reload).
- **Očekávaný výsledek:**
  - Tlačítko Zpět neumožní provádět žádné autorizované změny v profilu.
  - Po obnovení stránky nebo pokusu o interakci systém neakceptuje relaci a přesměruje uživatele na přihlášení nebo zobrazí prázdnou/anonymní stránku bez citlivých uživatelských dat.
  - Uživatelské sezení zůstává nekompromisně ukončeno.

---

### [TC-US04-05] Trvalá dostupnost tlačítka odhlášení na všech typech stránek a rozlišení
- **Pokrývá kritérium:** AC-1
- **Typ testu:** Pozitivní
- **Priorita:** Medium
- **Předpoklady:**
  - Uživatel je přihlášen do aplikace.
- **Testovací data:**
  - Přihlášený běžný uživatel.
  - Zobrazení: Desktopové rozlišení (1920x1080) a mobilní zobrazení (375x667).
- **Kroky:**
  1. V desktopovém zobrazení otevři katalog kurzů (`/courses`) a ověř přítomnost tlačítka "Odhlásit se" v horní navigaci.
  2. Otevři detail libovolného nabízeného kurzu a ověř přítomnost tlačítka "Odhlásit se" v navigaci.
  3. Přejdi do sekce profilu (`/profile`) a sekce mých kurzů (`/my-courses`) a ověř viditelnost tlačítka "Odhlásit se".
  4. Přepni zobrazení na mobilní viewport (např. šířka 375 px) a ověř, že tlačítko pro odhlášení je dostupné přímo v liště nebo v rozklikávacím hamburger menu na max. 1–2 kliky.
  5. Přímo z detailu kurzu nebo mobilního menu klikni na tlačítko "Odhlásit se".
- **Očekávaný výsledek:**
  - Tlačítko "Odhlásit se" je trvale a konzistentně dostupné na všech typech stránek v přihlášeném stavu bez ohledu na velikost obrazovky.
  - Kliknutí na odhlášení odkudkoliv z aplikace spolehlivě ukončí sezení a vrátí uživatele do veřejného režimu.

---

### [TC-US04-06] Odhlášení v jedné záložce a souběžná interakce v druhé otevřené záložce
- **Pokrývá kritérium:** AC-2, AC-4
- **Typ testu:** Hraniční
- **Priorita:** High
- **Předpoklady:**
  - Uživatel je přihlášen do aplikace ve stejném prohlížeči ve dvou souběžně otevřených záložkách (Záložka A a Záložka B).
  - V Záložce A je otevřen katalog kurzů (`/courses`).
  - V Záložce B je otevřena privátní editace profilu (`/profile`).
- **Testovací data:**
  - Přihlášený uživatelský účet se sdíleným sezením prohlížeče.
- **Kroky:**
  1. V Záložce A klikni na tlačítko "Odhlásit se" a vyčkej na dokončení odhlášení.
  2. Přepni se do Záložky B (kde je UI vizuálně stále ve zdánlivě přihlášeném stavu).
  3. V Záložce B se pokus odeslat formulář úpravy profilu kliknutím na tlačítko Uložit / Změnit.
  4. V Záložce B zkus kliknout na privátní navigační odkaz (např. "Moje kurzy") nebo provést obnovení stránky (F5).
- **Očekávaný výsledek:**
  - Aplikace v Záložce B neprovede uložení dat ani neskončí neošetřenou systémovou chybou (500 Internal Server Error).
  - Požadavek je serverem zamítnut z důvodu neplatného/ukončeného sezení.
  - Uživatel je v Záložce B okamžitě přesměrován na přihlašovací obrazovku s informací o vypršení sezení a horní navigace se synchronizuje do odhlášeného stavu.
