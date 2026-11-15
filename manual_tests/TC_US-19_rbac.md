# Test Casy: US-19 Řízení přístupu na základě rolí (RBAC a autorizace API)

**Zdrojová User Story:** US-19  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + Nezávislý QA Kontrolor  

---

### [TC-US19-01] Dostupnost veřejných sekcí aplikace pro nepřihlášeného návštěvníka
- **Pokrývá kritérium:** AC-1
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - Uživatel není přihlášen (anonymní návštěvník).
- **Testovací data:**
  - Seznam veřejně povolených cest: `/`, `/courses`, `/courses/1`, `/login`, `/register`.
- **Kroky:**
  1. Otevři v prohlížeči úvodní rozcestník `/`.
  2. Přejdi do katalogu kurzů `/courses`.
  3. Otevři základní detail libovolného kurzu (např. `/courses/1`).
  4. Otevři přihlašovací formulář `/login` a následně registrační formulář `/register`.
- **Očekávaný výsledek:**
  - Všechny uvedené veřejné stránky jsou anonymnímu návštěvníkovi plně přístupné bez vyžádání přihlášení.
  - V horní navigaci se zobrazuje volba pro přihlášení a registraci.
  - Na detailu kurzu se zobrazuje název, popis a vypsané termíny, přičemž privátní tlačítka zápisu či správy lektora nejsou aktivní.

---

### [TC-US19-02] Zamezení přístupu a automatické přesměrování neautentizovaného uživatele na katalog kurzů
- **Pokrývá kritérium:** AC-2, AC-6
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Uživatel není přihlášen do systému.
- **Testovací data:**
  - Seznam chráněných privátních URL:
    - `/profile` (Uživatelský profil)
    - `/my-courses` (Mé zapsané kurzy)
    - `/courses/create` (Vytvoření kurzu)
    - `/courses/1/register` (Registrační formulář na kurz)
- **Kroky:**
  1. Zadej do adresního řádku URL profilu `/profile` a stiskni Enter.
  2. Zkontroluj reakci systému a výslednou URL adresu.
  3. Zadej do adresního řádku URL sekce zapsaných kurzů `/my-courses` a stiskni Enter.
  4. Zadej URL lektorské tvorby kurzu `/courses/create` a stiskni Enter.
  5. Zadej URL objednávky kurzu `/courses/1/register` a stiskni Enter.
- **Očekávaný výsledek:**
  - Systém striktně odmítne přístup k jakékoliv privátní sekci bez platného sezení.
  - Žádná soukromá data profilu, kurzů ani formuláře se nezobrazí.
  - Nepřihlášený uživatel je v souladu s AC-6 automaticky přesměrován na katalog kurzů (`/courses`).

---

### [TC-US19-03] Zpřístupnění lektorských akcí výhradně pro uživatele v roli Lektor
- **Pokrývá kritérium:** AC-3
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - V systému existuje uživatelský účet s přiřazenou rolí lektora.
  - Lektor je úspěšně přihlášen do aplikace.
- **Testovací data:**
  - Přihlašovací údaje lektora (např. `lektor@example.com` / `HesloLektor123`).
- **Kroky:**
  1. Po přihlášení lektora otevři katalog kurzů `/courses`.
  2. Zkontroluj přítomnost tlačítka pro vytvoření nového kurzu ("Přidat kurz") v horní části katalogu.
  3. Klikni na "Přidat kurz" a ověř načtení formuláře `/courses/create`.
  4. Přejdi na detail libovolného existujícího kurzu (`/courses/1`).
  5. Ověř přítomnost tlačítka pro vypsání nového běhu ("Přidat iteraci") a tlačítka pro zobrazení přihlášených studentů ("Přihlášení").
  6. Kliknutím na "Přihlášení" otevři seznam účastníků běhu kurzu (`/courses/1/participants`).
- **Očekávaný výsledek:**
  - Lektor má v rozhraní plně dostupné všechny lektorské nástroje: tvorbu nového kurzu, vypisování termínů i zobrazení seznamu přihlášených studentů.
  - Všechny související formuláře a tabulky se lektorovi korektně a bez chyb zobrazí.

---

