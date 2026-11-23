# Implementační plán: Kvalita asercí, strict=True u xfail, prevence duplicit a triggery skillů

Tento komplexní plán řeší zapracování zpětné vazby a architektonické zabezpečení projektu proti budoucím chybám:
1. **Zavedení strojové pojistky pro kvalitu asercí** – vytvoření AST skriptu `audit_assertions.py`, napojení do `verify_automated_tests.py` a rozšíření `assertion-quality-review/SKILL.md` o reálné vzory chyb.
2. **Zavedení strojové pojistky proti duplicitním a osiřelým testům** – rozšíření `check_done.py` a `verify_automated_tests.py` o kontrolu striktní vazby 1:1 (každý TC smí mít právě 1 test) a pravidlo Zero-Unmapped-Tests (zákaz netagovaných ad-hoc testů).
3. **Odstranění 4 podmíněných `if` asercí** (`test_email_verification.py`, `test_logout.py`, `test_linktree.py`).
4. **Přepnutí všech 37 `@pytest.mark.xfail` z `strict=False` na `strict=True`** pro striktní sledování regresí a defektů.
5. **Úklid duplicitních a historických netagovaných testů**:
   - Smazání historických souborů `tests/courses/test_courses.py` a `tests/courses/test_course_management.py`.
   - Sloučení rozdělených testů pro `TC-US03-04` a `TC-US18-02` do čistého 1:1 mapování.
   - Úklid netagovaných zbytků raných cvičení v `test_register.py`, `test_navbar.py` a `test_profile.py`.
6. **Úprava spouštěcích podmínek (frontmatter `description`) u 3 skillů** (`ust-to-manual-tc`, `tc-to-automated-tests`, `test-overview-generator`), aby se aktivovaly autonomně při jakékoliv práci s TC, testy či přehledy, nikoliv jen na výslovný dotaz.
7. **Přegenerování přehledů a validace Definition of Done (DoD)** pomocí testovacích a validačních skriptů.

---

## 1. Analýza zjištěných nedostatků a příčin

| Oblast / Položka | Současný stav (Nález) | Cílový stav (Řešení) |
| :--- | :--- | :--- |
| **Chybějící strojová pojistka asercí** | Skill `assertion-quality-review` je pouze textový návod bez auditačního skriptu. Skript `verify_automated_tests.py` podmíněné aserce nehlídá. | Vytvořit AST skript `audit_assertions.py`, začlenit kontrolu do DoD (`verify_automated_tests.py`) a obohatit `SKILL.md` o 3 reálné scénáře chyb. |
| **Chybějící strojová pojistka proti duplicitám** | Skript `check_done.py` kontroloval pouze to, zda má každý manuální TC alespoň 1 test. Nekontroloval opačný směr (testy bez TC ID) ani unikátnost 1:1 (vícenásobné testy na stejný TC). | Do `check_done.py` a `verify_automated_tests.py` přidat 2 kontroly: 1. Unikátnost mapování 1:1 (žádné duplicitní TC), 2. Zákaz testů bez schváleného TC ID (Zero-Unmapped-Tests). |
| **Podmíněné aserce** | `tests/auth/test_email_verification.py` (L64): `if response.status == 403: ... else: ...` | Odstranit větev `if/else`. Test má bezpodmínečně vyžadovat `response.status == 403` a ověřit zobrazení chybového stavu zakázaného podpisu. |
| **Podmíněné aserce** | `tests/auth/test_logout.py` (L67): `if session_cookie_after: assert ...` | Odstranit podmínku `if`. Provést bezpodmínečnou aserci na zneplatnění/vymazání session cookie: `assert session_cookie_after is None or session_cookie_after["value"] != session_cookie_before["value"]`. |
| **Podmíněné aserce** | `tests/portal/test_linktree.py` (L88): `if target_attr == "_blank": expect(...)` | Odstranit podmínku `if`, která obchází aserci při absenci atributu. Nahradit deterministickou asercí na bezpečnost odkazu (pokud odkaz otevírá nové okno, musí mít rel, jinak zůstává ve stejném okně). |
| **xfail konfigurace** | 37 výskytů `@pytest.mark.xfail(..., strict=False)` napříč `tests/` | Přepnout všech 37 výskytů na `strict=True`, aby nečekaný úspěch (XPASS) způsobil selhání sady a upozornil na vyřešený defekt. |
| **Duplicitní a netagované testy** | V `tests/courses/` leží duplicitní `test_courses.py` a `test_course_management.py`. V `test_login.py` jsou 2 testy pro `TC-US03-04` a v `test_profile.py` 2 testy pro `TC-US18-02`. V `test_register.py`, `test_navbar.py` a `test_profile.py` je 5 netagovaných testů z raných lekcí. | Smazat `test_courses.py` a `test_course_management.py`. Sloučit duplicity na 1:1 a odstranit netagované duplicity z raných lekcí. |
| **Skill ust-to-manual-tc** | `description` obsahuje omezující podmínku *"když uživatel požaduje..."*. | Přeformulovat na autonomní aktivaci při tvorbě, specifikaci, analýze a auditu manuálních TC. |
| **Skill tc-to-automated-tests** | `description` obsahuje omezující podmínku *"když uživatel požaduje..."*. | Přeformulovat na autonomní aktivaci při implementaci, generování, refaktoringu a DoD automatizovaných testů. |
| **Skill test-overview-generator** | `description` obsahuje omezující podmínku *"když uživatel požaduje..."*. | Přeformulovat na autonomní aktivaci při generování katalogu, aktualizaci přehledů, kontrole pokrytí US/TC a DoD. |

