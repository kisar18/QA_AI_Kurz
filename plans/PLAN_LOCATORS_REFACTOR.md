# Implementační plán: Refaktoring lokátorů dle Page Object Modelu (POM) a standardu `data-testid`

Tento plán detailně popisuje přechod na **čistý Page Object Model (POM)** s nulovým výskytem surových lokátorů v testech a jednotným využitím moderní Playwright metody `page.get_by_test_id(...)`.

---

## 1. Architektonické principy POM v tomto projektu

1. **Pravidlo Zero-Inline-Locators:**
   - Testovací metody v `tests/` **nesmí obsahovat žádné selektory** (`page.locator()`, `page.get_by_test_id()` ani CSS/XPath).
   - Testy komunikují se stránkou výhradně přes instance Page Objectů a jejich atributy/metody.
2. **Konzistentní lokalizace přes `data-testid`:**
   - Všechny Page Objecty používají nativní Playwright metodu `page.get_by_test_id("...")`.
3. **Samostatný Page Object pro každou logickou obrazovku:**
   - `/login` $\rightarrow$ `LoginPage`
   - `/register` $\rightarrow$ `RegisterPage`
   - `/forgot-password` $\rightarrow$ `ForgotPasswordPage`
   - `/home` (po registraci/přihlášení) $\rightarrow$ `HomePage`

---

## 2. Porovnání: Současný stav vs. Cílový POM stav

| Soubor / Místo | Současný stav | Cílový POM stav |
| :--- | :--- | :--- |
| **`pages/login_page.py`** | `page.locator("[data-testid='...']")` (11 prvků) | Převod na `page.get_by_test_id("...")` |
| **`pages/register_page.py`** | `page.locator("[data-testid='...']")` (6 prvků) | Převod na `page.get_by_test_id("...")` |
| **`pages/forgot_password_page.py`** | Neexistuje | **Nový POM**: Obsahuje `email_input`, `submit_button`, metodu `reset_password()` |
| **`pages/home_page.py`** | Neexistuje | **Nový POM**: Obsahuje `welcome_section` (`data-testid="home_section"`) |
| **`tests/test_login.py` (ř. 155–158)** | Surové `page.locator("[data-testid='email_input']")` a `page.locator("button")` | Použije instanci `ForgotPasswordPage(page)`: `expect(forgot_page.email_input)`, `expect(forgot_page.submit_button)` |
| **`tests/test_login.py` (ř. 169–172)** | Surové `page.locator("[data-testid='name_input']")` a `page.locator("[data-testid='register_button']")` | Použije instanci `RegisterPage(page)`: `expect(reg_page.name_input)`, `expect(reg_page.register_button)` |
| **`tests/test_register.py` (ř. 47)** | Surové `page.locator("body")` | Použije `HomePage(page)`: `expect(home_page.welcome_section).to_contain_text(...)` |

---

## 3. Fáze a kroky implementace

### Fáze 1: Aktualizace existujících Page Objectů
- [x] **Krok 1.1: Refaktor `pages/login_page.py`**
  - Nahradit zápisy `page.locator("[data-testid='...']")` metodou `page.get_by_test_id("...")` pro všech 11 lokátorů:
    - `email_input`, `password_input`, `login_button`, `login_title`, `error_message`, `forgot_password_link`, `register_link`, `nav_login_link`, `nav_courses_link`, `logout_button`, `profile_link`.
- [x] **Krok 1.2: Refaktor `pages/register_page.py`**
  - Nahradit zápisy `page.locator("[data-testid='...']")` metodou `page.get_by_test_id("...")` pro všech 6 lokátorů:
    - `name_input`, `email_input`, `password_input`, `password_again_input`, `register_button`, `login_link`.

### Fáze 2: Vytvoření nových Page Objectů pro chybějící stránky
- [x] **Krok 2.1: Vytvoření `pages/forgot_password_page.py`**
  - Třída `ForgotPasswordPage`:
    - `URL = "http://testovani.kitner.cz/forgot-password"`
    - `self.email_input = page.get_by_test_id("email_input")`
    - `self.submit_button = page.get_by_test_id("submit_button")`
    - Pomocná metoda `navigate()`
- [x] **Krok 2.2: Vytvoření `pages/home_page.py`**
  - Třída `HomePage`:
    - `URL = "http://testovani.kitner.cz/home"`
    - `self.welcome_section = page.get_by_test_id("home_section")`

### Fáze 3: Refaktoring testů na čistý POM
- [x] **Krok 3.1: Vyčištění `tests/test_login.py`**
  - Importovat `ForgotPasswordPage` a `RegisterPage`.
  - V testu `test_forgot_password_link`:
    - Nahradit inline selektory instancí `forgot_page = ForgotPasswordPage(page)`.
    - Ověřit `forgot_page.email_input` a `forgot_page.submit_button`.
  - V testu `test_register_link`:
    - Nahradit inline selektory instancí `register_page = RegisterPage(page)`.
    - Ověřit `register_page.name_input` a `register_page.register_button`.
- [x] **Krok 3.2: Vyčištění `tests/test_register.py`**
  - Importovat `HomePage`.
  - V testu `test_successful_registration`:
    - Nahradit `page.locator("body")` voláním `home_page = HomePage(page)`.
    - Ověřit `expect(home_page.welcome_section).to_contain_text(f"Vítej uživateli {name}!")`.

### Fáze 4: Verifikace a regresní testování
- [x] **Krok 4.1: Běh testovací sady**
  - Spustit pytest:
    ```powershell
    .venv\Scripts\pytest -v
    ```
  - Ověřit, že všech 8+ testovacích scénářů proběhne bez chyb (100% zelené).
- [x] **Krok 4.2: Kontrola HTML reportu**
  - Zkontrolovat, že se správně vygeneroval report [`reports/report.html`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/reports/report.html).

### Fáze 5: Verzování na Git & Push na GitHub
- [x] **Krok 5.1: Vytvoření zásadního commitu**
  - Protože jde o klíčový architektonický milník, provést commit:
    ```powershell
    git add .
    git commit -m "Refactor: Full POM architecture with data-testid locators"
    ```
- [x] **Krok 5.2: Odeslání do GitHub repozitáře**
  - `git push origin main`

---

## 4. Přínosy tohoto řešení
- **Čistota kódu (Clean Code):** Testy se soustředí pouze na testovací logiku a asserty, ne na HTML strukturu.
- **Opakovatelnost a znovupoužitelnost:** Všechny prvky jsou definovány na jediném místě – při budoucí změně v aplikaci se upraví pouze jeden řádek v POM třídě.
- **Maximální stabilita:** Žádné tagové selektory (`body`, `button`), 100% krytí přes stabilní `data-testid`.