### [TC-US19-04] Zamezení přístupu běžného zákazníka k lektorským operacím v UI
- **Pokrývá kritérium:** AC-4
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Přihlášen uživatel v roli běžného zákazníka (studenta).
- **Testovací data:**
  - Zákaznický účet (např. `klient@example.com` / `Heslo123`).
  - Lektorské URL: `/courses/create`, `/courses/1/create-iteration`, `/courses/1/participants`.
- **Kroky:**
  1. V roli zákazníka otevři katalog kurzů `/courses`.
  2. Zkontroluj, zda se v rozhraní zobrazuje tlačítko "Přidat kurz" nebo tlačítka "Přidat iteraci".
  3. Otevři detail kurzu `/courses/1` a zkontroluj, zda je přítomno tlačítko pro zobrazení účastníků běhu.
  4. Zadej do adresního řádku prohlížeče přímou URL `/courses/create` a stiskni Enter.
  5. Zadej přímou URL pro vypsání termínu `/courses/1/create-iteration` a stiskni Enter.
  6. Zadej přímou URL seznamu studentů `/courses/1/participants` a stiskni Enter.
- **Očekávaný výsledek:**
  - Zákazník v uživatelském rozhraní vůbec nevidí tlačítka pro tvorbu kurzu, vypsání termínu ani seznam přihlášených účastníků.
  - Při pokusu o přímé vyvolání lektorských URL systém požadavek okamžitě zamítne (chyba 403 Forbidden, odmítnutí oprávnění, nebo přesměrování do klientské sekce).
  - Běžný student se v žádném případě nedostane k citlivým údajům ostatních studentů ani k modifikaci nabídky kurzů.

---

### [TC-US19-05] Zamezení zápisu na běhy kurzů pro uživatele v roli Lektor (UI i API úroveň)
- **Pokrývá kritérium:** AC-5
- **Typ testu:** Negativní
- **Priorita:** Medium
- **Předpoklady:**
  - Do aplikace je přihlášen uživatel v roli Lektor.
- **Testovací data:**
  - Účet lektora.
  - URL registračního formuláře kurzu: `/courses/1/register`.
- **Kroky:**
  1. V roli lektora otevři detail kurzu `/courses/1`.
  2. Zkontroluj vypsané termíny kurzu a přítomnost tlačítka pro zápis ("Nezávazná registrace").
  3. Zadej do adresního řádku přímou URL pro zápis na kurz `/courses/1/register` a stiskni Enter.
  4. Ve vývojářských nástrojích (DevTools Console / Network) simuluj odeslání HTTP POST požadavku pro registraci na kurz se sezením lektora (např. odesláním formuláře na koncový bod zápisu).
- **Očekávaný výsledek:**
  - Lektorovi se na kartách termínů nezobrazuje tlačítko pro registraci na kurz (místo něj má k dispozici lektorské akce).
  - Zápis na kurz je vyhrazen zákazníkům; přímý přístup na formulář zápisu je odmítnut.
  - Pokud lektor zkusí odeslat POST požadavek na zápis, backend operaci odmítne (vrátí chybu 403 Forbidden nebo validační chybu nepovolené role).

---

### [TC-US19-06] Nedostupnost servisních a údržbových rozhraní pro neautorizované návštěvníky
- **Pokrývá kritérium:** AC-7
- **Typ testu:** Hraniční
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží v testovacím/produkčním prostředí.
  - Uživatel není přihlášen, nebo je v běžné klientské roli.
- **Testovací data:**
  - Potenciální interní a servisní trasy: `/artisan`, `/migrate`, `/system-cache`, `/_ignition`, `/telescope`.
- **Kroky:**
  1. Zadej do adresního řádku prohlížeče URL `/artisan` a stiskni Enter.
  2. Zadej URL pro spouštění migrací `/migrate` a stiskni Enter.
  3. Zadej URL pro správu/čištění mezipaměti `/system-cache` a stiskni Enter.
  4. Zkontroluj HTTP stavové kódy odpovědí serveru.