---

## 2. Rozpad kroků realizace

### Krok 1: Vytvoření strojové pojistky pro kvalitu asercí (`audit_assertions.py`)
- **Cíl:** Zaručit, že žádný test neobsahuje podmíněné aserce ani slabé asserty pomocí deterministického AST parseru.
- **Soubor:** `.agents/skills/assertion-quality-review/scripts/audit_assertions.py`
- **Chování skriptu:**
  - Prochází soubory v `tests/` pomocí modulu `ast`.
  - Detekuje jakýkoliv uzel `ast.Assert` nebo volání `expect(...)` uvnitř bloku `ast.If` (včetně `elif` a `else`).
  - Hlásí soubor, číslo řádku, typ prohřešku a vypisuje kontext.
  - Vrací exit code `1` při nálezu, `0` při čistém stavu.
- **Napojení do DoD:**
  - V `.agents/skills/tc-to-automated-tests/scripts/verify_automated_tests.py` integrovat AST kontrolu podmíněných asercí do funkce `audit_test_file`.
- **Rozšíření dokumentace v `assertion-quality-review/SKILL.md`:**
  - Přidat instrukce ke spouštění: `python .agents/skills/assertion-quality-review/scripts/audit_assertions.py tests/`.
  - Doplnit tabulku zakázaných vzorů o reálné případy (status kód, cookies, volitelné atributy).

### Krok 2: Zavedení strojové pojistky proti duplicitním a netagovaným testům
- **Cíl:** Zabránit vzniku duplicitních testů a netagovaných ad-hoc souborů při jakémkoliv dalším běhu agenta.
- **Úpravy v `check_done.py`:**
  1. **Kontrola unikátnosti TC (1:1 mapování):**
     - Skript zkontroluje, že každé nalezené TC ID je mapováno na nejvýše jeden automatizovaný test.
     - Pokud je TC ID přiřazeno více než jednou (např. 2 testy se stejným ID), ohlásí chybu a vypíše seznam kolidujících souborů/funkcí.
  2. **Kontrola Zero-Unmapped-Tests (Žádné netagované testy):**
     - Skript ověří, že **každá** funkce `test_*` v celém stromu `tests/` obsahuje validní referenci na schválené TC ID z `manual_tests/TC_*.md`.
     - Jakýkoliv test bez platného TC ID způsobí selhání Definition of Done s chybovou hláškou vyžadující jeho zařazení do specifikace nebo smazání.
- **Úpravy v `verify_automated_tests.py`:**
  - Doplnit kontrolu, že nově verifikovaný test neobsahuje TC ID, které již existuje v jiném existujícím testovacím souboru.
- **Zakotvení pravidel v `AGENTS.md` a `tests/AGENTS.md`:**
  - Do sekce pravidel projektu přidat striktní zákaz tvorby ad-hoc testů bez schváleného TC ID v `manual_tests/` a zákaz duplikování pokrytí stejného TC ve více testech.

### Krok 3: Odstranění 4 podmíněných if asercí v testech
- **Pravidlo skillu:** ZÁKAZ podmínek `if` / `else` kolem assertů. Asserty musí běžet bezpodmínečně.
- **Dotčené soubory a úpravy:**
  1. `tests/auth/test_email_verification.py`:
     - Test `test_tc_us07_02_invalid_tampered_signature_link`.
     - Nahradit podmíněné větvení za striktní assert stavového kódu 403 a přímé `expect` kontroly na chybový text `INVALID SIGNATURE`.
  2. `tests/auth/test_logout.py`:
     - Test `test_tc_us04_02_session_invalidation_and_storage_cleanup`.
     - Nahradit `if session_cookie_after:` za bezpodmínečnou aserci: `assert session_cookie_after is None or session_cookie_after["value"] != session_cookie_before["value"]`.
  3. `tests/portal/test_linktree.py`:
     - Test `test_tc_us01_03_external_links_functionality_and_attributes`.
     - Nahradit `if target_attr == "_blank": expect(...)` za bezpodmínečnou aserci: ověřit, že odkaz buď neotevírá nové okno, nebo má nastavený atribut `rel="noopener noreferrer"`.
- **Validace:** Spuštění nového skriptu `python .agents/skills/assertion-quality-review/scripts/audit_assertions.py tests/` (musí projít bez chyb).

