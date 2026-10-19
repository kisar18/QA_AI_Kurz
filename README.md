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
│   ├── PLAN_PROJECT_STRUCTURE_REFACTOR.md
│   └── PLAN_USER_STORIES_COVERAGE.md # Implementační plán kompletního pokrytí US-01 až US-20
├── user stories/
│   └── požadavky_ust_podle_src.md # SPECIFIKACE – Agilní specifikace požadavků a akceptační kritéria
├── data/
│   ├── README.md                # TEST DATA DOCS – Dokumentace testovacích účtů a jejich rolí
│   ├── test_user.json           # TEST DATA – Uložené přihlašovací údaje zákazníka / studenta
│   ├── lector_user.json         # TEST DATA – Přihlašovací údaje lektora (správa kurzů)
│   ├── invalid_emails.json      # TEST DATA – Statická testovací data pro parametrizované testy
│   ├── test_16_9.png            # TEST DATA – Validní náhledový obrázek s poměrem stran 16:9
│   └── test_1_1.png             # TEST DATA – Nevalidní náhledový obrázek (čtverec 1:1)
├── utils/
│   ├── __init__.py
│   ├── data_generator.py        # UTILITIES – Nezávislé generátory (unikátní data, IČO modulo 11)
│   └── image_generator.py       # UTILITIES – Generátor testovacích PNG obrázků libovolných poměrů
├── helpers/
│   ├── __init__.py
│   ├── auth_helpers.py          # SHARED ACTIONS – Znovupoužitelné kroky autentizace (login, registrace)
│   ├── course_helpers.py        # SHARED ACTIONS – Znovupoužitelné kroky správy kurzů (vytvoření, zápis)
│   └── step_helpers.py          # SHARED ACTIONS – Záznam kroků a assert logging
├── pages/
│   ├── __init__.py
│   ├── base_page.py             # PAGE OBJECTS – Bázová třída pro POM (URL, navigace, navbar)
│   ├── linktree_page.py         # POM – Úvodní rozcestník portálu (/)
│   ├── home_page.py             # POM – Domovská nástěnka (/home)
│   ├── login_page.py            # POM – Přihlašovací stránka (/login)
│   ├── register_page.py         # POM – Registrační stránka (/register)
│   ├── forgot_password_page.py  # POM – Obnova hesla (/forgot-password)
│   ├── reset_password_page.py   # POM – Dokončení resetu hesla s tokenem (/password-reset/:token)
│   ├── profile_page.py          # POM – Profil uživatele (/profile)
│   ├── my_courses_page.py       # POM – Přehled zapsaných kurzů (/my-courses)
│   ├── courses_page.py          # POM – Katalog a detail kurzů (/courses, /courses/:id)
│   ├── course_create_page.py    # POM – Vytváření kurzu lektorem (/courses/create)
│   ├── course_enroll_page.py    # POM – Nezávazná registrace na běh kurzu (/courses/:id/register)
│   ├── course_iteration_create_page.py # POM – Vypsání nového termínu lektorem (/courses/:id/create-iteration)
│   ├── students_list_page.py    # POM – Seznam přihlášených studentů běhu (/courses/:id/participants)
│   └── components/
│       ├── __init__.py
│       └── navbar.py            # PAGE OBJECTS – Sdílená navigační lišta (Navbar)
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # TEST SUITES – Pytest fixtures, registrace, HTML report
│   ├── portal/                  # TEST SUITES: Rozcestník a nástěnka (4 testy)
│   │   ├── test_linktree.py     # US-01 – Rozcestník portálu na /
│   │   └── test_home_dashboard.py # US-17 – Personalizovaná domovská stránka /home
│   ├── auth/                    # TEST SUITES: Autentizace a sezení (35 testů)
│   │   ├── test_login.py        # US-03 – Přihlášení (case-insensitive, trim, Enter klávesa)
│   │   ├── test_logout.py       # US-04 – Bezpečné odhlášení
│   │   ├── test_register.py     # US-02 – Registrace zákazníka a validace
│   │   ├── test_forgot_password.py # US-05 – Žádost o obnovu hesla
│   │   ├── test_reset_password.py # US-06 – Dokončení resetu hesla s tokenem
│   │   ├── test_email_verification.py # US-07 – Ověřování e-mailu a ochrana
│   │   └── test_rate_limiting.py # US-08 – Ochrana proti útokům hrubou silou
│   ├── courses/                 # TEST SUITES: Katalog a správa kurzů (17 testů)
│   │   ├── test_courses.py      # US-09, US-10, US-11 – Katalog, detail a kapacita běhů
│   │   ├── test_course_management.py # US-14 – Vytvoření kurzu a validace poměru stran 16:9
│   │   ├── test_course_iterations.py # US-15, US-16 – Vypsání termínu a seznam účastníků
│   │   └── test_enrollment.py   # US-12, US-13 – Nezávazný zápis na běh a Moje kurzy
│   ├── profile/                 # TEST SUITES: Profil klienta (6 testů)
│   │   └── test_profile.py      # US-18, US-13 – Editace údajů profilu, validace IČO
│   ├── security/                # TEST SUITES: Bezpečnost a řízení přístupu (6 testů)
│   │   ├── test_rbac.py         # US-19 – Role-Based Access Control
│   │   └── test_csrf.py         # US-20 – CSRF ochrana a regenerace sezení
│   └── navigation/              # TEST SUITES: Navigační komponenty (1 test)
│       └── test_navbar.py       # Navigační prokliky v hlavičce
└── reports/                     # OUTPUT – Místně generované HTML reporty a screenshoty
    ├── report.html              # Kompletní HTML report (ignorován gitem)
    └── report_style.css         # Vlastní moderní styl reportu
