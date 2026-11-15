# Test Casy: US-03 Přihlášení do aplikace

**Zdrojová User Story:** US-03  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + Nezávislý QA Kontrolor  

---

### [TC-US03-01] Úspěšné přihlášení s platnými údaji a adaptace horní navigace podle role
- **Pokrývá kritérium:** AC-1, AC-5, AC-6
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - V systému existují dva platné účty: jeden v roli Zákazník a druhý v roli Lektor.
  - Otevřena přihlašovací stránka `/login`.
- **Testovací data:**
  - Účet A (Zákazník): `klient@example.com` / `HesloKlient123`
  - Účet B (Lektor): `lektor@example.com` / `HesloLektor123`
- **Kroky:**
  1. Otevři stránku `/login`.
  2. Zadej přihlašovací údaje Účtu A (Zákazník) a klikni na "Přihlásit se".
  3. Zkontroluj přesměrování a položky v horní navigaci pro zákazníka.
  4. Odhlas se kliknutím na "Odhlásit se".
  5. Na stránce `/login` zadej údaje Účtu B (Lektor) a klikni na "Přihlásit se".
  6. Zkontroluj přesměrování a položky v horní navigaci pro lektora.
- **Očekávaný výsledek:**
  - V obou případech je uživatel úspěšně přihlášen a přesměrován do systému na domovskou/katalogovou stránku (`/courses` nebo `/home`).
  - Odkaz "Přihlásit se" je v horní navigaci vždy skryt a zobrazí se tlačítko "Odhlásit se".
  - Navigace se přesně přizpůsobí roli:
    - **Pro Zákazníka:** Zpřístupní se zákaznické privátní sekce ("Moje kurzy", "Můj profil").
    - **Pro Lektora:** Zpřístupní se lektorské možnosti správy ("Přidat kurz", lektorská administrace).

---

### [TC-US03-02] Validace povinných polí a neplatného formátu e-mailu
- **Pokrývá kritérium:** AC-1, AC-2
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Otevřena přihlašovací stránka `/login`.
  - Uživatel není přihlášen.
- **Testovací data:**
  - Prázdné hodnoty.
  - Syntakticky neplatný e-mail: `chybi-zavinac-domena.cz`, `neplatny@`.
  - Platné heslo: `BezpecneHeslo123`.
- **Kroky:**
  1. Otevři stránku `/login`.
  2. Ponech obě pole (E-mail i Heslo) prázdná a klikni na tlačítko "Přihlásit se".
  3. Zkontroluj reakci prohlížeče a validační zprávy.
  4. Vyplň pouze platný e-mail, pole Heslo vymaž a klikni na "Přihlásit se".
  5. Vymaž pole E-mail, vyplň pouze heslo a klikni na "Přihlásit se".
  6. Do pole E-mail zadej neplatný formát bez zavináče `chybi-zavinac-domena.cz`, vyplň heslo a klikni na "Přihlásit se".
- **Očekávaný výsledek:**
  - Formulář se v žádném z případů neodešle a stránka zůstává na URL `/login`.
  - Prohlížeč aktivuje validační hlášku upozorňující na chybějící povinný údaj (při prázdných polích) nebo na neplatný formát e-mailové adresy (HTML5 type="email" validace).
  - Uživatel není přihlášen a žádný síťový neautorizovaný stav nevznikne.

---

### [TC-US03-03] Tolerance k velikosti písmen a automatické ořezávání mezer v e-mailu
- **Pokrývá kritérium:** AC-3, AC-5
- **Typ testu:** Pozitivní
- **Priorita:** Medium
- **Předpoklady:**
  - V systému existuje platný registrovaný uživatel (např. s e-mailem `jan.novak@example.com`).
  - Otevřena přihlašovací stránka `/login`.
- **Testovací data:**
  - Varianta e-mailu: `   JAN.NOVAK@EXAMPLE.COM   ` (velká písmena + úvodní a koncové mezery).
  - Platné heslo k danému účtu.
- **Kroky:**
  1. Do pole E-mail vlož adresu s mezerami na začátku a konci a zapsanou velkými písmeny.
  2. Do pole Heslo zadej platné heslo.
  3. Klikni na tlačítko "Přihlásit se".
- **Očekávaný výsledek:**
  - Systém automaticky normalizuje e-mail (odstraní bílé znaky na okrajích a provede case-insensitive porovnání).
  - Uživatel je úspěšně přihlášen a přesměrován do aplikace stejně jako při zadání přesného tvaru malými písmeny bez mezer.

---

### [TC-US03-04] Jednotná chybová hláška a bezpečnostní vyčištění pole hesla
- **Pokrývá kritérium:** AC-4
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Otevřena stránka `/login`.
  - V systému existuje uživatel `existujici.uzivatel@example.com`.
