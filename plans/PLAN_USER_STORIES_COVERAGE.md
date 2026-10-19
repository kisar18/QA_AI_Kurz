# Implementační plán: Pokrytí požadavků (User Stories US-01 až US-20) automatizovanými testy

Tento plán specifikuje kompletní strategii implementace automatizovaných testů v jazyce Python (Playwright + Pytest) s **100% pokrytím a přímou vazbou na všech 20 User Stories (US-01 až US-20)** ze specifikace [`user stories/požadavky_ust_podle_src.md`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/user%20stories/po%C5%BEadavky_ust_podle_src.md).

---

## 1. Traceability Matrix: Přehled pokrytí US-01 až US-20

| User Story | Název a stručný popis | Testovací modul / soubor | Stav |
| :--- | :--- | :--- | :--- |
| **US-01** | Úvodní navigační rozcestník testovacích aplikací | `tests/portal/test_linktree.py` | 🆕 Nový testovací modul |
| **US-02** | Registrace zákaznického účtu s automatickým přihlášením | `tests/auth/test_register.py` | 🔄 Rozšíření o trim a case-insensitivity |
| **US-03** | Přihlášení do aplikace | `tests/auth/test_login.py` | 🔄 Rozšíření o trim, case a klávesnici (`Enter`) |
| **US-04** | Bezpečné odhlášení ze systému | `tests/auth/test_logout.py` | ✅ Zahrnuto a verifikováno |
| **US-05** | Žádost o obnovu zapomenutého hesla | `tests/auth/test_forgot_password.py` | ✅ Zahrnuto a verifikováno |
| **US-06** | Dokončení změny hesla pomocí tokenu | `tests/auth/test_reset_password.py` | 🆕 Nový test (token v URL, nové heslo) |
| **US-07** | Ověření e-mailové adresy | `tests/auth/test_email_verification.py` | 🆕 Nový test (potvrzovací odkaz a resend) |
| **US-08** | Ochrana proti útokům hrubou silou na přihlášení | `tests/auth/test_rate_limiting.py` | 🆕 Nový test (5 neúspěšných pokusů $\rightarrow$ blokace) |
| **US-09** | Prohlížení katalogu kurzů | `tests/courses/test_courses.py` | 🔄 Rozšíření o výzvu pro nepřihlášené |
| **US-10** | Detail kurzu a vypsané termíny | `tests/courses/test_courses.py` | 🔄 Rozšíření o formát obsazenosti (*X/Y*) a termíny |
| **US-11** | Vizuální indikace a zamezení zápisu při plné kapacitě | `tests/courses/test_courses.py` | 🆕 Nový test (plná kapacita $\rightarrow$ blokace zápisu) |
| **US-12** | Nezávazná registrace na běh kurzu (IČO a telefon) | `tests/courses/test_enrollment.py` | 🆕 Nový test (zápis, modulo 11, min 9 číslic tel.) |
| **US-13** | Přehled mých zapsaných kurzů | `tests/profile/test_profile.py` | 🔄 Rozšíření o ověření organizačních dat kurzu |
| **US-14** | Vytvoření nového kurzu lektorem | `tests/courses/test_course_management.py` | 🔄 Rozšíření o validaci poměru stran 16:9 obrázku |
| **US-15** | Vypsání nového termínu (běhu) kurzu lektorem | `tests/courses/test_course_iterations.py` | 🆕 Nový test (termín, datum, čas, lektor) |
| **US-16** | Zobrazení seznamu přihlášených účastníků pro lektora | `tests/courses/test_course_iterations.py` | 🆕 Nový test (tabulka studentů vs. zamezení studentovi) |
| **US-17** | Domovská uvítací nástěnka po přihlášení | `tests/portal/test_home_dashboard.py` | 🆕 Nový test (uvítání se jménem + tlačítko „Domů“) |
| **US-18** | Správa a editace uživatelského profilu | `tests/profile/test_profile.py` | ✅ Zahrnuto a verifikováno |
| **US-19** | Řízení přístupu na základě rolí (RBAC) | `tests/security/test_rbac.py` | 🆕 Nový testovací modul (role student vs lektor vs anonym) |
| **US-20** | Ochrana proti podvržení požadavků CSRF | `tests/security/test_csrf.py` | 🆕 Nový test (přítomnost a validace CSRF tokenu) |

---

## 2. Nové a rozšířené Page Objecty (POM)