```

---

## Pokryté testovací scénáře (69 testů pokrývajících US-01 až US-20)

| Modul | Testovací soubor | Pokryté User Stories | Počet testů |
| :--- | :--- | :--- | :---: |
| **Portál & Nástěnka** | `tests/portal/test_linktree.py` | US-01 (Rozcestník portálu a demo-login) | 2 |
| | `tests/portal/test_home_dashboard.py` | US-17 (Personalizované uvítání a navigace Domů) | 2 |
| **Autentizace & Sezení** | `tests/auth/test_login.py` | US-03 (Přihlášení, case-insensitive, trim, klávesa Enter) | 12 |
| | `tests/auth/test_logout.py` | US-04 (Okamžité zneplatnění sezení a odhlášení) | 1 |
| | `tests/auth/test_register.py` | US-02 (Registrace, unifikace e-mailu, validace) | 9 |
| | `tests/auth/test_forgot_password.py` | US-05 (Žádost o obnovu hesla, validace) | 4 |
| | `tests/auth/test_reset_password.py` | US-06 (Reset hesla s tokenem, kontrola shody) | 3 |
| | `tests/auth/test_email_verification.py` | US-07 (Ověření e-mailu, znovuzaslání, zabezpečení) | 3 |
| | `tests/auth/test_rate_limiting.py` | US-08 (Ochrana proti hrubé síle po 5 pokusech) | 1 |
| **Katalog & Kurzy** | `tests/courses/test_courses.py` | US-09, US-10, US-11 (Katalog, výzva, detail, kapacita X/Y) | 7 |
| | `tests/courses/test_course_management.py` | US-14 (Tvorba kurzu, validace 16:9 náhledu) | 3 |
| | `tests/courses/test_course_iterations.py` | US-15, US-16 (Vypsání běhu a seznam studentů lektorem) | 3 |
| | `tests/courses/test_enrollment.py` | US-12, US-13 (Zápis s IČO modulo 11, Moje kurzy) | 4 |
| **Profil klienta** | `tests/profile/test_profile.py` | US-18, US-13 (Předvyplnění, editace, neplatné IČO) | 6 |
| **Bezpečnost (Security)** | `tests/security/test_rbac.py` | US-19 (Omezení oprávnění student vs lektor vs anonym) | 3 |
| | `tests/security/test_csrf.py` | US-20 (CSRF ochrana, regenerace sezení) | 3 |
| **Navigace** | `tests/navigation/test_navbar.py` | Navigační lišta | 1 |
| **Celkem** | **17 testovacích souborů** | **US-01 až US-20 (100% pokrytí požadavků)** | **69 testů** |
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