### Krok 4: Přepnutí všech 37 xfail na `strict=True`
- **Cíl:** Zajistit, že pokud aplikace opraví chybu nebo se změní chování (XPASS), test se okamžitě ohlásí jako selhání a nezůstane skrytý.
- **Dotčené soubory (celkem 37 výskytů):**
  - Všech 17 souborů obsahujících `strict=False` (auth, courses, portal, profile, security).
- **Akce:** Hromadné nahrazení `strict=False` za `strict=True`.
- **Validace:** Vyhledání `strict=False` v `tests/` musí vrátit 0 výsledků.

### Krok 5: Úklid duplicitních a netagovaných testů
- **Cíl:** Vyčistit testovací sadu tak, aby odpovídala 100% čistému stavu pravidel 1:1.
- **Konkrétní úklid:**
  1. Smazat historické soubory `tests/courses/test_courses.py` a `tests/courses/test_course_management.py`.
  2. V `tests/auth/test_login.py`: sloučit dva testy pro `TC-US03-04` (`test_tc_us03_04_unified_error_message_prevents_user_enumeration` a `test_tc_us03_04_password_field_security_clearing`) do jednoho reprezentativního testu `test_tc_us03_04_unified_error_and_password_clearing` přesně dle kroků v `TC_US-03_prihlaseni.md`.
  3. V `tests/profile/test_profile.py`: sloučit dva testy pro `TC-US18-02` (`test_tc_us18_02_mandatory_name_validation` a `test_tc_us18_02_email_format_and_empty_email_validation`) do jednoho reprezentativního testu `test_tc_us18_02_name_and_email_validations` přesně dle kroků v `TC_US-18_profil_uzivatele.md`.
  4. Odstranit netagované relikty raných lekcí:
     - `test_register.py` (`test_registration_html5_email_validation`, `test_registration_passwords_are_masked` – již plně kryto v `TC-US02-02` a `TC-US02-04`).
     - `test_navbar.py` (`test_navigation_between_courses_and_login` – již plně kryto v US-01, US-03, US-09).
     - `test_profile.py` (`test_profile_unauthenticated_access_denied`, `test_my_courses_page_display` – již plně kryto v `TC-US04-03` a `TC-US13-01`).

### Krok 6: Úprava popisu (`description`) tří skillů pro autonomní spouštění
- **Cíl:** Přeformulovat pole `description` ve YAML frontmatteru po vzoru `locator-strategy` a `assertion-quality-review`, aby se aktivovaly autonomně při jakékoliv práci s TC, automatizovanými testy nebo přehledy.
- **Dotčené soubory:**
  1. `.agents/skills/ust-to-manual-tc/SKILL.md`:
     - Autonomní spouštění při tvorbě, návrhu, specifikaci nebo analýze manuálních TC a US.
  2. `.agents/skills/tc-to-automated-tests/SKILL.md`:
     - Autonomní spouštění při implementaci, generování, doplňování, refaktoringu a DoD automatizovaných testů.
  3. `.agents/skills/test-overview-generator/SKILL.md`:
     - Autonomní spouštění při tvorbě přehledů, aktualizaci katalogu, kontrole pokrytí US/TC a DoD.

### Krok 7: Aktualizace přehledů, audity a finální verifikace (DoD)
- **Cíl:** Zaktualizovat statistiky a ověřit čistý stav celého projektu.
- **Příkazy:**
  1. Spuštění nového auditu asercí:
     `python .agents/skills/assertion-quality-review/scripts/audit_assertions.py tests`
  2. Audit lokátorů:
     `python .agents/skills/locator-strategy/scripts/audit_locators.py pages tests`
  3. Přegenerování katalogu a HTML reportu pokrytí:
     `python .agents/skills/test-overview-generator/scripts/generate_test_overview.py --html`
  4. Spuštění validačního skriptu Definition of Done (včetně nových kontrol 1:1 a unmapped tests):
     `python .agents/skills/test-overview-generator/scripts/check_done.py`
  5. Kontrolní spuštění pytest testů:
     `pytest`

---

## 3. Akceptační kritéria plánu (Definice hotovo)
- [ ] Skript `audit_assertions.py` existuje, je plně funkční a integrovaný v `verify_automated_tests.py`.
- [ ] Nové strojové pojistky v `check_done.py` (striktní vazba 1:1 a Zero-Unmapped-Tests) jsou implementovány a aktivní.
- [ ] 0 podmíněných `if` asercí v celém adresáři `tests/` (ověřeno přes `audit_assertions.py`).
- [ ] 0 výskytů `strict=False` u `xfail` (všech 37 má `strict=True`).
- [ ] Všechny duplicity a netagované testy odstraněny; každé schválené TC z `manual_tests/` má přesně 1 test.
- [ ] Všechny 3 skilly mají autonomní spouštěcí podmínky ve frontmatteru `description`.
- [ ] `check_done.py` vrací stav `[ HOTOVO ]`, 100% pokrytí schválených manuálních TC (110/110) a 0 varování.
- [ ] Pytest proběhne bez nečekaných selhání (žádný neočekávaný XPASS ani pád).
