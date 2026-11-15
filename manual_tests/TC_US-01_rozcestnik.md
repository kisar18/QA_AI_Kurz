# Test Casy: US-01 Úvodní navigační rozcestník testovacích aplikací

**Zdrojová User Story:** US-01  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + Nezávislý QA Kontrolor  

---

### [TC-US01-01] Zobrazení rozcestníku, metadat stránky a přítomnost všech navigačních odkazů
- **Pokrývá kritérium:** AC-1, AC-2, AC-3
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - Prohlížeč je otevřen v čistém anonymním okně (nepřihlášený návštěvník).
- **Testovací data:**
  - Výchozí URL: `/`.
  - Očekávané textové odkazy rozcestníku:
    - `Kalkulacka`
    - `Testovací login`
    - `NextDate`
    - `Registrace na kurz`
    - `(výpis)`
    - `Demo-login`
- **Kroky:**
  1. Otevři v prohlížeči úvodní stránku `/`.
  2. Zkontroluj titulek okna prohlížeče (`<title>`) a přítomnost hlavního nadpisu rozcestníku (`<h1>`).
  3. Zkontroluj, zda se stránka načetla bez chyb (stavový kód HTTP 200 OK).
  4. Zkontroluj přehledný vertikální seznam odkazů na testovací nástroje (Linktree styl).
  5. Ověř viditelnost odkazů na Kalkulačku, Testovací login, NextDate a Registraci na kurz (včetně doplňkového odkazu výpisu).
  6. Ověř přítomnost a vizuální odlišení výrazného odkazu "Demo-login" pro vstup do aplikace kurzů.
- **Očekávaný výsledek:**
  - Titulek stránky v záložce prohlížeče i hlavní nadpis odpovídají testovacímu portálu (např. *Testovací portál Kitner*).
  - Úvodní stránka přehledně zobrazuje seznam všech dostupných testovacích aplikací a nástrojů portálu.
  - Všechny uvedené textové odkazy jsou viditelné a čitelné.
  - Odkaz "Demo-login" je zřetelně prezentován jako dominantní vstup do aplikace kurzů.

---

### [TC-US01-02] Navigace přes odkaz 'Demo-login' přímo do katalogu kurzů
- **Pokrývá kritérium:** AC-3
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Návštěvník se nachází na úvodním rozcestníku `/`.
  - Prohlížeč je v anonymním režimu (případně má platnou uživatelskou relaci).
- **Testovací data:**
  - Cílová URL katalogu kurzů: `/courses`.
- **Kroky:**
  1. Na úvodním rozcestníku `/` vyhledej výrazný odkaz/tlačítko "Demo-login".
  2. Klikni na odkaz "Demo-login".
  3. Zkontroluj URL v adresním řádku prohlížeče a obsah načtené stránky.
- **Očekávaný výsledek:**
  - Prohlížeč je okamžitě nasměrován na URL `/courses`.
  - Úspěšně se zobrazí stránka katalogu kurzů s nabídkou dostupných témat pro studenty.

---

### [TC-US01-03] Funkčnost, cílové adresy a bezpečnostní atributy externích odkazů
- **Pokrývá kritérium:** AC-2
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Otevřena úvodní stránka rozcestníku `/`.
- **Testovací data:**
  - Konkrétní cílové adresy (atribut `href`) a bezpečnostní atributy:
    - `Kalkulacka` -> URL směřující na modul kalkulačky (`/kalkulacka` nebo externí subdoména)
    - `Testovací login` -> URL směřující na testovací formulář přihlášení
    - `NextDate` -> URL modulu NextDate (`/nextdate`)
    - `Registrace na kurz` -> URL formuláře registrace
    - `(výpis)` -> URL pro výpis registrovaných účastníků kurzu
