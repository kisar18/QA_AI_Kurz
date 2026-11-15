# Test Casy: US-08 Ochrana proti útokům hrubou silou na přihlášení (Rate Limiting)

**Zdrojová User Story:** US-08  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + Nezávislý QA Kontrolor  

---

### [TC-US08-01] Průchod povoleného limitu 1 až 5 neúspěšných pokusů o přihlášení
- **Pokrývá kritérium:** AC-1, AC-2
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - Otevřena přihlašovací stránka `/login`.
  - Pro daný e-mail ani přístupové místo (IP adresu) nebyl v nedávné době aktivován rate limiter.
- **Testovací data:**
  - Testovací e-mail: platný registrovaný e-mail (např. `rate.test.user@example.com`).
  - Neplatné heslo: `SpatneHeslo123!`
- **Kroky:**
  1. Otevři stránku `/login`.
  2. Zadej testovací e-mail a neplatné heslo a klikni na "Přihlásit se" (1. pokus).
  3. Zkontroluj zobrazenou chybovou zprávu.
  4. Opakuj krok 2 a 3 pro 2., 3., 4. a 5. pokus se stejným e-mailem a neplatným heslem.
- **Očekávaný výsledek:**
  - Při každém z pokusů 1 až 5 systém pokus o přihlášení zamítne se standardní chybovou hláškou o neshodě údajů (např. `These credentials do not match our records.`).
  - Ani při 5. pokusu nedojde k blokaci formuláře a uživateli je stále umožněno provést další pokus.

---

### [TC-US08-02] Dočasná blokace při 6. neúspěšném pokusu a zobrazení odpočtu sekund
- **Pokrývá kritérium:** AC-1, AC-2, AC-3
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Pro testovací e-mail bylo bezprostředně před testem provedeno přesně 5 neúspěšných pokusů o přihlášení (podle TC-US08-01).
- **Testovací data:**
  - Testovací e-mail: stejný jako v předchozích 5 pokusech.
  - Heslo: libovolné heslo (neplatné i platné).
- **Kroky:**
  1. Na stránce `/login` zadej stejný testovací e-mail a neplatné heslo (6. pokus v řadě).
  2. Klikni na tlačítko "Přihlásit se".
  3. Ve vývojářských nástrojích (F12 -> Network) zkontroluj HTTP stavovou odpověď serveru (kód 429 Too Many Requests a hlavičku `Retry-After`).
  4. Zkontroluj zobrazené chybové hlášení v uživatelském rozhraní.
  5. Okamžitě zkus zadat správné heslo k danému e-mailu a znovu klikni na "Přihlásit se".
- **Očekávaný výsledek:**
  - 6. pokus je systémem okamžitě zablokován ochranným mechanismem Rate Limiting.
  - V rozhraní se zobrazí výstražná chybová zpráva o překročení počtu pokusů s konkrétním počtem sekund, po které je nutné vyčkat (např. `Too many login attempts. Please try again in 60 seconds.`).
  - Server vrací validační stavový kód 422 (případně 429) s chybovou zprávou odpovídající zobrazenému času.
  - Systém odmítne přihlášení i v případě, že uživatel během aktivní doby blokace zadá správné heslo.

---

### [TC-US08-03] Automatické vynulování počítadla neúspěšných pokusů po úspěšném přihlášení
- **Pokrývá kritérium:** AC-4
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - V systému existuje platný registrovaný uživatel.
  - Otevřena přihlašovací stránka `/login`.
- **Testovací data:**
  - E-mail: platný existující účet (např. `jan.novak@example.com`).
  - Správné heslo: `BezpecneHeslo123`
  - Chybné heslo: `ChybneHeslo999!`
- **Kroky:**
  1. Zadej platný e-mail a chybné heslo a odešli formulář celkem 4× za sebou.
  2. Ověř, že při každém pokusu se zobrazila standardní chyba o neplatných údajích (limit 5 pokusů nebyl překročen).
  3. Na 5. pokus zadej správné heslo a klikni na "Přihlásit se".
  4. Ověř úspěšné přihlášení a přesměrování do aplikace.
  5. V horní navigaci klikni na "Odhlásit se".
  6. Po přesměrování na `/login` zadej tentýž e-mail a chybné heslo (1. pokus po odhlášení).
- **Očekávaný výsledek:**
  - Po zadání správného hesla ve 3. kroku byl uživatel řádně přihlášen a systém interní čítač neúspěšných pokusů vynuloval na hodnotu 0.
  - Následný neúspěšný pokus v 6. kroku nezpůsobí blokaci, ale vyhodnotí se jako běžný 1. neúspěšný pokus nové série se standardní chybovou hláškou.

---

### [TC-US08-04] Obnovení možnosti přihlášení po vypršení časového limitu blokace
- **Pokrývá kritérium:** AC-3
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Testovací účet je v aktivním stavu blokace (vyvoláno 6 neúspěšnými pokusy) s oznámeným časovým limitem (např. 60 sekund).
- **Testovací data:**
  - Platný registrovaný e-mail a jeho správné heslo.
- **Kroky:**
  1. Zaznamenej čas začátku blokace a počet sekund indikovaných v chybové hlášce.
  2. Vyčkej po celou dobu indikovaného časového limitu plus 2 sekundy bezpečnostní rezerva.
  3. Zadej do formuláře na `/login` stejný e-mail a tentokrát správné heslo.
  4. Klikni na tlačítko "Přihlásit se".
- **Očekávaný výsledek:**
  - Po uplynutí zadaného intervalu dočasná blokace automaticky expirovala.
  - Pokus o přihlášení se správnými údaji proběhne úspěšně bez zobrazení hlášky o rate limitingu.
  - Uživatel je přihlášen a přesměrován do aplikace.

