# Test Casy: US-14 Vytvoření nového kurzu s kontrolou poměru stran obrázku

**Zdrojová User Story:** US-14  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + QA Tester  

---

### [TC-US14-01] Úspěšné vytvoření kurzu lektorem s obrázkem v poměru 16:9
- **Pokrývá kritérium:** AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - Přihlášen uživatel v roli lektora.
  - Otevřena stránka pro vytvoření kurzu `/courses/create`.
- **Testovací data:**
  - Název kurzu: `Automatizované testování v Pythonu`
  - Popis kurzu: `Kompletní kurz zaměřený na Playwright a Pytest od základů po CI/CD.`
  - Kapacita: `15` (kladné celé číslo)
  - Cena: `7500` (číselná hodnota v Kč)
  - Náhledový obrázek: grafický soubor s rozlišením `1920x1080` px (přesný poměr stran 16:9).
- **Kroky:**
  1. Otevři formulář `/courses/create`.
  2. Zkontroluj přítomnost polí: název, popis, kapacita, cena a pole pro nahrání souboru náhledu.
  3. Vyplň název kurzu a podrobný popis.
  4. Vyplň kapacitu `15` a cenu `7500`.
  5. Nahraj připravený obrázek v poměru stran 16:9.
  6. Klikni na tlačítko "Vytvořit kurz" / "Uložit".
- **Očekávaný výsledek:**
  - Formulář se úspěšně zpracuje bez chyb.
  - Nový kurz je vytvořen v databázi a zařazen do nabídky.
  - Lektor je přesměrován do přehledu kurzů (`/courses`), kde je nově vytvořený kurz ihned zobrazen včetně nahraného obrázku náhledu.

---

### [TC-US14-02] Validace povinných polí a číselných hodnot kapacity a ceny
- **Pokrývá kritérium:** AC-2, AC-3
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Přihlášen lektor na stránce `/courses/create`.
- **Testovací data:**
  - Test A: prázdný formulář.
  - Test B: neplatná kapacita `-5` nebo `nula`, nečíselná cena `zdarma`.
- **Kroky:**
  1. Ponech všechna pole prázdná a klikni na vytvoření kurzu (Test A).
  2. Zkontroluj zobrazené validační chyby u povinných polí.
  3. Zadej zápornou kapacitu `-5` a do ceny text `zdarma` (Test B) a odešli formulář.
  4. Zkontroluj reakci systému.
- **Očekávaný výsledek:**
  - Formulář se neuloží a kurz nevznikne.
  - Systém vyžaduje vyplnění všech povinných polí.
  - Pro pole kapacity systém vyžaduje kladné celé číslo a pro pole ceny platnou číselnou částku.

---

### [TC-US14-03] Odmítnutí náhledového obrázku s nevyhovujícím poměrem stran
- **Pokrývá kritérium:** AC-4, AC-5
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Přihlášen lektor na formuláři `/courses/create`.
- **Testovací data:**
  - Platný název, popis, kapacita i cena.
  - Čtvercový obrázek: rozlišení `800x800` px (poměr stran 1:1, odchylka od 16:9 výrazně přesahuje 5 %).
- **Kroky:**
  1. Vyplň platné textové údaje kurzu.
  2. Nahraj čtvercový obrázek o rozměrech `800x800` px.
  3. Klikni na tlačítko pro uložení kurzu.
- **Očekávaný výsledek:**
  - Systém detekuje nesprávný poměr stran nahrávaného souboru.
  - Kurz se neuloží a lektor je vyzván chybovou hláškou k výběru širokoúhlého obrázku v požadovaném poměru přibližně 16:9.

---

### [TC-US14-04] Zamezení přístupu k tvorbě kurzu pro zákazníka a nepřihlášeného hosta (RBAC)
- **Pokrývá kritérium:** AC-1
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Uživatel je přihlášen v roli Zákazník, nebo je nepřihlášen.
- **Testovací data:**
  - URL formuláře pro vytvoření kurzu: `/courses/create`.
- **Kroky:**
  1. Jako běžný zákazník otevři katalog kurzů `/courses` a zkontroluj přítomnost tlačítka "Přidat kurz".
  2. Zadej do adresního řádku přímou URL `/courses/create` a stiskni Enter.
  3. Zopakuj pokus v anonymním nepřihlášeném okně.
- **Očekávaný výsledek:**
  - Tlačítko pro vytvoření nového kurzu se zákazníkovi ani hostovi nenabízí.
  - Přímý přístup na URL `/courses/create` je systémem zamítnut (kód 403 Forbidden nebo přesměrování na přihlášení).

---

### [TC-US14-05] Akceptace obrázku v rámci povolené 5% odchylky poměru stran
- **Pokrývá kritérium:** AC-5, AC-6
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Přihlášen lektor na formuláři `/courses/create`.
- **Testovací data:**
  - Obrázek s mírnou odchylkou: rozlišení `1280x750` px (poměr ~1,707 vs ideální 16:9 ~1,778, odchylka cca 4 %, tedy v limitu do 5 %).
- **Kroky:**
  1. Vyplň platné parametry kurzu.
  2. Nahraj obrázek `1280x750` px v rámci povolené 5% tolerance.
  3. Odešli formulář.
- **Očekávaný výsledek:**
  - Systém obrázek akceptuje, protože jeho poměr stran se vejde do povolené tolerance 5 %.
  - Kurz je úspěšně vytvořen a zařazen do katalogu.