- **Očekávaný výsledek:**
  - Žádné servisní, diagnostické ani údržbové funkce nejsou vystaveny veřejnému přístupu.
  - Server vrací kód 404 Not Found nebo 403 Forbidden.
  - Systém nezveřejňuje žádné interní ladicí informace, konfigurace prostředí ani výpisy zásobníku (stack trace).

---

### [TC-US19-07] Přepnutí rolí a okamžitá aktualizace autorizačních oprávnění v sezení
- **Pokrývá kritérium:** AC-3, AC-4
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - K dispozici jsou dva testovací účty: jeden s rolí Zákazník a druhý s rolí Lektor.
- **Testovací data:**
  - Účet zákazníka a účet lektora.
- **Kroky:**
  1. Přihlas se do aplikace jako Zákazník.
  2. Ověř nepřítomnost lektorských prvků v katalogu kurzů `/courses`.
  3. Odhlas se z aplikace.
  4. V tomtéž okně prohlížeče se ihned přihlas jako Lektor.
  5. Otevři katalog kurzů `/courses` a ověř, že se lektorské prvky (např. tlačítko "Přidat kurz") okamžitě zobrazují.
  6. Odhlas se a znovu přihlas jako Zákazník.
- **Očekávaný výsledek:**
  - Oprávnění uživatele jsou deterministicky řízena jeho aktuální rolí v aktivním sezení.
  - V aplikaci nedochází k uvíznutí mezipaměti oprávnění (permission caching) ani k prolínání práv mezi různými přihlášeními v rámci jednoho prohlížeče.

---

### [TC-US19-08] Zamezení neoprávněné manipulace s daty přes přímé API / POST požadavky
- **Pokrývá kritérium:** AC-2, AC-4
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Přihlášen uživatel v roli Zákazník, nebo je relace nepřihlášená.
- **Testovací data:**
  - Payload pro vytvoření kurzu: `{"name": "Hacker Course", "description": "Test", "capacity": 10, "price": 1000}`.
  - Koncový bod: `POST /courses` (nebo odpovídající backend route pro tvorbu kurzu).
- **Kroky:**
  1. Jako běžný zákazník otevři vývojářské nástroje prohlížeče (F12 -> Console / Network) nebo použij REST klienta s aktivním session cookie zákazníka.
  2. Odešli přímý HTTP POST požadavek na vytvoření kurzu s platným payloadem a CSRF tokenem.
  3. Zkontroluj HTTP stavový kód odpovědi serveru.
  4. V katalogu kurzů ověř, zda nedošlo k vytvoření nového kurzu.
- **Očekávaný výsledek:**
  - Backend provádí striktní kontrolu role na straně serveru (nejen skrýváním UI prvků).
  - Požadavek zákazníka je odmítnut stavovým kódem 403 Forbidden (nebo 401 Unauthorized pro nepřihlášeného).
  - V databázi ani v katalogu kurzů žádný neautorizovaný kurz nevznikne.

---

### [TC-US19-09] Ochrana proti horizontální eskalaci práv (IDOR) mezi lektory
- **Pokrývá kritérium:** AC-3, AC-4
- **Typ testu:** Hraniční
- **Priorita:** High
- **Předpoklady:**
  - V systému existují dva lektoři: Lektor A a Lektor B.
  - Lektor A spravuje Kurz 1, na jehož běh jsou přihlášeni studenti s osobními údaji (telefon, IČO, e-mail).
  - Přihlášen je Lektor B.
- **Testovací data:**
  - Účet Lektora B.
  - ID běhu kurzu patřícího Lektoru A (např. `/courses/1/participants`).
- **Kroky:**
  1. Po přihlášení Lektora B zadej do adresního řádku URL seznamu účastníků cizího kurzu `/courses/1/participants` a stiskni Enter.
  2. Zkontroluj odpověď systému a zobrazená data.
- **Očekávaný výsledek:**
  - Lektor B nemá oprávnění nahlížet do seznamu účastníků kurzu, jehož není garantem.
  - Systém přístup odmítne (kód 403 Forbidden nebo přesměrování s chybovou zprávou o nepovoleném přístupu).
  - Osobní údaje studentů Kurzu 1 zůstávají chráněny před neoprávněným přístupem jiných lektorů (prevence narušení ochrany osobních údajů).