---

### [TC-US08-05] Izolace počítadla neúspěšných pokusů na konkrétní e-mailovou adresu
- **Pokrývá kritérium:** AC-1
- **Typ testu:** Hraniční
- **Priorita:** High
- **Předpoklady:**
  - V systému existují dva různé registrované uživatelské účty: Účet A a Účet B.
- **Testovací data:**
  - Účet A: `user.alpha@example.com` / `HesloAlpha123`
  - Účet B: `user.beta@example.com` / `HesloBeta123`
  - Chybné heslo: `ZcelaChybneHeslo000!`
- **Kroky:**
  1. Pro Účet A zadej 6× chybné heslo, dokud nedojde k aktivaci rate limitingu a blokaci pro Účet A.
  2. Ověř, že pokus pro Účet A je zablokován hláškou `Too many login attempts`.
  3. Na stejné stránce `/login` bez změny IP adresy či prohlížeče vyplň Účet B se správným heslem `HesloBeta123`.
  4. Klikni na tlačítko "Přihlásit se".
- **Očekávaný výsledek:**
  - Blokace účtu A neovlivní možnost přihlášení nezávislého legitimního účtu B.
  - Uživatel účtu B je úspěšně přihlášen a přesměrován do aplikace.
  - Rate limiting spolehlivě rozlišuje cíl útoku a nezpůsobuje plošný Denial of Service (DoS) pro ostatní uživatele.

---

### [TC-US08-06] Sjednocení počítadla při různé velikosti písmen v e-mailu (Case Sensitivity & Normalizace)
- **Pokrývá kritérium:** AC-1, AC-2
- **Typ testu:** Hraniční
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí.
  - Otevřena přihlašovací stránka `/login`.
- **Testovací data:**
  - Různé formáty zápisu téhož e-mailu:
    - 1. pokus: `caselimit.user@example.com`
    - 2. pokus: `CaseLimit.User@example.com`
    - 3. pokus: `CASELIMIT.USER@EXAMPLE.COM`
    - 4. pokus: ` CaseLimit.user@example.com ` (s mezerami na začátku a konci)
    - 5. pokus: `cAsElImIt.uSeR@example.com`
    - 6. pokus: `caselimit.user@example.com`
  - Neplatné heslo: `ChybneHeslo123!`
- **Kroky:**
  1. Postupně zadej 1. až 5. pokus s výše uvedenými variantami zápisu e-mailu a chybným heslem.
  2. Ověř, že každý pokus 1 až 5 vrací standardní chybovou hlášku o neshodě údajů.
  3. Jako 6. pokus zadej základní formát e-mailu `caselimit.user@example.com` s chybným heslem.
  4. Klikni na tlačítko "Přihlásit se".
- **Očekávaný výsledek:**
  - Systém interně normalizuje e-mail (odstranění mezer a převod na malá písmena) i pro účely rate limitingu.
  - Na 6. pokus je požadavek zablokován hláškou `Too many login attempts`.
  - Útočník nemůže obcházet limit pokusů střídáním malých a velkých písmen nebo vkládáním bílých znaků.

---

### [TC-US08-07] Ochrana proti útokům hrubou silou na neexistující účty (Prevence User Enumeration)
- **Pokrývá kritérium:** AC-1, AC-3
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Otevřena přihlašovací stránka `/login`.
- **Testovací data:**
  - Neexistující e-mail: náhodně vygenerovaná adresa, která v databázi prokazatelně neexistuje (např. `nonexistent.probe.999@example.com`).
  - Libovolné testovací heslo.
- **Kroky:**
  1. Zadej neexistující e-mail a heslo a odešli formulář 5× za sebou.
  2. Zkontroluj, že systém vrací jednotnou chybovou hlášku o neplatných údajích.
  3. Zadej tentýž neexistující e-mail pošesté (6. pokus) a klikni na "Přihlásit se".
- **Očekávaný výsledek:**
  - Po 5 neúspěšných pokusech dojde i u neexistujícího e-mailu k aktivaci ochrany Rate Limiting.
  - Na 6. pokus je požadavek zablokován chybou 429 s oznámením o nutnosti vyčkat zadaný počet sekund (`Too many login attempts. Please try again in X seconds.`).
  - Chování systému je identické pro existující i neexistující e-maily, což znemožňuje útočníkovi zjišťovat přítomnost účtů v systému (User Enumeration).

---

### [TC-US08-08] Pokus o odeslání přihlášení uprostřed doby aktivní blokace a kontrola odpočtu
- **Pokrývá kritérium:** AC-3
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Pro daný e-mail byla vyvolána blokace na 60 sekund (např. podle TC-US08-02).
- **Testovací data:**
  - Zablokovaný e-mail a platné heslo.
- **Kroky:**
  1. Bezprostředně po blokaci zaznamenej výchozí čas (60 sekund).
  2. Počkej přesně 20 sekund.
  3. Zadej tentýž e-mail a heslo a klikni na tlačítko "Přihlásit se".
  4. Zkontroluj novou chybovou zprávu a počet indikovaných sekund.
- **Očekávaný výsledek:**
  - Požadavek v době trvající blokace je serverem znovu zamítnut (stavový kód 429).
  - V chybové hlášce se zobrazí aktualizovaný zbývající čas odpovídající reálnému odpočtu (přibližně 40 sekund, tolerance ±2 s).
  - Předčasný pokus v průběhu blokace nezpůsobí pád aplikace ani nežádoucí okamžité vynulování čítače.
