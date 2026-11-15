# Implementační plán: Dokončení převodu zbývajících TC do automatizovaných testů

Tento plán stanovuje postup systematického převodu všech zbývajících manuálních test casů (`manual_tests/TC_US-*.md`) do automatizovaných E2E testů (Playwright + pytest, POM) v souladu se skillem `tc-to-automated-tests`.

---

## 1. Souhrnný stav projektu – 100 % DOKONČENO

- **Celkový počet User Stories:** 20 (US-01 až US-20)
- **Kompletně naimplementováno, nezávisle auditováno a ověřeno (DoD PASS 3×, exit code 0):** **20/20 User Stories (100 %)**
- **Celkový počet testů v sadě:** 127 testů ve 23 testovacích souborech s 626 kontrolami.
- **Výsledek celého testovacího běhu pytestu:** `90 passed, 37 xfailed in 517.27s (Exit code 0)`
- **Kvalita lokátorů:** 0 ERROR nálezů v celém projektu (`audit_locators.py`). Žádné inline lokátory v testech.

---

## 2. Přehled implementace a verifikace všech dávek

### Dávka 1: Autentizace a správa účtu (Auth & Security) – KOMPLETNĚ HOTOVO
| User Story | Zdrojový soubor TC | Cílový testovací soubor | Dotčené Page Objecty | Stav DoD (3x PASS) | QA Audit |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **US-01** (Rozcestník) | `manual_tests/TC_US-01_rozcestnik.md` | `tests/portal/test_linktree.py` | `LinktreePage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-02** (Registrace) | `manual_tests/TC_US-02_registrace.md` | `tests/auth/test_register.py` | `RegisterPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-03** (Přihlášení) | `manual_tests/TC_US-03_prihlaseni.md` | `tests/auth/test_login.py` | `LoginPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-04** (Odhlášení) | `manual_tests/TC_US-04_odhlaseni.md` | `tests/auth/test_logout.py` | `LoginPage`, `Navbar` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-05** (Obnova hesla) | `manual_tests/TC_US-05_zadost_o_obnovu_hesla.md` | `tests/auth/test_forgot_password.py` | `ForgotPasswordPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-06** (Dokončení změny) | `manual_tests/TC_US-06_dokonceni_zmeny_hesla.md` | `tests/auth/test_reset_password.py` | `ResetPasswordPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-07** (Ověření e-mailu) | `manual_tests/TC_US-07_overeni_emailu.md` | `tests/auth/test_email_verification.py` | `LoginPage`, `RegisterPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-08** (Rate limiting) | `manual_tests/TC_US-08_rate_limiting.md` | `tests/auth/test_rate_limiting.py` | `LoginPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-18** (Profil uživatele) | `manual_tests/TC_US-18_profil_uzivatele.md` | `tests/profile/test_profile.py` | `ProfilePage` | **HOTOVO (3x PASS)** | SCHVÁLENO |

---

### Dávka 2: Katalog a zápis kurzů (Courses & Enrollment) – KOMPLETNĚ HOTOVO
| User Story | Zdrojový soubor TC | Cílový testovací soubor | Dotčené Page Objecty | Stav DoD (3x PASS) | QA Audit |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **US-09** (Katalog kurzů) | `manual_tests/TC_US-09_katalog_kurzu.md` | `tests/courses/test_courses_catalog.py` | `CoursesPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-10** (Detail kurzu) | `manual_tests/TC_US-10_detail_kurzu.md` | `tests/courses/test_course_detail.py` | `CoursesPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-11** (Kapacita kurzu) | `manual_tests/TC_US-11_kapacita_kurzu.md` | `tests/courses/test_course_capacity.py` | `CoursesPage`, `CourseEnrollPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-12** (Registrace na kurz)| `manual_tests/TC_US-12_registrace_na_kurz.md` | `tests/courses/test_enrollment.py` | `CoursesPage`, `CourseEnrollPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-13** (Moje kurzy) | `manual_tests/TC_US-13_moje_kurzy.md` | `tests/courses/test_my_courses.py` | `MyCoursesPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |

---

### Dávka 3: Lektorská správa kurzů a účastníci (Lector & Course Management) – KOMPLETNĚ HOTOVO
| User Story | Zdrojový soubor TC | Cílový testovací soubor | Dotčené Page Objecty | Stav DoD (3x PASS) | QA Audit |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **US-14** (Vytvoření kurzu) | `manual_tests/TC_US-14_vytvoreni_kurzu.md` | `tests/courses/test_course_create.py` | `CourseCreatePage`, `CoursesPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-15** (Vypsání termínu běhu)| `manual_tests/TC_US-15_vypsani_terminu.md` | `tests/courses/test_course_iterations.py`| `CourseIterationCreatePage`, `CoursesPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-16** (Seznam účastníků) | `manual_tests/TC_US-16_seznam_ucastniku.md` | `tests/courses/test_students_list.py` | `StudentsListPage`, `CoursesPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |

---

### Dávka 4: Portál, dashboard a bezpečnost (Portal & Security) – KOMPLETNĚ HOTOVO
| User Story | Zdrojový soubor TC | Cílový testovací soubor | Dotčené Page Objecty | Stav DoD (3x PASS) | QA Audit |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **US-17** (Domovská nástěnka)| `manual_tests/TC_US-17_domovska_nastenka.md` | `tests/portal/test_home_dashboard.py`| `HomePage` | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-19** (Řízení přístupu RBAC)| `manual_tests/TC_US-19_rbac.md` | `tests/security/test_rbac.py` | `CoursesPage`, `ProfilePage`, `Navbar`, atd. | **HOTOVO (3x PASS)** | SCHVÁLENO |
| **US-20** (Ochrana proti CSRF)| `manual_tests/TC_US-20_csrf_ochrana.md` | `tests/security/test_csrf.py` | `LoginPage`, `RegisterPage` | **HOTOVO (3x PASS)** | SCHVÁLENO |

---

## 3. Výsledné artefakty projektu

1. **`TEST_OVERVIEW.md`**: Kompletní katalog 127 automatizovaných testů s rozpadem kroků a 626 kontrol.
2. **`reports/coverage_overview.html`**: Interaktivní HTML report mapující pokrytí všech User Stories a Test Casů.
3. **`reports/report.html`**: Detailní HTML report z exekuce pytestu se screenshoty a logy.
