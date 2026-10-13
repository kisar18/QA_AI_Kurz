# Implementační plán: Refaktoring všech lokátorů na standard `data-testid`

Tento plán popisuje kroky k jednotnému přechodu všech lokátorů v projektu na nativní Playwright metodu `page.get_by_test_id(...)` a eliminaci zbývajících obecných HTML tagů (`button`, `body`).

---

## 1. Analýza současného stavu

V projektu jsou identifikována následující místa vyžadující úpravu:

### A. Page Objecty (`pages/`)
V současnosti používají syntaxi CSS selektoru `page.locator("[data-testid='...']")`:
- **`pages/login_page.py`** (11 lokátorů):
  - `email_input`, `password_input`, `login_button`, `login_title`, `error_message`, `forgot_password_link`, `register_link`, `nav_login_link`, `nav_courses_link`, `logout_button`, `profile_link`
- **`pages/register_page.py`** (6 lokátorů):
  - `name_input`, `email_input`, `password_input`, `password_again_input`, `register_button`, `login_link`

### B. Testovací soubory (`tests/`)
Obsahují inline selektory a obecné HTML tagy, které nemají stabilní vazbu na `data-testid`:
- **`tests/test_login.py` (řádek 158)**:
  - Používá `page.locator("button")` pro ověření tlačítka na `/forgot-password`.
  - *Zjištěný skutečný atribut v DOM:* `data-testid="submit_button"`.
- **`tests/test_login.py` (řádky 155, 169, 172)**:
  - Používá surové CSS selektory `page.locator("[data-testid='...']")`.
- **`tests/test_register.py` (řádek 47)**:
  - Používá `page.locator("body")` pro ověření uvítacího textu `to_contain_text(f"Vítej uživateli {name}!")`.
  - *Zjištěný skutečný atribut v DOM:* `<div data-testid="home_section">`.

---

## 2. Cílový stav (Target Architecture)

1. **Všechny lokátory v Page Objectech** budou používat čistou a doporučenou Playwright metodu:
   ```python
   self.email_input: Locator = page.get_by_test_id("email_input")
   ```
2. **Eliminace tagových selektorů v testech**:
   - `page.locator("button")` $\rightarrow$ `page.get_by_test_id("submit_button")`
   - `page.locator("body")` $\rightarrow$ `page.get_by_test_id("home_section")`
3. **Dodržení Page Object Modelu (POM)**:
   - Pokud se prvek logicky vztahuje ke stránce nebo procesu, doplnit jej jako vlastnost přímo do příslušného Page Objectu namísto ad-hoc volání v testu.

---

## 3. Fáze a kroky implementace

### Fáze 1: Refaktoring Page Objectů
- [ ] **Krok 1.1**: Upravit [`pages/login_page.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/login_page.py) – převést všech 11 atributů z `page.locator("[data-testid='...']")` na `page.get_by_test_id("...")`.
- [ ] **Krok 1.2**: Upravit [`pages/register_page.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/register_page.py) – převést všech 6 atributů na `page.get_by_test_id("...")`. Přidat lokátor pro uvítací hlášku `self.welcome_message = page.get_by_test_id("home_section")`.

### Fáze 2: Refaktoring testovacích souborů
- [ ] **Krok 2.1**: Upravit [`tests/test_login.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/test_login.py):
  - Na řádku 155 převést na `page.get_by_test_id("email_input")`
  - Na řádku 158 nahradit `page.locator("button")` za `page.get_by_test_id("submit_button")`
  - Na řádcích 169 a 172 převést na `page.get_by_test_id(...)`
- [ ] **Krok 2.2**: Upravit [`tests/test_register.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/test_register.py):
  - Na řádku 47 nahradit `page.locator("body")` za `page.get_by_test_id("home_section")` (nebo využít Page Object).

### Fáze 3: Verifikace a spuštění testů
- [ ] **Krok 3.1**: Spustit kompletní sadu testů pomocí pytestu:
  ```powershell
  .venv\Scripts\pytest -v
  ```
- [ ] **Krok 3.2**: Zkontrolovat vygenerovaný HTML report v [`reports/report.html`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/reports/report.html).

### Fáze 4: Verzování zásadní změny (Git Commit)
- [ ] **Krok 4.1**: Protože se jedná o ucelený architektonický refaktoring lokátorů v celém projektu, vytvořit zásadní commit:
  ```bash
  git commit -m "Refactor: Unified all locators to Playwright get_by_test_id"
  ```

---

## 4. Očekávané přínosy
- **100% imunita vůči změnám CSS a HTML tagů**: Žádný test nebude záviset na obecných tazích (`body`, `button`) ani CSS selektorech.
- **Konzistentní kód**: Čistší, kratší a moderní zápis doporučovaný týmem Playwright.
