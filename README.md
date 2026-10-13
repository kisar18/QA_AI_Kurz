# Automatizované testy pro Demo Login (kitner.cz)

Projekt obsahuje sadu automatizovaných E2E testů pro ověření přihlašovacího formuláře na adrese [http://testovani.kitner.cz/courses](http://testovani.kitner.cz/courses) pomocí **Playwright** a **Pytest** v jazyce Python.

## Struktura projektu

- `pages/login_page.py` – Page Object Model pro přihlašovací stránku
- `pages/register_page.py` – Page Object Model pro registrační stránku
- `tests/conftest.py` – Pytest fixtures (vč. automatické registrace a ukládání `test_user.json`)
- `tests/test_login.py` – Testovací scénáře pro přihlášení a odhlášení
- `tests/test_register.py` – Testovací scénáře pro registraci
- `test_user.json` – Uložené přihlašovací údaje pro opakované použití v testech
- `reports/report.html` – Automaticky generovaný HTML report s výsledky testů
- `pytest.ini` – Konfigurace pro spouštění testů a generování reportu
- `requirements.txt` – Seznam potřebných knihoven

## Pokryté testovací scénáře

### Přihlášení a odhlášení (`tests/test_login.py`)
1. **Navigace na přihlášení:** Ověření přechodu z `/courses` do přihlášení `/login` přes odkaz v menu.
2. **Kontrola UI prvků:** Ověření existence a viditelnosti vstupních polí (email, heslo), tlačítka odeslání a odkazů.
3. **Úspěšné přihlášení a odhlášení:** Přihlášení platným účtem, ověření přesměrování a následné odhlášení.
4. **Validace hesla:** Ověření maskování zadaného hesla (`type="password"`).
5. **Nativní HTML5 validace:** Ověření validace formátu e-mailu před odesláním.
6. **Neplatné přihlášení:** Ověření zobrazení validační chybové hlášky (*"These credentials do not match our records."*).
7. **Parametrizované testy neplatných údajů:** Testování různých kombinací neplatných e-mailů a hesel.
8. **Odkaz na zapomenuté heslo:** Ověření přesměrování na `/forgot-password`.
9. **Odkaz na registraci:** Ověření přesměrování na `/register`.

### Registrace (`tests/test_register.py`)
1. **Kontrola UI prvků:** Ověření existence polí (jméno, email, heslo, heslo znovu) a tlačítka.
2. **Úspěšná registrace:** Registrace nového uživatele a ověření uvítání na domovské stránce.

## Jak testy spustit

1. **Aktivace virtuálního prostředí:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Spuštění testů v headless režimu:**
   ```powershell
   pytest
   ```

3. **Spuštění testů s viditelným oknem prohlížeče (headed):**
   ```powershell
   pytest --headed
   ```

4. **Spuštění s pomalejším krokem pro sledování (slowmo):**
   ```powershell
   pytest --headed --slowmo 500
   ```