- **Testovací data:**
  - Scénář A (neexistující e-mail): `zcela.neexistujici.adresa999@example.com` / `Heslo123`
  - Scénář B (chybné heslo k existujícímu účtu): `existujici.uzivatel@example.com` / `SpatneHeslo999!`
- **Kroky:**
  1. Zadej neexistující e-mail a libovolné heslo (Scénář A) a klikni na "Přihlásit se".
  2. Zaznamenej zobrazenou chybovou zprávu a zkontroluj stav polí E-mail a Heslo.
  3. Zadej existující e-mail a chybné heslo (Scénář B) a klikni na "Přihlásit se".
  4. Porovnej chybovou zprávu ze Scénáře B s chybovou zprávou ze Scénáře A.
  5. Zkontroluj stav vstupních polí po zobrazení chyby ve Scénáři B.
- **Očekávaný výsledek:**
  - V obou scénářích je pokus o přihlášení zamítnut a uživatel zůstává na stránce `/login`.
  - Systém v obou případech zobrazí identickou, jednotnou chybovou hlášku (`These credentials do not match our records.`), která neprozrazuje existenci účtu (ochrana proti User Enumeration).
  - **Bezpečnostní a UX chování formuláře:** Pole pro zadání hesla je automaticky vymazáno (ochrana proti odpozorování hesla), zatímco zadaný e-mail zůstává předvyplněn pro usnadnění opravy.

---

### [TC-US03-05] Přístupné ovládání přihlašovacího formuláře z klávesnice
- **Pokrývá kritérium:** AC-7
- **Typ testu:** Pozitivní
- **Priorita:** Medium
- **Předpoklady:**
  - Načtena stránka `/login`.
- **Testovací data:**
  - Platný e-mail a heslo.
  - Klávesy `Tab`, `Shift+Tab`, `Enter`.
- **Kroky:**
  1. Klikni do záhlaví stránky a stiskni klávesu `Tab` pro přechod do prvního vstupního pole.
  2. Ověř, že aktivní focus je na poli E-mail, a vepiš platný e-mail.
  3. Stiskni klávesu `Tab` a ověř, že focus se přesunul do pole Heslo.
  4. Vepiš platné heslo do pole Heslo.
  5. Stiskni klávesu `Enter` přímo z pole pro zadání hesla (případně stiskni `Tab` na tlačítko "Přihlásit se" a stiskni `Enter`).
- **Očekávaný výsledek:**
  - Navigace mezi formulářovými prvky pomocí klávesy Tab probíhá v logickém pořadí (Email -> Heslo -> Přihlásit).
  - Každý prvek má při focusu zřetelný vizuální obrys (focus ring).
  - Stisk klávesy Enter formulář korektně odešle a provede úspěšné přihlášení a přesměrování.

---

### [TC-US03-06] Maskování zadaného hesla a doprovodné navigační odkazy formuláře
- **Pokrývá kritérium:** AC-1, AC-4
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Otevřena stránka `/login`.
- **Testovací data:**
  - Testovací heslo: `MojeTajneHeslo123`
- **Kroky:**
  1. Do pole Heslo vepiš testovací heslo.
  2. Zkontroluj, zda jsou zadané znaky maskovány tečkami nebo hvězdičkami a nejsou čitelné v prostém textu.
  3. Ve vývojářských nástrojích (F12) ověř, že vstupní element má atribut `type="password"`.
  4. Zkontroluj přítomnost doplňkových odkazů:
     - Odkaz pro obnovu zapomenutého hesla ("Zapomněli jste heslo?")
     - Odkaz na registraci nového účtu ("Zaregistrujte se")
  5. Klikni na odkaz pro obnovu hesla a ověř přechod na `/forgot-password`.
- **Očekávaný výsledek:**
  - Pole hesla striktně maskuje zadané znaky na obrazovce a zabraňuje neoprávněnému odpozorování (shoulder surfing).
  - Doprovodné odkazy pro obnovu hesla i registraci jsou viditelné a funkční.

---

### [TC-US03-07] Chování při pokusu o otevření stránky přihlášení již přihlášeným uživatelem
- **Pokrývá kritérium:** AC-5, AC-6
- **Typ testu:** Hraniční
- **Priorita:** Low
- **Předpoklady:**
  - Uživatel je již úspěšně přihlášen do aplikace.
- **Testovací data:**
  - URL přihlášení: `/login`.
- **Kroky:**
  1. V přihlášeném stavu zadej do adresního řádku prohlížeče URL `/login` a stiskni Enter.
  2. Zkontroluj chování aplikace a výslednou adresu.
- **Očekávaný výsledek:**
  - Aplikace nedovolí přihlášenému uživateli znovu vyplňovat přihlašovací formulář.
  - Uživatel je automaticky přesměrován zpět na výchozí domovskou/katalogovou stránku (`/courses` nebo `/home`).
  - Aktivní uživatelské sezení zůstává zachováno bez přerušení.
