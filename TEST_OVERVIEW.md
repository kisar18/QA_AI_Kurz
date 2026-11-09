# Přehled automatizovaných testů (Test Catalog)

> Automaticky vygenerovaný přehled všech testů, kroků a kontrol v projektu.
> Datum vygenerování: **2026-11-09 20:13:20**

## Souhrnná statistika

| Metrika | Hodnota |
| :--- | :--- |
| **Celkem testovacích souborů** | 17 |
| **Celkem automatizovaných testů** | 67 |
| **Celkem akčních kroků** | 252 |
| **Celkem ověření a kontrol** | 234 |
| **Oblasti / moduly** | 6 (`auth, courses, navigation, portal, profile, security`) |

## Rychlá navigace podle oblastí

- [Auth (33 testů)](#oblast-auth)
- [Courses (17 testů)](#oblast-courses)
- [Navigation (1 testů)](#oblast-navigation)
- [Portal (4 testů)](#oblast-portal)
- [Profile (6 testů)](#oblast-profile)
- [Security (6 testů)](#oblast-security)

---

<a id="oblast-auth"></a>
## Oblast: Auth
*Počet testů v oblasti: **33***

### Soubor: `tests/auth/test_email_verification.py`
#### `TestEmailVerification` -> `test_unauthenticated_verification_notification_rejected` (řádek 10)

**Popis:** Ověření, že neautentizovaný požadavek na zaslání ověřovacího odkazu je zamítnut (401).

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `response = page.request.post(f'{BASE_URL}/email/verification-notification', headers={'Accept': 'application/json'})` – *Získání hodnoty/stavu z aplikace*
2. 🔍 **Kontrola:** `assert response.status == 401`
3. ⚙️ **Krok:** `data = response.json()` – *Příprava testovacích dat*
4. 🔍 **Kontrola:** `assert data.get('message') == 'Unauthenticated.'`

#### `TestEmailVerification` -> `test_invalid_or_tampered_verification_link_rejected` (řádek 20)

**Popis:** Ověření, že neplatný nebo podvržený ověřovací odkaz není akceptován jako platné ověření.

**Souhrn:** `1` akcí, `1` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `response = page.request.get(f'{BASE_URL}/verify-email/99999/invalidhash?expires=1234567890&signature=tampered_signature', headers={'Accept': 'application/json'})` – *Získání hodnoty/stavu z aplikace*
2. 🔍 **Kontrola:** `assert response.status in (401, 403)`

#### `TestEmailVerification` -> `test_authenticated_user_verification_endpoint_available` (řádek 29)

**Popis:** Ověření, že přihlášený uživatel má přístup k endpointu pro znovuzaslání ověření.

**Souhrn:** `5` akcí, `1` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `login_page = LoginPage(page)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `login_page.navigate()`
3. ⚙️ **Krok:** `login_page.login(registered_user['email'], registered_user['password'])`
4. ⚙️ **Krok:** `page.wait_for_url('**/courses')`
5. ⚙️ **Krok:** `res = page.evaluate("async () => {\n            const xsrf = decodeURIComponent(\n                document.cookie.split('; ')\n                    .find(row => row.startsWith('XSRF-TOKEN='))\n                    ?.split('=')[1] || ''\n            );\n            const resp = await fetch('/email/verification-notification', {\n                method: 'POST',\n                headers: {\n                    'Accept': 'application/json',\n                    'X-XSRF-TOKEN': xsrf\n                }\n            });\n            return resp.status;\n        }")` – *Získání hodnoty/stavu z aplikace*
6. 🔍 **Kontrola:** `assert res in (200, 202, 204, 302, 429, 500)`

### Soubor: `tests/auth/test_forgot_password.py`
#### `TestForgotPassword` -> `test_form_elements_are_visible` (řádek 19)

**Popis:** Ověří, že formulář pro obnovu hesla obsahuje vstupní pole pro e-mail
a tlačítko pro odeslání žádosti.

**Souhrn:** `0` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. 🔍 **Kontrola:** `expect(self.forgot_page.email_input).to_be_visible()`
2. 🔍 **Kontrola:** `expect(self.forgot_page.submit_button).to_be_visible()`

#### `TestForgotPassword` -> `test_invalid_email_format_prevented` (řádek 28)

**Popis:** Ověří, že prohlížečová HTML5 validace zabrání odeslání formuláře
při zadání řetězce bez znaku '@' (neplatný e-mail z data/invalid_emails.json).

**Souhrn:** `3` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `invalid_sample = invalid_emails[0]` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `self.forgot_page.email_input.fill(invalid_sample)`
3. ⚙️ **Krok:** `self.forgot_page.submit_button.click()`
4. 🔍 **Kontrola:** `expect(self.page).to_have_url(self.forgot_page.url)`
5. 🔍 **Kontrola:** `expect(self.forgot_page.email_input).to_have_value(invalid_sample)`

#### `TestForgotPassword` -> `test_submit_valid_email_shows_feedback` (řádek 44)

**Popis:** Ověří, že odeslání formuláře s platným registrovaným e-mailem zobrazí potvrzovací zprávu (US-05).

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `page.route('**/forgot-password', lambda route: route.fulfill(status=200, content_type='application/json', json={'status': 'Odkaz na obnovení hesla byl odeslán.'}))`
2. ⚙️ **Krok:** `self.forgot_page.request_password_reset(registered_user['email'])`
3. 🔍 **Kontrola:** `expect(self.forgot_page.status_message).to_be_visible()`
4. 🔍 **Kontrola:** `expect(self.forgot_page.status_message).to_contain_text('Odkaz na obnovení hesla')`

#### `TestForgotPassword` -> `test_non_existent_email_shows_user_not_found_message` (řádek 64)

**Popis:** Ověří, že zadání neexistujícího e-mailu zobrazí chybovou hlášku (US-05).

**Souhrn:** `2` akcí, `1` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.forgot_page.request_password_reset('non_existent_user_99999@example.com')`
2. ⚙️ **Krok:** `self.page.wait_for_timeout(1000)`
3. 🔍 **Kontrola:** `expect(self.forgot_page.user_not_found_message).to_be_visible()`

### Soubor: `tests/auth/test_login.py`
#### `TestDemoLogin` -> `test_navigate_from_courses_to_login` (řádek 16)

**Popis:** Ověření prokliku z hlavní stránky kurzů do formuláře přihlášení.

**Souhrn:** `1` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate_via_courses()`
2. 🔍 **Kontrola:** Ověřeno přesměrování na URL /login
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/login')`
3. 🔍 **Kontrola:** Ověřena viditelnost nadpisu formuláře
   - Technicky: `expect(self.login_page.login_title).to_be_visible()`
4. 🔍 **Kontrola:** Ověřen text nadpisu 'Přihlášení'
   - Technicky: `expect(self.login_page.login_title).to_have_text('Přihlášení')`

#### `TestDemoLogin` -> `test_login_form_elements_presence` (řádek 29)

**Popis:** Ověření přítomnosti a viditelnosti všech klíčových prvků formuláře.

**Souhrn:** `1` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. 🔍 **Kontrola:** Ověřeno pole pro zadání e-mailu
   - Technicky: `expect(self.login_page.email_input).to_be_visible()`
3. 🔍 **Kontrola:** Ověřeno pole pro zadání hesla
   - Technicky: `expect(self.login_page.password_input).to_be_visible()`
4. 🔍 **Kontrola:** Ověřeno tlačítko pro přihlášení
   - Technicky: `expect(self.login_page.login_button).to_be_visible()`
5. 🔍 **Kontrola:** Ověřen odkaz 'Zapomněli jste heslo?'
   - Technicky: `expect(self.login_page.forgot_password_link).to_be_visible()`
6. 🔍 **Kontrola:** Ověřen odkaz na registraci
   - Technicky: `expect(self.login_page.register_link).to_be_visible()`

#### `TestDemoLogin` -> `test_successful_login_and_logout` (řádek 48)

**Popis:** Ověření úspěšného přihlášení s platným účtem a následného odhlášení.

**Souhrn:** `3` akcí, `7` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.login(registered_user['email'], registered_user['password'])`
3. 🔍 **Kontrola:** Ověřeno přesměrování na stránku kurzů (/courses)
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/courses')`
4. 🔍 **Kontrola:** Ověřeno úspěšné přihlášení uživatele ({registered_user['email']}) – v menu je viditelné tlačítko 'Odhlásit se'
   - Technicky: `expect(self.login_page.logout_button).to_be_visible()`
5. 🔍 **Kontrola:** Ověřeno, že v menu je viditelný odkaz na 'Můj Profil'
   - Technicky: `expect(self.login_page.profile_link).to_be_visible()`
6. 🔍 **Kontrola:** Ověřeno, že odkaz 'Přihlásit se' již v menu NENÍ zobrazen
   - Technicky: `expect(self.login_page.nav_login_link).not_to_be_visible()`
7. ⚙️ **Krok:** `self.login_page.logout()`
8. 🔍 **Kontrola:** Ověřeno úspěšné odhlášení uživatele – v menu se znovu objevil odkaz 'Přihlásit se'
   - Technicky: `expect(self.login_page.nav_login_link).to_be_visible()`
9. 🔍 **Kontrola:** Ověřeno, že tlačítko 'Odhlásit se' po odhlášení zmizelo
   - Technicky: `expect(self.login_page.logout_button).not_to_be_visible()`
10. 🔍 **Kontrola:** Ověřeno, že odkaz 'Můj Profil' po odhlášení zmizel
   - Technicky: `expect(self.login_page.profile_link).not_to_be_visible()`

#### `TestDemoLogin` -> `test_html5_validation_on_invalid_email_format` (řádek 78)

**Popis:** Ověření nativní HTML5 validace pro neplatný formát e-mailu (formulář se neodešle).

**Souhrn:** `3` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.login(invalid_emails[0], 'TajneHeslo123')`
3. ⚙️ **Krok:** `validation_message = self.login_page.email_input.evaluate('el => el.validationMessage')` – *Příprava testovacích dat*
4. 🔍 **Kontrola:** Ověřeno spuštění HTML5 validace pro neplatný formát e-mailu
   - Technicky: `assert len(validation_message) > 0`
5. 🔍 **Kontrola:** Ověřeno, že stránka zůstala na /login a formulář se neodeslal
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/login')`
6. 🔍 **Kontrola:** Ověřeno, že se nezobrazila serverová chyba
   - Technicky: `expect(self.login_page.error_message).not_to_be_visible()`
7. 🔍 **Kontrola:** Ověřeno, že tlačítko 'Přihlásit' zůstává připraveno k odeslání
   - Technicky: `expect(self.login_page.login_button).to_be_visible()`

#### `TestDemoLogin` -> `test_login_with_invalid_credentials` (řádek 96)

**Popis:** Ověření zobrazení chybové hlášky při zadání neexistujícího uživatele.

**Souhrn:** `2` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.login('neplatny_uzivatel@example.com', 'SpatneHeslo123')`
3. 🔍 **Kontrola:** Ověřena viditelnost chybové hlášky
   - Technicky: `expect(self.login_page.error_message).to_be_visible()`
4. 🔍 **Kontrola:** Ověřen text chybové hlášky 'These credentials do not match our records.'
   - Technicky: `expect(self.login_page.error_message).to_contain_text('These credentials do not match our records.')`
5. 🔍 **Kontrola:** Ověřeno, že uživatel zůstal na stránce /login
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/login')`
6. 🔍 **Kontrola:** Ověřeno, že v navigaci stále svítí 'Přihlásit se'
   - Technicky: `expect(self.login_page.nav_login_link).to_be_visible()`
7. 🔍 **Kontrola:** Ověřeno, že v navigaci NENÍ 'Odhlásit se'
   - Technicky: `expect(self.login_page.logout_button).not_to_be_visible()`

#### `TestDemoLogin` -> `test_login_invalid_credentials_matrix` (řádek 125) `[parametrize('email, password', [('test.user@domena.cz', 'wrong_password_xyz'), ('admin@unknown.test', '123456'), ('jan.novak@seznam.cz', 'spatneHeslo')], ids=['wrong_password', 'unknown_admin', 'czech_domain_user'])]`

**Popis:** Parametrizovaný test pro různé kombinace neexistujících/neplatných přihlašovacích údajů.

**Souhrn:** `2` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.login(email, password)`
3. 🔍 **Kontrola:** Ověřena chybová hláška pro e-mail: {email}
   - Technicky: `expect(self.login_page.error_message).to_be_visible()`
4. 🔍 **Kontrola:** Ověřeno, že text chybové hlášky není prázdný
   - Technicky: `assert len(self.login_page.get_error_message()) > 0`
5. 🔍 **Kontrola:** Ověřeno zachování URL /login
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/login')`
6. 🔍 **Kontrola:** Ověřeno, že uživatel nebyl přihlášen
   - Technicky: `expect(self.login_page.logout_button).not_to_be_visible()`

#### `TestDemoLogin` -> `test_password_field_is_masked` (řádek 142)

**Popis:** Ověření, že pole pro heslo má type='password' (maskovaný vstup).

**Souhrn:** `1` akcí, `1` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. 🔍 **Kontrola:** Ověřen atribut type='password' u pole pro heslo
   - Technicky: `expect(self.login_page.password_input).to_have_attribute('type', 'password')`

#### `TestDemoLogin` -> `test_forgot_password_link` (řádek 149)

**Popis:** Ověření funkčnosti odkazu 'Zapomněli jste heslo?'.

**Souhrn:** `3` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.forgot_password_link.click()`
3. 🔍 **Kontrola:** Ověřeno přesměrování na /forgot-password
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/forgot-password')`
4. ⚙️ **Krok:** `forgot_page = ForgotPasswordPage(page)` – *Příprava testovacích dat*
5. 🔍 **Kontrola:** Ověřena přítomnost pole pro zadání resetovacího e-mailu
   - Technicky: `expect(forgot_page.email_input).to_be_visible()`
6. 🔍 **Kontrola:** Ověřena přítomnost odesílacího tlačítka
   - Technicky: `expect(forgot_page.submit_button).to_be_visible()`

#### `TestDemoLogin` -> `test_register_link` (řádek 164)

**Popis:** Ověření funkčnosti odkazu na registraci.

**Souhrn:** `3` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.register_link.click()`
3. 🔍 **Kontrola:** Ověřeno přesměrování na /register
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/register')`
4. ⚙️ **Krok:** `register_page = RegisterPage(page)` – *Příprava testovacích dat*
5. 🔍 **Kontrola:** Ověřeno pole pro jméno na stránce registrace
   - Technicky: `expect(register_page.name_input).to_be_visible()`
6. 🔍 **Kontrola:** Ověřeno tlačítko 'Registrovat'
   - Technicky: `expect(register_page.register_button).to_be_visible()`

#### `TestDemoLogin` -> `test_login_case_insensitive_email` (řádek 179)

**Popis:** Ověření, že zadání e-mailu s velkými písmeny je platné a přihlásí uživatele (US-03).

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.login(registered_user['email'].upper(), registered_user['password'])`
3. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.login_page.base_url}/courses')`
4. 🔍 **Kontrola:** Ověřeno úspěšné přihlášení s verzí e-mailu velkými písmeny: {registered_user['email'].upper()}
   - Technicky: `expect(self.login_page.logout_button).to_be_visible()`

#### `TestDemoLogin` -> `test_login_email_whitespace_trimmed` (řádek 188)

**Popis:** Ověření, že systém automaticky ořízne mezery před a za e-mailovou adresou (US-03).

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.login(f"   {registered_user['email']}   ", registered_user['password'])`
3. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.login_page.base_url}/courses')`
4. 🔍 **Kontrola:** Ověřeno úspěšné přihlášení s e-mailem obsahujícím počáteční a koncové mezery
   - Technicky: `expect(self.login_page.logout_button).to_be_visible()`

#### `TestDemoLogin` -> `test_login_submission_via_enter_key` (řádek 197)

**Popis:** Ověření přístupnosti: formulář přihlášení lze odeslat stiskem klávesy Enter (US-03).

**Souhrn:** `4` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.email_input.fill(registered_user['email'])`
3. ⚙️ **Krok:** `self.login_page.password_input.fill(registered_user['password'])`
4. ⚙️ **Krok:** `self.login_page.password_input.press('Enter')`
5. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.login_page.base_url}/courses')`
6. 🔍 **Kontrola:** Ověřeno úspěšné odeslání přihlašovacího formuláře klávesou Enter z pole hesla
   - Technicky: `expect(self.login_page.logout_button).to_be_visible()`

### Soubor: `tests/auth/test_logout.py`
#### `TestDemoLogout` -> `test_user_can_logout_successfully` (řádek 11)

**Popis:** Ověření, že přihlášený uživatel se může úspěšně odhlásit přes navbar.

**Souhrn:** `5` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `login_page = LoginPage(page)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `navbar = Navbar(page)` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `login_page.navigate()`
4. ⚙️ **Krok:** `login_page.login(registered_user['email'], registered_user['password'])`
5. 🔍 **Kontrola:** Uživatel je přihlášen – tlačítko Odhlásit se je viditelné
   - Technicky: `expect(navbar.logout_button).to_be_visible()`
6. ⚙️ **Krok:** `navbar.logout()`
7. 🔍 **Kontrola:** `expect(navbar.login_link).to_be_visible()`
8. 🔍 **Kontrola:** Uživatel byl úspěšně odhlášen – odkaz Přihlásit se je znovu zobrazen
   - Technicky: `expect(navbar.logout_button).not_to_be_visible()`

### Soubor: `tests/auth/test_rate_limiting.py`
#### `TestRateLimiting` -> `test_brute_force_login_triggers_rate_limiting` (řádek 11)

**Popis:** Ověření, že po 5 po sobě jdoucích neúspěšných pokusech systém dočasně zablokuje další přihlášení (US-08).

**Souhrn:** `7` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `login_page = LoginPage(page)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `login_page.navigate()`
3. ⚙️ **Krok:** `probe_email = generate_random_email('probe_rate_limit')` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `wrong_password = 'InvalidPassword999!'` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
6. ⚙️ **Krok:** `login_page.login_with_response(probe_email, wrong_password)`
7. 🔍 **Kontrola:** `expect(login_page.error_message).to_be_visible()`
8. 🔍 **Kontrola:** Pokus {attempt}/5: Zobrazena standardní chybová hláška o neplatných údajích
   - Technicky: `expect(login_page.error_message).to_contain_text('These credentials do not match our records.')`
9. ⚙️ **Krok:** `login_page.login_with_response(probe_email, wrong_password)`
10. 🔍 **Kontrola:** `expect(login_page.error_message).to_be_visible()`
11. 🔍 **Kontrola:** Pokus 6: Úspěšně zachycena blokace – zobrazena hláška 'Too many login attempts'
   - Technicky: `expect(login_page.error_message).to_contain_text('Too many login attempts')`

### Soubor: `tests/auth/test_register.py`
#### `TestDemoRegister` -> `test_register_form_elements_presence` (řádek 16)

**Popis:** Ověření přítomnosti prvků formuláře registrace.

**Souhrn:** `1` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. 🔍 **Kontrola:** Ověřeno pole pro jméno
   - Technicky: `expect(self.register_page.name_input).to_be_visible()`
3. 🔍 **Kontrola:** Ověřeno pole pro e-mail
   - Technicky: `expect(self.register_page.email_input).to_be_visible()`
4. 🔍 **Kontrola:** Ověřeno pole pro heslo
   - Technicky: `expect(self.register_page.password_input).to_be_visible()`
5. 🔍 **Kontrola:** Ověřeno pole pro potvrzení hesla
   - Technicky: `expect(self.register_page.password_again_input).to_be_visible()`
6. 🔍 **Kontrola:** Ověřeno tlačítko 'Registrovat'
   - Technicky: `expect(self.register_page.register_button).to_be_visible()`

#### `TestDemoRegister` -> `test_successful_registration` (řádek 35)

**Popis:** Ověření úspěšné registrace nového uživatele.

**Souhrn:** `7` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `unique_id = uuid.uuid4().hex[:8]` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `name = f'User {unique_id}'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `email = f'test_reg_{unique_id}@example.com'` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `password = 'Password123!'` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `self.register_page.navigate()`
6. ⚙️ **Krok:** `self.register_page.register(name, email, password, password)`
7. 🔍 **Kontrola:** Ověřeno přesměrování po registraci na /home
   - Technicky: `expect(page).to_have_url(f'{self.register_page.base_url}/home')`
8. ⚙️ **Krok:** `home_page = HomePage(page)` – *Příprava testovacích dat*
9. 🔍 **Kontrola:** Ověřena uvítací zpráva pro uživatele {name}
   - Technicky: `expect(home_page.welcome_section).to_contain_text(f'Vítej uživateli {name}!')`

#### `TestDemoRegister` -> `test_registration_password_mismatch` (řádek 52)

**Popis:** Ověření zobrazení chyby při zadání neshodných hesel.

**Souhrn:** `2` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. ⚙️ **Krok:** `self.register_page.register(name='Mismatch User', email='mismatch_user@example.com', password='Password123!', password_again='DifferentPassword456!')`
3. 🔍 **Kontrola:** Ověřeno, že stránka zůstala na /register
   - Technicky: `expect(page).to_have_url(f'{self.register_page.base_url}/register')`
4. 🔍 **Kontrola:** `expect(self.register_page.password_error).to_be_visible()`
5. 🔍 **Kontrola:** Ověřena chybová hláška 'The password field confirmation does not match.'
   - Technicky: `expect(self.register_page.password_error).to_contain_text('The password field confirmation does not match.')`

#### `TestDemoRegister` -> `test_registration_duplicate_email` (řádek 69)

**Popis:** Ověření chybové hlášky při pokusu o registraci s již obsazeným e-mailem.

**Souhrn:** `2` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. ⚙️ **Krok:** `self.register_page.register(name='Duplicate Tester', email=registered_user['email'], password='Password123!', password_again='Password123!')`
3. 🔍 **Kontrola:** Ověřeno, že registrace nebyla dokončena a zůstává na /register
   - Technicky: `expect(page).to_have_url(f'{self.register_page.base_url}/register')`
4. 🔍 **Kontrola:** `expect(self.register_page.email_error).to_be_visible()`
5. 🔍 **Kontrola:** Ověřena chybová hláška 'The email has already been taken.'
   - Technicky: `expect(self.register_page.email_error).to_contain_text('The email has already been taken.')`

#### `TestDemoRegister` -> `test_registration_html5_email_validation` (řádek 86)

**Popis:** Ověření HTML5 validace při zadání neplatného formátu e-mailu (z data/invalid_emails.json).

**Souhrn:** `3` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. ⚙️ **Krok:** `self.register_page.register(name='Valid Name', email=invalid_emails[0], password='Password123!', password_again='Password123!')`
3. ⚙️ **Krok:** `validation_message = self.register_page.email_input.evaluate('el => el.validationMessage')` – *Příprava testovacích dat*
4. 🔍 **Kontrola:** Ověřeno spuštění nativní HTML5 validace e-mailu
   - Technicky: `assert len(validation_message) > 0`
5. 🔍 **Kontrola:** Ověřeno, že formulář se neodeslal
   - Technicky: `expect(page).to_have_url(f'{self.register_page.base_url}/register')`

#### `TestDemoRegister` -> `test_registration_passwords_are_masked` (řádek 103)

**Popis:** Ověření, že obě pole pro heslo mají atribut type='password'.

**Souhrn:** `1` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. 🔍 **Kontrola:** Ověřen atribut type='password' u prvního pole pro heslo
   - Technicky: `expect(self.register_page.password_input).to_have_attribute('type', 'password')`
3. 🔍 **Kontrola:** Ověřen atribut type='password' u potvrzovacího pole pro heslo
   - Technicky: `expect(self.register_page.password_again_input).to_have_attribute('type', 'password')`

#### `TestDemoRegister` -> `test_registration_empty_form_validation` (řádek 113)

**Popis:** Ověření zobrazení chybových hlášek pro povinná pole při odeslání prázdného formuláře.

**Souhrn:** `2` akcí, `7` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. ⚙️ **Krok:** `self.register_page.register_button.click()`
3. 🔍 **Kontrola:** Ověřeno, že prázdný formulář se neodeslal a stránka zůstává na /register
   - Technicky: `expect(page).to_have_url(f'{self.register_page.base_url}/register')`
4. 🔍 **Kontrola:** `expect(self.register_page.name_error).to_be_visible()`
5. 🔍 **Kontrola:** Ověřena chybová hláška pro povinné jméno: 'The name field is required.'
   - Technicky: `expect(self.register_page.name_error).to_contain_text('The name field is required.')`
6. 🔍 **Kontrola:** `expect(self.register_page.email_error).to_be_visible()`
7. 🔍 **Kontrola:** Ověřena chybová hláška pro povinný e-mail: 'The email field is required.'
   - Technicky: `expect(self.register_page.email_error).to_contain_text('The email field is required.')`
8. 🔍 **Kontrola:** `expect(self.register_page.password_error).to_be_visible()`
9. 🔍 **Kontrola:** Ověřena chybová hláška pro povinné heslo: 'The password field is required.'
   - Technicky: `expect(self.register_page.password_error).to_contain_text('The password field is required.')`

#### `TestDemoRegister` -> `test_registration_duplicate_email_case_insensitive` (řádek 133)

**Popis:** Ověření, že kontrola unikátnosti e-mailu je case-insensitive (US-02).

**Souhrn:** `2` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. ⚙️ **Krok:** `self.register_page.register(name='Upper Case Tester', email=registered_user['email'].upper(), password='Password123!', password_again='Password123!')`
3. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.register_page.base_url}/register')`
4. 🔍 **Kontrola:** `expect(self.register_page.email_error).to_be_visible()`
5. 🔍 **Kontrola:** Ověřeno zamítnutí duplicitní registrace i při zadání e-mailu velkými písmeny
   - Technicky: `expect(self.register_page.email_error).to_contain_text('The email has already been taken.')`

#### `TestDemoRegister` -> `test_registration_email_whitespace_trimmed` (řádek 148)

**Popis:** Ověření, že zadaný e-mail je před registrací normalizován ořezáním mezer (US-02).

**Souhrn:** `4` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `email = generate_random_email('qa_trim')` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `name = f'Trim Tester {generate_random_string(4)}'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `self.register_page.navigate()`
4. ⚙️ **Krok:** `self.register_page.register(name=name, email=f'   {email}   ', password='Password123!', password_again='Password123!')`
5. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.register_page.base_url}/home')`
6. 🔍 **Kontrola:** Ověřena úspěšná registrace uživatele se zadaným e-mailem obsahujícím okrajové mezery
   - Technicky: `expect(self.register_page.navbar.logout_button).to_be_visible()`

### Soubor: `tests/auth/test_reset_password.py`
#### `TestResetPassword` -> `test_reset_password_form_elements_present` (řádek 9)

**Popis:** Ověření, že stránka pro reset hesla obsahuje všechny formulářové prvky.

**Souhrn:** `2` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `reset_page = ResetPasswordPage(page)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `reset_page.open_with_token(token='sample-test-token', email='test@example.com')`
3. 🔍 **Kontrola:** `expect(reset_page.section).to_be_visible()`
4. 🔍 **Kontrola:** `expect(reset_page.password_input).to_be_visible()`
5. 🔍 **Kontrola:** `expect(reset_page.password_again_input).to_be_visible()`
6. 🔍 **Kontrola:** `expect(reset_page.submit_button).to_be_visible()`
7. 🔍 **Kontrola:** `expect(reset_page.submit_button).to_have_text('Změnit heslo')`

#### `TestResetPassword` -> `test_reset_password_passwords_mismatch` (řádek 20)

**Popis:** Ověření zobrazení validační chyby při zadání neshodujících se hesel.

**Souhrn:** `3` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `reset_page = ResetPasswordPage(page)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `reset_page.open_with_token(token='sample-test-token', email='test@example.com')`
3. ⚙️ **Krok:** `reset_page.reset_password('Secret123!', 'Different123!')`
4. 🔍 **Kontrola:** `expect(reset_page.password_error).to_be_visible()`
5. 🔍 **Kontrola:** `expect(reset_page.password_error).to_contain_text('password field confirmation does not match')`

#### `TestResetPassword` -> `test_reset_password_invalid_token_rejected` (řádek 30)

**Popis:** Ověření odmítnutí neplatného tokenu pro existujícího uživatele.

**Souhrn:** `6` akcí, `1` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `reset_page = ResetPasswordPage(page)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `reset_page.open_with_token(token='invalid-expired-token', email=registered_user['email'])`
3. ⚙️ **Krok:** `with:` – *Řídicí blok (with)*
4. ⚙️ **Krok:** `reset_page.reset_password('NewPassword123!', 'NewPassword123!')`
5. ⚙️ **Krok:** `resp = response_info.value` – *Příprava testovacích dat*
6. ⚙️ **Krok:** `body = resp.json()` – *Příprava testovacích dat*
7. 🔍 **Kontrola:** `assert 'password reset token is invalid' in body.get('message', '').lower() or any(('invalid' in err.lower() for err_list in body.get('errors', {}).values() for err in err_list))`

---

<a id="oblast-courses"></a>
## Oblast: Courses
*Počet testů v oblasti: **17***

### Soubor: `tests/courses/test_course_iterations.py`
#### `TestCourseIterations` -> `test_lector_can_create_new_iteration` (řádek 26)

**Popis:** [US-15] Ověření vytvoření nového termínu (běhu) kurzu lektorem.

**Souhrn:** `4` akcí, `7` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, lector_user)`
2. ⚙️ **Krok:** `self.iteration_create_page.open_for_course(1)`
3. 🔍 **Kontrola:** `expect(self.iteration_create_page.container).to_be_visible()`
4. 🔍 **Kontrola:** `expect(self.iteration_create_page.start_input).to_be_visible()`
5. 🔍 **Kontrola:** `expect(self.iteration_create_page.end_input).to_be_visible()`
6. 🔍 **Kontrola:** `expect(self.iteration_create_page.day_select).to_be_visible()`
7. 🔍 **Kontrola:** `expect(self.iteration_create_page.time_input).to_be_visible()`
8. 🔍 **Kontrola:** Ověřeny všechny formulářové prvky pro vypsání nového běhu kurzu
   - Technicky: `expect(self.iteration_create_page.location_input).to_be_visible()`
9. ⚙️ **Krok:** `self.iteration_create_page.fill_and_submit(start_date='2026-11-01', end_date='2026-12-01', day_of_week='Pondělí', time_str='18:00', location='Praha - Školicí centrum / Online')`
10. ⚙️ **Krok:** `page.wait_for_url(re.compile('.*/courses/1$'))`
11. 🔍 **Kontrola:** Ověřeno úspěšné vypsání termínu a přesměrování na detail kurzu
   - Technicky: `expect(self.courses_page.course_detail).to_be_visible()`

#### `TestCourseIterations` -> `test_lector_can_view_participants_list` (řádek 55)

**Popis:** [US-16] Ověření, že lektor má přístup k seznamu účastníků běhu kurzu.

**Souhrn:** `7` akcí, `7` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, lector_user)`
2. ⚙️ **Krok:** `self.courses_page.navigate('/courses/1')`
3. 🔍 **Kontrola:** `expect(self.courses_page.course_detail).to_be_visible()`
4. ⚙️ **Krok:** `participants_button = self.courses_page.participants_buttons.first` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `if participants_button.count() > 0 and participants_button.is_visible():` – *Řídicí blok (if)*
6. ⚙️ **Krok:** `participants_button.click()`
7. ⚙️ **Krok:** `page.wait_for_url(re.compile('.*/courses/\\d+/participants'))`
8. 🔍 **Kontrola:** `expect(self.students_page.heading).to_be_visible()`
9. 🔍 **Kontrola:** `expect(self.students_page.heading).to_have_text('Seznam přihlášených')`
10. 🔍 **Kontrola:** Ověřeno zobrazení tabulky přihlášených účastníků pro roli lektora
   - Technicky: `expect(self.students_page.participants_table).to_be_visible()`
11. ⚙️ **Krok:** `self.students_page.open_for_iteration(1)`
12. 🔍 **Kontrola:** `expect(self.students_page.heading).to_be_visible()`
13. 🔍 **Kontrola:** `expect(self.students_page.heading).to_have_text('Seznam přihlášených')`
14. 🔍 **Kontrola:** Ověřeno zobrazení tabulky účastníků na /courses/:id/participants
   - Technicky: `expect(self.students_page.participants_table).to_be_visible()`

#### `TestCourseIterations` -> `test_student_cannot_access_participants_management` (řádek 80)

**Popis:** [US-16] Ověření, že běžný zákazník/student nemá přístup k lektorskému seznamu účastníků.

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.courses_page.navigate('/courses/1')`
3. 🔍 **Kontrola:** `expect(self.courses_page.course_detail).to_be_visible()`
4. 🔍 **Kontrola:** Ověřeno, že tlačítko 'Přihlášení' (seznam účastníků) není studentovi nabízeno
   - Technicky: `expect(self.courses_page.participants_buttons).not_to_be_visible()`

### Soubor: `tests/courses/test_course_management.py`
#### `TestCourseManagement` -> `test_course_create_form_elements_presence` (řádek 23)

**Popis:** Ověření zobrazení formuláře pro vytvoření kurzu a jeho polí (pod účtem lektora).

**Souhrn:** `2` akcí, `7` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, lector_user)`
2. ⚙️ **Krok:** `self.course_create_page.navigate()`
3. 🔍 **Kontrola:** Ověřena URL /courses/create
   - Technicky: `expect(page).to_have_url(self.course_create_page.url)`
4. 🔍 **Kontrola:** Ověřen nadpis 'Vytvořit kurz'
   - Technicky: `expect(self.course_create_page.heading).to_be_visible()`
5. 🔍 **Kontrola:** Ověřeno pole pro název kurzu
   - Technicky: `expect(self.course_create_page.name_input).to_be_visible()`
6. 🔍 **Kontrola:** Ověřeno pole pro popis kurzu
   - Technicky: `expect(self.course_create_page.description_input).to_be_visible()`
7. 🔍 **Kontrola:** Ověřeno pole pro kapacitu
   - Technicky: `expect(self.course_create_page.capacity_input).to_be_visible()`
8. 🔍 **Kontrola:** Ověřeno pole pro cenu
   - Technicky: `expect(self.course_create_page.price_input).to_be_visible()`
9. 🔍 **Kontrola:** Ověřeno tlačítko 'Vytvořit kurz'
   - Technicky: `expect(self.course_create_page.submit_button).to_be_visible()`

#### `TestCourseManagement` -> `test_course_create_submission_flow` (řádek 49)

**Popis:** Ověření vyplnění a odeslání formuláře nového kurzu lektorem s přesměrováním do přehledu.

**Souhrn:** `5` akcí, `1` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, lector_user)`
2. ⚙️ **Krok:** `self.course_create_page.navigate()`
3. ⚙️ **Krok:** `course_name = 'Automatizovaný QA Kurz'` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `description = 'Testovací popis pro ověření odeslání kurzu'` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `self.course_create_page.create_course(name=course_name, description=description, capacity=12, price=1990)`
6. 🔍 **Kontrola:** Ověřeno úspěšné odeslání formuláře a přesměrování na přehled kurzů (/courses/)
   - Technicky: `expect(page).to_have_url(f'{self.course_create_page.base_url}/courses/')`

#### `TestCourseManagement` -> `test_course_create_image_aspect_ratio_validation` (řádek 67)

**Popis:** [US-14] Ověření validace poměru stran náhledového obrázku kurzu (požadován 16:9 s tolerancí 5 %).

**Souhrn:** `11` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `invalid_img = create_png_image(tmp_path / 'test_1_1.png', width=100, height=100)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `valid_img = create_png_image(tmp_path / 'test_16_9.png', width=160, height=90)` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `self._login(page, lector_user)`
4. ⚙️ **Krok:** `self.course_create_page.navigate()`
5. ⚙️ **Krok:** `alert_messages = []` – *Příprava testovacích dat*
6. ⚙️ **Krok:** `page.on('dialog', handle_dialog)`
7. ⚙️ **Krok:** `self.course_create_page.image_input.set_input_files(str(invalid_img.resolve()))`
8. ⚙️ **Krok:** `page.wait_for_timeout(1000)`
9. 🔍 **Kontrola:** Očekávané chybové hlášení v alertu se nezobrazilo: {alert_messages}
   - Technicky: `assert any(('správný poměr stran' in msg for msg in alert_messages))`
10. 🔍 **Kontrola:** Input souboru měl být po neplatném poměru stran vymazán
   - Technicky: `assert self.course_create_page.image_input.input_value() == ''`
11. 🔍 **Kontrola:** Ověřeno zamítnutí obrázku s neplatným poměrem stran (1:1) a zobrazení varovného alertu
   - Technicky: `step('Ověřeno zamítnutí obrázku s neplatným poměrem stran (1:1) a zobrazení varovného alertu')`
12. ⚙️ **Krok:** `alert_messages.clear()`
13. ⚙️ **Krok:** `self.course_create_page.image_input.set_input_files(str(valid_img.resolve()))`
14. ⚙️ **Krok:** `page.wait_for_timeout(1000)`
15. 🔍 **Kontrola:** Pro platný poměr stran 16:9 se neměl zobrazit žádný alert: {alert_messages}
   - Technicky: `assert len(alert_messages) == 0`
16. 🔍 **Kontrola:** Platný obrázek 16:9 měl zůstat v inputu nastaven
   - Technicky: `assert self.course_create_page.image_input.input_value() != ''`
17. 🔍 **Kontrola:** Ověřeno úspěšné přijetí obrázku s poměrem stran 16:9
   - Technicky: `step('Ověřeno úspěšné přijetí obrázku s poměrem stran 16:9')`

### Soubor: `tests/courses/test_courses.py`
#### `TestCoursesCatalog` -> `test_courses_catalog_display` (řádek 17)

**Popis:** [US-09] Ověření správného načtení katalogu kurzů.

**Souhrn:** `2` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. 🔍 **Kontrola:** Ověřena URL /courses
   - Technicky: `expect(page).to_have_url(self.courses_page.url)`
3. 🔍 **Kontrola:** Ověřen nadpis katalogu kurzů
   - Technicky: `expect(self.courses_page.title).to_be_visible()`
4. 🔍 **Kontrola:** Ověřena hlavní sekce s kurzy
   - Technicky: `expect(self.courses_page.courses_section).to_be_visible()`
5. ⚙️ **Krok:** `course_count = self.courses_page.course_names.count()` – *Získání hodnoty/stavu z aplikace*
6. 🔍 **Kontrola:** Očekáván alespoň 1 kurz, nalezeno: {course_count}
   - Technicky: `assert course_count > 0`
7. 🔍 **Kontrola:** Ověřeno úspěšné načtení kurzů z backendu (nalezeno kurzů: {course_count})
   - Technicky: `step(f'Ověřeno úspěšné načtení kurzů z backendu (nalezeno kurzů: {course_count})')`

#### `TestCoursesCatalog` -> `test_course_card_elements_presence` (řádek 34)

**Popis:** [US-09] Ověření přítomnosti klíčových informací na kartě kurzu: název, popis, cena zaokrouhlená na celé Kč, kapacita a obrázek.

**Souhrn:** `8` akcí, `11` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. ⚙️ **Krok:** `first_name = self.courses_page.course_names.first` – *Příprava testovacích dat*
3. 🔍 **Kontrola:** `expect(first_name).to_be_visible()`
4. 🔍 **Kontrola:** Ověřen název prvního kurzu: '{first_name.inner_text().strip()}'
   - Technicky: `assert len(first_name.inner_text().strip()) > 0`
5. ⚙️ **Krok:** `first_desc = self.courses_page.course_descriptions.first` – *Příprava testovacích dat*
6. 🔍 **Kontrola:** `expect(first_desc).to_be_visible()`
7. 🔍 **Kontrola:** Ověřen popis kurzu
   - Technicky: `assert len(first_desc.inner_text().strip()) > 0`
8. ⚙️ **Krok:** `first_capacity = self.courses_page.course_capacities.first` – *Příprava testovacích dat*
9. 🔍 **Kontrola:** `expect(first_capacity).to_be_visible()`
10. 🔍 **Kontrola:** Ověřena kapacita kurzu: '{first_capacity.inner_text().strip()}'
   - Technicky: `assert 'Kapacita:' in first_capacity.inner_text()`
11. ⚙️ **Krok:** `first_price = self.courses_page.course_prices.first` – *Příprava testovacích dat*
12. 🔍 **Kontrola:** `expect(first_price).to_be_visible()`
13. ⚙️ **Krok:** `price_text = first_price.inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
14. 🔍 **Kontrola:** Cena neodpovídá formátu celých Kč: {price_text}
   - Technicky: `assert re.search('Cena:\\s*\\d+\\s*Kč', price_text)`
15. 🔍 **Kontrola:** Ověřena zaokrouhlená cena kurzu: '{price_text}'
   - Technicky: `step(f"Ověřena zaokrouhlená cena kurzu: '{price_text}'")`
16. ⚙️ **Krok:** `first_img = self.courses_page.course_images.first` – *Příprava testovacích dat*
17. 🔍 **Kontrola:** Ověřeno zobrazení náhledového obrázku kurzu
   - Technicky: `expect(first_img).to_be_visible()`
18. ⚙️ **Krok:** `first_btn = self.courses_page.see_more_buttons.first` – *Příprava testovacích dat*
19. 🔍 **Kontrola:** Ověřeno tlačítko pro zobrazení detailu kurzu
   - Technicky: `expect(first_btn).to_be_visible()`

#### `TestCoursesCatalog` -> `test_anonymous_user_registration_prompt_in_catalog` (řádek 68)

**Popis:** [US-09] Ověření zobrazení výzvy k registraci pro nepřihlášeného návštěvníka pod katalogem.

**Souhrn:** `3` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. 🔍 **Kontrola:** `expect(self.courses_page.interest_title).to_be_visible()`
3. 🔍 **Kontrola:** Ověřen text výzvy k registraci pro anonymního návštěvníka
   - Technicky: `expect(self.courses_page.interest_title).to_contain_text('Máte zájem o naše kurzy?')`
4. 🔍 **Kontrola:** `expect(self.courses_page.registration_link).to_be_visible()`
5. ⚙️ **Krok:** `self.courses_page.registration_link.click()`
6. ⚙️ **Krok:** `page.wait_for_load_state('networkidle')`
7. 🔍 **Kontrola:** Ověřeno přesměrování z výzvy přímo na registrační formulář
   - Technicky: `expect(page).to_have_url(re.compile('.*/register'))`

#### `TestCoursesCatalog` -> `test_navigate_to_course_detail` (řádek 82)

**Popis:** [US-09, US-10] Ověření prokliku z katalogu do detailu konkrétního kurzu.

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
3. 🔍 **Kontrola:** Ověřeno přesměrování na detail kurzu (/courses/:id)
   - Technicky: `expect(page).to_have_url(re.compile(f'^{re.escape(self.courses_page.base_url)}/courses/\\d+$'))`
4. 🔍 **Kontrola:** Ověřeno načtení kontejneru detailu kurzu
   - Technicky: `expect(self.courses_page.course_detail).to_be_visible()`

#### `TestCoursesCatalog` -> `test_course_detail_content_and_iterations_format` (řádek 93)

**Popis:** [US-10] Ověření detailu kurzu: popis, cena a formát termínů (termín, datum, kapacita ve formátu X/Y).

**Souhrn:** `7` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
3. 🔍 **Kontrola:** Ověřen nadpis 'Vypsané běhy kurzu:'
   - Technicky: `expect(self.courses_page.iterations_heading).to_be_visible()`
4. ⚙️ **Krok:** `iteration_count = self.courses_page.iteration_cards.count()` – *Získání hodnoty/stavu z aplikace*
5. ⚙️ **Krok:** `if iteration_count > 0:` – *Řídicí blok (if)*
6. ⚙️ **Krok:** `first_iteration = self.courses_page.iteration_cards.first` – *Příprava testovacích dat*
7. 🔍 **Kontrola:** `expect(first_iteration).to_be_visible()`
8. ⚙️ **Krok:** `iteration_text = first_iteration.inner_text()` – *Získání hodnoty/stavu z aplikace*
9. 🔍 **Kontrola:** `assert 'Zahájení:' in iteration_text`
10. 🔍 **Kontrola:** Ověřeno zobrazení data zahájení a ukončení běhu kurzu
   - Technicky: `assert 'Ukončení:' in iteration_text`
11. ⚙️ **Krok:** `capacity_match = re.search('Kapacita:\\s*\\d+/\\d+', iteration_text)` – *Příprava testovacích dat*
12. 🔍 **Kontrola:** Formát kapacity X/Y nenalezen: {iteration_text}
   - Technicky: `assert capacity_match`
13. 🔍 **Kontrola:** Ověřen správný formát poměru obsazenosti a kapacity: {capacity_match.group(0)}
   - Technicky: `step(f'Ověřen správný formát poměru obsazenosti a kapacity: {capacity_match.group(0)}')`

#### `TestCoursesCatalog` -> `test_course_detail_iterations_anonymous_vs_authenticated` (řádek 119)

**Popis:** [US-10, US-11] Ověření, že termíny běhů kurzu se zobrazují anonymně a tlačítka zápisu se aktivují po přihlášení.

**Souhrn:** `6` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
3. 🔍 **Kontrola:** Ověřen nadpis 'Vypsané běhy kurzu' pro nepřihlášeného návštěvníka
   - Technicky: `expect(self.courses_page.iterations_heading).to_be_visible()`
4. 🔍 **Kontrola:** Ověřeno, že tlačítka pro zápis nejsou pro anonymního uživatele zobrazena
   - Technicky: `expect(self.courses_page.enroll_buttons.first).not_to_be_visible()`
5. 🔍 **Kontrola:** Ověřena výzva k registraci pro nepřihlášeného návštěvníka na detailu kurzu
   - Technicky: `expect(self.courses_page.registration_prompt).to_be_visible()`
6. ⚙️ **Krok:** `self.login_page.navigate()`
7. ⚙️ **Krok:** `self.login_page.login(registered_user['email'], registered_user['password'])`
8. ⚙️ **Krok:** `page.wait_for_url('**/courses')`
9. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
10. 🔍 **Kontrola:** Ověřeno, že po přihlášení jsou tlačítka 'Nezávazná registrace' pro volný běh viditelná
   - Technicky: `expect(self.courses_page.enroll_buttons.first).to_be_visible()`

#### `TestCoursesCatalog` -> `test_fully_booked_iteration_indication` (řádek 143)

**Popis:** [US-11] Ověření chování při plně obsazené kapacitě běhu kurzu (kapacita dosáhla maxima -> tlačítko zápisu je skryto/nedostupné).

**Souhrn:** `5` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `page.route('**/api/courses/*/iterations', mock_full_capacity)`
2. ⚙️ **Krok:** `self.courses_page.navigate()`
3. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
4. ⚙️ **Krok:** `first_iteration = self.courses_page.iteration_cards.first` – *Příprava testovacích dat*
5. 🔍 **Kontrola:** `expect(first_iteration).to_be_visible()`
6. 🔍 **Kontrola:** Běh by měl indikovat plnou obsazenost
   - Technicky: `assert re.search('Kapacita:\\s*(\\d+)/\\1', first_iteration.inner_text())`
7. ⚙️ **Krok:** `enroll_btn = self.courses_page.get_iteration_enroll_button(first_iteration)` – *Příprava testovacích dat*
8. 🔍 **Kontrola:** Ověřeno, že pro plně obsazený běh není tlačítko registrace zobrazeno
   - Technicky: `expect(enroll_btn).not_to_be_visible()`

### Soubor: `tests/courses/test_enrollment.py`
#### `TestCourseEnrollment` -> `test_enrollment_form_elements_presence` (řádek 22)

**Popis:** [US-12] Ověření přítomnosti formulářových prvků pro zápis na kurz.

**Souhrn:** `6` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.login(registered_user['email'], registered_user['password'])`
3. ⚙️ **Krok:** `page.wait_for_url('**/courses')`
4. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
5. 🔍 **Kontrola:** `expect(self.courses_page.enroll_buttons.first).to_be_visible()`
6. ⚙️ **Krok:** `self.courses_page.enroll_buttons.first.click()`
7. ⚙️ **Krok:** `page.wait_for_url(re.compile('.*/courses/\\d+/register'))`
8. 🔍 **Kontrola:** `expect(self.enroll_page.registration_section).to_be_visible()`
9. 🔍 **Kontrola:** `expect(self.enroll_page.registration_title).to_be_visible()`
10. 🔍 **Kontrola:** `expect(self.enroll_page.ico_input).to_be_visible()`
11. 🔍 **Kontrola:** `expect(self.enroll_page.phone_input).to_be_visible()`
12. 🔍 **Kontrola:** Ověřena přítomnost všech prvků formuláře pro zápis na kurz
   - Technicky: `expect(self.enroll_page.submit_button).to_be_visible()`

#### `TestCourseEnrollment` -> `test_enrollment_ico_validation` (řádek 40)

**Popis:** [US-12] Ověření validace IČO pomocí váženého kontrolního součtu modulo 11.

**Souhrn:** `8` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.login(registered_user['email'], registered_user['password'])`
3. ⚙️ **Krok:** `page.wait_for_url('**/courses')`
4. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
5. ⚙️ **Krok:** `self.courses_page.enroll_buttons.first.click()`
6. ⚙️ **Krok:** `page.wait_for_url(re.compile('.*/courses/\\d+/register'))`
7. ⚙️ **Krok:** `invalid_ico = generate_invalid_ico()` – *Příprava testovacích dat*
8. ⚙️ **Krok:** `self.enroll_page.fill_and_submit(ico=invalid_ico, phone='+420777123456')`
9. 🔍 **Kontrola:** `expect(self.enroll_page.ico_error).to_be_visible()`
10. 🔍 **Kontrola:** Ověřeno odmítnutí neplatného IČO '{invalid_ico}' a zobrazení chybové hlášky
   - Technicky: `expect(self.enroll_page.ico_error).to_have_text('Neplatné IČO')`

#### `TestCourseEnrollment` -> `test_enrollment_phone_validation` (řádek 57)

**Popis:** [US-12] Ověření validace telefonního čísla (minimálně 9 číslic).

**Souhrn:** `8` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.login(registered_user['email'], registered_user['password'])`
3. ⚙️ **Krok:** `page.wait_for_url('**/courses')`
4. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
5. ⚙️ **Krok:** `self.courses_page.enroll_buttons.first.click()`
6. ⚙️ **Krok:** `page.wait_for_url(re.compile('.*/courses/\\d+/register'))`
7. ⚙️ **Krok:** `valid_ico = generate_valid_ico()` – *Příprava testovacích dat*
8. ⚙️ **Krok:** `self.enroll_page.fill_and_submit(ico=valid_ico, phone='12345')`
9. 🔍 **Kontrola:** `expect(self.enroll_page.phone_error).to_be_visible()`
10. 🔍 **Kontrola:** Ověřeno zobrazení validační chyby při zadání krátkého telefonního čísla
   - Technicky: `expect(self.enroll_page.phone_error).to_have_text('Telefonní číslo musí obsahovat alespoň 9 číslic.')`

#### `TestCourseEnrollment` -> `test_successful_enrollment_and_my_courses_display` (řádek 74)

**Popis:** [US-12, US-13] Úspěšné odeslání zápisu na kurz a ověření zobrazení v 'Moje kurzy'.

**Souhrn:** `12` akcí, `8` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.login(registered_user['email'], registered_user['password'])`
3. ⚙️ **Krok:** `page.wait_for_url('**/courses')`
4. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
5. 🔍 **Kontrola:** `expect(self.courses_page.enroll_buttons.first).to_be_visible()`
6. ⚙️ **Krok:** `self.courses_page.enroll_buttons.first.click()`
7. ⚙️ **Krok:** `page.wait_for_url(re.compile('.*/courses/\\d+/register'))`
8. ⚙️ **Krok:** `valid_ico = generate_valid_ico()` – *Příprava testovacích dat*
9. ⚙️ **Krok:** `valid_phone = '+420777888999'` – *Příprava testovacích dat*
10. ⚙️ **Krok:** `page.on('dialog', lambda dialog: dialog.accept())`
11. ⚙️ **Krok:** `self.enroll_page.fill_and_submit(ico=valid_ico, phone=valid_phone)`
12. ⚙️ **Krok:** `page.wait_for_url('**/my-courses')`
13. 🔍 **Kontrola:** `expect(self.my_courses_page.title).to_be_visible()`
14. 🔍 **Kontrola:** Ověřeno přesměrování po úspěšném zápisu na stránku /my-courses
   - Technicky: `expect(self.my_courses_page.title).to_have_text('Mé zapsané kurzy')`
15. 🔍 **Kontrola:** `expect(self.my_courses_page.courses_section).to_be_visible()`
16. ⚙️ **Krok:** `if self.my_courses_page.date_time_from.count() > 0:` – *Řídicí blok (if)*
17. 🔍 **Kontrola:** `expect(self.my_courses_page.date_time_from.first).to_be_visible()`
18. 🔍 **Kontrola:** `expect(self.my_courses_page.date_time_to.first).to_be_visible()`
19. 🔍 **Kontrola:** `expect(self.my_courses_page.day_information.first).to_be_visible()`
20. 🔍 **Kontrola:** Ověřeno zobrazení termínů lekcí, dne a místa konání zapsaného kurzu
   - Technicky: `expect(self.my_courses_page.place_information.first).to_be_visible()`

---

<a id="oblast-navigation"></a>
## Oblast: Navigation
*Počet testů v oblasti: **1***

### Soubor: `tests/navigation/test_navbar.py`
#### `TestNavigationNavbar` -> `test_navigation_between_courses_and_login` (řádek 12)

**Popis:** Ověření navigace mezi katalogem kurzů a přihlášením přes navbar.

**Souhrn:** `8` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `courses_page = CoursesPage(page)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `login_page = LoginPage(page)` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `navbar = Navbar(page)` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `courses_page.navigate()`
5. 🔍 **Kontrola:** `expect(navbar.courses_link).to_be_visible()`
6. 🔍 **Kontrola:** Navbar prvky v katalogu kurzů jsou viditelné
   - Technicky: `expect(navbar.login_link).to_be_visible()`
7. ⚙️ **Krok:** `navbar.login_link.click()`
8. ⚙️ **Krok:** `page.wait_for_url('**/login')`
9. 🔍 **Kontrola:** Úspěšná navigace z katalogu kurzů do přihlášení
   - Technicky: `expect(login_page.login_title).to_be_visible()`
10. ⚙️ **Krok:** `navbar.courses_link.click()`
11. ⚙️ **Krok:** `page.wait_for_url('**/courses')`
12. 🔍 **Kontrola:** Úspěšná zpětná navigace z přihlášení do katalogu kurzů
   - Technicky: `expect(courses_page.title).to_be_visible()`

---

<a id="oblast-portal"></a>
## Oblast: Portal
*Počet testů v oblasti: **4***

### Soubor: `tests/portal/test_home_dashboard.py`
#### `TestHomeDashboard` -> `test_authenticated_user_sees_personalized_welcome` (řádek 12)

**Popis:** Ověření, že po přihlášení se uživateli zobrazí personalizované uvítání se jménem (US-17).

**Souhrn:** `7` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `login_page = LoginPage(page)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `home_page = HomePage(page)` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `login_page.navigate()`
4. ⚙️ **Krok:** `login_page.login(registered_user['email'], registered_user['password'])`
5. ⚙️ **Krok:** `page.wait_for_url('**/courses')`
6. ⚙️ **Krok:** `page.wait_for_load_state('networkidle')`
7. ⚙️ **Krok:** `home_page.navigate()`
8. 🔍 **Kontrola:** Ověřena URL domovské stránky (/home)
   - Technicky: `expect(page).to_have_url(home_page.url)`
9. 🔍 **Kontrola:** `expect(home_page.welcome_section).to_be_visible()`
10. 🔍 **Kontrola:** Ověřeno personalizované uvítání uživatele: 'Vítej uživateli {registered_user['name']}!'
   - Technicky: `expect(home_page.welcome_section).to_contain_text(f"Vítej uživateli {registered_user['name']}!")`

#### `TestHomeDashboard` -> `test_navbar_home_link_navigates_to_dashboard` (řádek 32)

**Popis:** Ověření, že volba 'Domů' v horní navigaci spolehlivě přepne na domovskou nástěnku (US-17).

**Souhrn:** `7` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `login_page = LoginPage(page)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `navbar = Navbar(page)` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `home_page = HomePage(page)` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `login_page.navigate()`
5. ⚙️ **Krok:** `login_page.login(registered_user['email'], registered_user['password'])`
6. 🔍 **Kontrola:** `expect(navbar.home_link).to_be_visible()`
7. ⚙️ **Krok:** `navbar.home_link.click()`
8. ⚙️ **Krok:** `page.wait_for_url('**/home')`
9. 🔍 **Kontrola:** `expect(page).to_have_url(home_page.url)`
10. 🔍 **Kontrola:** Ověřen úspěšný přechod na domovskou stránku přes odkaz 'Domů' v navigaci
   - Technicky: `expect(home_page.welcome_section).to_be_visible()`

### Soubor: `tests/portal/test_linktree.py`
#### `TestPortalLinktree` -> `test_portal_linktree_elements_presence` (řádek 14)

**Popis:** Ověření, že úvodní stránka / obsahuje všechny klíčové navigační odkazy portálu (US-01).

**Souhrn:** `1` akcí, `7` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.linktree_page.navigate()`
2. 🔍 **Kontrola:** Ověřena úvodní URL portálu (/)
   - Technicky: `expect(page).to_have_url(f'{self.linktree_page.base_url}/')`
3. 🔍 **Kontrola:** Ověřen odkaz na aplikaci Kalkulačka
   - Technicky: `expect(self.linktree_page.calculator_link).to_be_visible()`
4. 🔍 **Kontrola:** Ověřen odkaz na Testovací login
   - Technicky: `expect(self.linktree_page.test_login_link).to_be_visible()`
5. 🔍 **Kontrola:** Ověřen odkaz na NextDate
   - Technicky: `expect(self.linktree_page.nextdate_link).to_be_visible()`
6. 🔍 **Kontrola:** Ověřen odkaz na Registraci na kurz
   - Technicky: `expect(self.linktree_page.course_registration_link).to_be_visible()`
7. 🔍 **Kontrola:** Ověřen odkaz na (výpis) kurzu
   - Technicky: `expect(self.linktree_page.course_list_link).to_be_visible()`
8. 🔍 **Kontrola:** Ověřen odkaz na 'Demo-login' pro vstup do aplikace kurzů
   - Technicky: `expect(self.linktree_page.demo_login_link).to_be_visible()`

#### `TestPortalLinktree` -> `test_portal_linktree_navigation_to_courses` (řádek 39)

**Popis:** Ověření, že kliknutí na 'Demo-login' nasměruje návštěvníka přímo do katalogu kurzů (US-01).

**Souhrn:** `2` akcí, `1` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.linktree_page.navigate()`
2. ⚙️ **Krok:** `self.linktree_page.open_demo_login()`
3. 🔍 **Kontrola:** Ověřeno úspěšné přesměrování z rozcestníku do katalogu kurzů (/courses)
   - Technicky: `expect(page).to_have_url(f'{self.linktree_page.base_url}/courses')`

---

<a id="oblast-profile"></a>
## Oblast: Profile
*Počet testů v oblasti: **6***

### Soubor: `tests/profile/test_profile.py`
#### `TestUserProfile` -> `test_profile_elements_presence_and_prefilled_data` (řádek 22)

**Popis:** Ověření zobrazení prvků profilu a předvyplněných údajů přihlášeného klienta.

**Souhrn:** `2` akcí, `9` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.profile_page.navigate()`
3. 🔍 **Kontrola:** `expect(self.profile_page.heading).to_be_visible()`
4. 🔍 **Kontrola:** Ověřen nadpis 'Profil'
   - Technicky: `expect(self.profile_page.heading).to_have_text('Profil')`
5. 🔍 **Kontrola:** `expect(self.profile_page.name_input).to_be_visible()`
6. 🔍 **Kontrola:** Ověřeno předvyplněné jméno: {registered_user['name']}
   - Technicky: `assert self.profile_page.name_input.input_value() == registered_user['name']`
7. 🔍 **Kontrola:** `expect(self.profile_page.email_input).to_be_visible()`
8. 🔍 **Kontrola:** Ověřen předvyplněný e-mail: {registered_user['email']}
   - Technicky: `assert self.profile_page.email_input.input_value() == registered_user['email']`
9. 🔍 **Kontrola:** Ověřeno pole pro telefon
   - Technicky: `expect(self.profile_page.phone_input).to_be_visible()`
10. 🔍 **Kontrola:** Ověřeno pole pro IČO
   - Technicky: `expect(self.profile_page.ico_input).to_be_visible()`
11. 🔍 **Kontrola:** Ověřeno tlačítko 'Uložit'
   - Technicky: `expect(self.profile_page.save_button).to_be_visible()`

#### `TestUserProfile` -> `test_profile_successful_update` (řádek 48)

**Popis:** Ověření úspěšné aktualizace údajů profilu (platný telefon a platné IČO s kontrolním součtem).

**Souhrn:** `5` akcí, `1` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.profile_page.navigate()`
3. ⚙️ **Krok:** `valid_ico = '27082440'` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `valid_phone = '+420777123456'` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `self.profile_page.update_profile(phone=valid_phone, ico=valid_ico)`
6. 🔍 **Kontrola:** Ověřeno přesměrování na /home po úspěšném uložení profilu
   - Technicky: `expect(page).to_have_url(f'{self.profile_page.base_url}/home')`

#### `TestUserProfile` -> `test_profile_invalid_ico_validation` (řádek 62)

**Popis:** Ověření odmítnutí neplatného IČO (nevyhovující kontrolní součet).

**Souhrn:** `3` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.profile_page.navigate()`
3. ⚙️ **Krok:** `self.profile_page.update_profile(phone='+420777123456', ico='12345678')`
4. 🔍 **Kontrola:** Ověřeno, že formulář se neodeslal a stránka zůstává na /profile
   - Technicky: `expect(page).to_have_url(f'{self.profile_page.base_url}/profile')`
5. 🔍 **Kontrola:** Ověřena validační hláška 'Neplatné IČO'
   - Technicky: `expect(self.profile_page.ico_error).to_be_visible()`

#### `TestUserProfile` -> `test_profile_invalid_phone_validation` (řádek 76)

**Popis:** Ověření odmítnutí neplatného telefonního čísla.

**Souhrn:** `3` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.profile_page.navigate()`
3. ⚙️ **Krok:** `self.profile_page.update_profile(phone='12', ico='27082440')`
4. 🔍 **Kontrola:** Ověřeno, že formulář se neodeslal při neplatném telefonu
   - Technicky: `expect(page).to_have_url(f'{self.profile_page.base_url}/profile')`
5. 🔍 **Kontrola:** Ověřena validační hláška 'Neplatné telefonní číslo'
   - Technicky: `expect(self.profile_page.phone_error).to_be_visible()`

#### `TestUserProfile` -> `test_profile_unauthenticated_access_denied` (řádek 90)

**Popis:** Ověření, že bez přihlášení není formulář profilu zobrazen.

**Souhrn:** `1` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.profile_page.navigate()`
2. 🔍 **Kontrola:** `expect(self.profile_page.name_input).not_to_be_visible()`
3. 🔍 **Kontrola:** Ověřeno, že nepřihlášený uživatel nemá přístup k datům profilu
   - Technicky: `expect(self.profile_page.heading).not_to_be_visible()`

#### `TestMyCourses` -> `test_my_courses_page_display` (řádek 112)

**Popis:** Ověření načtení stránky zapsaných kurzů přihlášeného klienta (/my-courses).

**Souhrn:** `2` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.my_courses_page.navigate()`
3. 🔍 **Kontrola:** Ověřena URL /my-courses
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/my-courses')`
4. 🔍 **Kontrola:** `expect(self.my_courses_page.title).to_be_visible()`
5. 🔍 **Kontrola:** Ověřen nadpis sekce 'Mé zapsané kurzy'
   - Technicky: `expect(self.my_courses_page.title).to_have_text('Mé zapsané kurzy')`
6. 🔍 **Kontrola:** Ověřena sekce pro zobrazení kurzů uživatele
   - Technicky: `expect(self.my_courses_page.courses_section).to_be_visible()`

---

<a id="oblast-security"></a>
## Oblast: Security
*Počet testů v oblasti: **6***

### Soubor: `tests/security/test_csrf.py`
#### `TestCsrfAndSessionIntegrity` -> `test_csrf_cookie_present_on_app_initialization` (řádek 11)

**Popis:** [US-20] Ověření, že aplikace po inicializaci získá platnou CSRF cookie (XSRF-TOKEN).

**Souhrn:** `4` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `page.goto(f'{BASE_URL}/login')`
2. ⚙️ **Krok:** `page.wait_for_load_state('networkidle')`
3. ⚙️ **Krok:** `cookies = page.context.cookies()` – *Získání hodnoty/stavu z aplikace*
4. ⚙️ **Krok:** `xsrf_cookie = next((c for c in cookies if c['name'] == 'XSRF-TOKEN'), None)` – *Příprava testovacích dat*
5. 🔍 **Kontrola:** Cookie XSRF-TOKEN nebyla po načtení stránky nalezena
   - Technicky: `assert xsrf_cookie is not None`
6. 🔍 **Kontrola:** Cookie XSRF-TOKEN je prázdná
   - Technicky: `assert len(xsrf_cookie['value']) > 0`
7. 🔍 **Kontrola:** Ověřena přítomnost CSRF tokenu v cookies: {xsrf_cookie['name']}
   - Technicky: `step(f"Ověřena přítomnost CSRF tokenu v cookies: {xsrf_cookie['name']}")`

#### `TestCsrfAndSessionIntegrity` -> `test_unauthorized_state_changing_request_rejected` (řádek 23)

**Popis:** [US-20] Ověření, že neautentizovaný požadavek na změnu stavu bez platného sezení a tokenu je zamítnut.

**Souhrn:** `1` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `response = page.request.post(f'{BASE_URL}/api/courses', headers={'Accept': 'application/json'}, data={'name': 'Útočný kurz', 'price': 1000})` – *Získání hodnoty/stavu z aplikace*
2. 🔍 **Kontrola:** Očekáváno zamítnutí neautorizovaného požadavku, obdrženo: {response.status}
   - Technicky: `assert response.status in (401, 403, 419)`
3. 🔍 **Kontrola:** Ověřeno bezpečné zamítnutí neoprávněného POST požadavku (HTTP {response.status})
   - Technicky: `step(f'Ověřeno bezpečné zamítnutí neoprávněného POST požadavku (HTTP {response.status})')`

#### `TestCsrfAndSessionIntegrity` -> `test_session_regeneration_on_login_and_logout` (řádek 35)

**Popis:** [US-20] Ověření regenerace sezení po přihlášení a odhlášení (ochrana proti Session Fixation).

**Souhrn:** `13` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `login_page = LoginPage(page)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `login_page.navigate()`
3. ⚙️ **Krok:** `anon_cookies = page.context.cookies()` – *Získání hodnoty/stavu z aplikace*
4. ⚙️ **Krok:** `anon_session = next((c['value'] for c in anon_cookies if 'session' in c['name'].lower()), None)` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `login_page.login(registered_user['email'], registered_user['password'])`
6. ⚙️ **Krok:** `page.wait_for_url('**/courses')`
7. ⚙️ **Krok:** `auth_cookies = page.context.cookies()` – *Získání hodnoty/stavu z aplikace*
8. ⚙️ **Krok:** `auth_session = next((c['value'] for c in auth_cookies if 'session' in c['name'].lower()), None)` – *Příprava testovacích dat*
9. ⚙️ **Krok:** `if anon_session and auth_session:` – *Řídicí blok (if)*
10. 🔍 **Kontrola:** Session cookie nebyla po přihlášení regenerována (Session Fixation riziko)
   - Technicky: `assert anon_session != auth_session`
11. 🔍 **Kontrola:** Ověřena úspěšná regenerace sezení při přihlášení uživatele
   - Technicky: `step('Ověřena úspěšná regenerace sezení při přihlášení uživatele')`
12. ⚙️ **Krok:** `login_page.logout()`
13. 🔍 **Kontrola:** `expect(login_page.nav_login_link).to_be_visible()`
14. ⚙️ **Krok:** `post_logout_cookies = page.context.cookies()` – *Získání hodnoty/stavu z aplikace*
15. ⚙️ **Krok:** `post_logout_session = next((c['value'] for c in post_logout_cookies if 'session' in c['name'].lower()), None)` – *Příprava testovacích dat*
16. ⚙️ **Krok:** `if auth_session and post_logout_session:` – *Řídicí blok (if)*
17. 🔍 **Kontrola:** Session cookie nebyla po odhlášení změněna/zneplatněna
   - Technicky: `assert auth_session != post_logout_session`
18. 🔍 **Kontrola:** Ověřeno zneplatnění sezení po odhlášení uživatele
   - Technicky: `step('Ověřeno zneplatnění sezení po odhlášení uživatele')`

### Soubor: `tests/security/test_rbac.py`
#### `TestRoleBasedAccessControl` -> `test_anonymous_access_to_private_routes_is_restricted` (řádek 26)

**Popis:** [US-19] Ověření, že nepřihlášený návštěvník nemá přístup k privátním sekcím (/profile a /my-courses).

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.profile_page.navigate()`
2. 🔍 **Kontrola:** Ověřeno, že nepřihlášený uživatel nevidí profil
   - Technicky: `expect(self.profile_page.name_input).not_to_be_visible()`
3. ⚙️ **Krok:** `self.my_courses_page.navigate()`
4. 🔍 **Kontrola:** Ověřeno, že nepřihlášený uživatel nevidí zapsané kurzy
   - Technicky: `expect(self.my_courses_page.date_time_from).not_to_be_visible()`

#### `TestRoleBasedAccessControl` -> `test_student_cannot_access_lector_create_course` (řádek 40)

**Popis:** [US-19] Ověření, že běžný student nemá v navigaci tlačítko pro přidání kurzu ani oprávnění pro lektorské rozhraní.

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.courses_page.navigate()`
3. 🔍 **Kontrola:** Ověřeno, že student nemá v přehledu kurzů tlačítko 'Přidat kurz'
   - Technicky: `expect(self.courses_page.add_course_button).not_to_be_visible()`
4. 🔍 **Kontrola:** Ověřeno, že student nemá tlačítka 'Přidat iteraci'
   - Technicky: `expect(self.courses_page.add_iteration_buttons).not_to_be_visible()`

#### `TestRoleBasedAccessControl` -> `test_lector_cannot_enroll_in_course_as_customer` (řádek 53)

**Popis:** [US-19] Ověření, že lektor nemá možnost se zapsat na běh kurzu (místo tlačítka zápisu vidí tlačítko přihlášených studentů).

**Souhrn:** `2` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, lector_user)`
2. ⚙️ **Krok:** `self.courses_page.navigate('/courses/1')`
3. 🔍 **Kontrola:** `expect(self.courses_page.course_detail).to_be_visible()`
4. 🔍 **Kontrola:** Ověřeno, že role lektora nemá možnost registrovat se na kurz jako zákazník
   - Technicky: `expect(self.courses_page.enroll_buttons).not_to_be_visible()`
5. 🔍 **Kontrola:** Ověřeno, že role lektora vidí tlačítko pro správu účastníků
   - Technicky: `expect(self.courses_page.participants_buttons.first).to_be_visible()`

---