Všechny Page Objecty dědí z [`pages/base_page.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/base_page.py) a eliminují inline selektory v testech:

1. **`pages/linktree_page.py`** (`LinktreePage`): Rozcestník portálu na `/` (odkazy: Kalkulačka, Testovací login, NextDate, Registrace, Demo-login).
2. **`pages/reset_password_page.py`** (`ResetPasswordPage`): Formulář pro nastavení nového hesla na `/reset-password/:token`.
3. **`pages/course_enroll_page.py`** (`CourseEnrollPage`): Formulář nezávazné registrace na běh kurzu (IČO, telefon).
4. **`pages/course_iteration_create_page.py`** (`CourseIterationCreatePage`): Formulář vypsání termínu lektorem na `/courses/:id/create-iteration`.
5. **`pages/students_list_page.py`** (`StudentsListPage`): Přehled přihlášených studentů u běhu kurzu.
6. **Rozšíření `pages/home_page.py`**: Lokátor pro personalizované uvítání uživatele na `/home`.

---

## 3. Fáze a kroky realizace (se všemi US-01 až US-20)

### Fáze 1: Úvodní navigační rozcestník a domovská nástěnka (US-01, US-17)
- [x] **Krok 1.1 [US-01]**: Vytvořit [`pages/linktree_page.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/linktree_page.py) a testovací soubor [`tests/portal/test_linktree.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/portal/test_linktree.py):
  - Test přítomnosti odkazů portálu na `/` (Kalkulačka, Testovací login, NextDate, Registrace na kurz, Demo-login).
  - Test přesměrování z tlačítka „Demo-login“ přímo do katalogu kurzů `/courses`.
- [x] **Krok 1.2 [US-17]**: Rozšířit [`pages/home_page.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/home_page.py) a vytvořit [`tests/portal/test_home_dashboard.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/portal/test_home_dashboard.py):
  - Test personalizovaného uvítání uživatele na `/home` obsahující jeho jméno po přihlášení i po registraci.
  - Test trvalé dostupnosti položky „Domů“ v horním navigačním menu.

---

### Fáze 2: Autentizace, sezení a ochrana proti zneužití (US-02, US-03, US-04, US-05, US-06, US-07, US-08)
- [x] **Krok 2.1 [US-02]**: Rozšířit [`tests/auth/test_register.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/auth/test_register.py):
  - Test automatického oříznutí mezer (trim) na začátku a konci zadávaného e-mailu.
  - Test necitlivosti na velikost písmen při ověřování unikátnosti registrace (case-insensitivity).
- [x] **Krok 2.2 [US-03]**: Rozšířit [`tests/auth/test_login.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/auth/test_login.py):
  - Test přihlášení s e-mailem obsahujícím velká písmena (`USER@EXAMPLE.COM`).
  - Test přihlášení s mezerami před/za adresou (`"  user@example.com  "`).
  - Test přístupnosti z klávesnice: odeslání přihlášení stiskem klávesy `Enter`.
- [x] **Krok 2.3 [US-04]**: Revize a verifikace [`tests/auth/test_logout.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/auth/test_logout.py):
  - Test bezpečného odhlášení: okamžité zneplatnění sezení, návrat na výchozí stav a skrytí privátního menu.
- [x] **Krok 2.4 [US-05]**: Revize a verifikace [`tests/auth/test_forgot_password.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/auth/test_forgot_password.py):
  - Test formuláře žádosti o obnovu hesla, validace povinného e-mailu a zobrazení potvrzení o odeslání.
- [x] **Krok 2.5 [US-06]**: Vytvořit [`pages/reset_password_page.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/reset_password_page.py) a [`tests/auth/test_reset_password.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/auth/test_reset_password.py):
  - Test načtení formuláře pro zadání nového hesla s platným tokenem v URL (`/reset-password/:token`).
  - Test validace shody hesel a zobrazení potvrzení po uložení nového hesla.
  - Test odmítnutí neplatného či expirovaného tokenu.
- [x] **Krok 2.6 [US-07]**: Vytvořit [`tests/auth/test_email_verification.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/auth/test_email_verification.py):
  - Test zobrazení výzvy k ověření e-mailu a funkčnosti tlačítka pro znovuzaslání ověřovacího odkazu (resend).
- [x] **Krok 2.7 [US-08]**: Vytvořit [`tests/auth/test_rate_limiting.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/auth/test_rate_limiting.py):
  - Test odeslání 5 po sobě jdoucích neúspěšných přihlášení $\rightarrow$ ověření dočasné blokace a hlášky o nutnosti vyčkat.

---

### Fáze 3: Katalog kurzů, detail a kapacita (US-09, US-10, US-11)
- [x] **Krok 3.1 [US-09]**: Rozšířit [`tests/courses/test_courses.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/courses/test_courses.py):
  - Test zobrazení karty kurzu (název, popis, zaokrouhlená cena, kapacita).
  - Test zobrazení výzvy k registraci pro nepřihlášeného návštěvníka pod katalogem kurzů.
