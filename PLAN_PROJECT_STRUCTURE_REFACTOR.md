# Implementační plán: Refaktoring struktury adresáře projektu dle vzoru pro testovací automatizaci

Tento plán specifikuje kompletní refaktoring a sjednocení struktury projektu **`Lekce1`** na standardní a škálovatelnou architekturu dle referenčního vzoru pro Python Playwright/Pytest testovací automatizaci.

---

## 1. Cílová architektura projektu

```
<project_name>/
├── .github/
│   └── workflows/
│       └── tests.yml            # CI/CD & WORKFLOWS – Spouštění testů při Pull Requestech / pushi
├── pyproject.toml               # CONFIGURATION – Moderní správa konfigurace Pytestu a závislostí
├── .env.example                 # ENVIRONMENT – Vzor konfigurace proměnných prostředí
├── config/
│   ├── __init__.py
│   └── settings.py              # ENVIRONMENT – Globální nastavení, URL, browser options, secrets
├── data/
│   ├── test_user.json           # TEST DATA – Přihlašovací údaje testovacího uživatele
│   └── invalid_emails.json      # TEST DATA – Statická testovací data pro parametrizované testy
├── utils/
│   ├── __init__.py
│   └── data_generator.py        # UTILITIES – Pomocné generátory (unikátní data, IČO mod 11, náhodné řetězce)
├── helpers/
│   ├── __init__.py
│   ├── auth_helpers.py          # SHARED ACTIONS – Znovupoužitelné kroky autentizace (login, registrace)
│   └── course_helpers.py        # SHARED ACTIONS – Znovupoužitelné kroky správy kurzů (vytvoření, zápis)
├── pages/
│   ├── __init__.py
│   ├── base_page.py             # PAGE OBJECTS – Abstraktní bázový Page Object (URL, navigace, page instance)
│   ├── login_page.py            # POM – Přihlašovací stránka
│   ├── register_page.py         # POM – Registrační stránka
│   ├── forgot_password_page.py  # POM – Obnova hesla
│   ├── home_page.py             # POM – Domovská uvítací stránka
│   ├── profile_page.py          # POM – Profil uživatele
│   ├── courses_page.py          # POM – Katalog a detail kurzů
│   ├── course_create_page.py    # POM – Vytváření kurzu a termínů
│   └── components/
│       ├── __init__.py
│       └── navbar.py            # PAGE OBJECTS – Sdílené komponenty (hlavní navigační lišta)
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # TEST SUITES – Globální fixtures, inicializace prohlížeče, reporting
│   ├── auth/                    # TEST SUITES: Autentizace a účet
│   │   ├── __init__.py
│   │   ├── test_login.py
│   │   ├── test_register.py
│   │   └── test_forgot_password.py
│   ├── courses/                 # TEST SUITES: Katalog a správa kurzů
│   │   ├── __init__.py
│   │   ├── test_courses.py
│   │   └── test_course_management.py
│   ├── profile/                 # TEST SUITES: Profil uživatele
│   │   ├── __init__.py
│   │   └── test_profile.py
│   └── navigation/              # TEST SUITES: Navigace a globální prvky
│       ├── __init__.py
│       └── test_navbar.py       # Převedení obecných navigačních kontrol
├── reports/                     # OUTPUT – Místní HTML reporty a screenshoty (ignorovány gitem)
│   ├── report_style.css
│   └── .gitkeep
├── requirements.txt             # Pip závislosti
├── README.md                    # Dokumentace projektu a struktury
└── .gitignore                   # Nastavení ignorování dočasných souborů a reportů
```

---

## 2. Analýza současného stavu vs. Cílový stav

| Modul / Komponenta | Současný stav v repozitáři | Cílový stav dle diagramu |
| :--- | :--- | :--- |
| **CI/CD** | Žádný workflow (`.github/` neexistuje) | `.github/workflows/tests.yml` pro GitHub Actions |
| **Konfigurace** | Pouze `pytest.ini` a `requirements.txt` | Doplnit `pyproject.toml` (standard moderního Pythonu) a zachovat kompatibilitu |
| **Prostředí & Nastavení** | Pevné URL v kódu, rozpracované `config/settings.py` | `config/settings.py` s podporou `os.getenv` + vzor `.env.example` |
| **Testovací data** | `test_user.json` v kořenu projektu | Složka `data/` obsahující `data/test_user.json` a `data/invalid_emails.json` |
| **Utility** | Neexistuje | `utils/data_generator.py` pro generování unikátních údajů (validní/nevalidní IČO, e-maily) |
| **Sdílené akce (helpers)** | Rozpracované `helpers/step_helpers.py`, staré `pages/helpers.py` | Rozdělení na `helpers/auth_helpers.py` a `helpers/course_helpers.py`, smazání starých |
| **Page Objects (pages)** | POM soubory v `pages/`, rozpracované `base_page.py` a `navbar.py` | Všechny POM dědí z `BasePage`, `navbar.py` obsluhuje navigaci |
| **Testy (tests)** | Duplicita: ploché `tests/test_*.py` i dílčí složky `tests/auth/`, `tests/courses/`... | Vyčistit ploché soubory; testy striktně ve složkách `auth/`, `courses/`, `profile/`, `navigation/` |
| **Reporty (reports)** | `reports/report.html` a `report_style.css` | V `.gitignore` ignorovat HTML reporty a screenshoty, ponechat CSS styl a strukturu |

---

## 3. Fáze a kroky implementace

