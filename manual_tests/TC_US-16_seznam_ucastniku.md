# Test Casy: US-16 Zobrazení seznamu přihlášených účastníků pro lektora

**Zdrojová User Story:** US-16  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + QA Tester  

---

### [TC-US16-01] Zobrazení tabulky účastníků běhu kurzu lektorem a kompletní údaje
- **Pokrývá kritérium:** AC-1, AC-2
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - Přihlášen uživatel v roli lektora.
  - U vybraného běhu kurzu jsou zapsáni studenti.
- **Testovací data:**
  - Detail kurzu: `/courses/1`.
  - Termín běhu s registrovanými účastníky.
- **Kroky:**
  1. V roli lektora otevři detail kurzu `/courses/1`.
  2. U vybraného běhu vyhledej tlačítko pro správu účastníků ("Přihlášení").
  3. Klikni na tlačítko "Přihlášení" (přechod na `/courses/<iteration_id>/participants`).
  4. Zkontroluj zobrazenou tabulku účastníků a její sloupce.
- **Očekávaný výsledek:**
  - Možnost zobrazit účastníky je lektorovi bez problémů dostupná.
  - Tabulka přehledně zobrazuje všechny zapsané studenty.
  - U každého studenta jsou uvedeny kompletní údaje: jméno a příjmení, e-mail, telefonní číslo a IČO.

---

### [TC-US16-02] Zobrazení zástupné hodnoty 'Neuvedeno' při nevyplněném IČO studenta
- **Pokrývá kritérium:** AC-2, AC-3
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - V seznamu přihlášených je student, který se zapsal jako nepodnikající fyzická osoba a pole IČO ponechal prázdné.
  - Přihlášen lektor na stránce účastníků běhu.
- **Testovací data:**
  - Student bez vyplněného IČO.
- **Kroky:**
  1. Otevři seznam účastníků daného běhu.
  2. Vyhledej řádek studenta, který při zápisu nezadal IČO.
  3. Zkontroluj hodnotu v buňce sloupce IČO.
- **Očekávaný výsledek:**
  - Buňka nezůstává prázdná ani nezobrazuje `null` či chybu.
  - V buňce IČO se zřetelně zobrazí zástupný text *Neuvedeno*.

---

### [TC-US16-03] Zamezení přístupu k seznamu účastníků pro běžného zákazníka a hosta (Ochrana soukromí)
- **Pokrývá kritérium:** AC-1, AC-4
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Uživatel je přihlášen v roli Zákazník, nebo je nepřihlášen.
- **Testovací data:**
  - URL seznamu účastníků: `/courses/1/participants`.
- **Kroky:**
  1. Jako běžný zákazník otevři detail kurzu `/courses/1` a ověř, zda je viditelné tlačítko pro účastníky.
  2. Zadej do adresního řádku přímou URL `/courses/1/participants` a stiskni Enter.
  3. Zopakuj pokus v anonymním okně bez přihlášení.
- **Očekávaný výsledek:**
  - Tlačítko pro zobrazení účastníků se zákazníkům ani hostům nezobrazuje.
  - Přímý přístup na URL `/courses/1/participants` je systémem striktně zamítnut (vrácen stav 403 Forbidden nebo přesměrování).
  - Osobní a fakturační data studentů nejsou vystavena nepovolaným osobám.

---

### [TC-US16-04] Zobrazení seznamu pro běh kurzu bez dosud přihlášených studentů (Empty State)
- **Pokrývá kritérium:** AC-1, AC-2
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Přihlášen lektor.
  - Běh kurzu byl čerstvě vypsán a nemá zatím žádného zapsaného studenta.
- **Testovací data:**
  - Běh kurzu s 0 přihlášenými.
- **Kroky:**
  1. Otevři seznam účastníků pro nově vypsaný běh.
  2. Zkontroluj načtení stránky a obsah tabulky.
- **Očekávaný výsledek:**
  - Stránka se korektně načte bez chyb.
  - Tabulka zobrazuje informaci o tom, že na tento běh zatím nejsou přihlášeni žádní studenti.
