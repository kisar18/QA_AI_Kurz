# Automatizované testy – testovani.kitner.cz

Projekt obsahuje kompletní sadu automatizovaných **E2E testů** pro webovou aplikaci [testovani.kitner.cz](http://testovani.kitner.cz) postavenou na **Playwright** a **Pytest** v jazyce Python. Testy pokrývají všechny klíčové funkce aplikace a jsou organizovány podle vzoru **Page Object Model (POM)**.

---

## Struktura projektu

```
├── pages/                        # Page Object Model – lokátory a akce
│   ├── login_page.py             # Přihlašovací stránka (/login)
│   ├── register_page.py          # Registrační stránka (/register)
│   ├── forgot_password_page.py   # Obnova hesla (/forgot-password)
│   ├── home_page.py              # Domovská stránka po přihlášení (/home)
│   ├── profile_page.py           # Profil uživatele (/profile)
│   ├── courses_page.py           # Katalog kurzů (/courses, /courses/:id)
│   └── course_create_page.py     # Vytvoření kurzu (/courses/create)
│
├── tests/                        # Testovací scénáře
│   ├── conftest.py               # Pytest fixtures (registrace, HTML report)
│   ├── test_login.py             # 9 testů – přihlášení
│   ├── test_register.py          # 7 testů – registrace
│   ├── test_forgot_password.py   # 3 testy – obnova hesla
│   ├── test_profile.py           # 5 testů – profil uživatele
│   ├── test_courses.py           # 4 testy – katalog a detail kurzů
│   └── test_course_management.py # 3 testy – vytváření kurzů a Moje kurzy
│
├── reports/report.html           # Automaticky generovaný HTML report
├── pytest.ini                    # Konfigurace Pytest a reportu
├── requirements.txt              # Závislosti projektu
└── test_user.json                # Uložené testovací přihlašovací údaje
```

---

## Pokryté testovací scénáře (33 testů)

### 1. Přihlášení – `tests/test_login.py` (9 testů)
1. Navigace z `/courses` na `/login` přes odkaz v menu
2. Kontrola přítomnosti a viditelnosti UI prvků formuláře
3. Úspěšné přihlášení a odhlášení (ověření přesměrování + odhlášení)
4. Maskování pole hesla (`type="password"`)
5. HTML5 validace formátu e-mailu
6. Neplatné přihlašovací údaje (chybová hláška)
7. Parametrizovaná matice neplatných přihlášení (2 kombinace)
8. Odkaz „Zapomenuté heslo" → `/forgot-password`
9. Odkaz „Registrace" → `/register`

### 2. Registrace – `tests/test_register.py` (7 testů)
1. Kontrola přítomnosti UI prvků registračního formuláře
2. Úspěšná registrace nového uživatele + ověření uvítání
3. Neshodná hesla – chybová hláška
4. Duplicitní e-mail – chybová hláška
5. HTML5 validace formátu e-mailu
6. Maskování obou polí pro heslo
7. Odeslání prázdného formuláře – validační hlášky pro všechna povinná pole

### 3. Obnova hesla – `tests/test_forgot_password.py` (3 testy)
1. Zobrazení formuláře a jeho prvků (pole e-mail, tlačítko)
2. HTML5 validace – zamezení odeslání při neplatném formátu e-mailu
3. Odeslání žádosti s platným e-mailem + ověření odpovědi aplikace

### 4. Profil uživatele – `tests/test_profile.py` (5 testů)
1. Načtení profilu – předvyplněné údaje uživatele
2. Úspěšná aktualizace profilu (telefon, IČO) a přesměrování
3. Validace neplatného IČO (ARES modulo 11)
4. Validace neplatného telefonního čísla
5. Ochrana před nepřihlášeným uživatelem (přesměrování na `/login`)

### 5. Katalog a detail kurzů – `tests/test_courses.py` (4 testy)
1. Zobrazení katalogu kurzů a nadpisu stránky
2. Přítomnost prvků karet kurzů (název, cena, odkaz)
3. Proklik na detail kurzu `/courses/:id`
4. Zobrazení termínů běhu kurzu – anonymní vs. přihlášený uživatel

### 6. Správa kurzů – `tests/test_course_management.py` (3 testy)
1. Přítomnost formuláře pro vytvoření kurzu na `/courses/create`
2. Odeslání formuláře – vytvoření nového kurzu
3. Zobrazení stránky Moje kurzy `/my-courses`

---

## Jak testy spustit

### Požadavky
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

### Spuštění s viditelným prohlížečem
```powershell
pytest --headed
```

### Spuštění se zpomaleným krokem (pro sledování)
```powershell
pytest --headed --slowmo 500
```

### Spuštění konkrétního modulu
```powershell
pytest tests/test_login.py -v
```

### HTML report
Po každém spuštění je automaticky vygenerován report:
```
reports/report.html
```

---

## Architektura – Page Object Model

Všechny lokátory jsou definovány výhradně v souborech `pages/*.py` pomocí nativního Playwright API:
```python
page.get_by_test_id("email_input")
```
Testovací soubory v `tests/` neobsahují žádné inline selektory – veškerá interakce probíhá přes metody Page Objectů.
