# Automatizované testy – testovani.kitner.cz

Projekt obsahuje kompletní sadu automatizovaných **E2E testů** pro webovou aplikaci [testovani.kitner.cz](http://testovani.kitner.cz) postavenou na **Playwright** a **Pytest** v jazyce Python. Testy pokrývají všechny klíčové funkce aplikace a jsou organizovány podle vzoru **Page Object Model (POM)** v modulární adresářové struktuře dle osvědčených standardů pro automatizaci testování.

---

## Struktura projektu

Architektura projektu odpovídá osvědčenému modelu **Test Project Structure**:

```
├── .github/
│   └── workflows/
│       └── tests.yml            # CI/CD & WORKFLOWS – Spouštění testů v GitHub Actions na PR/push
├── pyproject.toml               # CONFIGURATION – Konfigurace testovacího frameworku a závislosti
├── .env.example                 # ENVIRONMENT – Vzor konfigurace proměnných prostředí
├── config/
│   ├── __init__.py
│   └── settings.py              # ENVIRONMENT – Globální nastavení, URL, browser options a cesty
├── plans/                       # IMPLEMENTAČNÍ PLÁNY – Architektura, POM refaktor, pokrytí testy
│   ├── PLAN_LOCATORS_REFACTOR.md
│   ├── PLAN_TEST_COVERAGE.md
│   └── PLAN_PROJECT_STRUCTURE_REFACTOR.md
├── user stories/
│   └── požadavky_ust_podle_src.md # SPECIFIKACE – Agilní specifikace požadavků a akceptační kritéria
├── data/
│   ├── README.md                # TEST DATA DOCS – Dokumentace testovacích účtů a jejich rolí
│   ├── test_user.json           # TEST DATA – Uložené přihlašovací údaje zákazníka / studenta
│   ├── lector_user.json         # TEST DATA – Přihlašovací údaje lektora (správa kurzů)
│   └── invalid_emails.json      # TEST DATA – Statická testovací data pro parametrizované testy
├── utils/
│   ├── __init__.py
│   └── data_generator.py        # UTILITIES – Nezávislé generátory (unikátní data, IČO modulo 11)
├── helpers/
│   ├── __init__.py
│   ├── auth_helpers.py          # SHARED ACTIONS – Znovupoužitelné kroky autentizace (login, registrace)
│   ├── course_helpers.py        # SHARED ACTIONS – Znovupoužitelné kroky správy kurzů (vytvoření, zápis)
│   └── step_helpers.py          # SHARED ACTIONS – Záznam kroků a assert logging
├── pages/
│   ├── __init__.py
│   ├── base_page.py             # PAGE OBJECTS – Bázová třída pro POM (URL, navigace, navbar)
│   ├── login_page.py            # POM – Přihlašovací stránka (/login)
│   ├── register_page.py         # POM – Registrační stránka (/register)
│   ├── forgot_password_page.py  # POM – Obnova hesla (/forgot-password)
│   ├── home_page.py             # POM – Domovská uvítací stránka (/home)
│   ├── profile_page.py          # POM – Profil uživatele (/profile)
│   ├── courses_page.py          # POM – Katalog a detail kurzů (/courses, /courses/:id)
│   ├── course_create_page.py    # POM – Vytváření kurzu (/courses/create)
│   └── components/
│       ├── __init__.py
│       └── navbar.py            # PAGE OBJECTS – Sdílená navigační lišta (Navbar)
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # TEST SUITES – Pytest fixtures, registrace, HTML report
│   ├── auth/                    # TEST SUITES: Autentizace a správa účtu (11 testů)
│   │   ├── __init__.py
│   │   ├── test_login.py        # Přihlášení (9 testů)
│   │   ├── test_logout.py       # Bezpečné odhlášení (1 test)
│   │   ├── test_register.py     # Registrace (7 testů)
│   │   └── test_forgot_password.py # Obnova hesla (3 testy)
│   ├── courses/                 # TEST SUITES: Katalog a správa kurzů (6 testů)
│   │   ├── __init__.py
│   │   ├── test_courses.py      # Katalog a detail kurzů (4 testy)
│   │   └── test_course_management.py # Vytváření kurzů a Moje kurzy (2 testy)
│   ├── profile/                 # TEST SUITES: Profil uživatele (6 testů)
│   │   ├── __init__.py
│   │   └── test_profile.py      # Profil klienta a Moje kurzy (6 testů)
│   └── navigation/              # TEST SUITES: Navigace a globální prvky (1 test)
│       ├── __init__.py
│       └── test_navbar.py       # Navigační prokliky v hlavičce
└── reports/                     # OUTPUT – Místně generované HTML reporty a screenshoty
    ├── report.html              # Kompletní HTML report (ignorován gitem)
    └── report_style.css         # Vlastní moderní styl reportu
```

---

## Pokryté testovací scénáře (35 testů)

### 1. Autentizace – `tests/auth/`
- **Přihlášení (`test_login.py`)**:
  - Navigace z `/courses` na `/login` přes odkaz v menu
  - Kontrola přítomnosti a viditelnosti UI prvků formuláře
  - Úspěšné přihlášení a odhlášení
  - Maskování pole hesla (`type="password"`)
  - HTML5 validace formátu e-mailu
  - Neplatné přihlašovací údaje (chybová hláška)
  - Parametrizovaná matice neplatných přihlášení (2 kombinace)
  - Odkazy „Zapomenuté heslo" a „Registrace"
- **Odhlášení (`test_logout.py`)**:
  - Bezpečné odhlášení přihlášeného uživatele přes navbar a kontrola stavu menu
- **Registrace (`test_register.py`)**:
  - Kontrola prvků formuláře registrace
  - Úspěšná registrace nového uživatele
  - Validace neshodných hesel a duplicitního e-mailu
  - HTML5 validace e-mailu, maskování hesel a prázdný formulář
- **Obnova hesla (`test_forgot_password.py`)**:
  - Zobrazení prvků, HTML5 validace e-mailu a odeslání žádosti

### 2. Kurzy – `tests/courses/`
- **Katalog a detail (`test_courses.py`)**:
  - Načtení katalogu a prvků karet kurzů (název, cena, odkaz)
  - Proklik do detailu kurzu `/courses/:id`
  - Termíny běhů – anonymní zobrazení vs. aktivace po přihlášení
- **Správa kurzů (`test_course_management.py`)**:
  - Zobrazení formuláře pro vytvoření kurzu na `/courses/create`
  - Vytvoření nového kurzu s přesměrováním do přehledu

### 3. Profil uživatele – `tests/profile/`
- **Profil klienta (`test_profile.py`)**:
  - Načtení profilu a předvyplněné údaje přihlášeného klienta
  - Úspěšná aktualizace údajů (telefon, platné IČO s kontrolním součtem modulo 11)
  - Validace neplatného IČO a telefonního čísla
  - Ochrana před nepřihlášeným uživatelem (přesměrování na `/login`)
  - Zobrazení sekce zapsaných kurzů na `/my-courses`

### 4. Navigace – `tests/navigation/`
- **Navigační lišta (`test_navbar.py`)**:
  - Přepínání a obousměrná navigace mezi katalogem kurzů a přihlášením

---

## Jak testy spustit

### Požadavky a instalace
```powershell
pip install -r requirements.txt
playwright install chromium
```

### Aktivace virtuálního prostředí
```powershell
.\.venv\Scripts\Activate.ps1
```

### Spuštění všech testů
```powershell
pytest
```

### Spuštění konkrétní testovací suity
```powershell
# Pouze autentizace:
pytest tests/auth/ -v

# Pouze správa kurzů:
pytest tests/courses/ -v

# Pouze profil:
pytest tests/profile/ -v

# Pouze navigace:
pytest tests/navigation/ -v
```

### Spuštění s viditelným prohlížečem
```powershell
pytest --headed
```

### Spuštění se zpomaleným krokem (pro sledování)
```powershell
pytest --headed --slowmo 500
```

### HTML report
Po každém spuštění je automaticky vygenerován samostatný report s vloženými styly a případnými screenshoty chyb:
```
reports/report.html
```

---

## Architektura a principy
- **Page Object Model (POM):** Každá stránka a komponenta má vlastní třídu dědící z `BasePage`. Testy neobsahují žádné surové lokátory.
- **Stabilní lokátory `data-testid`:** Veškeré elementy jsou lokalizovány přes `page.get_by_test_id(...)`.
- **Modularita a škálovatelnost:** Přehledné oddělení konfigurace (`config/`), dat (`data/`), utilit (`utils/`), sdílených flow (`helpers/`) a samotných testovacích suit (`tests/`).
- **CI/CD:** Automatizované spouštění v GitHub Actions (`.github/workflows/tests.yml`).
