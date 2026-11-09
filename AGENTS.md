# AGENTS.md – pravidla projektu

Automatizované E2E testy (Python, **Playwright + pytest**, vzor **Page Object Model**) pro webovou aplikaci http://testovani.kitner.cz. Tento soubor platí pro celý projekt. V podadresářích ho doplňují specifičtější pravidla (např. [tests/AGENTS.md](tests/AGENTS.md)).

Jazyk: komentáře, docstringy a dokumentace **česky**, identifikátory v kódu **anglicky**.

---

## 1. Struktura projektu – co kam patří

| Adresář / soubor | Co do něj patří |
| :--- | :--- |
| `tests/` | **Všechny testy.** Podadresáře podle oblasti: `auth/`, `courses/`, `profile/`, `security/`, `portal/`, `navigation/`. Soubory `test_*.py`. Fixtures patří do `tests/conftest.py`. |
| `pages/` | **Všechny Page Objecty** (jedna třída = jedna obrazovka, dědí z `BasePage`). **Všechny lokátory žijí jen zde.** |
| `pages/components/` | Sdílené komponenty stránek (např. `Navbar`). |
| `helpers/` | Znovupoužitelné kroky přes více testů (přihlášení, registrace, vytvoření kurzu, logování kroků). |
| `utils/` | Nezávislé utility bez znalosti stránek (generátory dat, obrázků). |
| `data/` | **Všechna testovací data** (`*.json`) a dokumentace účtů (`data/README.md`). |
| `config/` | Centrální konfigurace (`settings.py`): URL, timeouty, cesty. Hodnoty se čtou z proměnných prostředí. |
| `reports/` | Pouze **výstup** testů (HTML report, screenshoty). Kromě `report_style.css` se necommituje. |
| `plans/` | Implementační plány (`PLAN_*.md`). Plán patří sem, ne jen do interních složek nástrojů. |
| `user stories/` | Specifikace požadavků a akceptační kritéria (US-01 až US-20). |
| `.agents/skills/` | Skilly pro agenty: `locator-strategy`, `assertion-quality-review`, `test-overview-generator`. |
| `.github/workflows/` | CI (`tests.yml`). |
| `pyproject.toml` | Konfigurace pytestu (markery, `addopts`) a závislosti. |
| `.env.example` | Vzor proměnných prostředí. Skutečný `.env` se necommituje. |

### Kam s novým kódem
- Nový test → `tests/<oblast>/test_<téma>.py`.
- Nová stránka → `pages/<nazev>_page.py` (třída dědí z `BasePage`).
- Nový lokátor → atribut Page Objectu v `pages/`.
- Nová testovací data → `data/`. Cesta se přidá do `config/settings.py`.
- Opakující se sekvence kroků ve více testech → `helpers/`.
- Nový plán → `plans/PLAN_<NAZEV>.md`.

---

## 2. Jak se testy spouštějí

Virtuální prostředí je `.venv` (Windows PowerShell).

```powershell
# Instalace (jednorázově)
pip install -r requirements.txt
playwright install chromium

# Aktivace prostředí
.\.venv\Scripts\Activate.ps1

# Všechny testy
pytest

# Jedna oblast / soubor / test
pytest tests/auth/ -v
pytest tests/auth/test_login.py -v
pytest tests/auth/test_login.py::test_nazev_testu -v

# Podle markeru (smoke, auth, courses, profile)
pytest -m smoke

# S viditelným prohlížečem, případně zpomaleně
pytest --headed
pytest --headed --slowmo 500

# Audit lokátorů (nic nemění, jen vypisuje nálezy)
python .agents/skills/locator-strategy/scripts/audit_locators.py pages tests
```

- `pyproject.toml` už nastavuje Chromium a generování reportu `reports/report.html`. Tyto přepínače se nezadávají ručně.
- URL aplikace se mění proměnnou prostředí `BASE_URL`, režim prohlížeče proměnnou `HEADLESS`.
- Po změně testů nebo Page Objectů vždy spusť dotčené testy. Nesmí zůstat červené kvůli tvé změně.
- CI (`.github/workflows/tests.yml`) spouští `pytest -v` při push a pull requestu na `main`.

---

## 3. Co se v projektu nesmí NIKDY

### Lokátory a Page Objecty
1. **Nikdy žádné lokátory v `tests/`.** Žádné `page.locator()`, `page.get_by_*()`, CSS ani XPath v testech. Testy používají jen atributy a metody Page Objectů.
2. **Nikdy XPath, `:nth-child`, CSS třídy ze stylování** v lokátorech. Priorita je `get_by_test_id`, jinak postup podle skillu `locator-strategy`.
3. **Nikdy `.first` / `.nth()` jako zkratka kolem strict mode violation.** Lokátor se zpřesní. Povoleno jen s komentářem, proč na pořadí nezáleží (např. test záměrně ověřuje libovolnou položku seznamu).

### Testy a asserty
4. **Nikdy `time.sleep()` ani `wait_for_timeout()` jako náhrada za čekání na stav.** Používej web-first `expect(...)` s auto-retry. Výjimka jen s komentářem, proč `expect` nestačí (např. ověření, že se nic nestalo).
5. **Nikdy neslabit asserty**, aby test zezelenal (mazání kontroly, zvágnění podmínky), ani používat statické kontroly typu `assert locator.is_visible()`. Vždy web-first `expect(locator)...`. Podrobná pravidla jsou v [tests/AGENTS.md](tests/AGENTS.md) a ve skillu `assertion-quality-review`.
6. **Nikdy závislost testů na pořadí spuštění** ani na datech zbylých po jiném testu. Každý test si připraví vlastní stav.
7. **Nikdy neukládat testy mimo `tests/`** ani testovací data mimo `data/`.

### Konfigurace a tajemství
8. **Nikdy natvrdo URL aplikace** v testech ani Page Objectech. Používá se `BASE_URL` z `config/settings.py`.
9. **Nikdy necommitovat `.env`**, tokeny ani osobní přihlašovací údaje. Výjimkou jsou veřejné testovací účty z `data/`.
10. **Nikdy necommitovat vygenerované výstupy** z `reports/` (HTML reporty, screenshoty).

### Git a změny
11. **Nikdy `git push --force`** na `main` a nikdy nepřepisovat historii bez výslovného pokynu.
12. **Nikdy nemazat ani neobcházet přihlášení ke GitHubu / CI.** Když push selže na autentizaci, nahlas to uživateli.
13. **Nikdy neměnit cizí soubory mimo zadání** (např. cizí Page Objecty při psaní nového testu). Souvisejí-li změny, navrhni je zvlášť.