- [x] **Krok 3.2 [US-10]**: Rozšířit [`tests/courses/test_courses.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/courses/test_courses.py):
  - Test detailu kurzu: kompletní popis, seznam vypsaných termínů, datum zahájení a ukončení.
  - Test formátu poměru obsazenosti běhu vůči kapacitě (např. *3/12*).
- [x] **Krok 3.3 [US-11]**: Doplnit do [`tests/courses/test_courses.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/courses/test_courses.py):
  - Test indikace plně obsazeného běhu a ověření, že tlačítko pro nezávaznou registraci není k dispozici / je zablokováno.

---

### Fáze 4: Zápis na kurz a správa zapsaných kurzů (US-12, US-13)
- [x] **Krok 4.1 [US-12]**: Vytvořit [`pages/course_enroll_page.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/course_enroll_page.py) a [`tests/courses/test_enrollment.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/courses/test_enrollment.py):
  - Test formuláře nezávazné registrace zákazníka na běh kurzu (IČO a telefon).
  - Test validace povinného telefonu (musí obsahovat alespoň 9 číslic).
  - Test validace IČO pomocí váženého kontrolního součtu modulo 11 (využití `utils/data_generator.py`).
  - Test úspěšného odeslání zápisu a přesměrování do `/my-courses`.
- [x] **Krok 4.2 [US-13]**: Rozšířit testy v [`tests/profile/test_profile.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/profile/test_profile.py):
  - Test přehledu v sekci „Moje kurzy“: zobrazení aktivního zápisu studenta včetně názvu, ceny, termínů první/poslední lekce a formy výuky.

---

### Fáze 5: Správa kurzů a výuky pro roli lektora (US-14, US-15, US-16)
- [x] **Krok 5.1 [US-14]**: Doplnit do [`tests/courses/test_course_management.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/courses/test_course_management.py):
  - Test vytvoření kurzu lektorem včetně validace nahrávaného grafického náhledu (kontrola poměru stran 16:9 s tolerancí 5 %).
- [x] **Krok 5.2 [US-15]**: Vytvořit [`pages/course_iteration_create_page.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/course_iteration_create_page.py) a test v [`tests/courses/test_course_iterations.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/courses/test_course_iterations.py):
  - Test vypsání nového termínu (běhu) kurzu lektorem na `/courses/:id/create-iteration`: datum zahájení, datum ukončení, den v týdnu, čas a místo.
  - Test přesměrování na detail kurzu a okamžitého zobrazení nového termínu.
- [x] **Krok 5.3 [US-16]**: Vytvořit [`pages/students_list_page.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/students_list_page.py) a test v [`tests/courses/test_course_iterations.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/courses/test_course_iterations.py):
  - Test zobrazení tabulky přihlášených studentů lektorem (jméno, e-mail, telefon, IČO nebo „Neuvedeno“).
  - Test, že běžný zákazník ani nepřihlášený návštěvník nemá k seznamu účastníků přístup.

---

### Fáze 6: Uživatelský profil klienta (US-18)
- [x] **Krok 6.1 [US-18]**: Revize a verifikace testů v [`tests/profile/test_profile.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/profile/test_profile.py):
  - Test předvyplnění údajů uživatele (jméno, e-mail, IČO, telefon).
  - Test úspěšné editace profilu a přesměrování na domovskou stránku.
  - Test validace neplatného IČO a neplatného telefonního čísla.

---

### Fáze 7: Bezpečnost, řízení přístupu a integrita sezení (US-19, US-20)
- [x] **Krok 7.1 [US-19]**: Vytvořit [`tests/security/test_rbac.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/security/test_rbac.py):
  - Test pokusu nepřihlášeného návštěvníka o otevření privátních URL (`/profile`, `/my-courses`) $\rightarrow$ přesměrování.
  - Test pokusu běžného studenta o přístup k lektorským funkcím (`/courses/create`, `/courses/:id/create-iteration`) $\rightarrow$ odepření přístupu.
  - Test, že lektor se nemůže zapsat na běh kurzu (zápis je vyhrazen zákazníkům).
- [x] **Krok 7.2 [US-20]**: Vytvořit [`tests/security/test_csrf.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/security/test_csrf.py):
  - Test přítomnosti platného CSRF tokenu ve všech formulářích (přihlášení, registrace, vytvoření kurzu, zápis).
  - Test odmítnutí požadavků s chybějícím nebo neplatným CSRF tokenem.
  - Test regenerace sezení po přihlášení a odhlášení (ochrana proti Session Fixation).

---

### Fáze 8: Celková verifikace, CI/CD a reportování
- [x] **Krok 8.1**: Spustit kompletní sadu testů (cca 50–55 testů):
  ```powershell
  .venv\Scripts\pytest -v
  ```
- [x] **Krok 8.2**: Zkontrolovat generovaný report [`reports/report.html`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/reports/report.html).
- [x] **Krok 8.3**: Aktualizovat [README.md](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/README.md) a odeslat commit do GitHub repozitáře.
