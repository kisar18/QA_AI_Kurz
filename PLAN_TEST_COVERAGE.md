# Implementační plán: Rozšíření testovacího pokrytí na všechny klíčové funkce aplikace (včetně správy kurzů)

Tento plán specifikuje kompletní strategii rozšíření automatizovaných testů pro webovou aplikaci **`testovani.kitner.cz`**. Zahrnuje jak stávající moduly (Login, Registrace, Profil), tak **kompletní životní cyklus kurzů (vytvoření kurzu, vypsání běhu kurzu, zápis účastníka a Moje kurzy)**.

---

## 1. Technická analýza správy kurzů v aplikaci

Detailní analýza zdrojového kódu a API aplikace odhalila:
- ✅ **Vytvoření kurzu:** Plně podporováno na `/courses/create` (`POST /api/courses`) s formulářovými prvky `course_name_input`, `course_description_input`, `course_capacity_input`, `course_price_input` a tlačítkem `registration_link`.
- ✅ **Vytvoření běhu kurzu (Iteration):** Plně podporováno na `/courses/:id/create-iteration` (`POST /api/courses/:id/iterations`) s tlačítkem `course_iteration_submit_button`.
- ✅ **Zápis na kurz (Enrollment):** Plně podporováno na `/courses/:id/register` (`POST /api/courses/enroll/:id`).
- ✅ **Moje kurzy:** Plně podporováno na `/my-courses` (`GET /api/courses/my`).
- ❌ **Úprava a smazání kurzu:** Aplikace v UI ani v REST API tyto operace nepodporuje (kurzy jsou po vytvoření neměnné a nelze je smazat).

---

## 2. Přehled modulů a cílového pokrytí

| Modul aplikace | URL | Cílové testy |
| :--- | :--- | :--- |
| **1. Přihlášení (Login)** | `/login` | **9 testů (Hotovo)** – pozitivní, negativní matrix, HTML5, maskování |
| **2. Registrace (Register)** | `/register` | **7 testů (+5 nových)** – happy path, neshodná hesla, duplicitní e-mail, prázdná pole, HTML5 validace e-mailu, maskování hesel |
| **3. Profil uživatele (Profile)** | `/profile` | **4 testy (Nové)** – načtení údajů, editace telefonu a IČO (`profile_save_button`), validace, ochrana před nepřihlášeným uživatelem |
| **4. Katalog a Detail kurzů** | `/courses`, `/courses/:id` | **4 testy (Nové)** – výpis katalogu, ověření karet, detail kurzu, vypsané běhy |
| **5. Správa kurzů (Vytvoření & Běhy)** | `/courses/create`, `/courses/:id/create-iteration` | **4 testy (Nové)** – vytvoření nového kurzu, validace povinných polí, vypsání nového běhu kurzu, zápis na kurz a kontrola v `/my-courses` |
| **6. Obnova hesla (Forgot)** | `/forgot-password` | **3 testy (Nové)** – formulář obnovy, HTML5 e-mail validace, odeslání žádosti |

---

## 3. Nové Page Objecty (POM)

1. **`pages/course_create_page.py`** (`CourseCreatePage`):
   - Lokátory: `name_input`, `description_input`, `capacity_input`, `price_input`, `submit_button`
   - Metody: `navigate()`, `create_course(name, description, capacity, price)`
2. **`pages/courses_page.py`** (`CoursesPage`):
   - Lokátory: `courses_title`, `courses_section`, `course_cards`, `course_names`, `course_prices`, `registration_links`
   - Metody: `navigate()`, `open_course_detail(index_or_id)`, `get_courses_count()`
3. **`pages/profile_page.py`** (`ProfilePage`):
   - Lokátory: `profile_heading`, `name_input`, `email_input`, `phone_input`, `ico_input`, `save_button`
   - Metody: `navigate()`, `update_profile(name, phone, ico)`

---

## 4. Fáze a kroky implementace

### Fáze 1: Rozšíření testů registrace ([`tests/test_register.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/test_register.py))
- [ ] **Krok 1.1**: Test neshodných hesel (`password != password_again`).
- [ ] **Krok 1.2**: Test duplicitní registrace (pokus o registraci s existujícím e-mailem).
- [ ] **Krok 1.3**: Test HTML5 validace formátu e-mailu.
- [ ] **Krok 1.4**: Test ověření atributů `type="password"` u obou hesel.
- [ ] **Krok 1.5**: Test odeslání prázdného formuláře.

### Fáze 2: Page Object a testy profilu uživatele
- [ ] **Krok 2.1**: Vytvořit [`pages/profile_page.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/profile_page.py).
- [ ] **Krok 2.2**: Vytvořit [`tests/test_profile.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/test_profile.py) (načtení profilu, editace telefonu/IČO, uložení přes `profile_save_button`, kontrola přístupu bez přihlášení).

### Fáze 3: Page Object a testy katalogu kurzů
- [ ] **Krok 3.1**: Vytvořit [`pages/courses_page.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/courses_page.py).
- [ ] **Krok 3.2**: Vytvořit [`tests/test_courses.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/test_courses.py) (zobrazení katalogu, kontrola prvků karet kurzů, proklik na detail `/courses/:id`, zobrazení termínů běhu).

### Fáze 4: Page Object a testy vytváření kurzů & zápisu (Course Lifecycle)
- [ ] **Krok 4.1**: Vytvořit [`pages/course_create_page.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/pages/course_create_page.py).
- [ ] **Krok 4.2**: Vytvořit [`tests/test_course_management.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/test_course_management.py):
  - Test úspěšného vytvoření nového kurzu na `/courses/create` a ověření přesměrování do `/courses`.
  - Test validace povinných polí při vytváření kurzu.
  - Test vypsání nového běhu kurzu na `/courses/:id/create-iteration`.
  - Test zápisu na kurz a ověření, že se kurz objeví v `/my-courses`.

### Fáze 5: Testy pro obnovu hesla ([`tests/test_forgot_password.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/test_forgot_password.py))
- [ ] **Krok 5.1**: Test zobrazení formuláře a prvků.
- [ ] **Krok 5.2**: Test HTML5 validace formátu e-mailu.
- [ ] **Krok 5.3**: Test odeslání požadavku na obnovu hesla.

### Fáze 6: Verifikace celé testovací sady & Reporting
- [ ] **Krok 6.1**: Spustit kompletní sadu testů:
  ```powershell
  .venv\Scripts\pytest -v
  ```
- [ ] **Krok 6.2**: Ověřit celkový počet testů (~28 testů) a generovaný HTML report [`reports/report.html`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/reports/report.html).

### Fáze 7: Verzování milníku na Git a GitHub
- [ ] **Krok 7.1**: Vytvořit souhrnný git commit:
  ```powershell
  git add .
  git commit -m "Test: Comprehensive test suite covering core features and course lifecycle"
  ```
- [ ] **Krok 7.2**: Push do vzdáleného repozitáře:
  ```powershell
  git push origin main
  ```