### Fáze 1: Konfigurace prostředí a závislostí
- [ ] **Krok 1.1**: Vytvořit `.env.example` se šablonou proměnných (`BASE_URL`, `HEADLESS`, `BROWSER_SLOWMO`).
- [ ] **Krok 1.2**: Zpřesnit `config/settings.py` tak, aby četl hodnoty z proměnných prostředí s bezpečnými výchozími hodnotami:
  - `BASE_URL = os.getenv("BASE_URL", "http://testovani.kitner.cz")`
  - Konfigurace výchozích timeoutů a chování prohlížeče.
- [ ] **Krok 1.3**: Vytvořit `pyproject.toml` s definicí konfigurace pytestu (markery, `testpaths = ["tests"]`, `addopts = "--html=reports/report.html --self-contained-html"`).

### Fáze 2: Složka pro testovací data (`data/`) a utility (`utils/`)
- [ ] **Krok 2.1**: Vytvořit adresář `data/` a přesunout do něj `test_user.json` $\rightarrow$ `data/test_user.json`.
- [ ] **Krok 2.2**: Vytvořit `data/invalid_emails.json` se sadou neplatných e-mailových formátů pro parametrizaci testů.
- [ ] **Krok 2.3**: Vytvořit `utils/data_generator.py` s pomocnými funkcemi:
  - `generate_random_email()`, `generate_random_string()`
  - `generate_valid_ico()` a `generate_invalid_ico()` (ARES kontrolní součet modulo 11).

### Fáze 3: Dokončení Page Object Modelu a komponent (`pages/`)
- [ ] **Krok 3.1**: Dokončit [`pages/base_page.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/base_page.py) – bázová třída s `Page`, `base_url`, metodou `navigate()` a přístupem k navigaci `navbar`.
- [ ] **Krok 3.2**: Dokončit [`pages/components/navbar.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/components/navbar.py) – zapouzdření odkazů v hlavičce (`nav_login_link`, `nav_courses_link`, `profile_link`, `logout_button`).
- [ ] **Krok 3.3**: Refaktorovat všechny existující Page Objecty (`login_page.py`, `register_page.py`, `forgot_password_page.py`, `home_page.py`, `profile_page.py`, `courses_page.py`, `course_create_page.py`):
  - Dědění z `BasePage`.
  - Odstranění duplicitního kódu pro navigaci a přihlašovací menu (delegace na `Navbar`).
- [ ] **Krok 3.4**: Odstranit zastaralý modul `pages/helpers.py`.

### Fáze 4: Sdílené kroky a workflow (`helpers/`)
- [ ] **Krok 4.1**: Vytvořit `helpers/auth_helpers.py` obsahující znovupoužitelné vysokoúrovňové akce:
  - `login_user(page, email, password)`
  - `register_user(page, name, email, password)`
- [ ] **Krok 4.2**: Vytvořit `helpers/course_helpers.py` obsahující:
  - `create_course(page, name, description, capacity, price)`
  - `enroll_to_course(page, course_id)`
- [ ] **Krok 4.3**: Odstranit provizorní soubor `helpers/step_helpers.py`.

### Fáze 5: Konsolidace a rozdělení testovacích suit (`tests/`)
- [ ] **Krok 5.1**: Zrevidovat testy v `tests/auth/`:
  - `tests/auth/test_login.py` (včetně přenesení testu odhlášení `test_logout`)
  - `tests/auth/test_register.py`
  - `tests/auth/test_forgot_password.py`
- [ ] **Krok 5.2**: Zrevidovat testy v `tests/courses/`:
  - `tests/courses/test_courses.py`
  - `tests/courses/test_course_management.py`
- [ ] **Krok 5.3**: Zrevidovat testy v `tests/profile/`:
  - `tests/profile/test_profile.py`
- [ ] **Krok 5.4**: Vytvořit `tests/navigation/test_navbar.py`:
  - Přesunout sem obecné navigační testy (prokliky v hlavičce mezi stránkami).
- [ ] **Krok 5.5**: Smazat původní ploché testovací soubory z kořene `tests/` (`test_login.py`, `test_register.py`, `test_forgot_password.py`, `test_profile.py`, `test_courses.py`, `test_course_management.py`).
- [ ] **Krok 5.6**: Aktualizovat `tests/conftest.py` na nové importy (`data/test_user.json`, `config.settings`).

### Fáze 6: CI/CD Pipeline a správa výstupů
- [ ] **Krok 6.1**: Vytvořit `.github/workflows/tests.yml`:
  - Spouštění na `push` a `pull_request`.
  - Běh na `ubuntu-latest` s instalací Pythonu, Playwright prohlížečů a spuštěním `pytest`.
  - Publikace HTML reportu jako GitHub artifact.
- [ ] **Krok 6.2**: Aktualizovat `.gitignore`:
  - Ignorovat `reports/*.html`, `.env`, screenshots, `test_user.json` (pokud obsahuje osobní tajné údaje).
  - Ponechat `reports/report_style.css` a `reports/.gitkeep`.

### Fáze 7: Ověření, dokumentace a verzování
- [ ] **Krok 7.1**: Spustit kompletní sadu testů ve virtuálním prostředí:
  ```powershell
  .venv\Scripts\pytest -v
  ```
  Ověřit, že všech 33 testů bezchybně projde (100% zelené).
- [ ] **Krok 7.2**: Aktualizovat `README.md` – upravit diagram adresářové struktury a příkazy pro spouštění dílčích suit.
- [ ] **Krok 7.3**: Vytvořit strukturovaný git commit:
  ```powershell
  git add .
  git commit -m "Refactor: Modular project structure conforming to test automation standard"
  ```