- **Kroky:**
  1. Ve vývojářských nástrojích (F12) zkontroluj atributy `href` a způsob otevírání externích odkazů:
     - Pokud odkaz otevírá novou záložku (`target="_blank"`), ověř přítomnost bezpečnostního atributu `rel="noopener noreferrer"` (ochrana proti Reverse Tabnabbing).
  2. Klikni na odkaz "Kalkulacka" a ověř úspěšné načtení aplikace kalkulačky.
  3. Vrať se na rozcestník a klikni na odkaz "Testovací login". Ověř načtení přihlašovacího testovacího formuláře.
  4. Vrať se na rozcestník a klikni na odkaz "NextDate". Ověř načtení formuláře pro výpočet následujícího data.
  5. Vrať se na rozcestník a klikni na odkaz "Registrace na kurz" a odkaz "(výpis)". Ověř dostupnost obou stránek.
- **Očekávaný výsledek:**
  - Všechny externí odkazy v seznamu jsou funkční a směrují na odpovídající testovací moduly.
  - Otevírání externích oken je zabezpečeno atributem `rel="noopener noreferrer"`.
  - Žádný z odkazů nevede na chybovou stránku (HTTP 404 Not Found ani 500 Internal Server Error).

---

### [TC-US01-04] Zpracování neexistující podstránky z rozcestníku
- **Pokrývá kritérium:** AC-1
- **Typ testu:** Negativní
- **Priorita:** Low
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí.
- **Testovací data:**
  - Neexistující URL pod rozcestníkem (např. `/neexistujici-nastroj-12345`).
- **Kroky:**
  1. Zadej do adresního řádku neexistující URL pod doménou portálu.
  2. Stiskni Enter.
  3. Zkontroluj reakci systému a stavový kód odpovědi (404 Not Found).
  4. Zkontroluj, zda chybová stránka nabízí možnost návratu na úvodní rozcestník.
- **Očekávaný výsledek:**
  - Systém korektně zachytí požadavek a vrátí standardní chybovou stránku 404 bez pádu aplikace či odhalení interních výpisů běhového prostředí.
  - Uživatel má možnost se jednoduše vrátit zpět na funkční rozcestník.

---

### [TC-US01-05] Responzivní zobrazení a čitelnost rozcestníku na mobilním zařízení
- **Pokrývá kritérium:** AC-1, AC-3
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Otevřen prohlížeč s možností emulace mobilního zařízení (DevTools Device Mode).
- **Testovací data:**
  - Mobilní viewport: šířka 375 px (např. iPhone SE / Android standard).
- **Kroky:**
  1. Nastav šířku okna na mobilní rozlišení (375x667).
  2. Načti úvodní stránku `/`.
  3. Zkontroluj rozložení odkazů (Linktree styl) a jejich čitelnost.
  4. Ověř, že texty odkazů se nepřekrývají, nevytváří nežádoucí horizontální posuvník a prvky mají dostatečnou dotykovou plochu pro kliknutí.
  5. Klikni na mobilním rozlišení na "Demo-login".
- **Očekávaný výsledek:**
  - Rozcestník se na mobilním zařízení zobrazuje přehledně, vertikální seznam odkazů je zarovnaný a plně čitelný.
  - Tlačítko "Demo-login" zůstává dominantní a funkční; přesměrování do katalogu funguje bez chyb i na mobilním zobrazení.

---

### [TC-US01-06] Přístupnost a navigace rozcestníku pomocí klávesnice
- **Pokrývá kritérium:** AC-1, AC-3
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Načtena úvodní stránka `/`.
- **Testovací data:**
  - Klávesy `Tab`, `Shift+Tab`, `Enter`.
- **Kroky:**
  1. Klikni do prázdného místa v záhlaví a stiskni klávesu `Tab`.
  2. Postupně procházej jednotlivé odkazy rozcestníku opakovaným stiskem klávesy `Tab`.
  3. Sleduj, zda je aktuálně vybraný odkaz vizuálně zvýrazněn (viditelný focus indikátor).
  4. Jakmile focus dorazí na odkaz "Demo-login", stiskni klávesu `Enter`.
- **Očekávaný výsledek:**
  - Všechny odkazy rozcestníku jsou sekvenčně dosažitelné pomocí klávesy Tab v logickém pořadí.
  - Každý odkaz má zřetelný obrys/focus indikátor při procházení.
  - Stisk klávesy Enter na odkazu "Demo-login" spolehlivě provede přesměrování do katalogu kurzů.
