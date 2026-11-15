# Test Casy: US-17 Domovská uvítací nástěnka po přihlášení

**Zdrojová User Story:** US-17  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + QA Tester  

---

### [TC-US17-01] Zobrazení personalizované uvítací zprávy se jménem uživatele po přihlášení
- **Pokrývá kritérium:** AC-1
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - V systému existuje registrovaný uživatel se zadaným jménem (např. *Petr Svoboda*).
- **Testovací data:**
  - Jméno uživatele: `Petr Svoboda`.
  - Přihlašovací údaje k účtu.
- **Kroky:**
  1. Otevři přihlašovací stránku `/login`.
  2. Zadej e-mail a heslo uživatele Petr Svoboda a klikni na "Přihlásit se".
  3. Po přihlášení zkontroluj domovskou stránku / nástěnku.
  4. Vyhledej prvek uvítací zprávy v záhlaví nebo na nástěnce.
- **Očekávaný výsledek:**
  - Uživatel je po přihlášení uvítán personalizovanou zprávou (např. *Vítejte, Petr Svoboda*).
  - Zpráva přesně obsahuje jméno a příjmení přihlášeného uživatele.

---

### [TC-US17-02] Trvalá dostupnost volby 'Domů' v horní navigaci pro přihlášeného uživatele
- **Pokrývá kritérium:** AC-2
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Uživatel je přihlášen do systému.
  - Uživatel se nachází na libovolné podstránce aplikace (např. `/courses` nebo `/profile`).
- **Testovací data:**
  - Odkaz "Domů" v horní navigační liště.
- **Kroky:**
  1. Přejdi na podstránku profilu `/profile`.
  2. Zkontroluj položky v horní navigační liště.
  3. Klikni na odkaz "Domů".
  4. Zkontroluj výslednou URL adresu a zobrazenou stránku.
- **Očekávaný výsledek:**
  - Volba "Domů" je pro přihlášeného uživatele trvale viditelná v horní navigaci na všech podstránkách.
  - Kliknutí na "Domů" spolehlivě nasměruje uživatele zpět na domovskou stránku (`/home`).

---

### [TC-US17-03] Zamezení přístupu na domovskou nástěnku pro nepřihlášeného návštěvníka
- **Pokrývá kritérium:** AC-2
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Prohlížeč je v anonymním režimu (uživatel není přihlášen).
- **Testovací data:**
  - URL domovské nástěnky: `/home`.
- **Kroky:**
  1. Zadej do adresního řádku URL `/home` a stiskni Enter.
  2. Zkontroluj reakci systému.
- **Očekávaný výsledek:**
  - Systém nepřihlášenému návštěvníkovi neumožní přístup na personalizovanou domovskou nástěnku.
  - Uživatel je přesměrován na přihlašovací formulář `/login` nebo katalog `/courses`.

---

### [TC-US17-04] Zobrazení uvítací zprávy pro uživatele s českou diakritikou ve jméně
- **Pokrývá kritérium:** AC-1
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Uživatel je registrován se jménem obsahujícím složitou diakritiku (např. *Eliška Řehořová-Žáčková*).
- **Testovací data:**
  - Jméno: `Eliška Řehořová-Žáčková`.
- **Kroky:**
  1. Přihlas se pod tímto uživatelským účtem.
  2. Zkontroluj text uvítací zprávy na domovské stránce.
- **Očekávaný výsledek:**
  - Diakritika je vykreslena bez chyb kódování (žádné rozsypané znaky, otazníky ani HTML entity).
  - Jméno je zobrazeno čistě a korektně.
