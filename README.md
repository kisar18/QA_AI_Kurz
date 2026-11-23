# Automatizované testy – testovani.kitner.cz

Projekt obsahuje kompletní sadu automatizovaných **E2E testů** pro webovou aplikaci [testovani.kitner.cz](http://testovani.kitner.cz) postavenou na **Playwright** a **pytest** v jazyce Python. Testy pokrývají 100 % požadavků ze všech User Stories (US-01 až US-20) i schválených manuálních test casů, splňují definici hotovo (DoD) a jsou striktně organizovány podle vzoru **Page Object Model (POM)**.

---

## 📊 Přehled testovací sady v číslech

- **Pokryté User Stories:** **20 / 20 (100 %)**
- **Počet automatizovaných testů:** **127 testů** ve **23 testovacích souborech**
- **Počet ověřovaných kontrol (assertions):** **626 kontrol**
- **Výsledek celkového běhu pytestu:** `90 passed, 37 xfailed in ~8 minut (Exit code 0)`
- **Kvalita lokátorů:** **0 chyb (Zero Inline Locators)** – v `tests/` se nenachází jediný inline lokátor (`.locator()`, `.get_by_*()`), vše je zapouzdřeno v Page Objectech.
- **Auto-retry aserce:** Výhradně web-first `expect(...)`, v celém projektu je 0 výskytů `time.sleep()`.

---

## 📁 Struktura projektu

Projekt odpovídá doporučenému standardu pro automatizované testování v Pythonu s Playwrightem:

```
├── .github/
│   └── workflows/
│       └── tests.yml            # CI/CD – Spouštění testů v GitHub Actions při push / PR na main
├── pyproject.toml               # CONFIGURATION – Konfigurace pytestu (addopts, markery, pluginy)
├── .env.example                 # ENVIRONMENT – Vzor proměnných prostředí (BASE_URL, HEADLESS)
├── AGENTS.md                    # PRAVIDLA PROJEKTU – Závazná pravidla pro POM, lokátory a asserty
├── TEST_OVERVIEW.md             # PŘEHLED TESTŮ – Automaticky generovaný katalog 127 testů a 626 kontrol
├── config/
│   ├── __init__.py
│   └── settings.py              # Konfigurace prostředí, URL aplikace a časové limity
├── manual_tests/                # MANUÁLNÍ TEST CASY – Schválené testovací scénáře (TC_US-01 až TC_US-20)
├── user stories/                # SPECIFIKACE – Agilní specifikace požadavků a akceptační kritéria
├── plans/                       # IMPLEMENTAČNÍ PLÁNY – Postupy převodu a architektury
│   └── PLAN_ALL_TC_TO_AUTOMATED_TESTS.md # Finální souhrnný plán převodu všech 20 US
├── data/
│   ├── README.md                # Dokumentace testovacích účtů
│   ├── test_user.json           # Testovací účet studenta / zákazníka
│   ├── lector_user.json         # Testovací účet lektora (správa kurzů)
│   └── invalid_emails.json      # Testovací datasety pro neplatné e-maily
├── utils/
│   ├── data_generator.py        # Generátory náhodných dat a validního IČO (modulo 11)
│   └── image_generator.py       # Čistý generátor PNG obrázků v paměti (poměry 16:9, 1:1 atd.)
├── helpers/
│   ├── auth_helpers.py          # Znovupoužitelné kroky autentizace
│   ├── course_helpers.py        # Znovupoužitelné kroky správy kurzů
│   └── step_helpers.py          # Logování kroků do konzole a reportu (step)
├── pages/                       # PAGE OBJECT MODEL – Všechny lokátory a UI interakce
│   ├── base_page.py             # Bázová stránka (navigace, base_url, navbar)
│   ├── linktree_page.py         # Úvodní rozcestník portálu (/)
│   ├── home_page.py             # Domovská nástěnka (/home)
│   ├── login_page.py            # Přihlášení (/login)
│   ├── register_page.py         # Registrace uživatele (/register)
│   ├── forgot_password_page.py  # Žádost o obnovu hesla (/forgot-password)
│   ├── reset_password_page.py   # Nastavení nového hesla (/password-reset/:token)
│   ├── email_verification_page.py # Ověření e-mailu (/email/verify/:id/:hash)
│   ├── profile_page.py          # Profil uživatele (/profile)
│   ├── my_courses_page.py       # Přehled mých zapsaných kurzů (/my-courses)
│   ├── courses_page.py          # Katalog a detail kurzů (/courses, /courses/:id)
│   ├── course_create_page.py    # Vytvoření nového kurzu lektorem (/courses/create)
│   ├── course_enroll_page.py    # Zápisový formulář na běh kurzu (/courses/:id/register)
│   ├── course_iteration_create_page.py # Vypsání termínu běhu (/courses/:id/create-iteration)
│   ├── students_list_page.py    # Seznam zapsaných studentů (/courses/:id/participants)
│   └── components/
│       └── navbar.py            # Sdílená navigační lišta (Navbar)
├── tests/                       # AUTOMATIZOVANÉ E2E TESTY
│   ├── conftest.py              # Pytest fixtures (browser, user fixtures, HTML report hooks)
│   ├── auth/                    # Autentizace, sezení, bezpečnost účtu (US-02 až US-08)
│   ├── courses/                 # Katalog, registrace, kapacity, lektor (US-09 až US-16)
│   ├── portal/                  # Rozcestník a domovská nástěnka (US-01, US-17)
│   ├── profile/                 # Profil klienta, editace, validace (US-18)
│   ├── security/                # Bezpečnost: RBAC a CSRF ochrana (US-19, US-20)
│   └── navigation/              # Navigační prokliky
├── docs/                        # DOKUMENTACE A PŘEHLEDY POKRYTÍ (verzováno v Gitu)
│   └── coverage_overview.html   # Přehled pokrytí User Stories a test casů
└── reports/                     # VÝSTUPY TESTŮ (necommitují se s výjimkou stylů)
    ├── report.html              # HTML report z exekuce pytestu
    └── report_style.css         # Moderní design reportu
```

---

## 🧪 Pokrytí User Stories (US-01 až US-20)

Každý testovací případ odpovídá schváleným manuálním test casům a v docstringu nese standardizovaný tag `[TC-USxx-yy]`:

| Oblast | Testovací soubor | Pokryté User Stories | Test Casů | Stav DoD |
| :--- | :--- | :--- | :---: | :---: |
| **Portál & Rozcestník** | `tests/portal/test_linktree.py` | **US-01** (Rozcestník portálu a demo vstupy) | 6 | ✅ 3× PASS |
| **Registrace** | `tests/auth/test_register.py` | **US-02** (Registrace, unifikace e-mailu, validace) | 9 | ✅ 3× PASS |
| **Přihlášení** | `tests/auth/test_login.py` | **US-03** (Přihlášení, trimování, klávesa Enter) | 8 | ✅ 3× PASS |
| **Odhlášení** | `tests/auth/test_logout.py` | **US-04** (Zneplatnění sezení, historie prohlížeče) | 6 | ✅ 3× PASS |
| **Žádost o reset hesla**| `tests/auth/test_forgot_password.py` | **US-05** (Formulář obnovy, validace e-mailu) | 4 | ✅ 3× PASS |
| **Dokončení resetu hesla**| `tests/auth/test_reset_password.py` | **US-06** (Zadání nového hesla, token, shoda) | 4 | ✅ 3× PASS |
| **Ověření e-mailu** | `tests/auth/test_email_verification.py`| **US-07** (Verifikační odkaz, znovuzaslání) | 4 | ✅ 3× PASS |
| **Rate Limiting** | `tests/auth/test_rate_limiting.py` | **US-08** (Ochrana proti hrubé síle, throttling) | 7 | ✅ 3× PASS |
| **Katalog kurzů** | `tests/courses/test_courses_catalog.py`| **US-09** (Katalog, karty, ceny, výzva k registraci) | 6 | ✅ 3× PASS |
| **Detail kurzu** | `tests/courses/test_course_detail.py` | **US-10** (Detail, osnova, termíny, 404 neexistující) | 6 | ✅ 3× PASS |
| **Kapacita kurzu** | `tests/courses/test_course_capacity.py`| **US-11** (Obsazenost X/Y, blokace při vyčerpání) | 5 | ✅ 3× PASS |
| **Zápis na kurz** | `tests/courses/test_enrollment.py` | **US-12** (Objednávkový formulář, validace IČO modulo 11) | 8 | ✅ 3× PASS |
| **Moje zapsané kurzy** | `tests/courses/test_my_courses.py` | **US-13** (Přehled kurzů klienta, organizační údaje) | 8 | ✅ 3× PASS |
| **Tvorba nového kurzu**| `tests/courses/test_course_create.py` | **US-14** (Lektorský formulář, poměr stran náhledu 16:9)| 5 | ✅ 3× PASS |
| **Vypsání nového termínu**| `tests/courses/test_course_iterations.py`| **US-15** (Vypsání běhu, čas, termíny, RBAC) | 8 | ✅ 3× PASS |
| **Seznam účastníků** | `tests/courses/test_students_list.py` | **US-16** (Tabulka přihlášených pro lektora, IČO) | 4 | ✅ 3× PASS |
| **Domovská nástěnka** | `tests/portal/test_home_dashboard.py`| **US-17** (Personalizované uvítání, navigace Domů) | 4 | ✅ 3× PASS |
| **Profil uživatele** | `tests/profile/test_profile.py` | **US-18** (Zobrazení a editace profilu, validace) | 7 | ✅ 3× PASS |
| **Řízení přístupu (RBAC)**| `tests/security/test_rbac.py` | **US-19** (Oprávnění rolí: Host vs Zákazník vs Lektor) | 9 | ✅ 3× PASS |
| **Ochrana proti CSRF** | `tests/security/test_csrf.py` | **US-20** (CSRF token, ochrana proti Session Fixation)| 3 | ✅ 3× PASS |
| **Celkem** | **23 testovacích souborů** | **US-01 až US-20 (100% pokrytí požadavků)** | **127 testů** | **100 % HOTOVO** |

---

## 🚀 Jak testy spustit

### 1. Požadavky a instalace
```powershell
# Klonování repozitáře a přechod do adresáře
git clone https://github.com/kisar18/QA_AI_Kurz.git
cd Lekce1

# Vytvoření a aktivace virtuálního prostředí
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalace závislostí a prohlížečů Playwright
pip install -r requirements.txt
playwright install chromium
```

### 2. Spuštění všech testů
`pyproject.toml` automaticky nastavuje generování reportu `reports/report.html` a běh v prohlížeči Chromium:
```powershell
pytest
```

### 3. Spuštění konkrétní oblasti nebo testu
```powershell
# Pouze autentizace a správa účtu:
pytest tests/auth/ -v

# Pouze kurzy a zápisy:
pytest tests/courses/ -v

# Pouze bezpečnost (RBAC a CSRF):
pytest tests/security/ -v

# Konkrétní testovací soubor:
pytest tests/courses/test_enrollment.py -v

# Konkrétní testovací metoda:
pytest tests/courses/test_enrollment.py::TestCourseEnrollment::test_tc_us12_01_successful_enrollment_with_ico -v
```

### 4. Spuštění v grafickém režimu (Headed & SlowMo)
```powershell
# S viditelným oknem prohlížeče:
pytest --headed

# Zpomalený běh pro prezentaci nebo ladění (500 ms krok):
pytest --headed --slowmo 500
```

### 5. Statický audit kvality lokátorů
Projekt obsahuje auditní skript kontrolující zákaz inline lokátorů v `tests/` i čistotu Page Objectů:
```powershell
python .agents/skills/locator-strategy/scripts/audit_locators.py pages tests
```

### 6. Ověření Definice hotovo (DoD) pro konkrétní User Story
```powershell
python .agents/skills/tc-to-automated-tests/scripts/verify_automated_tests.py --tc-file manual_tests/TC_US-12_registrace_na_kurz.md --test-file tests/courses/test_enrollment.py --runs 3
```

---

## 🛡️ Zpracování defektů aplikace (`@pytest.mark.xfail`)

V souladu s pravidly projektu **nikdy nebyly oslabovány aserce ani odstraňovány kontroly**, aby testy uměle zezelenaly. Pokud chování aplikace odporuje specifikaci nebo obsahuje bezpečnostní slabinu, je test označen dekorátorem `@pytest.mark.xfail(reason=..., strict=False)`.

Všechny tyto případy jsou transparentně zdokumentovány, např.:
- **US-01 / US-10:** Neznámá URL nevrací HTTP 404, ale prázdný kontejner se stavovým kódem 200.
- **US-09:** 2 z 936 kurzů v katalogu mají chybějící soubor na disku a aplikace neposkytuje fallback na výchozí obrázek.
- **US-11:** Backend nevynucuje kapacitu na API úrovni a umožňuje překročení limitu účastníků.
- **US-12 / US-16 / US-18:** Pole IČO je specifikováno jako nepovinné, ale klientská validace vyžaduje jeho vyplnění.
- **US-14:** Kontrola poměru stran používá absolutní rozdíl namísto relativní 5% tolerance.
- **US-19:** Klientský router neomezuje přístup k formulářům tvorby kurzu pro studenty (RBAC).
- **US-20:** Backend server akceptuje požadavky bez platného CSRF tokenu (vrací HTTP 200).

---

## 📈 Vygenerované reporty

Po spuštění testovací sady nebo generátorů jsou k dispozici:
1. **`reports/report.html`**: Kompletní grafický HTML report s logem kroků a screenshoty.
2. **`docs/coverage_overview.html`**: Matice pokrytí User Stories a Test Casů (schválené test casy z `manual_tests/`).
3. **`TEST_OVERVIEW.md`**: Detailní Markdown katalog všech 127 testů a 626 kontrol.
