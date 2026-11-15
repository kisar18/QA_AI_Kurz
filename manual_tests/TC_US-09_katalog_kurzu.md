# Test Casy: US-09 Prohlížení katalogu kurzů

**Zdrojová User Story:** US-09  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + QA Tester  

---

### [TC-US09-01] Přehledné zobrazení katalogu kurzů a povinných údajů na kartách
- **Pokrývá kritérium:** AC-1, AC-2, AC-3
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - V databázi existují publikované kurzy s definovanou kapacitou, cenou a popisem.
- **Testovací data:**
  - URL katalogu: `/courses`.
- **Kroky:**
  1. Otevři stránku katalogu `/courses`.
  2. Zkontroluj přehledný seznam karet nabízených kurzů.
  3. U každé karty kurzu ověř přítomnost:
     - Název kurzu
     - Stručný popis kurzu
     - Maximální kapacita účastníků (např. *Kapacita: 12*)
     - Cena kurzu zaokrouhlená na celé koruny (např. *Cena: 5000 Kč*)
     - Grafický náhled kurzu
- **Očekávaný výsledek:**
  - Katalog přehledně zobrazuje všechny aktuálně nabízené kurzy.
  - Všechny karty obsahují název, popis, číselnou kapacitu i celou částku ceny v Kč.
  - Kurzy s nahraným obrázkem zobrazují svůj specifický grafický náhled.

---

### [TC-US09-02] Zobrazení neutrálního výchozího obrázku u kurzu bez vlastního náhledu
- **Pokrývá kritérium:** AC-3
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - V nabídce je kurz, který nemá lektorem nahraný specifický obrázek náhledu (nebo odkaz na obrázek chybí).
- **Testovací data:**
  - Kurz bez obrázku.
- **Kroky:**
  1. Na stránce `/courses` vyhledej kartu kurzu bez vlastního náhledu.
  2. Zkontroluj zobrazený grafický prvek karty.
- **Očekávaný výsledek:**
  - Karta kurzu nezobrazuje rozbitý obrázek (broken image ikonu).
  - Místo toho se korektně zobrazí předem definovaný neutrální výchozí obrázek.

---

### [TC-US09-03] Přechod na podrobný detail kurzu z karty v katalogu
- **Pokrývá kritérium:** AC-4
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Otevřena stránka katalogu `/courses`.
- **Testovací data:**
  - Karta kurzu (např. kurz s ID 1).
- **Kroky:**
  1. Na kartě kurzu klikni na tlačítko "Detail kurzu" (nebo na název kurzu).
  2. Zkontroluj výslednou URL v adresním řádku.
- **Očekávaný výsledek:**
  - Uživatel je přesměrován na podrobný detail kurzu (URL vzor `/courses/<id>`).
  - Zobrazí se kompletní specifikace kurzu s vypsanými termíny.

---

### [TC-US09-04] Zobrazení výzvy k registraci pro nepřihlášeného návštěvníka
- **Pokrývá kritérium:** AC-5
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Návštěvník není přihlášen do aplikace (anonymní režim).
- **Testovací data:**
  - URL katalogu: `/courses`.
- **Kroky:**
  1. Otevři `/courses` jako nepřihlášený návštěvník.
  2. Přejdi do spodní části stránky pod seznamem nabízených kurzů.
  3. Zkontroluj přítomnost sekce s výzvou k registraci (CTA).
  4. Klikni na odkaz v textu výzvy k registraci.
- **Očekávaný výsledek:**
  - Pod nabídkou kurzů se zřetelně zobrazuje výzva k vytvoření účtu.
  - Kliknutí na odkaz přesměruje návštěvníka na registrační formulář `/register`.

---

### [TC-US09-05] Absence výzvy k registraci pro již přihlášeného uživatele
- **Pokrývá kritérium:** AC-5
- **Typ testu:** Negativní
- **Priorita:** Low
- **Předpoklady:**
  - Uživatel je úspěšně přihlášen (jako zákazník nebo lektor).
- **Testovací data:**
  - Přihlášený uživatel.
- **Kroky:**
  1. V přihlášeném stavu otevři katalog kurzů `/courses`.
  2. Prohlédni spodní část stránky pod nabídkou kurzů.
- **Očekávaný výsledek:**
  - Výzva k registraci se již přihlášenému uživateli nezobrazuje.
