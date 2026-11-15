# Přehled automatizovaných testů (Test Catalog)

> Automaticky vygenerovaný přehled všech testů, kroků a kontrol v projektu.
> Datum vygenerování: **2026-11-15 18:38:34**

## Souhrnná statistika

| Metrika | Hodnota |
| :--- | :--- |
| **Celkem testovacích souborů** | 23 |
| **Celkem automatizovaných testů** | 127 |
| **Celkem akčních kroků** | 633 |
| **Celkem ověření a kontrol** | 626 |
| **Oblasti / moduly** | 6 (`auth, courses, navigation, portal, profile, security`) |

## Rychlá navigace podle oblastí

- [Auth (43 testů)](#oblast-auth)
- [Courses (52 testů)](#oblast-courses)
- [Navigation (1 testů)](#oblast-navigation)
- [Portal (10 testů)](#oblast-portal)
- [Profile (9 testů)](#oblast-profile)
- [Security (12 testů)](#oblast-security)

---

<a id="oblast-auth"></a>
## Oblast: Auth
*Počet testů v oblasti: **43***

### Soubor: `tests/auth/test_email_verification.py`
#### `TestDemoEmailVerification` -> `test_tc_us07_01_successful_email_verification_with_valid_link` (řádek 27) `[xfail(reason='Defekt infrastruktury/aplikace: Nelze vygenerovat a doručit platný podepsaný odkaz kvůli vyčerpané kvótě Mailtrap na backendu (500)', strict=False)]`

**Popis:** [TC-US07-01] Úspěšné ověření e-mailu pomocí platného podepsaného odkazu.

**Souhrn:** `2` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. 🔍 **Kontrola:** Uživatel přihlášen k neověřenému účtu
   - Technicky: `step('Uživatel přihlášen k neověřenému účtu')`
3. ⚙️ **Krok:** `self.verify_page.open_verification_link(user_id='1', token_hash='valid_hash_sample', signature='valid_signed_hmac')`
4. 🔍 **Kontrola:** Otevřen ověřovací odkaz ze schránky uživatele
   - Technicky: `step('Otevřen ověřovací odkaz ze schránky uživatele')`
5. 🔍 **Kontrola:** Ověřeno potvrzení o úspěšném ověření e-mailu
   - Technicky: `expect(self.verify_page.status_message).to_be_visible()`

#### `TestDemoEmailVerification` -> `test_tc_us07_02_tampered_or_expired_verification_link_rejected` (řádek 45)

**Popis:** [TC-US07-02] Odmítnutí pozměněného nebo vypršeného ověřovacího odkazu.

**Souhrn:** `3` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. 🔍 **Kontrola:** Uživatel přihlášen v systému
   - Technicky: `step('Uživatel přihlášen v systému')`
3. ⚙️ **Krok:** `response = self.verify_page.open_verification_link(user_id='99999', token_hash='invalidhash', signature='tampered_signature_12345', expires=1234567890)` – *Příprava testovacích dat*
4. 🔍 **Kontrola:** Zadán ověřovací odkaz s neplatným/pozměněným podpisem
   - Technicky: `step('Zadán ověřovací odkaz s neplatným/pozměněným podpisem')`
5. 🔍 **Kontrola:** Server nevrátil 403 Forbidden ani 429 pro neplatný podpis, ale: {response.status}
   - Technicky: `assert response.status in (403, 429)`
6. ⚙️ **Krok:** `if response.status == 403:` – *Řídicí blok (if)*
7. 🔍 **Kontrola:** `expect(self.verify_page.forbidden_heading).to_be_visible()`
8. 🔍 **Kontrola:** Ověřeno odmítnutí požadavku serverem se stavem 403 Forbidden a zobrazení INVALID SIGNATURE
   - Technicky: `expect(self.verify_page.invalid_signature_text).to_be_visible()`
9. 🔍 **Kontrola:** Ověřeno odmítnutí požadavku serverem se stavem 429 Too Many Requests (Rate Limiter)
   - Technicky: `step('Ověřeno odmítnutí požadavku serverem se stavem 429 Too Many Requests (Rate Limiter)')`

#### `TestDemoEmailVerification` -> `test_tc_us07_03_resend_verification_link_request` (řádek 75) `[xfail(reason='Defekt aplikace: Backend testovani.kitner.cz selhává při odesílání ověřovacího e-mailu kvůli vyčerpané kvótě Mailtrap (500 TransportException)', strict=False)]`

**Popis:** [TC-US07-03] Opětovné vyžádání nového ověřovacího odkazu z rozhraní aplikace.

**Souhrn:** `2` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. 🔍 **Kontrola:** Uživatel přihlášen v systému
   - Technicky: `step('Uživatel přihlášen v systému')`
3. ⚙️ **Krok:** `status = self.verify_page.send_resend_notification()` – *Získání hodnoty/stavu z aplikace*
4. 🔍 **Kontrola:** Odeslán požadavek na znovuzaslání ověřovacího e-mailu
   - Technicky: `step('Odeslán požadavek na znovuzaslání ověřovacího e-mailu')`
5. 🔍 **Kontrola:** Server nepotvrdil úspěšné odeslání ověřovacího odkazu, status: {status}
   - Technicky: `assert status in (200, 202, 204)`
6. 🔍 **Kontrola:** Ověřeno úspěšné přijetí požadavku serverem pro odeslání nového odkazu
   - Technicky: `step('Ověřeno úspěšné přijetí požadavku serverem pro odeslání nového odkazu')`

#### `TestDemoEmailVerification` -> `test_tc_us07_04_rate_limiting_resend_verification` (řádek 90)

**Popis:** [TC-US07-04] Ochrana proti zahlcení (Rate Limiting) při opakovaném vyžádání ověření.

**Souhrn:** `5` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `unique_email = f'qa_rate_{uuid.uuid4().hex[:8]}@example.com'` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `reg_page = RegisterPage(page)` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `reg_page.navigate()`
4. ⚙️ **Krok:** `reg_page.register('Rate User', unique_email, 'Password123!', 'Password123!')`
5. 🔍 **Kontrola:** Zaregistrován a přihlášen čerstvý uživatel: {unique_email}
   - Technicky: `expect(page).to_have_url(re.compile('/(courses|home)$'))`
6. ⚙️ **Krok:** `statuses = [self.verify_page.send_resend_notification() for _ in range(8)]` – *Získání hodnoty/stavu z aplikace*
7. 🔍 **Kontrola:** Odesláno 8 rychlých požadavků na znovuzaslání, návratové statusy: {statuses}
   - Technicky: `step(f'Odesláno 8 rychlých požadavků na znovuzaslání, návratové statusy: {statuses}')`
8. 🔍 **Kontrola:** Ochrana proti zahlcení (Rate Limiting) nebyla aktivována a server nevrátil 429: {statuses}
   - Technicky: `assert 429 in statuses`
9. 🔍 **Kontrola:** Ověřeno, že server při opakovaném vyžádání aktivoval Rate Limiting (stavový kód 429 Too Many Requests)
   - Technicky: `step('Ověřeno, že server při opakovaném vyžádání aktivoval Rate Limiting (stavový kód 429 Too Many Requests)')`

### Soubor: `tests/auth/test_forgot_password.py`
#### `TestDemoForgotPassword` -> `test_tc_us05_01_successful_password_reset_request_for_registered_email` (řádek 21) `[xfail(reason='Defekt aplikace: Backend testovani.kitner.cz selhává při odesílání e-mailu kvůli vyčerpané kvótě Mailtrap (500 Internal Server Error) nebo throttlingu (422)', strict=False)]`

**Popis:** [TC-US05-01] Úspěšné odeslání žádosti o reset hesla pro registrovaný e-mail.

**Souhrn:** `1` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. 🔍 **Kontrola:** `expect(self.forgot_page.email_input).to_be_visible()`
2. 🔍 **Kontrola:** Ověřena přítomnost pole pro e-mail a odesílacího tlačítka
   - Technicky: `expect(self.forgot_page.submit_button).to_be_visible()`
3. ⚙️ **Krok:** `self.forgot_page.request_password_reset(registered_user['email'])`
4. 🔍 **Kontrola:** Odeslána žádost o reset hesla pro e-mail: {registered_user['email']}
   - Technicky: `step(f"Odeslána žádost o reset hesla pro e-mail: {registered_user['email']}")`
5. 🔍 **Kontrola:** `expect(self.forgot_page.status_message).to_be_visible()`
6. 🔍 **Kontrola:** Ověřeno zobrazení potvrzovací zprávy o odeslání resetovacího odkazu
   - Technicky: `expect(self.forgot_page.status_message).to_contain_text('Odkaz na obnovení hesla')`

#### `TestDemoForgotPassword` -> `test_tc_us05_02_validation_mandatory_email_field` (řádek 36)

**Popis:** [TC-US05-02] Validace povinného pole při odeslání prázdného formuláře.

**Souhrn:** `1` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. 🔍 **Kontrola:** `expect(self.forgot_page.email_input).to_be_visible()`
2. ⚙️ **Krok:** `self.forgot_page.request_password_reset('')`
3. 🔍 **Kontrola:** Odeslán prázdný formulář bez vyplněného e-mailu
   - Technicky: `step('Odeslán prázdný formulář bez vyplněného e-mailu')`
4. 🔍 **Kontrola:** `expect(self.forgot_page.email_error).to_be_visible()`
5. 🔍 **Kontrola:** `expect(self.forgot_page.email_error).to_contain_text('The email field is required.')`
6. 🔍 **Kontrola:** Ověřena validace povinného pole: zobrazena chybová hláška a stránka zůstala na /forgot-password
   - Technicky: `expect(page).to_have_url(self.forgot_page.url)`

#### `TestDemoForgotPassword` -> `test_tc_us05_03_validation_invalid_email_format` (řádek 48)

**Popis:** [TC-US05-03] Validace neplatného formátu e-mailové adresy.

**Souhrn:** `2` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `invalid_sample = invalid_emails[0]` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `self.forgot_page.request_password_reset(invalid_sample)`
3. 🔍 **Kontrola:** Zadán syntakticky neplatný formát e-mailu: {invalid_sample}
   - Technicky: `step(f'Zadán syntakticky neplatný formát e-mailu: {invalid_sample}')`
4. 🔍 **Kontrola:** `expect(self.forgot_page.email_input).to_have_js_property('validity.valid', False)`
5. 🔍 **Kontrola:** Ověřena klientská validace formátu: formulář nebyl odeslán na server
   - Technicky: `expect(page).to_have_url(self.forgot_page.url)`

#### `TestDemoForgotPassword` -> `test_tc_us05_04_non_existent_email_user_enumeration_prevention` (řádek 62) `[xfail(reason="Defekt aplikace: Prevence odhadování účtů (User Enumeration) selhává – systém vrací 'We can't find a user with that email address' namísto neutrálního potvrzení", strict=False)]`

**Popis:** [TC-US05-04] Odeslání žádosti pro neexistující e-mail a prevence odhadování účtů.

**Souhrn:** `2` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `non_existent_email = 'zcela.neexistujici.konto999@example.com'` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `self.forgot_page.request_password_reset(non_existent_email)`
3. 🔍 **Kontrola:** Odeslána žádost s neexistujícím e-mailem: {non_existent_email}
   - Technicky: `step(f'Odeslána žádost s neexistujícím e-mailem: {non_existent_email}')`
4. 🔍 **Kontrola:** `expect(self.forgot_page.user_not_found_message).not_to_be_visible()`
5. 🔍 **Kontrola:** Ověřeno zobrazení neutrálního hlášení a absence prozrazení neexistence účtu
   - Technicky: `expect(self.forgot_page.status_message).to_be_visible()`

### Soubor: `tests/auth/test_login.py`
#### `TestDemoLogin` -> `test_tc_us03_01_successful_login_and_role_navigation_adaptation` (řádek 16)

**Popis:** [TC-US03-01] Úspěšné přihlášení s platnými údaji a adaptace horní navigace podle role.

**Souhrn:** `5` akcí, `10` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. 🔍 **Kontrola:** Otevřena stránka přihlášení (/login)
   - Technicky: `step('Otevřena stránka přihlášení (/login)')`
3. ⚙️ **Krok:** `self.login_page.login(registered_user['email'], registered_user['password'])`
4. 🔍 **Kontrola:** Ověřeno přesměrování zákazníka na /courses
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/courses')`
5. 🔍 **Kontrola:** `expect(self.login_page.logout_button).to_be_visible()`
6. 🔍 **Kontrola:** `expect(self.login_page.profile_link).to_be_visible()`
7. 🔍 **Kontrola:** Ověřena adaptace navigace pro zákazníka: tlačítko Odhlásit se, Můj profil a zánik Přihlásit se
   - Technicky: `expect(self.login_page.nav_login_link).not_to_be_visible()`
8. ⚙️ **Krok:** `self.login_page.logout()`
9. 🔍 **Kontrola:** `expect(self.login_page.nav_login_link).to_be_visible()`
10. 🔍 **Kontrola:** Ověřeno úspěšné odhlášení
   - Technicky: `expect(self.login_page.logout_button).not_to_be_visible()`
11. ⚙️ **Krok:** `self.login_page.navigate()`
12. ⚙️ **Krok:** `self.login_page.login(lector_user['email'], lector_user['password'])`
13. 🔍 **Kontrola:** Ověřeno přesměrování lektora na /courses
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/courses')`
14. 🔍 **Kontrola:** `expect(self.login_page.logout_button).to_be_visible()`
15. 🔍 **Kontrola:** Ověřeno úspěšné přihlášení lektora a přítomnost tlačítka Odhlásit se
   - Technicky: `expect(self.login_page.nav_login_link).not_to_be_visible()`

#### `TestDemoLogin` -> `test_tc_us03_02_validation_mandatory_fields_and_invalid_email_format` (řádek 49)

**Popis:** [TC-US03-02] Validace povinných polí a neplatného formátu e-mailu.

**Souhrn:** `4` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. 🔍 **Kontrola:** Otevřena stránka přihlášení
   - Technicky: `step('Otevřena stránka přihlášení')`
3. ⚙️ **Krok:** `self.login_page.login('', '')`
4. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.login_page.base_url}/login')`
5. 🔍 **Kontrola:** `expect(self.login_page.error_message).to_be_visible()`
6. 🔍 **Kontrola:** Ověřeno setrvání na /login a zobrazení chybové hlášky pro povinný e-mail
   - Technicky: `expect(self.login_page.error_message).to_contain_text('The email field is required.')`
7. ⚙️ **Krok:** `self.login_page.navigate()`
8. ⚙️ **Krok:** `self.login_page.login(invalid_emails[0], 'BezpecneHeslo123')`
9. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.login_page.base_url}/login')`
10. 🔍 **Kontrola:** Ověřeno spuštění HTML5 validace pro syntakticky neplatný formát e-mailu
   - Technicky: `expect(self.login_page.email_input).not_to_have_js_property('validationMessage', '')`

#### `TestDemoLogin` -> `test_tc_us03_03_case_insensitivity_and_whitespace_trimming` (řádek 70)

**Popis:** [TC-US03-03] Tolerance k velikosti písmen a automatické ořezávání mezer v e-mailu.

**Souhrn:** `3` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. 🔍 **Kontrola:** Otevřena stránka přihlášení
   - Technicky: `step('Otevřena stránka přihlášení')`
3. ⚙️ **Krok:** `raw_email = f"   {registered_user['email'].upper()}   "` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `self.login_page.login(raw_email, registered_user['password'])`
5. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.login_page.base_url}/courses')`
6. 🔍 **Kontrola:** Ověřeno úspěšné přihlášení s normalizovaným e-mailem (velká písmena + okrajové mezery)
   - Technicky: `expect(self.login_page.logout_button).to_be_visible()`

#### `TestDemoLogin` -> `test_tc_us03_04_unified_error_message_prevents_user_enumeration` (řádek 82)

**Popis:** [TC-US03-04] Jednotná chybová hláška chránící před user enumeration.

**Souhrn:** `5` akcí, `7` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `expected_error = 'These credentials do not match our records.'` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `self.login_page.navigate()`
3. ⚙️ **Krok:** `self.login_page.login('zcela.neexistujici.adresa999@example.com', 'Heslo123')`
4. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.login_page.base_url}/login')`
5. 🔍 **Kontrola:** `expect(self.login_page.error_message).to_be_visible()`
6. 🔍 **Kontrola:** Scénář A: Ověřena chybová hláška pro neexistující účet: '{expected_error}'
   - Technicky: `expect(self.login_page.error_message).to_contain_text(expected_error)`
7. ⚙️ **Krok:** `self.login_page.navigate()`
8. ⚙️ **Krok:** `self.login_page.login(registered_user['email'], 'SpatneHeslo999!')`
9. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.login_page.base_url}/login')`
10. 🔍 **Kontrola:** `expect(self.login_page.error_message).to_be_visible()`
11. 🔍 **Kontrola:** `expect(self.login_page.error_message).to_contain_text(expected_error)`
12. 🔍 **Kontrola:** Scénář B: Ověřena identická chybová zpráva a zachování předvyplněného e-mailu
   - Technicky: `expect(self.login_page.email_input).to_have_value(registered_user['email'])`

#### `TestDemoLogin` -> `test_tc_us03_04_password_field_security_clearing` (řádek 111) `[xfail(reason='Defekt aplikace: Po neúspěšném pokusu o přihlášení nedochází k bezpečnostnímu vymazání pole hesla', strict=False)]`

**Popis:** [TC-US03-04] Bezpečnostní vyčištění pole hesla po neúspěšném přihlášení.

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.login(registered_user['email'], 'SpatneHeslo999!')`
3. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.login_page.base_url}/login')`
4. 🔍 **Kontrola:** Ověřeno automatické bezpečnostní vymazání pole hesla po chybě přihlášení
   - Technicky: `expect(self.login_page.password_input).to_have_value('')`

#### `TestDemoLogin` -> `test_tc_us03_05_keyboard_accessibility_and_navigation` (řádek 120)

**Popis:** [TC-US03-05] Přístupné ovládání přihlašovacího formuláře z klávesnice.

**Souhrn:** `6` akcí, `7` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. 🔍 **Kontrola:** Otevřena stránka přihlášení
   - Technicky: `step('Otevřena stránka přihlášení')`
3. ⚙️ **Krok:** `self.login_page.email_input.focus()`
4. 🔍 **Kontrola:** `expect(self.login_page.email_input).to_be_focused()`
5. ⚙️ **Krok:** `self.login_page.email_input.fill(registered_user['email'])`
6. 🔍 **Kontrola:** Focus na pole E-mail a vyplnění e-mailu
   - Technicky: `step('Focus na pole E-mail a vyplnění e-mailu')`
7. ⚙️ **Krok:** `page.keyboard.press('Tab')`
8. 🔍 **Kontrola:** `expect(self.login_page.password_input).to_be_focused()`
9. ⚙️ **Krok:** `self.login_page.password_input.fill(registered_user['password'])`
10. 🔍 **Kontrola:** Focus na pole Heslo a vyplnění hesla
   - Technicky: `step('Focus na pole Heslo a vyplnění hesla')`
11. ⚙️ **Krok:** `page.keyboard.press('Enter')`
12. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.login_page.base_url}/courses')`
13. 🔍 **Kontrola:** Klávesa Enter: Úspěšné odeslání přihlašovacího formuláře a přechod na /courses
   - Technicky: `expect(self.login_page.logout_button).to_be_visible()`

#### `TestDemoLogin` -> `test_tc_us03_06_password_masking_and_navigation_links` (řádek 143)

**Popis:** [TC-US03-06] Maskování zadaného hesla a doprovodné navigační odkazy formuláře.

**Souhrn:** `2` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. 🔍 **Kontrola:** Otevřena stránka přihlášení
   - Technicky: `step('Otevřena stránka přihlášení')`
3. 🔍 **Kontrola:** Ověřeno maskování hesla (atribut type='password')
   - Technicky: `expect(self.login_page.password_input).to_have_attribute('type', 'password')`
4. 🔍 **Kontrola:** Ověřen odkaz pro registraci
   - Technicky: `expect(self.login_page.register_link).to_be_visible()`
5. 🔍 **Kontrola:** `expect(self.login_page.forgot_password_link).to_be_visible()`
6. ⚙️ **Krok:** `self.login_page.forgot_password_link.click()`
7. 🔍 **Kontrola:** Ověřen odkaz pro obnovu hesla a funkční přesměrování na /forgot-password
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/forgot-password')`

#### `TestDemoLogin` -> `test_tc_us03_07_authenticated_user_access_to_login_page_redirects` (řádek 163) `[xfail(reason='Defekt aplikace: Přihlášený uživatel není automaticky přesměrován z /login zpět do aplikace; aplikace umožní opětovné zobrazení formuláře přihlášení', strict=False)]`

**Popis:** [TC-US03-07] Chování při pokusu o otevření stránky přihlášení již přihlášeným uživatelem.

**Souhrn:** `3` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.login(registered_user['email'], registered_user['password'])`
3. 🔍 **Kontrola:** Uživatel úspěšně přihlášen
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/courses')`
4. ⚙️ **Krok:** `self.login_page.navigate()`
5. 🔍 **Kontrola:** `expect(page).not_to_have_url(f'{self.login_page.base_url}/login')`
6. 🔍 **Kontrola:** Ověřeno přesměrování přihlášeného uživatele z /login zpět do katalogu kurzů
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/courses')`

### Soubor: `tests/auth/test_logout.py`
#### `TestDemoLogout` -> `test_tc_us04_01_successful_logout_via_navbar` (řádek 32)

**Popis:** [TC-US04-01] Úspěšné odhlášení přihlášeného uživatele přes horní navigaci.

**Souhrn:** `2` akcí, `9` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. 🔍 **Kontrola:** Uživatel úspěšně přihlášen
   - Technicky: `step('Uživatel úspěšně přihlášen')`
3. 🔍 **Kontrola:** `expect(self.navbar.logout_button).to_be_visible()`
4. 🔍 **Kontrola:** `expect(self.navbar.profile_link).to_be_visible()`
5. 🔍 **Kontrola:** Ověřena přítomnost tlačítka pro odhlášení v navigaci
   - Technicky: `expect(self.navbar.login_link).not_to_be_visible()`
6. ⚙️ **Krok:** `self.navbar.logout()`
7. 🔍 **Kontrola:** Kliknuto na tlačítko 'Odhlásit se'
   - Technicky: `step("Kliknuto na tlačítko 'Odhlásit se'")`
8. 🔍 **Kontrola:** `expect(page).to_have_url(re.compile('/(courses|login)?$'))`
9. 🔍 **Kontrola:** `expect(self.navbar.login_link).to_be_visible()`
10. 🔍 **Kontrola:** `expect(self.navbar.logout_button).not_to_be_visible()`
11. 🔍 **Kontrola:** Ověřeno úspěšné odhlášení: zobrazen odkaz 'Přihlásit se', skryty privátní prvky a veřejná URL
   - Technicky: `expect(self.navbar.profile_link).not_to_be_visible()`

#### `TestDemoLogout` -> `test_tc_us04_02_session_invalidation_and_storage_cleanup` (řádek 51)

**Popis:** [TC-US04-02] Okamžité zneplatnění uživatelského sezení a smazání klientského úložiště.

**Souhrn:** `10` akcí, `8` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `context = page.context` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `cookies_before = context.cookies()` – *Získání hodnoty/stavu z aplikace*
4. ⚙️ **Krok:** `session_cookie_before = next((c for c in cookies_before if 'session' in c['name'].lower()), None)` – *Příprava testovacích dat*
5. 🔍 **Kontrola:** Před odhlášením nebyla nalezena session cookie
   - Technicky: `assert session_cookie_before is not None`
6. 🔍 **Kontrola:** Zaznamenána platná session cookie před odhlášením
   - Technicky: `step('Zaznamenána platná session cookie před odhlášením')`
7. ⚙️ **Krok:** `self.navbar.logout()`
8. 🔍 **Kontrola:** Uživatel se odhlásil
   - Technicky: `step('Uživatel se odhlásil')`
9. ⚙️ **Krok:** `cookies_after = context.cookies()` – *Získání hodnoty/stavu z aplikace*
10. ⚙️ **Krok:** `session_cookie_after = next((c for c in cookies_after if 'session' in c['name'].lower()), None)` – *Příprava testovacích dat*
11. ⚙️ **Krok:** `if session_cookie_after:` – *Řídicí blok (if)*
12. 🔍 **Kontrola:** Session cookie nebyla po odhlášení nahrazena anonymní relací
   - Technicky: `assert session_cookie_after['value'] != session_cookie_before['value']`
13. ⚙️ **Krok:** `token_storage = page.evaluate("() => localStorage.getItem('token') || sessionStorage.getItem('token')")` – *Příprava testovacích dat*
14. 🔍 **Kontrola:** V klientském úložišti zůstal citlivý autentizační token
   - Technicky: `assert not token_storage`
15. 🔍 **Kontrola:** Ověřeno nahrazení/vymazání session cookie a absence citlivých tokenů v Web Storage
   - Technicky: `step('Ověřeno nahrazení/vymazání session cookie a absence citlivých tokenů v Web Storage')`
16. ⚙️ **Krok:** `res = page.request.post(f'{self.login_page.base_url}/api/users/edit', headers={'Cookie': f"{session_cookie_before['name']}={session_cookie_before['value']}"}, data={'name': 'Hacked Session'}, max_redirects=0)` – *Získání hodnoty/stavu z aplikace*
17. 🔍 **Kontrola:** Stará session cookie nebyla odmítnuta, status: {res.status}, url: {res.url}
   - Technicky: `assert res.status in (302, 401, 419) or res.url.endswith('/login')`
18. 🔍 **Kontrola:** Ověřeno, že server striktně odmítl požadavek se starou session cookie (stav 302/401/419)
   - Technicky: `step('Ověřeno, že server striktně odmítl požadavek se starou session cookie (stav 302/401/419)')`

#### `TestDemoLogout` -> `test_tc_us04_03_restricted_private_routes_access_after_logout` (řádek 87)

**Popis:** [TC-US04-03] Zamezení přístupu k privátním funkcím a profilu po odhlášení přes přímou URL.

**Souhrn:** `4` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.navbar.logout()`
3. 🔍 **Kontrola:** Uživatel přihlášen a následně odhlášen
   - Technicky: `step('Uživatel přihlášen a následně odhlášen')`
4. ⚙️ **Krok:** `self.profile_page.navigate()`
5. 🔍 **Kontrola:** `expect(self.profile_page.name_input).not_to_be_visible()`
6. 🔍 **Kontrola:** `expect(self.profile_page.heading).not_to_be_visible()`
7. 🔍 **Kontrola:** Ověřeno, že odhlášený uživatel nemá přístup k datům profilu na /profile
   - Technicky: `expect(self.navbar.login_link).to_be_visible()`
8. ⚙️ **Krok:** `self.my_courses_page.navigate()`
9. 🔍 **Kontrola:** `expect(self.my_courses_page.date_time_from).not_to_be_visible()`
10. 🔍 **Kontrola:** Ověřeno, že odhlášený uživatel nevidí seznam zapsaných kurzů na /my-courses
   - Technicky: `expect(self.navbar.login_link).to_be_visible()`

#### `TestDemoLogout` -> `test_tc_us04_04_browser_back_button_security` (řádek 106)

**Popis:** [TC-US04-04] Zabezpečení proti neoprávněnému návratu pomocí tlačítka Zpět v prohlížeči.

**Souhrn:** `5` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.profile_page.navigate()`
3. 🔍 **Kontrola:** Otevřen profil v přihlášeném stavu
   - Technicky: `expect(self.profile_page.name_input).to_be_visible()`
4. ⚙️ **Krok:** `self.navbar.logout()`
5. 🔍 **Kontrola:** Uživatel odhlášen
   - Technicky: `expect(self.navbar.login_link).to_be_visible()`
6. ⚙️ **Krok:** `page.go_back()`
7. 🔍 **Kontrola:** Ověřeno, že návrat tlačítkem Zpět nezobrazí data profilu
   - Technicky: `expect(self.profile_page.name_input).not_to_be_visible()`
8. ⚙️ **Krok:** `page.reload()`
9. 🔍 **Kontrola:** `expect(self.profile_page.name_input).not_to_be_visible()`
10. 🔍 **Kontrola:** `expect(self.navbar.logout_button).not_to_be_visible()`
11. 🔍 **Kontrola:** Ověřeno, že ani po obnovení stránky nedošlo k obnovení sezení
   - Technicky: `expect(self.navbar.login_link).to_be_visible()`

#### `TestDemoLogout` -> `test_tc_us04_05_permanent_availability_of_logout_button` (řádek 129)

**Popis:** [TC-US04-05] Trvalá dostupnost tlačítka odhlášení na všech typech stránek a rozlišení.

**Souhrn:** `10` akcí, `8` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.courses_page.navigate()`
3. 🔍 **Kontrola:** Desktop: Tlačítko odhlášení viditelné na /courses
   - Technicky: `expect(self.navbar.logout_button).to_be_visible()`
4. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
5. 🔍 **Kontrola:** Desktop: Tlačítko odhlášení viditelné na detailu kurzu
   - Technicky: `expect(self.navbar.logout_button).to_be_visible()`
6. ⚙️ **Krok:** `self.profile_page.navigate()`
7. 🔍 **Kontrola:** Desktop: Tlačítko odhlášení viditelné na /profile
   - Technicky: `expect(self.navbar.logout_button).to_be_visible()`
8. ⚙️ **Krok:** `self.my_courses_page.navigate()`
9. 🔍 **Kontrola:** Desktop: Tlačítko odhlášení viditelné na /my-courses
   - Technicky: `expect(self.navbar.logout_button).to_be_visible()`
10. ⚙️ **Krok:** `page.set_viewport_size({'width': 375, 'height': 667})`
11. ⚙️ **Krok:** `self.courses_page.navigate()`
12. 🔍 **Kontrola:** `expect(self.navbar.hamburger_menu).to_be_visible()`
13. ⚙️ **Krok:** `self.navbar.open_mobile_menu()`
14. 🔍 **Kontrola:** Mobil: Tlačítko odhlášení dostupné v rozbaleném hamburger menu
   - Technicky: `expect(self.navbar.logout_button).to_be_visible()`
15. ⚙️ **Krok:** `self.navbar.logout()`
16. 🔍 **Kontrola:** `expect(self.navbar.hamburger_menu).to_be_visible()`
17. ⚙️ **Krok:** `self.navbar.open_mobile_menu()`
18. 🔍 **Kontrola:** Mobil: Úspěšné odhlášení z mobilního menu
   - Technicky: `expect(self.navbar.login_link).to_be_visible()`

#### `TestDemoLogout` -> `test_tc_us04_06_concurrent_tabs_logout_invalidation` (řádek 167)

**Popis:** [TC-US04-06] Odhlášení v jedné záložce a souběžná interakce v druhé otevřené záložce.

**Souhrn:** `22` akcí, `8` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `context = page.context` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `page_a = page` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `self._login(page_a, registered_user)`
4. ⚙️ **Krok:** `page_b = context.new_page()` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `profile_b = ProfilePage(page_b)` – *Příprava testovacích dat*
6. ⚙️ **Krok:** `profile_b.navigate()`
7. 🔍 **Kontrola:** Otevřeny dvě záložky: Záložka A (kurzy) a Záložka B (profil)
   - Technicky: `expect(profile_b.name_input).to_be_visible()`
8. ⚙️ **Krok:** `navbar_a = Navbar(page_a)` – *Příprava testovacích dat*
9. ⚙️ **Krok:** `navbar_a.logout()`
10. 🔍 **Kontrola:** V Záložce A provedeno odhlášení
   - Technicky: `expect(navbar_a.login_link).to_be_visible()`
11. ⚙️ **Krok:** `with:` – *Řídicí blok (with)*
12. ⚙️ **Krok:** `profile_b.update_profile(name='NeopravnenaZmena')`
13. ⚙️ **Krok:** `edit_response = resp_info.value` – *Příprava testovacích dat*
14. 🔍 **Kontrola:** Server v Záložce B nevrátil 401/419, ale: {edit_response.status}
   - Technicky: `assert edit_response.status in (401, 419)`
15. 🔍 **Kontrola:** Ověřeno, že server v Záložce B striktně zamítl požadavek se stavem 401/419
   - Technicky: `step('Ověřeno, že server v Záložce B striktně zamítl požadavek se stavem 401/419')`
16. ⚙️ **Krok:** `navbar_b = Navbar(page_b)` – *Příprava testovacích dat*
17. ⚙️ **Krok:** `page_b.reload()`
18. 🔍 **Kontrola:** `expect(navbar_b.login_link).to_be_visible()`
19. 🔍 **Kontrola:** Ověřeno, že po obnovení v Záložce B je uživatel odhlášen
   - Technicky: `expect(navbar_b.logout_button).not_to_be_visible()`
20. ⚙️ **Krok:** `page_c = context.new_page()` – *Příprava testovacích dat*
21. ⚙️ **Krok:** `login_c = LoginPage(page_c)` – *Příprava testovacích dat*
22. ⚙️ **Krok:** `profile_c = ProfilePage(page_c)` – *Příprava testovacích dat*
23. ⚙️ **Krok:** `login_c.navigate()`
24. ⚙️ **Krok:** `with:` – *Řídicí blok (with)*
25. ⚙️ **Krok:** `login_c.login(registered_user['email'], registered_user['password'])`
26. 🔍 **Kontrola:** `expect(page_c).to_have_url(f'{login_c.base_url}/courses', timeout=15000)`
27. ⚙️ **Krok:** `profile_c.navigate()`
28. 🔍 **Kontrola:** Ověřeno v čistém sezení, že neoprávněná změna se neuložila do databáze
   - Technicky: `expect(profile_c.name_input).not_to_have_value('NeopravnenaZmena')`
29. ⚙️ **Krok:** `page_b.close()`
30. ⚙️ **Krok:** `page_c.close()`

### Soubor: `tests/auth/test_rate_limiting.py`
#### `TestDemoRateLimiting` -> `test_tc_us08_01_attempts_1_to_5_allowed_without_blocking` (řádek 25)

**Popis:** [TC-US08-01] Průchod povoleného limitu 1 až 5 neúspěšných pokusů o přihlášení.

**Souhrn:** `5` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `probe_email = f'rate_probe1_{uuid.uuid4().hex[:6]}@example.com'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `wrong_pass = 'SpatneHeslo123!'` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
5. ⚙️ **Krok:** `resp = self.login_page.login_with_response(probe_email, wrong_pass)` – *Příprava testovacích dat*
6. 🔍 **Kontrola:** `assert resp.status in (302, 422)`
7. 🔍 **Kontrola:** `expect(self.login_page.error_message).to_be_visible()`
8. 🔍 **Kontrola:** Pokus {attempt}/5: Zobrazena standardní chybová hláška o neplatných údajích
   - Technicky: `expect(self.login_page.error_message).to_contain_text('These credentials do not match our records.')`

#### `TestDemoRateLimiting` -> `test_tc_us08_02_blocking_on_6th_attempt_and_countdown_display` (řádek 38)

**Popis:** [TC-US08-02] Dočasná blokace při 6. neúspěšném pokusu a zobrazení odpočtu sekund.

**Souhrn:** `6` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `probe_email = f'rate_probe2_{uuid.uuid4().hex[:6]}@example.com'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `wrong_pass = 'SpatneHeslo123!'` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
5. ⚙️ **Krok:** `self.login_page.login_with_response(probe_email, wrong_pass)`
6. ⚙️ **Krok:** `resp = self.login_page.login_with_response(probe_email, wrong_pass)` – *Příprava testovacích dat*
7. 🔍 **Kontrola:** `assert resp.status in (302, 422, 429)`
8. 🔍 **Kontrola:** `expect(self.login_page.error_message).to_be_visible()`
9. 🔍 **Kontrola:** `expect(self.login_page.error_message).to_contain_text('Too many login attempts')`
10. 🔍 **Kontrola:** Pokus 6: Zablokován – zobrazena výstraha Too many login attempts s odpočtem sekund
   - Technicky: `expect(self.login_page.error_message).to_contain_text(re.compile('try again in \\d+ seconds', re.IGNORECASE))`

#### `TestDemoRateLimiting` -> `test_tc_us08_03_counter_reset_after_successful_login` (řádek 55)

**Popis:** [TC-US08-03] Automatické vynulování počítadla neúspěšných pokusů po úspěšném přihlášení.

**Souhrn:** `13` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `user_email = f'rate_reset_{uuid.uuid4().hex[:6]}@example.com'` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `valid_pass = 'SpravneHeslo123!'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `self._register_user(page, user_email, valid_pass)`
4. ⚙️ **Krok:** `self.navbar.logout()`
5. ⚙️ **Krok:** `self.login_page.navigate()`
6. ⚙️ **Krok:** `wrong_pass = 'ChybneHeslo999!'` – *Příprava testovacích dat*
7. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
8. ⚙️ **Krok:** `self.login_page.login_with_response(user_email, wrong_pass)`
9. 🔍 **Kontrola:** Neúspěšný pokus {attempt}/4
   - Technicky: `expect(self.login_page.error_message).to_contain_text('These credentials do not match our records.')`
10. ⚙️ **Krok:** `with:` – *Řídicí blok (with)*
11. ⚙️ **Krok:** `self.login_page.login(user_email, valid_pass)`
12. 🔍 **Kontrola:** 5. pokus se správným heslem: Uživatel úspěšně přihlášen (čítač vynulován)
   - Technicky: `expect(page).to_have_url(f'{self.login_page.base_url}/courses', timeout=15000)`
13. ⚙️ **Krok:** `self.navbar.logout()`
14. ⚙️ **Krok:** `self.login_page.navigate()`
15. 🔍 **Kontrola:** `expect(self.login_page.email_input).to_be_visible()`
16. ⚙️ **Krok:** `resp = self.login_page.login_with_response(user_email, wrong_pass)` – *Příprava testovacích dat*
17. 🔍 **Kontrola:** `assert resp.status in (302, 422)`
18. 🔍 **Kontrola:** `expect(self.login_page.error_message).to_contain_text('These credentials do not match our records.', timeout=15000)`
19. 🔍 **Kontrola:** Nový neúspěšný pokus po přihlášení: Čítač byl vynulován, nedošlo k blokaci
   - Technicky: `expect(self.login_page.error_message).not_to_contain_text('Too many login attempts')`

#### `TestDemoRateLimiting` -> `test_tc_us08_04_restoration_of_login_after_throttle_expiration` (řádek 89)

**Popis:** [TC-US08-04] Obnovení možnosti přihlášení po vypršení časového limitu blokace.

**Souhrn:** `12` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `user_email = f'rate_expire_{uuid.uuid4().hex[:6]}@example.com'` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `valid_pass = 'ValidPass2026!'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `self._register_user(page, user_email, valid_pass)`
4. ⚙️ **Krok:** `self.navbar.logout()`
5. ⚙️ **Krok:** `self.login_page.navigate()`
6. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
7. ⚙️ **Krok:** `self.login_page.login_with_response(user_email, 'WrongPass123!')`
8. 🔍 **Kontrola:** Účet byl zablokován rate limiterem po 6 neúspěšných pokusech
   - Technicky: `expect(self.login_page.error_message).to_contain_text('Too many login attempts')`
9. ⚙️ **Krok:** `m = re.search('in (\\d+) seconds', self.login_page.error_message.inner_text())` – *Získání hodnoty/stavu z aplikace*
10. ⚙️ **Krok:** `wait_seconds = int(m.group(1)) if m else 60` – *Příprava testovacích dat*
11. 🔍 **Kontrola:** Zaznamenána doba blokace: {wait_seconds} s, vyčkávám na automatickou expiraci
   - Technicky: `step(f'Zaznamenána doba blokace: {wait_seconds} s, vyčkávám na automatickou expiraci')`
12. ⚙️ **Krok:** `page.wait_for_function(f'() => new Promise(r => setTimeout(r, {(wait_seconds + 2) * 1000}))', timeout=75000)`
13. ⚙️ **Krok:** `with:` – *Řídicí blok (with)*
14. ⚙️ **Krok:** `self.login_page.login(user_email, valid_pass)`
15. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.login_page.base_url}/courses', timeout=15000)`
16. 🔍 **Kontrola:** Ověřeno úspěšné přihlášení po automatickém vypršení doby blokace
   - Technicky: `expect(self.navbar.logout_button).to_be_visible()`

#### `TestDemoRateLimiting` -> `test_tc_us08_05_rate_limit_isolation_per_account` (řádek 120)

**Popis:** [TC-US08-05] Izolace počítadla neúspěšných pokusů na konkrétní e-mailovou adresu.

**Souhrn:** `9` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `email_b = f'rate_user_b_{uuid.uuid4().hex[:6]}@example.com'` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `pass_b = 'HesloBeta123!'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `self._register_user(page, email_b, pass_b)`
4. ⚙️ **Krok:** `self.navbar.logout()`
5. ⚙️ **Krok:** `self.login_page.navigate()`
6. ⚙️ **Krok:** `email_a = f'rate_user_a_{uuid.uuid4().hex[:6]}@example.com'` – *Příprava testovacích dat*
7. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
8. ⚙️ **Krok:** `self.login_page.login_with_response(email_a, 'WrongPassA123!')`
9. 🔍 **Kontrola:** Účet A byl úspěšně zablokován rate limiterem
   - Technicky: `expect(self.login_page.error_message).to_contain_text('Too many login attempts')`
10. ⚙️ **Krok:** `self.login_page.login(email_b, pass_b)`
11. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.login_page.base_url}/courses', timeout=15000)`
12. 🔍 **Kontrola:** Účet B se úspěšně přihlásil: Rate limiter izoluje pokusy per účet a nezpůsobuje DoS
   - Technicky: `expect(self.navbar.logout_button).to_be_visible()`

#### `TestDemoRateLimiting` -> `test_tc_us08_06_case_sensitivity_and_normalization_unification` (řádek 142)

**Popis:** [TC-US08-06] Sjednocení počítadla při různé velikosti písmen v e-mailu (Case Sensitivity & Normalizace).

**Souhrn:** `6` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `base_name = f'caselimit_{uuid.uuid4().hex[:6]}'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `variants = [f'{base_name}@example.com', f'{base_name.upper()}@example.com', f'{base_name.capitalize()}@EXAMPLE.COM', f'  {base_name}@example.com  ', f'{base_name.swapcase()}@Example.Com']` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
5. ⚙️ **Krok:** `self.login_page.login_with_response(email_variant, 'WrongPassword123!')`
6. 🔍 **Kontrola:** Pokus {idx}/5 s variantou zápisu: '{email_variant}'
   - Technicky: `expect(self.login_page.error_message).to_contain_text('These credentials do not match our records.')`
7. ⚙️ **Krok:** `self.login_page.login_with_response(f'{base_name}@example.com', 'WrongPassword123!')`
8. 🔍 **Kontrola:** Pokus 6: Počítadlo správně sjednotilo normalizované varianty e-mailu a aktivovalo blokaci
   - Technicky: `expect(self.login_page.error_message).to_contain_text('Too many login attempts')`

#### `TestDemoRateLimiting` -> `test_tc_us08_07_brute_force_protection_on_non_existent_accounts` (řádek 164)

**Popis:** [TC-US08-07] Ochrana proti útokům hrubou silou na neexistující účty (Prevence User Enumeration).

**Souhrn:** `6` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `non_existent_email = f'nonexistent_{uuid.uuid4().hex[:8]}@example.com'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `wrong_pass = 'ArbitraryPassword123!'` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
5. ⚙️ **Krok:** `self.login_page.login_with_response(non_existent_email, wrong_pass)`
6. 🔍 **Kontrola:** Pokus {attempt}/5 s neexistujícím e-mailem
   - Technicky: `expect(self.login_page.error_message).to_contain_text('These credentials do not match our records.')`
7. ⚙️ **Krok:** `self.login_page.login_with_response(non_existent_email, wrong_pass)`
8. 🔍 **Kontrola:** Pokus 6: Rate Limiting aktivován i pro neexistující e-mail – prevence User Enumeration splněna
   - Technicky: `expect(self.login_page.error_message).to_contain_text('Too many login attempts')`

#### `TestDemoRateLimiting` -> `test_tc_us08_08_submission_during_active_block_and_countdown_check` (řádek 180)

**Popis:** [TC-US08-08] Pokus o odeslání přihlášení uprostřed doby aktivní blokace a kontrola odpočtu.

**Souhrn:** `13` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `probe_email = f'rate_countdown_{uuid.uuid4().hex[:6]}@example.com'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `wrong_pass = 'WrongPass123!'` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
5. ⚙️ **Krok:** `self.login_page.login_with_response(probe_email, wrong_pass)`
6. 🔍 **Kontrola:** `expect(self.login_page.error_message).to_contain_text(re.compile('Too many login attempts\\. Please try again in (\\d+) seconds\\.'))`
7. ⚙️ **Krok:** `initial_text = self.login_page.error_message.inner_text()` – *Získání hodnoty/stavu z aplikace*
8. ⚙️ **Krok:** `m1 = re.search('in (\\d+) seconds', initial_text)` – *Příprava testovacích dat*
9. ⚙️ **Krok:** `initial_seconds = int(m1.group(1)) if m1 else 60` – *Příprava testovacích dat*
10. 🔍 **Kontrola:** Zaznamenán výchozí čas blokace: {initial_seconds} s
   - Technicky: `step(f'Zaznamenán výchozí čas blokace: {initial_seconds} s')`
11. ⚙️ **Krok:** `page.wait_for_function('() => new Promise(r => setTimeout(r, 2500))')`
12. ⚙️ **Krok:** `resp = self.login_page.login_with_response(probe_email, wrong_pass)` – *Příprava testovacích dat*
13. 🔍 **Kontrola:** `assert resp.status in (302, 422, 429)`
14. 🔍 **Kontrola:** `expect(self.login_page.error_message).to_contain_text('Too many login attempts')`
15. ⚙️ **Krok:** `updated_text = self.login_page.error_message.inner_text()` – *Získání hodnoty/stavu z aplikace*
16. ⚙️ **Krok:** `m2 = re.search('in (\\d+) seconds', updated_text)` – *Příprava testovacích dat*
17. ⚙️ **Krok:** `updated_seconds = int(m2.group(1)) if m2 else initial_seconds` – *Příprava testovacích dat*
18. 🔍 **Kontrola:** Čas odpočtu se nesnížil: původní {initial_seconds} s, nový {updated_seconds} s
   - Technicky: `assert updated_seconds < initial_seconds`
19. 🔍 **Kontrola:** Ověřeno setrvání blokace a reálný odpočet zbývajícího času ({updated_seconds} s < {initial_seconds} s)
   - Technicky: `step(f'Ověřeno setrvání blokace a reálný odpočet zbývajícího času ({updated_seconds} s < {initial_seconds} s)')`

### Soubor: `tests/auth/test_register.py`
#### `TestDemoRegister` -> `test_tc_us02_01_successful_registration` (řádek 16)

**Popis:** [TC-US02-01] Úspěšná registrace nového uživatele a automatické přihlášení.

**Souhrn:** `7` akcí, `11` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. 🔍 **Kontrola:** Otevřena stránka registrace (/register)
   - Technicky: `step('Otevřena stránka registrace (/register)')`
3. 🔍 **Kontrola:** `expect(self.register_page.name_input).to_be_visible()`
4. 🔍 **Kontrola:** `expect(self.register_page.email_input).to_be_visible()`
5. 🔍 **Kontrola:** `expect(self.register_page.password_input).to_be_visible()`
6. 🔍 **Kontrola:** `expect(self.register_page.password_again_input).to_be_visible()`
7. 🔍 **Kontrola:** Ověřena přítomnost všech polí registračního formuláře
   - Technicky: `expect(self.register_page.register_button).to_be_visible()`
8. ⚙️ **Krok:** `unique_id = uuid.uuid4().hex[:8]` – *Příprava testovacích dat*
9. ⚙️ **Krok:** `name = f'User {unique_id}'` – *Příprava testovacích dat*
10. ⚙️ **Krok:** `email = f'test_reg_{unique_id}@example.com'` – *Příprava testovacích dat*
11. ⚙️ **Krok:** `password = 'Password123!'` – *Příprava testovacích dat*
12. ⚙️ **Krok:** `self.register_page.register(name, email, password, password)`
13. 🔍 **Kontrola:** Vyplněn formulář novými údaji (e-mail: {email}) a odeslán
   - Technicky: `step(f'Vyplněn formulář novými údaji (e-mail: {email}) a odeslán')`
14. 🔍 **Kontrola:** Ověřeno automatické přihlášení a přesměrování na /home (AC-1, AC-7)
   - Technicky: `expect(page).to_have_url(f'{self.register_page.base_url}/home')`
15. ⚙️ **Krok:** `home_page = HomePage(page)` – *Příprava testovacích dat*
16. 🔍 **Kontrola:** `expect(home_page.welcome_section).to_contain_text(f'Vítej uživateli {name}!')`
17. 🔍 **Kontrola:** `expect(self.register_page.navbar.logout_button).to_be_visible()`
18. 🔍 **Kontrola:** Ověřena uvítací zpráva pro uživatele {name}, tlačítko odhlášení a zánik odkazu pro přihlášení
   - Technicky: `expect(self.register_page.navbar.login_link).not_to_be_visible()`

#### `TestDemoRegister` -> `test_tc_us02_02_empty_form_validation` (řádek 46)

**Popis:** [TC-US02-02] Validace povinných polí při odeslání prázdného formuláře.

**Souhrn:** `2` akcí, `9` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. 🔍 **Kontrola:** Otevřena stránka registrace
   - Technicky: `step('Otevřena stránka registrace')`
3. ⚙️ **Krok:** `self.register_page.register_button.click()`
4. 🔍 **Kontrola:** Kliknuto na tlačítko registrace bez vyplnění údajů
   - Technicky: `step('Kliknuto na tlačítko registrace bez vyplnění údajů')`
5. 🔍 **Kontrola:** Ověřeno setrvání na stránce /register
   - Technicky: `expect(page).to_have_url(f'{self.register_page.base_url}/register')`
6. 🔍 **Kontrola:** `expect(self.register_page.name_error).to_be_visible()`
7. 🔍 **Kontrola:** Ověřena chybová hláška pro povinné jméno
   - Technicky: `expect(self.register_page.name_error).to_contain_text('The name field is required.')`
8. 🔍 **Kontrola:** `expect(self.register_page.email_error).to_be_visible()`
9. 🔍 **Kontrola:** Ověřena chybová hláška pro povinný e-mail
   - Technicky: `expect(self.register_page.email_error).to_contain_text('The email field is required.')`
10. 🔍 **Kontrola:** `expect(self.register_page.password_error).to_be_visible()`
11. 🔍 **Kontrola:** Ověřena chybová hláška pro povinné heslo
   - Technicky: `expect(self.register_page.password_error).to_contain_text('The password field is required.')`

#### `TestDemoRegister` -> `test_tc_us02_03_registration_duplicate_email` (řádek 69)

**Popis:** [TC-US02-03] Pokus o registraci s již existujícím e-mailem.

**Souhrn:** `2` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. 🔍 **Kontrola:** Otevřena stránka registrace
   - Technicky: `step('Otevřena stránka registrace')`
3. ⚙️ **Krok:** `self.register_page.register(name='Duplicate Tester', email=registered_user['email'], password='Password123!', password_again='Password123!')`
4. 🔍 **Kontrola:** Odeslán formulář s existujícím e-mailem: {registered_user['email']}
   - Technicky: `step(f"Odeslán formulář s existujícím e-mailem: {registered_user['email']}")`
5. 🔍 **Kontrola:** Ověřeno zamítnutí registrace a setrvání na /register
   - Technicky: `expect(page).to_have_url(f'{self.register_page.base_url}/register')`
6. 🔍 **Kontrola:** `expect(self.register_page.email_error).to_be_visible()`
7. 🔍 **Kontrola:** Ověřena chybová hláška 'The email has already been taken.'
   - Technicky: `expect(self.register_page.email_error).to_contain_text('The email has already been taken.')`

#### `TestDemoRegister` -> `test_tc_us02_04_duplicate_email_case_insensitive_and_whitespace` (řádek 89)

**Popis:** [TC-US02-04] Normalizace e-mailu a case-insensitivity unikátnosti.

**Souhrn:** `3` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. 🔍 **Kontrola:** Otevřena stránka registrace
   - Technicky: `step('Otevřena stránka registrace')`
3. ⚙️ **Krok:** `raw_email = f"  {registered_user['email'].upper()}  "` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `self.register_page.register(name='Upper Case Tester', email=raw_email, password='Password123!', password_again='Password123!')`
5. 🔍 **Kontrola:** Odeslán formulář s e-mailem s mezerami a velkými písmeny: '{raw_email}'
   - Technicky: `step(f"Odeslán formulář s e-mailem s mezerami a velkými písmeny: '{raw_email}'")`
6. 🔍 **Kontrola:** Ověřeno, že registrace byla odmítnuta a stránka zůstává na /register
   - Technicky: `expect(page).to_have_url(f'{self.register_page.base_url}/register')`
7. 🔍 **Kontrola:** `expect(self.register_page.email_error).to_be_visible()`
8. 🔍 **Kontrola:** Ověřeno odmítnutí registrace z důvodu duplicity normalizovaného e-mailu (AC-4)
   - Technicky: `expect(self.register_page.email_error).to_contain_text('The email has already been taken.')`

#### `TestDemoRegister` -> `test_tc_us02_05_password_mismatch` (řádek 110)

**Popis:** [TC-US02-05] Neshoda hesla a potvrzení hesla.

**Souhrn:** `2` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. 🔍 **Kontrola:** Otevřena stránka registrace
   - Technicky: `step('Otevřena stránka registrace')`
3. ⚙️ **Krok:** `self.register_page.register(name='Mismatch User', email='mismatch_user@example.com', password='Password123!', password_again='DifferentPassword456!')`
4. 🔍 **Kontrola:** Vyplněn formulář s rozdílnými hesly
   - Technicky: `step('Vyplněn formulář s rozdílnými hesly')`
5. 🔍 **Kontrola:** Ověřeno setrvání na /register
   - Technicky: `expect(page).to_have_url(f'{self.register_page.base_url}/register')`
6. 🔍 **Kontrola:** `expect(self.register_page.password_error).to_be_visible()`
7. 🔍 **Kontrola:** Ověřena chybová hláška 'The password field confirmation does not match.'
   - Technicky: `expect(self.register_page.password_error).to_contain_text('The password field confirmation does not match.')`

#### `TestDemoRegister` -> `test_tc_us02_06_navigation_links` (řádek 130)

**Popis:** [TC-US02-06] Ověření navigačních odkazů na stránce registrace.

**Souhrn:** `4` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. 🔍 **Kontrola:** Otevřena stránka registrace
   - Technicky: `step('Otevřena stránka registrace')`
3. 🔍 **Kontrola:** `expect(self.register_page.login_link).to_be_visible()`
4. ⚙️ **Krok:** `self.register_page.login_link.click()`
5. 🔍 **Kontrola:** Ověřen odkaz na přihlášení a úspěšné přesměrování na /login
   - Technicky: `expect(page).to_have_url(f'{self.register_page.base_url}/login')`
6. ⚙️ **Krok:** `self.register_page.navigate()`
7. 🔍 **Kontrola:** `expect(self.register_page.forgot_password_link).to_be_visible()`
8. ⚙️ **Krok:** `self.register_page.forgot_password_link.click()`
9. 🔍 **Kontrola:** Ověřen odkaz pro obnovu hesla a přesměrování na /forgot-password
   - Technicky: `expect(page).to_have_url(f'{self.register_page.base_url}/forgot-password')`

#### `TestDemoRegister` -> `test_registration_html5_email_validation` (řádek 148)

**Popis:** Ověření HTML5 validace při zadání neplatného formátu e-mailu (z data/invalid_emails.json).

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. ⚙️ **Krok:** `self.register_page.register(name='Valid Name', email=invalid_emails[0], password='Password123!', password_again='Password123!')`
3. 🔍 **Kontrola:** Ověřeno spuštění nativní HTML5 validace e-mailu
   - Technicky: `expect(self.register_page.email_input).not_to_have_js_property('validationMessage', '')`
4. 🔍 **Kontrola:** Ověřeno, že formulář se neodeslal
   - Technicky: `expect(page).to_have_url(f'{self.register_page.base_url}/register')`

#### `TestDemoRegister` -> `test_registration_passwords_are_masked` (řádek 164)

**Popis:** Ověření, že obě pole pro heslo mají atribut type='password'.

**Souhrn:** `1` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.register_page.navigate()`
2. 🔍 **Kontrola:** Ověřen atribut type='password' u prvního pole pro heslo
   - Technicky: `expect(self.register_page.password_input).to_have_attribute('type', 'password')`
3. 🔍 **Kontrola:** Ověřen atribut type='password' u potvrzovacího pole pro heslo
   - Technicky: `expect(self.register_page.password_again_input).to_have_attribute('type', 'password')`

### Soubor: `tests/auth/test_reset_password.py`
#### `TestDemoResetPassword` -> `test_tc_us06_01_successful_password_reset_with_valid_token` (řádek 19) `[xfail(reason='Defekt infrastruktury/aplikace: Nelze vygenerovat a doručit platný resetovací token kvůli vyčerpané kvótě Mailtrap (500 na /forgot-password)', strict=False)]`

**Popis:** [TC-US06-01] Úspěšné nastavení nového hesla s platným tokenem.

**Souhrn:** `2` akcí, `7` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.reset_page.open_with_token(token='platny-aktivni-token-2026', email=registered_user['email'])`
2. 🔍 **Kontrola:** Otevřen formulář pro nastavení nového hesla s platným tokenem
   - Technicky: `step('Otevřen formulář pro nastavení nového hesla s platným tokenem')`
3. 🔍 **Kontrola:** `expect(self.reset_page.password_input).to_be_visible()`
4. 🔍 **Kontrola:** `expect(self.reset_page.password_again_input).to_be_visible()`
5. 🔍 **Kontrola:** Ověřena přítomnost polí pro nové heslo, potvrzení hesla a odesílacího tlačítka
   - Technicky: `expect(self.reset_page.submit_button).to_be_visible()`
6. ⚙️ **Krok:** `self.reset_page.reset_password('NoveSilneHeslo2026!', 'NoveSilneHeslo2026!')`
7. 🔍 **Kontrola:** Zadáno nové silné heslo se shodným potvrzením a odesláno
   - Technicky: `step('Zadáno nové silné heslo se shodným potvrzením a odesláno')`
8. 🔍 **Kontrola:** `expect(self.reset_page.status_div).to_be_visible()`
9. 🔍 **Kontrola:** Ověřeno potvrzení o úspěšné změně hesla a nabídka odkazu na přihlášení
   - Technicky: `expect(self.reset_page.login_link).to_be_visible()`

#### `TestDemoResetPassword` -> `test_tc_us06_02_validation_password_mismatch` (řádek 39)

**Popis:** [TC-US06-02] Validace neshody nového hesla a kontrolního potvrzení.

**Souhrn:** `2` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.reset_page.open_with_token(token='sample-token', email='test@example.com')`
2. 🔍 **Kontrola:** Otevřen formulář resetu hesla
   - Technicky: `step('Otevřen formulář resetu hesla')`
3. ⚙️ **Krok:** `self.reset_page.reset_password('HesloABC123!', 'HesloXYZ789!')`
4. 🔍 **Kontrola:** Zadána odlišná hesla do pole pro nové heslo a potvrzení
   - Technicky: `step('Zadána odlišná hesla do pole pro nové heslo a potvrzení')`
5. 🔍 **Kontrola:** `expect(self.reset_page.password_error).to_be_visible()`
6. 🔍 **Kontrola:** Ověřeno zobrazení validační chyby při neshodě hesel
   - Technicky: `expect(self.reset_page.password_error).to_contain_text('The password field confirmation does not match.')`

#### `TestDemoResetPassword` -> `test_tc_us06_03_invalid_or_tampered_token_rejection` (řádek 55) `[xfail(reason="Defekt aplikace: Frontend na /password-reset nezobrazuje v UI chybovou hlášku neplatného tokenu ('This password reset token is invalid'), ačkoliv server správně vrací 422", strict=False)]`

**Popis:** [TC-US06-03] Pokus o nastavení hesla s neplatným nebo pozměněným tokenem.

**Souhrn:** `5` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.reset_page.open_with_token(token='neplatny_token_12345', email=registered_user['email'])`
2. 🔍 **Kontrola:** Otevřen formulář resetu hesla s neplatným/pozměněným tokenem
   - Technicky: `step('Otevřen formulář resetu hesla s neplatným/pozměněným tokenem')`
3. ⚙️ **Krok:** `with:` – *Řídicí blok (with)*
4. ⚙️ **Krok:** `self.reset_page.reset_password('NovePlatneHeslo123!', 'NovePlatneHeslo123!')`
5. ⚙️ **Krok:** `resp = resp_info.value` – *Příprava testovacích dat*
6. 🔍 **Kontrola:** Server nevrátil 422 pro neplatný token, ale: {resp.status}
   - Technicky: `assert resp.status == 422`
7. ⚙️ **Krok:** `body = resp.json()` – *Příprava testovacích dat*
8. 🔍 **Kontrola:** Ověřeno, že server striktně odmítl neplatný token s kódem 422
   - Technicky: `assert 'password reset token is invalid' in body.get('message', '').lower() or any(('invalid' in err.lower() for err_list in body.get('errors', {}).values() for err in err_list))`
9. 🔍 **Kontrola:** Ověřeno zobrazení chybové zprávy pro uživatele v UI
   - Technicky: `expect(self.reset_page.status_div).to_be_visible()`

#### `TestDemoResetPassword` -> `test_tc_us06_04_expired_or_already_used_token_rejection` (řádek 83) `[xfail(reason='Defekt aplikace: Frontend na /password-reset nezobrazuje v UI chybovou hlášku expirovaného/použitého tokenu, ačkoliv server správně vrací 422', strict=False)]`

**Popis:** [TC-US06-04] Pokus o použití vypršeného nebo již jednou použitého tokenu.

**Souhrn:** `4` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.reset_page.open_with_token(token='expired-token-session-999', email=registered_user['email'])`
2. 🔍 **Kontrola:** Otevřen formulář s expirovaným/použitým tokenem
   - Technicky: `step('Otevřen formulář s expirovaným/použitým tokenem')`
3. ⚙️ **Krok:** `with:` – *Řídicí blok (with)*
4. ⚙️ **Krok:** `self.reset_page.reset_password('DalsiNoveHeslo123!', 'DalsiNoveHeslo123!')`
5. ⚙️ **Krok:** `resp = resp_info.value` – *Příprava testovacích dat*
6. 🔍 **Kontrola:** Server nevrátil 422 pro expirovaný token, ale: {resp.status}
   - Technicky: `assert resp.status == 422`
7. 🔍 **Kontrola:** Ověřeno, že server odmítl expirovaný token se stavovým kódem 422
   - Technicky: `step('Ověřeno, že server odmítl expirovaný token se stavovým kódem 422')`
8. 🔍 **Kontrola:** Ověřeno zobrazení informace o vypršení platnosti odkazu v UI
   - Technicky: `expect(self.reset_page.status_div).to_be_visible()`

#### `TestDemoResetPassword` -> `test_tc_us06_05_security_rules_minimum_password_strength` (řádek 103)

**Popis:** [TC-US06-05] Kontrola bezpečnostních pravidel pro minimální sílu hesla.

**Souhrn:** `2` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.reset_page.open_with_token(token='sample-token', email='test@example.com')`
2. 🔍 **Kontrola:** Otevřen formulář resetu hesla
   - Technicky: `step('Otevřen formulář resetu hesla')`
3. ⚙️ **Krok:** `self.reset_page.reset_password('123', '123')`
4. 🔍 **Kontrola:** Zadáno příliš krátké heslo (3 znaky)
   - Technicky: `step('Zadáno příliš krátké heslo (3 znaky)')`
5. 🔍 **Kontrola:** `expect(self.reset_page.password_error).to_be_visible()`
6. 🔍 **Kontrola:** Ověřeno odmítnutí slabého hesla a zobrazení požadavku na minimálně 8 znaků
   - Technicky: `expect(self.reset_page.password_error).to_contain_text('The password field must be at least 8 characters.')`

---

<a id="oblast-courses"></a>
## Oblast: Courses
*Počet testů v oblasti: **52***

### Soubor: `tests/courses/test_course_capacity.py`
> *Automatizované testy pro US-11: Vizuální indikace a zamezení zápisu při naplněné kapacitě.

Pokrývá test casy:
- [TC-US11-01] Zobrazení tlačítka registrace u běhu s volnou kapacitou a přesměrování
- [TC-US11-02] Skrytí registrace a indikace plné obsazenosti u vyčerpané kapacity
- [TC-US11-03] Zamezení přímého zápisu na plně obsazený běh přes přímou URL*

#### `TestCourseCapacity` -> `test_tc_us11_01_enroll_button_for_available_capacity` (řádek 35)

**Popis:** [TC-US11-01] Zobrazení tlačítka registrace u běhu s volnou kapacitou a přesměrování.

**Souhrn:** `17` akcí, `7` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_customer(page, registered_user)`
2. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
3. 🔍 **Kontrola:** `expect(self.courses_page.iterations_heading).to_be_visible()`
4. ⚙️ **Krok:** `cards = self.courses_page.iteration_cards` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `card_count = cards.count()` – *Získání hodnoty/stavu z aplikace*
6. 🔍 **Kontrola:** Detail kurzu musí obsahovat alespoň jeden běh
   - Technicky: `assert card_count > 0`
7. ⚙️ **Krok:** `free_card = None` – *Příprava testovacích dat*
8. ⚙️ **Krok:** `free_iteration_id = None` – *Příprava testovacích dat*
9. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
10. ⚙️ **Krok:** `card = cards.nth(i)` – *Příprava testovacích dat*
11. ⚙️ **Krok:** `text = card.inner_text()` – *Získání hodnoty/stavu z aplikace*
12. ⚙️ **Krok:** `m = re.search('Kapacita:\\s*(\\d+)/(\\d+)', text)` – *Příprava testovacích dat*
13. ⚙️ **Krok:** `if m and int(m.group(1)) < int(m.group(2)):` – *Řídicí blok (if)*
14. ⚙️ **Krok:** `free_card = card` – *Příprava testovacích dat*
15. ⚙️ **Krok:** `tid = card.get_attribute('data-testid') or ''` – *Příprava testovacích dat*
16. ⚙️ **Krok:** `free_iteration_id = tid.replace('iteration_', '')` – *Příprava testovacích dat*
17. 🔍 **Kontrola:** V nabídce nebyl nalezen žádný běh s volnou kapacitou
   - Technicky: `assert free_card is not None`
18. 🔍 **Kontrola:** Nalezen běh s volnou kapacitou: ID {free_iteration_id}
   - Technicky: `step(f'Nalezen běh s volnou kapacitou: ID {free_iteration_id}')`
19. ⚙️ **Krok:** `enroll_btn = self.courses_page.get_iteration_enroll_button(free_card)` – *Příprava testovacích dat*
20. 🔍 **Kontrola:** Ověřeno zobrazení tlačítka 'Nezávazná registrace' u termínu s volnou kapacitou
   - Technicky: `expect(enroll_btn).to_be_visible()`
21. ⚙️ **Krok:** `with:` – *Řídicí blok (with)*
22. ⚙️ **Krok:** `enroll_btn.click()`
23. 🔍 **Kontrola:** `expect(page).to_have_url(re.compile('.*/courses/\\d+/register'))`
24. 🔍 **Kontrola:** Ověřeno přesměrování do objednávkového formuláře (/courses/<iteration_id>/register)
   - Technicky: `expect(self.enroll_page.registration_section).to_be_visible()`

#### `TestCourseCapacity` -> `test_tc_us11_02_fully_booked_iteration_indication` (řádek 76)

**Popis:** [TC-US11-02] Skrytí registrace a indikace plné obsazenosti u vyčerpané kapacity.

**Souhrn:** `12` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_customer(page, registered_user)`
2. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
3. 🔍 **Kontrola:** `expect(self.courses_page.iterations_heading).to_be_visible()`
4. ⚙️ **Krok:** `cards = self.courses_page.iteration_cards` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `card_count = cards.count()` – *Získání hodnoty/stavu z aplikace*
6. 🔍 **Kontrola:** Detail kurzu musí obsahovat alespoň jeden běh
   - Technicky: `assert card_count > 0`
7. ⚙️ **Krok:** `full_card = None` – *Příprava testovacích dat*
8. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
9. ⚙️ **Krok:** `card = cards.nth(i)` – *Příprava testovacích dat*
10. ⚙️ **Krok:** `text = card.inner_text()` – *Získání hodnoty/stavu z aplikace*
11. ⚙️ **Krok:** `m = re.search('Kapacita:\\s*(\\d+)/(\\d+)', text)` – *Příprava testovacích dat*
12. ⚙️ **Krok:** `if m and int(m.group(1)) >= int(m.group(2)):` – *Řídicí blok (if)*
13. ⚙️ **Krok:** `full_card = card` – *Příprava testovacích dat*
14. 🔍 **Kontrola:** Nalezen plně obsazený běh: {m.group(0)}
   - Technicky: `step(f'Nalezen plně obsazený běh: {m.group(0)}')`
15. 🔍 **Kontrola:** V nabídce nebyl nalezen žádný plně obsazený běh pro ověření
   - Technicky: `assert full_card is not None`
16. ⚙️ **Krok:** `enroll_btn = self.courses_page.get_iteration_enroll_button(full_card)` – *Příprava testovacích dat*
17. 🔍 **Kontrola:** Ověřeno, že tlačítko pro registraci je pro plně obsazený běh skryto
   - Technicky: `expect(enroll_btn).not_to_be_visible()`

#### `TestCourseCapacity` -> `test_tc_us11_03_direct_url_access_to_fully_booked_iteration` (řádek 109) `[xfail(reason='Defekt aplikace: Backend neověřuje kapacitu a umožní odeslat registraci na plně obsazený běh bez zamítnutí', strict=False)]`

**Popis:** [TC-US11-03] Zamezení přímého zápisu na plně obsazený běh přes přímou URL.

**Souhrn:** `4` akcí, `1` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_customer(page, registered_user)`
2. ⚙️ **Krok:** `full_iteration_id = '1'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `self.enroll_page.open_for_iteration(full_iteration_id)`
4. ⚙️ **Krok:** `self.enroll_page.fill_and_submit('27082440', '+420777123456')`
5. 🔍 **Kontrola:** Ověřeno zamezení registrace na plně obsazený běh
   - Technicky: `expect(self.enroll_page.capacity_error).to_be_visible(timeout=5000)`

### Soubor: `tests/courses/test_course_create.py`
> *Automatizované testy pro US-14: Vytvoření nového kurzu s kontrolou poměru stran obrázku.

Pokrývá test casy:
- [TC-US14-01] Úspěšné vytvoření kurzu lektorem s obrázkem v poměru 16:9
- [TC-US14-02] Validace povinných polí a číselných hodnot kapacity a ceny
- [TC-US14-03] Odmítnutí náhledového obrázku s nevyhovujícím poměrem stran
- [TC-US14-04] Zamezení přístupu k tvorbě kurzu pro zákazníka a nepřihlášeného hosta (RBAC)
- [TC-US14-05] Akceptace obrázku v rámci povolené 5% odchylky poměru stran*

#### `TestCourseCreate` -> `test_tc_us14_01_create_course_success_with_16_9_image` (řádek 47)

**Popis:** [TC-US14-01] Úspěšné vytvoření kurzu lektorem s obrázkem v poměru 16:9.

**Souhrn:** `9` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `valid_img = create_png_image(tmp_path / 'course_16_9.png', width=1920, height=1080)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `unique_suffix = uuid.uuid4().hex[:6]` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `course_name = f'Playwright Kurz {unique_suffix}'` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `course_desc = 'Kompletní kurz zaměřený na Playwright a Pytest od základů po CI/CD.'` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
6. ⚙️ **Krok:** `self.course_create_page.navigate()`
7. 🔍 **Kontrola:** `expect(page).to_have_url(self.course_create_page.url)`
8. 🔍 **Kontrola:** Otevřen formulář pro vytvoření kurzu /courses/create
   - Technicky: `expect(self.course_create_page.heading).to_be_visible()`
9. ⚙️ **Krok:** `dialog_messages = []` – *Příprava testovacích dat*
10. ⚙️ **Krok:** `page.on('dialog', lambda d: (dialog_messages.append(d.message), d.accept()))`
11. ⚙️ **Krok:** `self.course_create_page.create_course(name=course_name, description=course_desc, capacity=15, price=7500, image_path=str(valid_img.resolve()))`
12. 🔍 **Kontrola:** Při nahrání validního 16:9 obrázku se zobrazil neočekávaný dialog: {dialog_messages}
   - Technicky: `assert len(dialog_messages) == 0`
13. 🔍 **Kontrola:** Ověřeno úspěšné odeslání a přesměrování do přehledu kurzů
   - Technicky: `expect(page).to_have_url(re.compile('.*/courses/?$'), timeout=10000)`

#### `TestCourseCreate` -> `test_tc_us14_02_validation_of_required_fields_and_numeric_values` (řádek 84) `[xfail(reason='Defekt aplikace: Formulář postrádá klientskou i serverovou validaci povinných polí a ukládá prázdný kurz', strict=False)]`

**Popis:** [TC-US14-02] Validace povinných polí a číselných hodnot kapacity a ceny.

**Souhrn:** `4` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
2. ⚙️ **Krok:** `self.course_create_page.navigate()`
3. ⚙️ **Krok:** `self.course_create_page.create_course(name='', description='', capacity='', price='')`
4. 🔍 **Kontrola:** Ověřeno, že prázdný formulář nebyl odeslán
   - Technicky: `expect(page).to_have_url(self.course_create_page.url)`
5. ⚙️ **Krok:** `self.course_create_page.create_course(name='Test Neplatná Data', description='Popis', capacity=-5, price='zdarma')`
6. 🔍 **Kontrola:** Ověřeno, že záporná kapacita a nečíselná cena jsou odmítnuty
   - Technicky: `expect(page).to_have_url(self.course_create_page.url)`

#### `TestCourseCreate` -> `test_tc_us14_03_rejection_of_image_with_invalid_aspect_ratio` (řádek 108)

**Popis:** [TC-US14-03] Odmítnutí náhledového obrázku s nevyhovujícím poměrem stran.

**Souhrn:** `10` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `square_img = create_png_image(tmp_path / 'square_img.png', width=800, height=800)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `alert_messages = []` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `page.on('dialog', handle_dialog)`
4. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
5. ⚙️ **Krok:** `self.course_create_page.navigate()`
6. ⚙️ **Krok:** `self.course_create_page.name_input.fill('Kurz s chybným obrázkem')`
7. ⚙️ **Krok:** `self.course_create_page.description_input.fill('Popis kurzu')`
8. ⚙️ **Krok:** `self.course_create_page.capacity_input.fill('10')`
9. ⚙️ **Krok:** `self.course_create_page.price_input.fill('5000')`
10. ⚙️ **Krok:** `self.course_create_page.image_input.set_input_files(str(square_img.resolve()))`
11. 🔍 **Kontrola:** `expect(self.course_create_page.image_input).to_have_value('')`
12. 🔍 **Kontrola:** Očekávané varovné hlášení o poměru stran nebylo zobrazeno: {alert_messages}
   - Technicky: `assert any(('správný poměr stran' in msg for msg in alert_messages))`
13. 🔍 **Kontrola:** Ověřeno zamítnutí obrázku s poměrem stran 1:1 a zobrazení varovného alertu
   - Technicky: `step('Ověřeno zamítnutí obrázku s poměrem stran 1:1 a zobrazení varovného alertu')`

#### `TestCourseCreate` -> `test_tc_us14_04_prevention_of_course_creation_for_customer_and_guest_rbac` (řádek 145) `[xfail(reason='Defekt aplikace (RBAC): Zákazník má neomezený přístup na formulář /courses/create', strict=False)]`

**Popis:** [TC-US14-04] Zamezení přístupu k tvorbě kurzu pro zákazníka a nepřihlášeného hosta (RBAC).

**Souhrn:** `5` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_customer(page, registered_user)`
2. ⚙️ **Krok:** `self.courses_page.navigate()`
3. 🔍 **Kontrola:** Ověřeno, že zákazník nevidí v přehledu tlačítko 'Přidat kurz'
   - Technicky: `expect(self.courses_page.add_course_button).not_to_be_visible()`
4. ⚙️ **Krok:** `self.course_create_page.navigate()`
5. 🔍 **Kontrola:** Ověřeno, že zákazník nemá přístup k formuláři vytvoření kurzu
   - Technicky: `expect(self.course_create_page.heading).not_to_be_visible()`
6. ⚙️ **Krok:** `page.context.clear_cookies()`
7. ⚙️ **Krok:** `self.course_create_page.navigate()`
8. 🔍 **Kontrola:** Ověřeno, že nepřihlášený host nemá přístup k formuláři vytvoření kurzu
   - Technicky: `expect(self.course_create_page.heading).not_to_be_visible()`

#### `TestCourseCreate` -> `test_tc_us14_05_acceptance_of_image_within_5_percent_aspect_ratio_tolerance` (řádek 170) `[xfail(reason='Defekt aplikace: Kontrola poměru stran používá chybný vzorec Math.abs(g-w) < 0.05 místo relativní 5% tolerance, takže odmítá obrázek 1280x750 s relativní odchylkou ~4 %', strict=False)]`

**Popis:** [TC-US14-05] Akceptace obrázku v rámci povolené 5% odchylky poměru stran.

**Souhrn:** `6` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `tolerated_img = create_png_image(tmp_path / 'tolerated_img.png', width=1280, height=750)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `alert_messages = []` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `page.on('dialog', handle_dialog)`
4. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
5. ⚙️ **Krok:** `self.course_create_page.navigate()`
6. ⚙️ **Krok:** `self.course_create_page.image_input.set_input_files(str(tolerated_img.resolve()))`
7. 🔍 **Kontrola:** `expect(self.course_create_page.image_input).not_to_have_value('')`
8. 🔍 **Kontrola:** Pro obrázek v toleranci 5 % se neměl zobrazit žádný varovný alert: {alert_messages}
   - Technicky: `assert len(alert_messages) == 0`
9. 🔍 **Kontrola:** Ověřeno, že obrázek v toleranci do 5 % odchylky byl úspěšně akceptován
   - Technicky: `step('Ověřeno, že obrázek v toleranci do 5 % odchylky byl úspěšně akceptován')`

### Soubor: `tests/courses/test_course_detail.py`
> *Automatizované testy pro US-10: Zobrazení detailu kurzu a vypsaných termínů.

Pokrývá test casy:
- [TC-US10-01] Zobrazení kompletních informací o kurzu a seznamu vypsaných běhů
- [TC-US10-02] Ověření formátu a výpočtu poměru obsazenosti termínu (např. 3/12)
- [TC-US10-03] Zobrazení výzvy k vytvoření účtu pro nepřihlášeného návštěvníka na detailu kurzu
- [TC-US10-04] Zpracování požadavku na neexistující ID kurzu*

#### `TestCourseDetail` -> `test_tc_us10_01_course_detail_content_and_iterations_list` (řádek 25)

**Popis:** [TC-US10-01] Zobrazení kompletních informací o kurzu a seznamu vypsaných běhů.

**Souhrn:** `10` akcí, `18` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
3. 🔍 **Kontrola:** Ověřen kontejner detailu kurzu
   - Technicky: `expect(self.courses_page.course_detail).to_be_visible()`
4. ⚙️ **Krok:** `first_name = self.courses_page.course_names.first` – *Příprava testovacích dat*
5. 🔍 **Kontrola:** `expect(first_name).to_be_visible()`
6. ⚙️ **Krok:** `name_text = first_name.inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
7. 🔍 **Kontrola:** Název kurzu na detailu nesmí být prázdný
   - Technicky: `assert len(name_text) > 0`
8. 🔍 **Kontrola:** Ověřen název kurzu: '{name_text}'
   - Technicky: `step(f"Ověřen název kurzu: '{name_text}'")`
9. ⚙️ **Krok:** `first_desc = self.courses_page.course_descriptions.first` – *Příprava testovacích dat*
10. 🔍 **Kontrola:** `expect(first_desc).to_be_visible()`
11. 🔍 **Kontrola:** Popis kurzu nesmí být prázdný
   - Technicky: `assert len(first_desc.inner_text().strip()) > 0`
12. 🔍 **Kontrola:** Ověřen podrobný popis kurzu
   - Technicky: `step('Ověřen podrobný popis kurzu')`
13. ⚙️ **Krok:** `first_price = self.courses_page.course_prices.first` – *Příprava testovacích dat*
14. 🔍 **Kontrola:** `expect(first_price).to_be_visible()`
15. ⚙️ **Krok:** `price_text = first_price.inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
16. 🔍 **Kontrola:** Cena neodpovídá celým Kč: '{price_text}'
   - Technicky: `assert re.search('Cena:\\s*\\d+\\s*Kč', price_text)`
17. 🔍 **Kontrola:** Ověřena cena kurzu: '{price_text}'
   - Technicky: `step(f"Ověřena cena kurzu: '{price_text}'")`
18. ⚙️ **Krok:** `img = self.courses_page.course_detail_image` – *Příprava testovacích dat*
19. 🔍 **Kontrola:** Ověřen náhledový obrázek kurzu
   - Technicky: `expect(img).to_be_visible()`
20. 🔍 **Kontrola:** `expect(self.courses_page.iterations_heading).to_be_visible()`
21. 🔍 **Kontrola:** Ověřen nadpis sekce vypsaných běhů
   - Technicky: `expect(self.courses_page.iterations_heading).to_contain_text('Vypsané běhy kurzu')`
22. ⚙️ **Krok:** `first_iteration = self.courses_page.iteration_cards.first` – *Příprava testovacích dat*
23. 🔍 **Kontrola:** `expect(first_iteration).to_be_visible()`
24. ⚙️ **Krok:** `iteration_text = first_iteration.inner_text()` – *Získání hodnoty/stavu z aplikace*
25. 🔍 **Kontrola:** Chybí informace o zahájení běhu
   - Technicky: `assert 'Zahájení:' in iteration_text`
26. 🔍 **Kontrola:** Chybí informace o ukončení běhu
   - Technicky: `assert 'Ukončení:' in iteration_text`
27. 🔍 **Kontrola:** Chybí informace o kapacitě běhu
   - Technicky: `assert 'Kapacita:' in iteration_text`
28. 🔍 **Kontrola:** Ověřeny povinné údaje běhu kurzu: zahájení, ukončení a kapacita
   - Technicky: `step('Ověřeny povinné údaje běhu kurzu: zahájení, ukončení a kapacita')`

#### `TestCourseDetail` -> `test_tc_us10_02_iteration_capacity_ratio_format` (řádek 73)

**Popis:** [TC-US10-02] Ověření formátu a výpočtu poměru obsazenosti termínu (např. 3/12).

**Souhrn:** `6` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
3. ⚙️ **Krok:** `first_iteration = self.courses_page.iteration_cards.first` – *Příprava testovacích dat*
4. 🔍 **Kontrola:** `expect(first_iteration).to_be_visible()`
5. ⚙️ **Krok:** `iteration_text = first_iteration.inner_text()` – *Získání hodnoty/stavu z aplikace*
6. ⚙️ **Krok:** `capacity_match = re.search('Kapacita:\\s*(\\d+)/(\\d+)', iteration_text)` – *Příprava testovacích dat*
7. 🔍 **Kontrola:** Formát kapacity poměrem X/Y nenalezen v textu: '{iteration_text}'
   - Technicky: `assert capacity_match`
8. ⚙️ **Krok:** `enrolled, total = (int(capacity_match.group(1)), int(capacity_match.group(2)))` – *Příprava testovacích dat*
9. 🔍 **Kontrola:** Počet zapsaných studentů nesmí být záporný
   - Technicky: `assert enrolled >= 0`
10. 🔍 **Kontrola:** Celková kapacita kurzu musí být větší než 0
   - Technicky: `assert total > 0`
11. 🔍 **Kontrola:** Ověřen formát kapacity poměrem: {capacity_match.group(0)} (zapsáno: {enrolled}, celkem: {total})
   - Technicky: `step(f'Ověřen formát kapacity poměrem: {capacity_match.group(0)} (zapsáno: {enrolled}, celkem: {total})')`

#### `TestCourseDetail` -> `test_tc_us10_03_registration_prompt_for_anonymous_user_on_detail` (řádek 91)

**Popis:** [TC-US10-03] Zobrazení výzvy k vytvoření účtu pro nepřihlášeného návštěvníka na detailu kurzu.

**Souhrn:** `4` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
3. 🔍 **Kontrola:** Ověřena výzva k vytvoření účtu na detailu kurzu
   - Technicky: `expect(self.courses_page.registration_prompt).to_be_visible()`
4. 🔍 **Kontrola:** `expect(self.courses_page.registration_link).to_be_visible()`
5. ⚙️ **Krok:** `with:` – *Řídicí blok (with)*
6. ⚙️ **Krok:** `self.courses_page.registration_link.click()`
7. 🔍 **Kontrola:** Ověřeno přesměrování z detailu kurzu na registrační formulář /register
   - Technicky: `expect(page).to_have_url(re.compile('.*/register'))`

#### `TestCourseDetail` -> `test_tc_us10_04_non_existent_course_id_handling` (řádek 111) `[xfail(reason='Aplikace pro neexistující kurz nevrací HTTP 404 Not Found ani chybovou stránku, ale vrací stavový kód 200 a prázdný kontejner', strict=False)]`

**Popis:** [TC-US10-04] Zpracování požadavku na neexistující ID kurzu.

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `response = page.goto(f'{self.courses_page.base_url}/courses/999999')` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `page.wait_for_load_state('networkidle')`
3. 🔍 **Kontrola:** Očekáván HTTP kód 404, vráceno: {response.status if response else 'None'}
   - Technicky: `assert response is not None and response.status == 404`
4. 🔍 **Kontrola:** Ověřen HTTP stav 404 pro neexistující ID kurzu
   - Technicky: `step('Ověřen HTTP stav 404 pro neexistující ID kurzu')`

### Soubor: `tests/courses/test_course_iterations.py`
> *Automatizované testy pro US-15: Vypsání nového běhu (termínu) kurzu.

Pokrývá test casy:
- [TC-US15-01] Úspěšné vypsání nového termínu kurzu lektorem a zobrazení v detailu
- [TC-US15-02] Validace povinných polí při odeslání prázdného nebo neúplného formuláře
- [TC-US15-03] Zamezení přístupu k vypsání nového termínu pro běžného studenta a hosta (RBAC)
- [TC-US15-04] Logická validace časové souslednosti termínu kurzu
- [TC-US15-05] Vypsání termínu s online formou výuky a kontrola zobrazení formátu
- [TC-US15-06] Vypsání více nezávislých termínů k jednomu kurzu a souběžné zobrazení
- [TC-US15-07] Validace data zahájení v minulosti
- [TC-US15-08] Omezení vypsání termínu k cizímu kurzu (Autorská oprávnění lektora)*

#### `TestCourseIterations` -> `test_tc_us15_01_create_new_iteration_success` (řádek 47)

**Popis:** [TC-US15-01] Úspěšné vypsání nového termínu kurzu lektorem a zobrazení v detailu.

**Souhrn:** `3` akcí, `10` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
2. ⚙️ **Krok:** `self.iteration_create_page.open_for_course(1)`
3. 🔍 **Kontrola:** Otevřen formulář pro vytvoření termínu (/courses/1/create-iteration)
   - Technicky: `expect(self.iteration_create_page.container).to_be_visible()`
4. 🔍 **Kontrola:** `expect(self.iteration_create_page.start_input).to_be_visible()`
5. 🔍 **Kontrola:** `expect(self.iteration_create_page.end_input).to_be_visible()`
6. 🔍 **Kontrola:** `expect(self.iteration_create_page.day_select).to_be_visible()`
7. 🔍 **Kontrola:** `expect(self.iteration_create_page.time_input).to_be_visible()`
8. 🔍 **Kontrola:** `expect(self.iteration_create_page.location_input).to_be_visible()`
9. 🔍 **Kontrola:** Ověřena přítomnost všech polí formuláře pro nový termín
   - Technicky: `expect(self.iteration_create_page.submit_button).to_be_visible()`
10. ⚙️ **Krok:** `self.iteration_create_page.fill_and_submit(start_date='2026-12-01', end_date='2027-01-15', day_of_week='Pondělí', time_str='18:00', location='Praha 1 - Školící centrum, Učebna B')`
11. 🔍 **Kontrola:** `expect(page).to_have_url(re.compile('.*/courses/1$'), timeout=10000)`
12. 🔍 **Kontrola:** `expect(self.courses_page.course_detail).to_be_visible()`
13. 🔍 **Kontrola:** Ověřeno úspěšné uložení termínu a přesměrování na detail kurzu /courses/1
   - Technicky: `expect(self.courses_page.iterations_heading).to_be_visible()`

#### `TestCourseIterations` -> `test_tc_us15_02_validation_of_required_fields_empty_form` (řádek 84) `[xfail(reason='Defekt aplikace: Formulář vypsání termínu postrádá validaci povinných polí a odešle i prázdný termín', strict=False)]`

**Popis:** [TC-US15-02] Validace povinných polí při odeslání prázdného nebo neúplného formuláře.

**Souhrn:** `3` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
2. ⚙️ **Krok:** `self.iteration_create_page.open_for_course(1)`
3. ⚙️ **Krok:** `self.iteration_create_page.fill_and_submit(start_date='', end_date='', day_of_week='', time_str='', location='')`
4. 🔍 **Kontrola:** `expect(self.iteration_create_page.container).to_be_visible()`
5. 🔍 **Kontrola:** Ověřeno, že prázdný formulář termínu nebyl odeslán
   - Technicky: `expect(page).to_have_url(re.compile('.*/create-iteration$'))`

#### `TestCourseIterations` -> `test_tc_us15_03_prevention_of_iteration_creation_for_student_and_guest_rbac` (řádek 107) `[xfail(reason='Defekt aplikace (RBAC): Běžný zákazník má přístup k formuláři vypsání nového termínu běhu kurzu', strict=False)]`

**Popis:** [TC-US15-03] Zamezení přístupu k vypsání nového termínu pro běžného studenta a hosta (RBAC).

**Souhrn:** `4` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_customer(page, registered_user)`
2. ⚙️ **Krok:** `self.iteration_create_page.open_for_course(1)`
3. 🔍 **Kontrola:** Ověřeno, že běžnému zákazníkovi se formulář vytvoření termínu nezobrazí
   - Technicky: `expect(self.iteration_create_page.container).not_to_be_visible()`
4. ⚙️ **Krok:** `page.context.clear_cookies()`
5. ⚙️ **Krok:** `self.iteration_create_page.open_for_course(1)`
6. 🔍 **Kontrola:** Ověřeno, že nepřihlášenému hostovi se formulář vytvoření termínu nezobrazí
   - Technicky: `expect(self.iteration_create_page.container).not_to_be_visible()`

#### `TestCourseIterations` -> `test_tc_us15_04_logical_validation_of_chronological_sequence` (řádek 127) `[xfail(reason='Defekt aplikace: Formulář postrádá logickou validaci časové souslednosti (umožní konec před začátkem)', strict=False)]`

**Popis:** [TC-US15-04] Logická validace časové souslednosti termínu kurzu.

**Souhrn:** `3` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
2. ⚙️ **Krok:** `self.iteration_create_page.open_for_course(1)`
3. ⚙️ **Krok:** `self.iteration_create_page.fill_and_submit(start_date='2026-12-15', end_date='2026-11-01', day_of_week='Úterý', time_str='18:00', location='Praha')`
4. 🔍 **Kontrola:** `expect(self.iteration_create_page.container).to_be_visible()`
5. 🔍 **Kontrola:** Ověřeno, že termín s datem ukončení před zahájením byl odmítnut
   - Technicky: `expect(page).to_have_url(re.compile('.*/create-iteration$'))`

#### `TestCourseIterations` -> `test_tc_us15_05_create_iteration_online_format` (řádek 146)

**Popis:** [TC-US15-05] Vypsání termínu s online formou výuky a kontrola zobrazení formátu.

**Souhrn:** `3` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
2. ⚙️ **Krok:** `self.iteration_create_page.open_for_course(1)`
3. ⚙️ **Krok:** `self.iteration_create_page.fill_and_submit(start_date='2027-02-01', end_date='2027-03-01', day_of_week='Středa', time_str='17:30', location='Online výuka (Google Meet / Zoom)')`
4. 🔍 **Kontrola:** `expect(page).to_have_url(re.compile('.*/courses/1$'), timeout=10000)`
5. 🔍 **Kontrola:** Ověřeno vypsání online termínu kurzu a zobrazení v detailu
   - Technicky: `expect(self.courses_page.course_detail).to_be_visible()`

#### `TestCourseIterations` -> `test_tc_us15_06_multiple_independent_iterations_for_single_course` (řádek 163)

**Popis:** [TC-US15-06] Vypsání více nezávislých termínů k jednomu kurzu a souběžné zobrazení.

**Souhrn:** `4` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
2. ⚙️ **Krok:** `self.iteration_create_page.open_for_course(1)`
3. ⚙️ **Krok:** `self.iteration_create_page.fill_and_submit(start_date='2027-04-10', end_date='2027-05-15', day_of_week='Sobota', time_str='09:00', location='Praha - Víkendová učebna')`
4. 🔍 **Kontrola:** `expect(page).to_have_url(re.compile('.*/courses/1$'), timeout=10000)`
5. 🔍 **Kontrola:** `expect(self.courses_page.course_detail).to_be_visible()`
6. 🔍 **Kontrola:** `expect(self.courses_page.iteration_cards.nth(1)).to_be_visible()`
7. ⚙️ **Krok:** `iteration_count = self.courses_page.iteration_cards.count()` – *Získání hodnoty/stavu z aplikace*
8. 🔍 **Kontrola:** Očekávány alespoň 2 vypsané termíny, nalezeno: {iteration_count}
   - Technicky: `assert iteration_count >= 2`
9. 🔍 **Kontrola:** Ověřena přítomnost {iteration_count} nezávislých termínů na detailu kurzu
   - Technicky: `step(f'Ověřena přítomnost {iteration_count} nezávislých termínů na detailu kurzu')`

#### `TestCourseIterations` -> `test_tc_us15_07_validation_of_past_start_date` (řádek 192) `[xfail(reason='Defekt aplikace: Systém nevaliduje datum zahájení a umožní vypsat termín v minulosti', strict=False)]`

**Popis:** [TC-US15-07] Validace data zahájení v minulosti.

**Souhrn:** `3` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
2. ⚙️ **Krok:** `self.iteration_create_page.open_for_course(1)`
3. ⚙️ **Krok:** `self.iteration_create_page.fill_and_submit(start_date='2020-01-01', end_date='2020-02-01', day_of_week='Pondělí', time_str='10:00', location='Minulost')`
4. 🔍 **Kontrola:** `expect(self.iteration_create_page.container).to_be_visible()`
5. 🔍 **Kontrola:** Ověřeno, že termín s datem v minulosti byl odmítnut
   - Technicky: `expect(page).to_have_url(re.compile('.*/create-iteration$'))`

#### `TestCourseIterations` -> `test_tc_us15_08_restriction_of_iteration_creation_for_foreign_course` (řádek 215) `[xfail(reason='Defekt aplikace / nepodporováno: V aplikaci neexistuje rozlišení vlastnictví kurzu mezi lektory a chybí autorizační kontrola', strict=False)]`

**Popis:** [TC-US15-08] Omezení vypsání termínu k cizímu kurzu (Autorská oprávnění lektora).

**Souhrn:** `2` akcí, `1` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
2. ⚙️ **Krok:** `self.iteration_create_page.open_for_course(999999)`
3. 🔍 **Kontrola:** Ověřeno, že lektor nemá přístup k vypsání termínu u cizího / neexistujícího kurzu
   - Technicky: `expect(self.iteration_create_page.container).not_to_be_visible()`

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

**Souhrn:** `9` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `invalid_img = create_png_image(tmp_path / 'test_1_1.png', width=100, height=100)` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `valid_img = create_png_image(tmp_path / 'test_16_9.png', width=160, height=90)` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `self._login(page, lector_user)`
4. ⚙️ **Krok:** `self.course_create_page.navigate()`
5. ⚙️ **Krok:** `alert_messages = []` – *Příprava testovacích dat*
6. ⚙️ **Krok:** `page.on('dialog', handle_dialog)`
7. ⚙️ **Krok:** `self.course_create_page.image_input.set_input_files(str(invalid_img.resolve()))`
8. 🔍 **Kontrola:** `expect(self.course_create_page.image_input).to_have_value('')`
9. 🔍 **Kontrola:** Očekávané chybové hlášení v alertu se nezobrazilo: {alert_messages}
   - Technicky: `assert any(('správný poměr stran' in msg for msg in alert_messages))`
10. 🔍 **Kontrola:** Ověřeno zamítnutí obrázku s neplatným poměrem stran (1:1) a zobrazení varovného alertu
   - Technicky: `step('Ověřeno zamítnutí obrázku s neplatným poměrem stran (1:1) a zobrazení varovného alertu')`
11. ⚙️ **Krok:** `alert_messages.clear()`
12. ⚙️ **Krok:** `self.course_create_page.image_input.set_input_files(str(valid_img.resolve()))`
13. 🔍 **Kontrola:** `expect(self.course_create_page.image_input).not_to_have_value('')`
14. 🔍 **Kontrola:** Pro platný poměr stran 16:9 se neměl zobrazit žádný alert: {alert_messages}
   - Technicky: `assert len(alert_messages) == 0`
15. 🔍 **Kontrola:** Ověřeno úspěšné přijetí obrázku s poměrem stran 16:9
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

**Souhrn:** `5` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
3. 🔍 **Kontrola:** Ověřen nadpis 'Vypsané běhy kurzu:'
   - Technicky: `expect(self.courses_page.iterations_heading).to_be_visible()`
4. ⚙️ **Krok:** `first_iteration = self.courses_page.iteration_cards.first` – *Příprava testovacích dat*
5. 🔍 **Kontrola:** `expect(first_iteration).to_be_visible()`
6. ⚙️ **Krok:** `iteration_text = first_iteration.inner_text()` – *Získání hodnoty/stavu z aplikace*
7. 🔍 **Kontrola:** `assert 'Zahájení:' in iteration_text`
8. 🔍 **Kontrola:** Ověřeno zobrazení data zahájení a ukončení běhu kurzu
   - Technicky: `assert 'Ukončení:' in iteration_text`
9. ⚙️ **Krok:** `capacity_match = re.search('Kapacita:\\s*\\d+/\\d+', iteration_text)` – *Příprava testovacích dat*
10. 🔍 **Kontrola:** Formát kapacity X/Y nenalezen: {iteration_text}
   - Technicky: `assert capacity_match`
11. 🔍 **Kontrola:** Ověřen správný formát poměru obsazenosti a kapacity: {capacity_match.group(0)}
   - Technicky: `step(f'Ověřen správný formát poměru obsazenosti a kapacity: {capacity_match.group(0)}')`

#### `TestCoursesCatalog` -> `test_course_detail_iterations_anonymous_vs_authenticated` (řádek 117)

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

#### `TestCoursesCatalog` -> `test_fully_booked_iteration_indication` (řádek 141)

**Popis:** [US-11] Ověření chování při plně obsazené kapacitě běhu kurzu (kapacita dosáhla maxima -> tlačítko zápisu je skryto/nedostupné).

**Souhrn:** `6` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
3. ⚙️ **Krok:** `first_iteration = self.courses_page.iteration_cards.first` – *Příprava testovacích dat*
4. 🔍 **Kontrola:** `expect(first_iteration).to_be_visible()`
5. ⚙️ **Krok:** `capacity_match = re.search('Kapacita:\\s*(\\d+)/(\\d+)', first_iteration.inner_text())` – *Získání hodnoty/stavu z aplikace*
6. 🔍 **Kontrola:** Formát kapacity X/Y nenalezen
   - Technicky: `assert capacity_match`
7. ⚙️ **Krok:** `users_count, capacity = (int(capacity_match.group(1)), int(capacity_match.group(2)))` – *Příprava testovacích dat*
8. 🔍 **Kontrola:** Běh by měl indikovat plnou obsazenost (obsazeno: {users_count}, kapacita: {capacity})
   - Technicky: `assert users_count >= capacity`
9. ⚙️ **Krok:** `enroll_btn = self.courses_page.get_iteration_enroll_button(first_iteration)` – *Příprava testovacích dat*
10. 🔍 **Kontrola:** Ověřeno, že pro plně obsazený běh není tlačítko registrace zobrazeno
   - Technicky: `expect(enroll_btn).not_to_be_visible()`

### Soubor: `tests/courses/test_courses_catalog.py`
> *Automatizované testy pro US-09: Prohlížení katalogu kurzů.

Pokrývá test casy:
- [TC-US09-01] Přehledné zobrazení katalogu kurzů a povinných údajů na kartách
- [TC-US09-02] Zobrazení neutrálního výchozího obrázku u kurzu bez vlastního náhledu
- [TC-US09-03] Přechod na podrobný detail kurzu z karty v katalogu
- [TC-US09-04] Zobrazení výzvy k registraci pro nepřihlášeného návštěvníka
- [TC-US09-05] Absence výzvy k registraci pro již přihlášeného uživatele*

#### `TestCoursesCatalog` -> `test_tc_us09_01_courses_catalog_display_and_card_elements` (řádek 28)

**Popis:** [TC-US09-01] Přehledné zobrazení katalogu kurzů a povinných údajů na kartách.

**Souhrn:** `10` akcí, `18` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. 🔍 **Kontrola:** Ověřena URL /courses
   - Technicky: `expect(page).to_have_url(self.courses_page.url)`
3. 🔍 **Kontrola:** Ověřen nadpis katalogu kurzů
   - Technicky: `expect(self.courses_page.title).to_be_visible()`
4. 🔍 **Kontrola:** Ověřena hlavní sekce s kurzy
   - Technicky: `expect(self.courses_page.courses_section).to_be_visible()`
5. ⚙️ **Krok:** `course_count = self.courses_page.course_names.count()` – *Získání hodnoty/stavu z aplikace*
6. 🔍 **Kontrola:** Očekáván alespoň 1 kurz v nabídce, nalezeno: {course_count}
   - Technicky: `assert course_count > 0`
7. 🔍 **Kontrola:** Nalezeno celkem {course_count} kurzů v katalogu
   - Technicky: `step(f'Nalezeno celkem {course_count} kurzů v katalogu')`
8. ⚙️ **Krok:** `first_name = self.courses_page.course_names.first` – *Příprava testovacích dat*
9. 🔍 **Kontrola:** `expect(first_name).to_be_visible()`
10. ⚙️ **Krok:** `name_text = first_name.inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
11. 🔍 **Kontrola:** Název kurzu nesmí být prázdný
   - Technicky: `assert len(name_text) > 0`
12. 🔍 **Kontrola:** Ověřen název kurzu: '{name_text}'
   - Technicky: `step(f"Ověřen název kurzu: '{name_text}'")`
13. ⚙️ **Krok:** `first_desc = self.courses_page.course_descriptions.first` – *Příprava testovacích dat*
14. 🔍 **Kontrola:** `expect(first_desc).to_be_visible()`
15. 🔍 **Kontrola:** Popis kurzu nesmí být prázdný
   - Technicky: `assert len(first_desc.inner_text().strip()) > 0`
16. 🔍 **Kontrola:** Ověřen stručný popis kurzu
   - Technicky: `step('Ověřen stručný popis kurzu')`
17. ⚙️ **Krok:** `first_capacity = self.courses_page.course_capacities.first` – *Příprava testovacích dat*
18. 🔍 **Kontrola:** `expect(first_capacity).to_be_visible()`
19. ⚙️ **Krok:** `capacity_text = first_capacity.inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
20. 🔍 **Kontrola:** Formát kapacity neodpovídá: '{capacity_text}'
   - Technicky: `assert re.search('Kapacita:\\s*\\d+', capacity_text)`
21. 🔍 **Kontrola:** Ověřena maximální kapacita: '{capacity_text}'
   - Technicky: `step(f"Ověřena maximální kapacita: '{capacity_text}'")`
22. ⚙️ **Krok:** `first_price = self.courses_page.course_prices.first` – *Příprava testovacích dat*
23. 🔍 **Kontrola:** `expect(first_price).to_be_visible()`
24. ⚙️ **Krok:** `price_text = first_price.inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
25. 🔍 **Kontrola:** Cena neodpovídá formátu celých Kč: '{price_text}'
   - Technicky: `assert re.search('Cena:\\s*\\d+\\s*Kč', price_text)`
26. 🔍 **Kontrola:** Ověřena cena zaokrouhlená na celé Kč: '{price_text}'
   - Technicky: `step(f"Ověřena cena zaokrouhlená na celé Kč: '{price_text}'")`
27. ⚙️ **Krok:** `first_img = self.courses_page.course_images.first` – *Příprava testovacích dat*
28. 🔍 **Kontrola:** Ověřen grafický náhled kurzu
   - Technicky: `expect(first_img).to_be_visible()`

#### `TestCoursesCatalog` -> `test_tc_us09_02_default_image_for_course_without_thumbnail` (řádek 83) `[xfail(reason='Aplikace neobsahuje fallback na výchozí neutrální obrázek při chybějícím souboru v úložišti (storage/app/public/... 404 vede na broken image)', strict=False)]`

**Popis:** [TC-US09-02] Zobrazení neutrálního výchozího obrázku u kurzu bez vlastního náhledu.

**Souhrn:** `7` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. ⚙️ **Krok:** `images = self.courses_page.course_images` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `img_count = images.count()` – *Získání hodnoty/stavu z aplikace*
4. 🔍 **Kontrola:** V katalogu musí být alespoň jeden obrázek kurzu
   - Technicky: `assert img_count > 0`
5. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
6. ⚙️ **Krok:** `img = images.nth(i)` – *Příprava testovacích dat*
7. 🔍 **Kontrola:** `expect(img).to_be_visible()`
8. ⚙️ **Krok:** `src = img.get_attribute('src')` – *Příprava testovacích dat*
9. 🔍 **Kontrola:** Obrázek na indexu {i} postrádá atribut src
   - Technicky: `assert src is not None and len(src) > 0`
10. ⚙️ **Krok:** `is_loaded = page.evaluate('(el) => el.complete && el.naturalWidth > 0', img.element_handle())` – *Příprava testovacích dat*
11. 🔍 **Kontrola:** Obrázek na indexu {i} nebyl korektně načten (broken image)
   - Technicky: `assert is_loaded`
12. 🔍 **Kontrola:** Ověřeno všech {img_count} obrázků v katalogu – žádný není rozbitý (broken image)
   - Technicky: `step(f'Ověřeno všech {img_count} obrázků v katalogu – žádný není rozbitý (broken image)')`

#### `TestCoursesCatalog` -> `test_tc_us09_03_navigate_to_course_detail` (řádek 103)

**Popis:** [TC-US09-03] Přechod na podrobný detail kurzu z karty v katalogu.

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
3. 🔍 **Kontrola:** Ověřeno přesměrování na URL detailu kurzu (/courses/<id>)
   - Technicky: `expect(page).to_have_url(re.compile(f'^{re.escape(self.courses_page.base_url)}/courses/\\d+$'))`
4. 🔍 **Kontrola:** Ověřeno načtení kontejneru detailu kurzu
   - Technicky: `expect(self.courses_page.course_detail).to_be_visible()`

#### `TestCoursesCatalog` -> `test_tc_us09_04_anonymous_user_registration_prompt` (řádek 114)

**Popis:** [TC-US09-04] Zobrazení výzvy k registraci pro nepřihlášeného návštěvníka.

**Souhrn:** `3` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. 🔍 **Kontrola:** `expect(self.courses_page.interest_title).to_be_visible()`
3. 🔍 **Kontrola:** Ověřena výzva k registraci pro anonymního návštěvníka
   - Technicky: `expect(self.courses_page.interest_title).to_contain_text('Máte zájem o naše kurzy?')`
4. 🔍 **Kontrola:** `expect(self.courses_page.registration_link).to_be_visible()`
5. ⚙️ **Krok:** `with:` – *Řídicí blok (with)*
6. ⚙️ **Krok:** `self.courses_page.registration_link.click()`
7. 🔍 **Kontrola:** Ověřeno přesměrování na registrační formulář /register
   - Technicky: `expect(page).to_have_url(re.compile('.*/register'))`

#### `TestCoursesCatalog` -> `test_tc_us09_05_absence_of_registration_prompt_for_authenticated_user` (řádek 129)

**Popis:** [TC-US09-05] Absence výzvy k registraci pro již přihlášeného uživatele.

**Souhrn:** `2` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `self.login_page.login(registered_user['email'], registered_user['password'])`
3. 🔍 **Kontrola:** Uživatel úspěšně přihlášen a přesměrován do katalogu kurzů
   - Technicky: `expect(page).to_have_url(f'{self.courses_page.base_url}/courses')`
4. 🔍 **Kontrola:** `expect(self.courses_page.interest_title).not_to_be_visible()`
5. 🔍 **Kontrola:** Ověřeno, že výzva k registraci se přihlášenému uživateli nezobrazuje
   - Technicky: `expect(self.courses_page.registration_link).not_to_be_visible()`

### Soubor: `tests/courses/test_enrollment.py`
> *Automatizované testy pro US-12: Nezávazná registrace na běh kurzu s validací IČO a telefonu.

Pokrývá test casy:
- [TC-US12-01] Úspěšná nezávazná registrace na běh kurzu s platným IČO a telefonem
- [TC-US12-02] Validace povinného pole a minimální délky telefonního čísla
- [TC-US12-03] Validace formální platnosti IČO pomocí váženého kontrolního součtu modulo 11
- [TC-US12-04] Zamezení zápisu na kurz pro nepovolané role (Lektor a nepřihlášený host)
- [TC-US12-05] Úspěšný zápis na kurz bez vyplnění nepovinného pole IČO*

#### `TestCourseEnrollment` -> `test_tc_us12_01_successful_enrollment_with_ico_and_phone` (řádek 39)

**Popis:** [TC-US12-01] Úspěšná nezávazná registrace na běh kurzu s platným IČO a telefonem.

**Souhrn:** `16` akcí, `8` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_customer(page, registered_user)`
2. ⚙️ **Krok:** `self.courses_page.open_first_course_detail()`
3. 🔍 **Kontrola:** `expect(self.courses_page.iterations_heading).to_be_visible()`
4. ⚙️ **Krok:** `cards = self.courses_page.iteration_cards` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `card_count = cards.count()` – *Získání hodnoty/stavu z aplikace*
6. ⚙️ **Krok:** `free_card = None` – *Příprava testovacích dat*
7. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
8. ⚙️ **Krok:** `card = cards.nth(i)` – *Příprava testovacích dat*
9. ⚙️ **Krok:** `text = card.inner_text()` – *Získání hodnoty/stavu z aplikace*
10. ⚙️ **Krok:** `m = re.search('Kapacita:\\s*(\\d+)/(\\d+)', text)` – *Příprava testovacích dat*
11. ⚙️ **Krok:** `if m and int(m.group(1)) < int(m.group(2)):` – *Řídicí blok (if)*
12. ⚙️ **Krok:** `free_card = card` – *Příprava testovacích dat*
13. 🔍 **Kontrola:** V nabídce nebyl nalezen volný běh
   - Technicky: `assert free_card is not None`
14. ⚙️ **Krok:** `enroll_btn = self.courses_page.get_iteration_enroll_button(free_card)` – *Příprava testovacích dat*
15. ⚙️ **Krok:** `with:` – *Řídicí blok (with)*
16. ⚙️ **Krok:** `enroll_btn.click()`
17. 🔍 **Kontrola:** `expect(self.enroll_page.registration_section).to_be_visible()`
18. 🔍 **Kontrola:** `expect(self.enroll_page.ico_input).to_be_visible()`
19. 🔍 **Kontrola:** Ověřena přítomnost formulářových polí pro IČO a telefon
   - Technicky: `expect(self.enroll_page.phone_input).to_be_visible()`
20. ⚙️ **Krok:** `with:` – *Řídicí blok (with)*
21. ⚙️ **Krok:** `self.enroll_page.fill_and_submit('27082440', '+420777123456')`
22. 🔍 **Kontrola:** `expect(page).to_have_url(re.compile('.*/my-courses'))`
23. 🔍 **Kontrola:** `expect(self.my_courses_page.title).to_be_visible()`
24. 🔍 **Kontrola:** Ověřeno úspěšné odeslání registrace a přesměrování na /my-courses
   - Technicky: `expect(self.my_courses_page.courses_section).to_be_visible()`

#### `TestCourseEnrollment` -> `test_tc_us12_02_validation_of_required_phone_and_minimum_length` (řádek 80)

**Popis:** [TC-US12-02] Validace povinného pole a minimální délky telefonního čísla.

**Souhrn:** `4` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_customer(page, registered_user)`
2. ⚙️ **Krok:** `self.enroll_page.open_for_iteration(32)`
3. 🔍 **Kontrola:** `expect(self.enroll_page.registration_section).to_be_visible()`
4. ⚙️ **Krok:** `self.enroll_page.fill_and_submit(ico='27082440', phone='')`
5. 🔍 **Kontrola:** Ověřena validační chyba pro prázdné telefonní číslo
   - Technicky: `expect(self.enroll_page.phone_error).to_be_visible()`
6. ⚙️ **Krok:** `self.enroll_page.fill_and_submit(ico='27082440', phone='12345')`
7. 🔍 **Kontrola:** `expect(self.enroll_page.phone_error).to_be_visible()`
8. 🔍 **Kontrola:** Ověřena validační chyba pro krátké telefonní číslo (méně než 9 číslic)
   - Technicky: `expect(self.enroll_page.phone_error).to_contain_text('Telefonní číslo musí obsahovat alespoň 9 číslic')`

#### `TestCourseEnrollment` -> `test_tc_us12_03_validation_of_ico_checksum_modulo_11` (řádek 99)

**Popis:** [TC-US12-03] Validace formální platnosti IČO pomocí váženého kontrolního součtu modulo 11.

**Souhrn:** `3` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_customer(page, registered_user)`
2. ⚙️ **Krok:** `self.enroll_page.open_for_iteration(32)`
3. 🔍 **Kontrola:** `expect(self.enroll_page.registration_section).to_be_visible()`
4. ⚙️ **Krok:** `self.enroll_page.fill_and_submit(ico='12345678', phone='+420777123456')`
5. 🔍 **Kontrola:** `expect(self.enroll_page.ico_error).to_be_visible()`
6. 🔍 **Kontrola:** Ověřeno zamítnutí registrace při neplatném kontrolním součtu IČO (chyba 'Neplatné IČO')
   - Technicky: `expect(self.enroll_page.ico_error).to_contain_text('Neplatné IČO')`

#### `TestCourseEnrollment` -> `test_tc_us12_04_prevention_of_enrollment_for_unauthorized_roles` (řádek 112)

**Popis:** [TC-US12-04] Zamezení zápisu na kurz pro nepovolané role (Lektor a nepřihlášený host).

**Souhrn:** `4` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.enroll_page.open_for_iteration(32)`
2. 🔍 **Kontrola:** Nepřihlášený návštěvník byl z přímé URL registrace přesměrován zpět
   - Technicky: `expect(page).to_have_url(re.compile('.*/courses'))`
3. ⚙️ **Krok:** `self.login_page.navigate()`
4. ⚙️ **Krok:** `self.login_page.login(lector_user['email'], lector_user['password'])`
5. ⚙️ **Krok:** `self.courses_page.navigate_to_detail(1)`
6. 🔍 **Kontrola:** `expect(self.courses_page.iterations_heading).to_be_visible()`
7. 🔍 **Kontrola:** Ověřeno, že lektorovi se tlačítka 'Nezávazná registrace' nezobrazují
   - Technicky: `expect(self.courses_page.enroll_buttons.first).not_to_be_visible()`

#### `TestCourseEnrollment` -> `test_tc_us12_05_successful_enrollment_without_optional_ico` (řádek 136) `[xfail(reason="Defekt aplikace: Pole IČO je v rozporu se specifikací validováno jako povinné (prázdné IČO vede na chybu 'Neplatné IČO')", strict=False)]`

**Popis:** [TC-US12-05] Úspěšný zápis na kurz bez vyplnění nepovinného pole IČO.

**Souhrn:** `4` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_customer(page, registered_user)`
2. ⚙️ **Krok:** `self.enroll_page.open_for_iteration(35)`
3. 🔍 **Kontrola:** `expect(self.enroll_page.registration_section).to_be_visible()`
4. ⚙️ **Krok:** `with:` – *Řídicí blok (with)*
5. ⚙️ **Krok:** `self.enroll_page.fill_and_submit(ico='', phone='+420777987654')`
6. 🔍 **Kontrola:** `expect(page).to_have_url(re.compile('.*/my-courses'))`
7. 🔍 **Kontrola:** Ověřen úspěšný zápis na kurz bez vyplnění nepovinného pole IČO
   - Technicky: `expect(self.my_courses_page.title).to_be_visible()`

### Soubor: `tests/courses/test_my_courses.py`
> *Automatizované testy pro US-13: Přehled mých zapsaných kurzů.

Pokrývá test casy:
- [TC-US13-01] Zobrazení zapsaného kurzu a kompletních organizačních informací
- [TC-US13-02] Dostupnost odkazu v navigaci a přístup do sekce pro přihlášeného zákazníka
- [TC-US13-03] Přechod na podrobný detail kurzu z karty v přehledu
- [TC-US13-04] Zamezení přístupu do sekce 'Moje kurzy' pro nepřihlášeného návštěvníka
- [TC-US13-05] Zobrazení sekce 'Moje kurzy' pro zákazníka bez aktivních zápisů (Empty State)
- [TC-US13-06] Zobrazení více souběžně zapsaných kurzů a nezávislost organizačních údajů
- [TC-US13-07] Omezení přístupu do sekce 'Moje kurzy' pro roli Lektor (RBAC)
- [TC-US13-08] Rozlišení nadcházejících kurzů a chronologické řazení termínů*

#### `TestMyCourses` -> `test_tc_us13_01_enrolled_course_display_and_organizational_info` (řádek 66)

**Popis:** [TC-US13-01] Zobrazení zapsaného kurzu a kompletních organizačních informací.

**Souhrn:** `11` akcí, `16` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_predefined_student(page)`
2. ⚙️ **Krok:** `self.my_courses_page.navigate()`
3. 🔍 **Kontrola:** Otevřena stránka /my-courses
   - Technicky: `expect(page).to_have_url(self.my_courses_page.url)`
4. 🔍 **Kontrola:** Ověřen nadpis sekce 'Moje kurzy'
   - Technicky: `expect(self.my_courses_page.title).to_be_visible()`
5. 🔍 **Kontrola:** Ověřena hlavní sekce zapsaných kurzů
   - Technicky: `expect(self.my_courses_page.courses_section).to_be_visible()`
6. ⚙️ **Krok:** `first_name = self.my_courses_page.course_names.first` – *Příprava testovacích dat*
7. 🔍 **Kontrola:** `expect(first_name).to_be_visible()`
8. ⚙️ **Krok:** `name_text = first_name.inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
9. 🔍 **Kontrola:** Název zapsaného kurzu nesmí být prázdný
   - Technicky: `assert len(name_text) > 0`
10. 🔍 **Kontrola:** Ověřen název kurzu v mých kurzech: '{name_text}'
   - Technicky: `step(f"Ověřen název kurzu v mých kurzech: '{name_text}'")`
11. ⚙️ **Krok:** `first_desc = self.my_courses_page.course_descriptions.first` – *Příprava testovacích dat*
12. 🔍 **Kontrola:** `expect(first_desc).to_be_visible()`
13. 🔍 **Kontrola:** Popis kurzu nesmí být prázdný
   - Technicky: `assert len(first_desc.inner_text().strip()) > 0`
14. 🔍 **Kontrola:** Ověřen popis kurzu
   - Technicky: `step('Ověřen popis kurzu')`
15. ⚙️ **Krok:** `first_price = self.my_courses_page.course_prices.first` – *Příprava testovacích dat*
16. 🔍 **Kontrola:** `expect(first_price).to_be_visible()`
17. ⚙️ **Krok:** `price_text = first_price.inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
18. 🔍 **Kontrola:** Cena neodpovídá celým Kč: '{price_text}'
   - Technicky: `assert re.search('Cena:\\s*\\d+\\s*Kč', price_text)`
19. 🔍 **Kontrola:** Ověřena cena kurzu: '{price_text}'
   - Technicky: `step(f"Ověřena cena kurzu: '{price_text}'")`
20. ⚙️ **Krok:** `first_from = self.my_courses_page.date_time_from.first` – *Příprava testovacích dat*
21. 🔍 **Kontrola:** Ověřeno datum zahájení kurzu (date_time_from)
   - Technicky: `expect(first_from).to_be_visible()`
22. ⚙️ **Krok:** `first_to = self.my_courses_page.date_time_to.first` – *Příprava testovacích dat*
23. 🔍 **Kontrola:** Ověřeno datum ukončení kurzu (date_time_to)
   - Technicky: `expect(first_to).to_be_visible()`
24. ⚙️ **Krok:** `first_day = self.my_courses_page.day_information.first` – *Příprava testovacích dat*
25. 🔍 **Kontrola:** Ověřen den v týdnu / čas konání lekcí
   - Technicky: `expect(first_day).to_be_visible()`
26. ⚙️ **Krok:** `first_place = self.my_courses_page.place_information.first` – *Příprava testovacích dat*
27. 🔍 **Kontrola:** Ověřeno místo konání / forma výuky
   - Technicky: `expect(first_place).to_be_visible()`

#### `TestMyCourses` -> `test_tc_us13_02_navbar_link_availability_for_customer` (řádek 120)

**Popis:** [TC-US13-02] Dostupnost odkazu v navigaci a přístup do sekce pro přihlášeného zákazníka.

**Souhrn:** `2` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_customer(page, registered_user)`
2. 🔍 **Kontrola:** Ověřena přítomnost odkazu 'Moje kurzy' v horní navigaci
   - Technicky: `expect(self.courses_page.navbar.my_courses_link).to_be_visible()`
3. ⚙️ **Krok:** `self.courses_page.navbar.my_courses_link.click()`
4. 🔍 **Kontrola:** `expect(page).to_have_url(self.my_courses_page.url)`
5. 🔍 **Kontrola:** Ověřeno úspěšné přesměrování z navigace na /my-courses
   - Technicky: `expect(self.my_courses_page.title).to_be_visible()`

#### `TestMyCourses` -> `test_tc_us13_03_navigate_to_course_detail_from_my_courses` (řádek 135)

**Popis:** [TC-US13-03] Přechod na podrobný detail kurzu z karty v přehledu.

**Souhrn:** `5` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_predefined_student(page)`
2. ⚙️ **Krok:** `self.my_courses_page.navigate()`
3. ⚙️ **Krok:** `first_detail_btn = self.my_courses_page.detail_buttons.first` – *Příprava testovacích dat*
4. 🔍 **Kontrola:** `expect(first_detail_btn).to_be_visible()`
5. ⚙️ **Krok:** `first_detail_btn.click()`
6. 🔍 **Kontrola:** `expect(page).to_have_url(re.compile('.*/courses/\\d+'))`
7. 🔍 **Kontrola:** Ověřeno přesměrování z mých kurzů na detail odpovídajícího kurzu
   - Technicky: `expect(self.courses_page.course_detail).to_be_visible()`
8. ⚙️ **Krok:** `self.courses_page.navbar.my_courses_link.click()`
9. 🔍 **Kontrola:** Ověřen úspěšný návrat zpět do přehledu 'Moje kurzy'
   - Technicky: `expect(page).to_have_url(self.my_courses_page.url)`

#### `TestMyCourses` -> `test_tc_us13_04_prevention_of_unauthenticated_access_to_my_courses` (řádek 160) `[xfail(reason='Defekt aplikace: Nepřihlášený návštěvník při přístupu na /my-courses není přesměrován na /login ani informován o nutnosti přihlášení', strict=False)]`

**Popis:** [TC-US13-04] Zamezení přístupu do sekce 'Moje kurzy' pro nepřihlášeného návštěvníka.

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.courses_page.navigate()`
2. 🔍 **Kontrola:** Ověřeno, že nepřihlášenému návštěvníkovi se odkaz 'Moje kurzy' v navigaci nezobrazuje
   - Technicky: `expect(self.courses_page.navbar.my_courses_link).not_to_be_visible()`
3. ⚙️ **Krok:** `self.my_courses_page.navigate()`
4. 🔍 **Kontrola:** Ověřeno, že systém zamezil neautorizovanému přístupu a přesměroval návštěvníka na /login nebo /courses
   - Technicky: `expect(page).to_have_url(re.compile('.*/login|.*/courses$'))`

#### `TestMyCourses` -> `test_tc_us13_05_empty_state_for_customer_without_enrollments` (řádek 172)

**Popis:** [TC-US13-05] Zobrazení sekce 'Moje kurzy' pro zákazníka bez aktivních zápisů (Empty State).

**Souhrn:** `7` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `unique_id = uuid.uuid4().hex[:6]` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `user_email = f'empty_{unique_id}@example.com'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `user_pass = 'EmptyPass123!'` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `self.register_page.navigate()`
5. ⚙️ **Krok:** `self.register_page.register(name=f'Empty User {unique_id}', email=user_email, password=user_pass, password_again=user_pass)`
6. 🔍 **Kontrola:** Zaregistrován nový uživatel bez zapsaných kurzů: {user_email}
   - Technicky: `expect(page).to_have_url(re.compile('.*/home|.*/courses'))`
7. ⚙️ **Krok:** `self.my_courses_page.navigate()`
8. 🔍 **Kontrola:** `expect(page).to_have_url(self.my_courses_page.url)`
9. 🔍 **Kontrola:** `expect(self.my_courses_page.title).to_be_visible()`
10. ⚙️ **Krok:** `course_count = self.my_courses_page.course_names.count()` – *Získání hodnoty/stavu z aplikace*
11. 🔍 **Kontrola:** Očekáván prázdný přehled (0 kurzů), nalezeno: {course_count}
   - Technicky: `assert course_count == 0`
12. 🔍 **Kontrola:** Ověřen správný stav Empty State (žádný zapsaný kurz)
   - Technicky: `step('Ověřen správný stav Empty State (žádný zapsaný kurz)')`

#### `TestMyCourses` -> `test_tc_us13_06_multiple_enrolled_courses_independent_data` (řádek 199)

**Popis:** [TC-US13-06] Zobrazení více souběžně zapsaných kurzů a nezávislost organizačních údajů.

**Souhrn:** `7` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_predefined_student(page)`
2. ⚙️ **Krok:** `self.my_courses_page.navigate()`
3. ⚙️ **Krok:** `course_count = self.my_courses_page.course_names.count()` – *Získání hodnoty/stavu z aplikace*
4. 🔍 **Kontrola:** Očekávány alespoň 2 zapsané kurzy pro ověření nezávislosti, nalezeno: {course_count}
   - Technicky: `assert course_count >= 2`
5. 🔍 **Kontrola:** Ověřen počet zapsaných kurzů: {course_count}
   - Technicky: `step(f'Ověřen počet zapsaných kurzů: {course_count}')`
6. ⚙️ **Krok:** `name_1 = self.my_courses_page.course_names.nth(0).inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
7. ⚙️ **Krok:** `name_2 = self.my_courses_page.course_names.nth(1).inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
8. 🔍 **Kontrola:** Kurzy by měly mít různé názvy: '{name_1}' vs '{name_2}'
   - Technicky: `assert name_1 != name_2`
9. ⚙️ **Krok:** `date_from_1 = self.my_courses_page.date_time_from.nth(0).inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
10. ⚙️ **Krok:** `date_from_2 = self.my_courses_page.date_time_from.nth(1).inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
11. 🔍 **Kontrola:** Kurzy by měly mít nezávislá data zahájení: '{date_from_1}' vs '{date_from_2}'
   - Technicky: `assert date_from_1 != date_from_2`
12. 🔍 **Kontrola:** Ověřena nezávislost údajů mezi '{name_1}' ({date_from_1}) a '{name_2}' ({date_from_2})
   - Technicky: `step(f"Ověřena nezávislost údajů mezi '{name_1}' ({date_from_1}) a '{name_2}' ({date_from_2})")`

#### `TestMyCourses` -> `test_tc_us13_07_restriction_of_my_courses_for_lector_rbac` (řádek 222) `[xfail(reason="Defekt aplikace (RBAC): Lektor má v navigaci zákaznický odkaz 'Moje kurzy' a sekce pro něj není omezena ani přesměrována", strict=False)]`

**Popis:** [TC-US13-07] Omezení přístupu do sekce 'Moje kurzy' pro roli Lektor (RBAC).

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_lector(page)`
2. 🔍 **Kontrola:** Ověřeno, že lektor nemá v navigaci zákaznický odkaz 'Moje kurzy'
   - Technicky: `expect(self.courses_page.navbar.my_courses_link).not_to_be_visible()`
3. ⚙️ **Krok:** `self.my_courses_page.navigate()`
4. 🔍 **Kontrola:** Ověřeno, že lektor byl z /my-courses přesměrován pryč
   - Technicky: `expect(page).not_to_have_url(self.my_courses_page.url)`

#### `TestMyCourses` -> `test_tc_us13_08_upcoming_courses_chronological_ordering` (řádek 239) `[xfail(reason='Defekt aplikace: Zapsané kurzy na /my-courses nejsou řazeny vzestupně chronologicky od nejbližšího data', strict=False)]`

**Popis:** [TC-US13-08] Rozlišení nadcházejících kurzů a chronologické řazení termínů.

**Souhrn:** `9` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_predefined_student(page)`
2. ⚙️ **Krok:** `self.my_courses_page.navigate()`
3. ⚙️ **Krok:** `dates_text = self.my_courses_page.date_time_from.all_inner_texts()` – *Příprava testovacích dat*
4. 🔍 **Kontrola:** Pro ověření chronologického řazení jsou potřeba alespoň 2 kurzy, nalezeno: {len(dates_text)}
   - Technicky: `assert len(dates_text) >= 2`
5. ⚙️ **Krok:** `parsed_dates = []` – *Příprava testovacích dat*
6. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
7. ⚙️ **Krok:** `match = re.search('(\\d+)\\.\\s*(\\d+)\\.\\s*(\\d{4})', dt_str)` – *Příprava testovacích dat*
8. 🔍 **Kontrola:** Nelze parsovat datum zahájení z textu: '{dt_str}'
   - Technicky: `assert match`
9. ⚙️ **Krok:** `day, month, year = (int(match.group(1)), int(match.group(2)), int(match.group(3)))` – *Příprava testovacích dat*
10. ⚙️ **Krok:** `parsed_dates.append(datetime(year, month, day))`
11. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
12. 🔍 **Kontrola:** Kurzy nejsou řazeny chronologicky vzestupně: {parsed_dates[i].strftime('%d.%m.%Y')} předchází {parsed_dates[i + 1].strftime('%d.%m.%Y')}
   - Technicky: `assert parsed_dates[i] <= parsed_dates[i + 1]`
13. 🔍 **Kontrola:** Ověřeno chronologické řazení kurzů na /my-courses
   - Technicky: `step('Ověřeno chronologické řazení kurzů na /my-courses')`

### Soubor: `tests/courses/test_students_list.py`
> *Automatizované testy pro US-16: Zobrazení seznamu přihlášených účastníků pro lektora.

Pokrývá test casy:
- [TC-US16-01] Zobrazení tabulky účastníků běhu kurzu lektorem a kompletní údaje
- [TC-US16-02] Zobrazení zástupné hodnoty 'Neuvedeno' při nevyplněném IČO studenta
- [TC-US16-03] Zamezení přístupu k seznamu účastníků pro běžného zákazníka a hosta (Ochrana soukromí)
- [TC-US16-04] Zobrazení seznamu pro běh kurzu bez dosud přihlášených studentů (Empty State)*

#### `TestStudentsList` -> `test_tc_us16_01_view_participants_table_and_complete_data` (řádek 43)

**Popis:** [TC-US16-01] Zobrazení tabulky účastníků běhu kurzu lektorem a kompletní údaje.

**Souhrn:** `8` akcí, `16` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
2. ⚙️ **Krok:** `self.courses_page.navigate_to_detail(1)`
3. 🔍 **Kontrola:** `expect(self.courses_page.course_detail).to_be_visible()`
4. ⚙️ **Krok:** `participants_btn = self.courses_page.participants_buttons.first` – *Příprava testovacích dat*
5. 🔍 **Kontrola:** `expect(participants_btn).to_be_visible()`
6. ⚙️ **Krok:** `participants_btn.click()`
7. 🔍 **Kontrola:** `expect(page).to_have_url(re.compile('.*/courses/\\d+/participants$'), timeout=10000)`
8. 🔍 **Kontrola:** `expect(self.students_page.heading).to_be_visible()`
9. 🔍 **Kontrola:** Otevřena stránka se seznamem přihlášených účastníků
   - Technicky: `expect(self.students_page.heading).to_have_text('Seznam přihlášených')`
10. 🔍 **Kontrola:** `expect(self.students_page.participants_table).to_be_visible()`
11. 🔍 **Kontrola:** `expect(self.students_page.name_header).to_be_visible()`
12. 🔍 **Kontrola:** `expect(self.students_page.email_header).to_be_visible()`
13. 🔍 **Kontrola:** `expect(self.students_page.phone_header).to_be_visible()`
14. 🔍 **Kontrola:** Ověřeny hlavičky tabulky (Jméno, Email, Telefon, IČO)
   - Technicky: `expect(self.students_page.ico_header).to_be_visible()`
15. 🔍 **Kontrola:** `expect(self.students_page.participant_rows.first).to_be_visible()`
16. ⚙️ **Krok:** `name = self.students_page.participant_names.first.inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
17. ⚙️ **Krok:** `email = self.students_page.participant_emails.first.inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
18. ⚙️ **Krok:** `phone = self.students_page.participant_phones.first.inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
19. ⚙️ **Krok:** `ico = self.students_page.participant_icos.first.inner_text().strip()` – *Získání hodnoty/stavu z aplikace*
20. 🔍 **Kontrola:** Jméno účastníka nesmí být prázdné
   - Technicky: `assert len(name) > 0`
21. 🔍 **Kontrola:** E-mail účastníka je neplatný: '{email}'
   - Technicky: `assert len(email) > 0 and '@' in email`
22. 🔍 **Kontrola:** Telefon účastníka nesmí být prázdný
   - Technicky: `assert len(phone) > 0`
23. 🔍 **Kontrola:** IČO účastníka nesmí být prázdné (má obsahovat IČO nebo 'Neuvedeno')
   - Technicky: `assert len(ico) > 0`
24. 🔍 **Kontrola:** Ověřeny kompletní údaje prvního účastníka: {name}, {email}, {phone}, IČO: {ico}
   - Technicky: `step(f'Ověřeny kompletní údaje prvního účastníka: {name}, {email}, {phone}, IČO: {ico}')`

#### `TestStudentsList` -> `test_tc_us16_02_placeholder_neuvedeno_for_empty_ico` (řádek 88) `[xfail(reason="Důsledek defektu US-12: Formulář přihlášky na kurz nedovolí odeslání bez IČO, v seznamu účastníků nelze ověřit hodnotu 'Neuvedeno'", strict=False)]`

**Popis:** [TC-US16-02] Zobrazení zástupné hodnoty 'Neuvedeno' při nevyplněném IČO studenta.

**Souhrn:** `3` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
2. ⚙️ **Krok:** `self.students_page.open_for_iteration(1)`
3. 🔍 **Kontrola:** `expect(self.students_page.participants_table).to_be_visible()`
4. 🔍 **Kontrola:** `expect(self.students_page.participant_rows.first).to_be_visible()`
5. ⚙️ **Krok:** `icos = self.students_page.participant_icos.all_inner_texts()` – *Příprava testovacích dat*
6. 🔍 **Kontrola:** V seznamu IČO účastníků se nenachází zástupný text 'Neuvedeno': {icos[:5]}
   - Technicky: `assert any((ico.strip() == 'Neuvedeno' for ico in icos))`
7. 🔍 **Kontrola:** Ověřena přítomnost zástupného textu 'Neuvedeno' u účastníka bez IČO
   - Technicky: `step("Ověřena přítomnost zástupného textu 'Neuvedeno' u účastníka bez IČO")`

#### `TestStudentsList` -> `test_tc_us16_03_prevention_of_participants_access_for_customer_and_guest_privacy` (řádek 102)

**Popis:** [TC-US16-03] Zamezení přístupu k seznamu účastníků pro běžného zákazníka a hosta (Ochrana soukromí).

**Souhrn:** `5` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_customer(page, registered_user)`
2. ⚙️ **Krok:** `self.courses_page.navigate_to_detail(1)`
3. 🔍 **Kontrola:** `expect(self.courses_page.course_detail).to_be_visible()`
4. 🔍 **Kontrola:** Ověřeno, že zákazník nevidí na detailu kurzu tlačítko 'Přihlášení'
   - Technicky: `expect(self.courses_page.participants_buttons).not_to_be_visible()`
5. ⚙️ **Krok:** `self.students_page.open_for_iteration(1)`
6. 🔍 **Kontrola:** `expect(self.students_page.participants_table).not_to_be_visible()`
7. 🔍 **Kontrola:** Ověřeno, že zákazník nemá přístup k tabulce účastníků (ochrana osobních údajů)
   - Technicky: `expect(self.students_page.heading).not_to_be_visible()`
8. ⚙️ **Krok:** `page.context.clear_cookies()`
9. ⚙️ **Krok:** `self.students_page.open_for_iteration(1)`
10. 🔍 **Kontrola:** `expect(self.students_page.participants_table).not_to_be_visible()`
11. 🔍 **Kontrola:** Ověřeno, že nepřihlášený host nemá přístup k tabulce účastníků
   - Technicky: `expect(self.students_page.heading).not_to_be_visible()`

#### `TestStudentsList` -> `test_tc_us16_04_empty_state_for_iteration_without_students` (řádek 130) `[xfail(reason='Defekt aplikace: Aplikace postrádá informativní empty state hlášení při 0 přihlášených studentech a zobrazuje pouze prázdný tbody', strict=False)]`

**Popis:** [TC-US16-04] Zobrazení seznamu pro běh kurzu bez dosud přihlášených studentů (Empty State).

**Souhrn:** `2` akcí, `1` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_as_lector(page, lector_user)`
2. ⚙️ **Krok:** `self.students_page.open_for_iteration(999999)`
3. 🔍 **Kontrola:** Ověřeno informativní sdělení empty state při nulovém počtu přihlášených studentů
   - Technicky: `expect(self.students_page.empty_state_message).to_be_visible()`

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
*Počet testů v oblasti: **10***

### Soubor: `tests/portal/test_home_dashboard.py`
> *Automatizované testy pro US-17: Domovská uvítací nástěnka po přihlášení.

Pokrývá test casy:
- [TC-US17-01] Zobrazení personalizované uvítací zprávy se jménem uživatele po přihlášení
- [TC-US17-02] Trvalá dostupnost volby 'Domů' v horní navigaci pro přihlášeného uživatele
- [TC-US17-03] Zamezení přístupu na domovskou nástěnku pro nepřihlášeného návštěvníka
- [TC-US17-04] Zobrazení uvítací zprávy pro uživatele s českou diakritikou ve jméně*

#### `TestHomeDashboard` -> `test_tc_us17_01_personalized_welcome_message_display` (řádek 41)

**Popis:** [TC-US17-01] Zobrazení personalizované uvítací zprávy se jménem uživatele po přihlášení.

**Souhrn:** `8` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `unique_suffix = uuid.uuid4().hex[:6]` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `user_name = f'Petr Svoboda {unique_suffix}'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `user_email = f'petr_{unique_suffix}@example.com'` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `user_pass = 'Heslo123!'` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `self.register_page.navigate()`
6. ⚙️ **Krok:** `self.register_page.register(name=user_name, email=user_email, password=user_pass, password_again=user_pass)`
7. 🔍 **Kontrola:** `expect(page).to_have_url(re.compile('.*/home|.*/courses'), timeout=10000)`
8. ⚙️ **Krok:** `self.home_page.navigate()`
9. 🔍 **Kontrola:** Otevřena stránka /home
   - Technicky: `expect(page).to_have_url(self.home_page.url)`
10. 🔍 **Kontrola:** `expect(self.home_page.welcome_section).to_be_visible()`
11. 🔍 **Kontrola:** `expect(self.home_page.welcome_section).to_contain_text(user_name)`
12. ⚙️ **Krok:** `welcome_text = self.home_page.get_welcome_text()` – *Příprava testovacích dat*
13. 🔍 **Kontrola:** Uvítací zpráva neobsahuje jméno uživatele: '{welcome_text}'
   - Technicky: `assert user_name in welcome_text`
14. 🔍 **Kontrola:** Ověřena personalizovaná uvítací zpráva: '{welcome_text}'
   - Technicky: `step(f"Ověřena personalizovaná uvítací zpráva: '{welcome_text}'")`

#### `TestHomeDashboard` -> `test_tc_us17_02_persistent_home_navigation_link` (řádek 70)

**Popis:** [TC-US17-02] Trvalá dostupnost volby 'Domů' v horní navigaci pro přihlášeného uživatele.

**Souhrn:** `5` akcí, `7` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login_user(page, registered_user)`
2. ⚙️ **Krok:** `self.profile_page.navigate()`
3. 🔍 **Kontrola:** `expect(page).to_have_url(self.profile_page.url)`
4. 🔍 **Kontrola:** Ověřena dostupnost odkazu 'Domů' na stránce profilu
   - Technicky: `expect(self.home_page.home_link).to_be_visible()`
5. ⚙️ **Krok:** `self.home_page.home_link.click()`
6. 🔍 **Kontrola:** `expect(page).to_have_url(self.home_page.url)`
7. 🔍 **Kontrola:** Ověřeno úspěšné přesměrování z profilu na /home
   - Technicky: `expect(self.home_page.welcome_section).to_be_visible()`
8. ⚙️ **Krok:** `self.courses_page.navigate()`
9. 🔍 **Kontrola:** `expect(self.home_page.home_link).to_be_visible()`
10. ⚙️ **Krok:** `self.home_page.home_link.click()`
11. 🔍 **Kontrola:** `expect(page).to_have_url(self.home_page.url)`
12. 🔍 **Kontrola:** Ověřeno úspěšné přesměrování z katalogu kurzů na /home
   - Technicky: `expect(self.home_page.welcome_section).to_be_visible()`

#### `TestHomeDashboard` -> `test_tc_us17_03_prevention_of_unauthenticated_access_to_dashboard` (řádek 98) `[xfail(reason='Defekt aplikace: Nepřihlášený návštěvník při vstupu na /home není přesměrován na /login ani /courses, obsah katalogu se vykreslí přímo na URL /home', strict=False)]`

**Popis:** [TC-US17-03] Zamezení přístupu na domovskou nástěnku pro nepřihlášeného návštěvníka.

**Souhrn:** `1` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.home_page.navigate()`
2. 🔍 **Kontrola:** Ověřeno, že nepřihlášenému návštěvníkovi se nezobrazuje uvítací sekce s privátními daty
   - Technicky: `expect(self.home_page.welcome_section).not_to_be_visible()`
3. 🔍 **Kontrola:** Ověřeno přesměrování nepřihlášeného návštěvníka na přihlášení nebo katalog
   - Technicky: `expect(page).to_have_url(re.compile('.*/login|.*/courses$'))`

#### `TestHomeDashboard` -> `test_tc_us17_04_welcome_message_with_czech_diacritics` (řádek 111)

**Popis:** [TC-US17-04] Zobrazení uvítací zprávy pro uživatele s českou diakritikou ve jméně.

**Souhrn:** `8` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `unique_suffix = uuid.uuid4().hex[:6]` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `diacritics_name = f'Eliška Řehořová-Žáčková {unique_suffix}'` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `user_email = f'eliska_{unique_suffix}@example.com'` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `user_pass = 'Diakritika123!'` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `self.register_page.navigate()`
6. ⚙️ **Krok:** `self.register_page.register(name=diacritics_name, email=user_email, password=user_pass, password_again=user_pass)`
7. 🔍 **Kontrola:** `expect(page).to_have_url(re.compile('.*/home|.*/courses'), timeout=10000)`
8. ⚙️ **Krok:** `self.home_page.navigate()`
9. 🔍 **Kontrola:** `expect(self.home_page.welcome_section).to_be_visible()`
10. 🔍 **Kontrola:** `expect(self.home_page.welcome_section).to_contain_text(diacritics_name)`
11. ⚙️ **Krok:** `welcome_text = self.home_page.get_welcome_text()` – *Příprava testovacích dat*
12. 🔍 **Kontrola:** Jméno s diakritikou nebylo správně nalezeno v uvítacím textu: '{welcome_text}'
   - Technicky: `assert diacritics_name in welcome_text`
13. 🔍 **Kontrola:** Ověřeno bezchybné zobrazení jména s diakritikou v uvítání: '{welcome_text}'
   - Technicky: `step(f"Ověřeno bezchybné zobrazení jména s diakritikou v uvítání: '{welcome_text}'")`

### Soubor: `tests/portal/test_linktree.py`
#### `TestPortalLinktree` -> `test_tc_us01_01_linktree_elements_and_metadata_display` (řádek 17)

**Popis:** [TC-US01-01] Zobrazení rozcestníku, metadat stránky a přítomnost všech navigačních odkazů.

**Souhrn:** `2` akcí, `12` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.linktree_page.navigate()`
2. 🔍 **Kontrola:** Otevřena úvodní stránka rozcestníku (/)
   - Technicky: `step('Otevřena úvodní stránka rozcestníku (/)')`
3. ⚙️ **Krok:** `res = page.request.get(self.linktree_page.url)` – *Získání hodnoty/stavu z aplikace*
4. 🔍 **Kontrola:** Ověřen úspěšný stavový kód HTTP 200 OK
   - Technicky: `assert res.status == 200`
5. 🔍 **Kontrola:** Ověřena cílová URL rozcestníku (/)
   - Technicky: `expect(page).to_have_url(f'{self.linktree_page.base_url}/')`
6. 🔍 **Kontrola:** Ověřen titulek stránky v záložce prohlížeče: '{self.linktree_page.TITLE_TEXT}'
   - Technicky: `expect(page).to_have_title(self.linktree_page.TITLE_TEXT)`
7. 🔍 **Kontrola:** `expect(self.linktree_page.heading).to_be_visible()`
8. 🔍 **Kontrola:** Ověřen hlavní nadpis H1: '{self.linktree_page.HEADING_TEXT}'
   - Technicky: `expect(self.linktree_page.heading).to_have_text(self.linktree_page.HEADING_TEXT)`
9. 🔍 **Kontrola:** Ověřen odkaz na aplikaci Kalkulačka
   - Technicky: `expect(self.linktree_page.calculator_link).to_be_visible()`
10. 🔍 **Kontrola:** Ověřen odkaz na Testovací login
   - Technicky: `expect(self.linktree_page.test_login_link).to_be_visible()`
11. 🔍 **Kontrola:** Ověřen odkaz na NextDate
   - Technicky: `expect(self.linktree_page.nextdate_link).to_be_visible()`
12. 🔍 **Kontrola:** Ověřen odkaz na Registraci na kurz
   - Technicky: `expect(self.linktree_page.course_registration_link).to_be_visible()`
13. 🔍 **Kontrola:** Ověřen doplňkový odkaz '(výpis)' kurzu
   - Technicky: `expect(self.linktree_page.course_list_link).to_be_visible()`
14. 🔍 **Kontrola:** Ověřen dominantní odkaz 'Demo-login' pro vstup do aplikace kurzů
   - Technicky: `expect(self.linktree_page.demo_login_link).to_be_visible()`

#### `TestPortalLinktree` -> `test_tc_us01_02_demo_login_navigation_to_courses` (řádek 55)

**Popis:** [TC-US01-02] Navigace přes odkaz 'Demo-login' přímo do katalogu kurzů.

**Souhrn:** `2` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.linktree_page.navigate()`
2. 🔍 **Kontrola:** Otevřena úvodní stránka rozcestníku
   - Technicky: `step('Otevřena úvodní stránka rozcestníku')`
3. ⚙️ **Krok:** `self.linktree_page.open_demo_login()`
4. 🔍 **Kontrola:** Kliknuto na odkaz 'Demo-login'
   - Technicky: `step("Kliknuto na odkaz 'Demo-login'")`
5. 🔍 **Kontrola:** Ověřeno okamžité přesměrování do katalogu kurzů (/courses)
   - Technicky: `expect(page).to_have_url(f'{self.linktree_page.base_url}/courses')`
6. 🔍 **Kontrola:** `expect(self.courses_page.title).to_be_visible()`
7. 🔍 **Kontrola:** Ověřeno úspěšné načtení sekce katalogu kurzů
   - Technicky: `expect(self.courses_page.courses_section).to_be_visible()`

#### `TestPortalLinktree` -> `test_tc_us01_03_external_links_functionality_and_attributes` (řádek 70)

**Popis:** [TC-US01-03] Funkčnost, cílové adresy a bezpečnostní atributy externích odkazů.

**Souhrn:** `8` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.linktree_page.navigate()`
2. 🔍 **Kontrola:** Otevřena úvodní stránka rozcestníku
   - Technicky: `step('Otevřena úvodní stránka rozcestníku')`
3. ⚙️ **Krok:** `links_to_verify = [(self.linktree_page.calculator_link, re.compile('/kalkulacka/kalkulacka\\.html$'), '/kalkulacka/kalkulacka.html', 'Kalkulačka'), (self.linktree_page.test_login_link, re.compile('/login_app/?$'), '/login_app/', 'Testovací login'), (self.linktree_page.nextdate_link, re.compile('/nextdate/?$'), '/nextdate/', 'NextDate'), (self.linktree_page.course_registration_link, re.compile('/regkurz/?$'), '/regkurz/', 'Registrace na kurz'), (self.linktree_page.course_list_link, re.compile('/regkurz/list\\.php$'), '/regkurz/list.php', '(výpis)')]` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
5. 🔍 **Kontrola:** Ověřen atribut href odkazu '{link_name}'
   - Technicky: `expect(link_locator).to_have_attribute('href', pattern)`
6. ⚙️ **Krok:** `target_attr = link_locator.get_attribute('target')` – *Příprava testovacích dat*
7. ⚙️ **Krok:** `if target_attr == '_blank':` – *Řídicí blok (if)*
8. 🔍 **Kontrola:** Ověřen bezpečnostní atribut rel='noopener noreferrer' pro odkaz '{link_name}'
   - Technicky: `expect(link_locator).to_have_attribute('rel', 'noopener noreferrer')`
9. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
10. ⚙️ **Krok:** `full_url = f'{self.linktree_page.base_url}{path}'` – *Příprava testovacích dat*
11. ⚙️ **Krok:** `res = page.request.get(full_url)` – *Získání hodnoty/stavu z aplikace*
12. 🔍 **Kontrola:** Odkaz na {name} ({full_url}) vrátil chybový status {res.status}
   - Technicky: `assert res.status == 200`
13. 🔍 **Kontrola:** Ověřena funkčnost a dostupnost endpointu pro '{name}' (HTTP 200 OK)
   - Technicky: `step(f"Ověřena funkčnost a dostupnost endpointu pro '{name}' (HTTP 200 OK)")`

#### `TestPortalLinktree` -> `test_tc_us01_04_handling_non_existent_subpage` (řádek 103) `[xfail(reason='Defekt aplikace: Aplikace nemá implementovanou chybovou stránku 404 pro neznámé routy; vykreslí prázdnou bílou stránku se stavovým kódem 200', strict=False)]`

**Popis:** [TC-US01-04] Zpracování neexistující podstránky z rozcestníku.

**Souhrn:** `3` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `non_existent_url = f'{self.linktree_page.base_url}/neexistujici-nastroj-12345'` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `response = page.goto(non_existent_url)` – *Příprava testovacích dat*
3. 🔍 **Kontrola:** Zadán požadavek na neexistující adresu {non_existent_url}
   - Technicky: `step(f'Zadán požadavek na neexistující adresu {non_existent_url}')`
4. 🔍 **Kontrola:** Ověřen stavový kód 404 Not Found
   - Technicky: `assert response is not None and response.status == 404`
5. 🔍 **Kontrola:** Ověřena přítomnost 404 chybové hlášky na stránce
   - Technicky: `expect(self.linktree_page.not_found_heading).to_be_visible()`
6. 🔍 **Kontrola:** `expect(self.linktree_page.not_found_back_link).to_be_visible()`
7. ⚙️ **Krok:** `self.linktree_page.not_found_back_link.click()`
8. 🔍 **Kontrola:** Ověřena možnost návratu z chybové stránky zpět na rozcestník
   - Technicky: `expect(page).to_have_url(f'{self.linktree_page.base_url}/')`

#### `TestPortalLinktree` -> `test_tc_us01_05_responsive_mobile_viewport` (řádek 120)

**Popis:** [TC-US01-05] Responzivní zobrazení a čitelnost rozcestníku na mobilním zařízení.

**Souhrn:** `5` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `page.set_viewport_size({'width': 375, 'height': 667})`
2. ⚙️ **Krok:** `self.linktree_page.navigate()`
3. 🔍 **Kontrola:** Nastaven mobilní viewport (375x667) a načten rozcestník
   - Technicky: `step('Nastaven mobilní viewport (375x667) a načten rozcestník')`
4. ⚙️ **Krok:** `scroll_width = page.evaluate('() => document.documentElement.scrollWidth')` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `client_width = page.evaluate('() => document.documentElement.clientWidth')` – *Příprava testovacích dat*
6. 🔍 **Kontrola:** Stránka na mobilním rozlišení přetéká horizontálně
   - Technicky: `assert scroll_width <= client_width`
7. 🔍 **Kontrola:** Ověřeno, že stránka nepřetéká horizontálně
   - Technicky: `step('Ověřeno, že stránka nepřetéká horizontálně')`
8. 🔍 **Kontrola:** `expect(self.linktree_page.demo_login_link).to_be_visible()`
9. ⚙️ **Krok:** `self.linktree_page.open_demo_login()`
10. 🔍 **Kontrola:** Ověřena funkčnost tlačítka 'Demo-login' a přechod do katalogu na mobilním viewportu
   - Technicky: `expect(page).to_have_url(f'{self.linktree_page.base_url}/courses')`

#### `TestPortalLinktree` -> `test_tc_us01_06_keyboard_accessibility_and_navigation` (řádek 138)

**Popis:** [TC-US01-06] Přístupnost a navigace rozcestníku pomocí klávesnice.

**Souhrn:** `8` akcí, `8` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.linktree_page.navigate()`
2. 🔍 **Kontrola:** Načtena úvodní stránka rozcestníku
   - Technicky: `step('Načtena úvodní stránka rozcestníku')`
3. ⚙️ **Krok:** `page.keyboard.press('Tab')`
4. 🔍 **Kontrola:** Klávesa Tab: Focus na odkaz Kalkulacka
   - Technicky: `expect(self.linktree_page.calculator_link).to_be_focused()`
5. ⚙️ **Krok:** `page.keyboard.press('Tab')`
6. 🔍 **Kontrola:** Klávesa Tab: Focus na odkaz Testovací login
   - Technicky: `expect(self.linktree_page.test_login_link).to_be_focused()`
7. ⚙️ **Krok:** `page.keyboard.press('Tab')`
8. 🔍 **Kontrola:** Klávesa Tab: Focus na odkaz NextDate
   - Technicky: `expect(self.linktree_page.nextdate_link).to_be_focused()`
9. ⚙️ **Krok:** `page.keyboard.press('Tab')`
10. 🔍 **Kontrola:** Klávesa Tab: Focus na odkaz Registrace na kurz
   - Technicky: `expect(self.linktree_page.course_registration_link).to_be_focused()`
11. ⚙️ **Krok:** `page.keyboard.press('Tab')`
12. 🔍 **Kontrola:** Klávesa Tab: Focus na odkaz (výpis)
   - Technicky: `expect(self.linktree_page.course_list_link).to_be_focused()`
13. ⚙️ **Krok:** `page.keyboard.press('Tab')`
14. 🔍 **Kontrola:** Klávesa Tab: Focus na dominantní odkaz Demo-login
   - Technicky: `expect(self.linktree_page.demo_login_link).to_be_focused()`
15. ⚙️ **Krok:** `page.keyboard.press('Enter')`
16. 🔍 **Kontrola:** Klávesa Enter: Úspěšné přesměrování do katalogu kurzů (/courses)
   - Technicky: `expect(page).to_have_url(f'{self.linktree_page.base_url}/courses')`

---

<a id="oblast-profile"></a>
## Oblast: Profile
*Počet testů v oblasti: **9***

### Soubor: `tests/profile/test_profile.py`
#### `TestUserProfile` -> `test_tc_us18_01_prefilled_data_and_successful_update` (řádek 22)

**Popis:** [TC-US18-01] Předvyplnění existujících údajů a úspěšná aktualizace profilu.

**Souhrn:** `7` akcí, `13` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.profile_page.navigate()`
3. 🔍 **Kontrola:** `expect(self.profile_page.heading).to_be_visible()`
4. 🔍 **Kontrola:** Ověřen nadpis 'Profil'
   - Technicky: `expect(self.profile_page.heading).to_have_text('Profil')`
5. 🔍 **Kontrola:** `expect(self.profile_page.name_input).to_be_visible()`
6. 🔍 **Kontrola:** Ověřeno, že pole pro jméno je předvyplněno aktuální hodnotou
   - Technicky: `expect(self.profile_page.name_input).not_to_have_value('')`
7. 🔍 **Kontrola:** `expect(self.profile_page.email_input).to_be_visible()`
8. 🔍 **Kontrola:** Ověřen předvyplněný e-mail: {registered_user['email']}
   - Technicky: `expect(self.profile_page.email_input).to_have_value(registered_user['email'])`
9. 🔍 **Kontrola:** Ověřeno pole pro telefon
   - Technicky: `expect(self.profile_page.phone_input).to_be_visible()`
10. 🔍 **Kontrola:** Ověřeno pole pro IČO
   - Technicky: `expect(self.profile_page.ico_input).to_be_visible()`
11. 🔍 **Kontrola:** Ověřeno tlačítko 'Uložit'
   - Technicky: `expect(self.profile_page.save_button).to_be_visible()`
12. ⚙️ **Krok:** `updated_name = f'QA Tester {uuid.uuid4().hex[:6]}'` – *Příprava testovacích dat*
13. ⚙️ **Krok:** `valid_phone = '+420777123456'` – *Příprava testovacích dat*
14. ⚙️ **Krok:** `valid_ico = '27082440'` – *Příprava testovacích dat*
15. ⚙️ **Krok:** `self.profile_page.update_profile(name=updated_name, phone=valid_phone, ico=valid_ico)`
16. 🔍 **Kontrola:** Ověřeno přesměrování na /home po úspěšném uložení profilu (AC-6)
   - Technicky: `expect(page).to_have_url(f'{self.profile_page.base_url}/home')`
17. ⚙️ **Krok:** `self.profile_page.navigate()`
18. 🔍 **Kontrola:** `expect(self.profile_page.name_input).to_have_value(updated_name)`
19. 🔍 **Kontrola:** `expect(self.profile_page.phone_input).to_have_value(valid_phone)`
20. 🔍 **Kontrola:** Ověřena perzistence aktualizovaných údajů po znovunačtení profilu
   - Technicky: `expect(self.profile_page.ico_input).to_have_value(valid_ico)`

#### `TestUserProfile` -> `test_tc_us18_02_email_format_and_empty_email_validation` (řádek 67)

**Popis:** [TC-US18-02] Validace povinných polí jména a e-mailu a kontrola formátu e-mailu - neplatný e-mail.

**Souhrn:** `4` akcí, `5` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.profile_page.navigate()`
3. ⚙️ **Krok:** `self.profile_page.update_profile(email='email-bez-zavinace')`
4. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.profile_page.base_url}/profile')`
5. 🔍 **Kontrola:** `expect(self.profile_page.email_error).to_be_visible()`
6. 🔍 **Kontrola:** Ověřeno odmítnutí neplatného formátu e-mailu a zobrazení chybové hlášky
   - Technicky: `expect(self.profile_page.email_error).to_have_text(self.profile_page.EMAIL_ERROR_TEXT)`
7. ⚙️ **Krok:** `self.profile_page.update_profile(email='')`
8. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.profile_page.base_url}/profile')`
9. 🔍 **Kontrola:** Ověřeno odmítnutí prázdného pole e-mailu
   - Technicky: `expect(self.profile_page.email_error).to_be_visible()`

#### `TestUserProfile` -> `test_tc_us18_02_mandatory_name_validation` (řádek 89) `[xfail(reason='Defekt aplikace: Chybí klientská validace povinného pole Jméno; aplikace při prázdném jménu chybně přesměruje na /home i přes 422 z backendu', strict=False)]`

**Popis:** [TC-US18-02] Validace povinných polí jména a e-mailu a kontrola formátu e-mailu - prázdné jméno.

**Souhrn:** `3` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.profile_page.navigate()`
3. ⚙️ **Krok:** `self.profile_page.update_profile(name='')`
4. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.profile_page.base_url}/profile')`
5. 🔍 **Kontrola:** Ověřeno zamezení uložení formuláře s prázdným jménem a zobrazení chybové hlášky
   - Technicky: `expect(self.profile_page.name_error).to_be_visible()`

#### `TestUserProfile` -> `test_tc_us18_03_duplicate_email_collision` (řádek 104) `[xfail(reason='Defekt aplikace: Při pokusu o uložení obsazeného e-mailu jiného uživatele frontend chybně přesměruje na /home místo zobrazení chybové hlášky na /profile', strict=False)]`

**Popis:** [TC-US18-03] Zamezení změny e-mailu na adresu již obsazenou jiným uživatelem.

**Souhrn:** `3` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.profile_page.navigate()`
3. ⚙️ **Krok:** `self.profile_page.update_profile(email=lector_user['email'])`
4. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.profile_page.base_url}/profile')`
5. 🔍 **Kontrola:** Ověřeno odmítnutí duplicitního e-mailu a zobrazení validační hlášky
   - Technicky: `expect(self.profile_page.email_collision_error).to_be_visible()`

#### `TestUserProfile` -> `test_tc_us18_04_invalid_ico_validation` (řádek 116)

**Popis:** [TC-US18-04] Validace formální platnosti IČO pomocí kontrolního součtu na profilu.

**Souhrn:** `3` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.profile_page.navigate()`
3. ⚙️ **Krok:** `self.profile_page.update_profile(phone='+420777123456', ico='12345678')`
4. 🔍 **Kontrola:** Ověřeno, že formulář se neodeslal a stránka zůstává na /profile
   - Technicky: `expect(page).to_have_url(f'{self.profile_page.base_url}/profile')`
5. 🔍 **Kontrola:** `expect(self.profile_page.ico_error).to_be_visible()`
6. 🔍 **Kontrola:** Ověřena validační hláška 'Neplatné IČO'
   - Technicky: `expect(self.profile_page.ico_error).to_have_text(self.profile_page.ICO_ERROR_TEXT)`

#### `TestUserProfile` -> `test_tc_us18_05_invalid_phone_validation` (řádek 131)

**Popis:** [TC-US18-05] Validace formátu telefonního čísla na profilu.

**Souhrn:** `3` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.profile_page.navigate()`
3. ⚙️ **Krok:** `self.profile_page.update_profile(phone='12', ico='27082440')`
4. 🔍 **Kontrola:** Ověřeno, že formulář se neodeslal při neplatném telefonu
   - Technicky: `expect(page).to_have_url(f'{self.profile_page.base_url}/profile')`
5. 🔍 **Kontrola:** `expect(self.profile_page.phone_error).to_be_visible()`
6. 🔍 **Kontrola:** Ověřena validační hláška 'Neplatné telefonní číslo'
   - Technicky: `expect(self.profile_page.phone_error).to_have_text(self.profile_page.PHONE_ERROR_TEXT)`

#### `TestUserProfile` -> `test_tc_us18_06_clear_optional_ico_and_phone` (řádek 150) `[xfail(reason='Defekt aplikace: Klientská validace IČO a telefonu nepovoluje prázdné hodnoty a brání smazání nepovinných polí (AC-3)', strict=False)]`

**Popis:** [TC-US18-06] Úspěšné uložení profilu s vymazáním nepovinných údajů (IČO a telefon).

**Souhrn:** `4` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.profile_page.navigate()`
3. ⚙️ **Krok:** `self.profile_page.update_profile(ico='', phone='')`
4. 🔍 **Kontrola:** Ověřeno přesměrování po vymazání nepovinných údajů
   - Technicky: `expect(page).to_have_url(f'{self.profile_page.base_url}/home')`
5. ⚙️ **Krok:** `self.profile_page.navigate()`
6. 🔍 **Kontrola:** `expect(self.profile_page.ico_input).to_have_value('')`
7. 🔍 **Kontrola:** Ověřeno, že doplňkové údaje IČO a telefon jsou na profilu prázdné
   - Technicky: `expect(self.profile_page.phone_input).to_have_value('')`

#### `TestUserProfile` -> `test_profile_unauthenticated_access_denied` (řádek 166)

**Popis:** Ověření, že bez přihlášení není formulář profilu zobrazen.

**Souhrn:** `1` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.profile_page.navigate()`
2. 🔍 **Kontrola:** `expect(self.profile_page.name_input).not_to_be_visible()`
3. 🔍 **Kontrola:** Ověřeno, že nepřihlášený uživatel nemá přístup k datům profilu
   - Technicky: `expect(self.profile_page.heading).not_to_be_visible()`

#### `TestMyCourses` -> `test_my_courses_page_display` (řádek 188)

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
*Počet testů v oblasti: **12***

### Soubor: `tests/security/test_csrf.py`
> *Automatizované testy pro US-20: Ochrana proti podvržení požadavků (CSRF) a integrita sezení.

Pokrývá test casy:
- [TC-US20-01] Přítomnost platného bezpečnostního CSRF tokenu ve formulářích
- [TC-US20-02] Odmítnutí formulářového požadavku s chybějícím nebo neplatným CSRF tokenem
- [TC-US20-03] Regenerace identifikátoru sezení při přihlášení a odhlášení (Session Fixation ochrana)*

#### `TestCsrfAndSessionIntegrity` -> `test_tc_us20_01_presence_of_valid_csrf_token` (řádek 27)

**Popis:** [TC-US20-01] Přítomnost platného bezpečnostního CSRF tokenu ve formulářích.

**Souhrn:** `6` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `cookies = page.context.cookies()` – *Získání hodnoty/stavu z aplikace*
3. ⚙️ **Krok:** `xsrf_cookie = next((c for c in cookies if c['name'] == 'XSRF-TOKEN'), None)` – *Příprava testovacích dat*
4. 🔍 **Kontrola:** Cookie XSRF-TOKEN nebyla na stránce /login nalezena
   - Technicky: `assert xsrf_cookie is not None`
5. 🔍 **Kontrola:** Cookie XSRF-TOKEN je prázdná
   - Technicky: `assert len(xsrf_cookie['value']) > 0`
6. 🔍 **Kontrola:** Ověřena přítomnost platné XSRF-TOKEN cookie na /login
   - Technicky: `step('Ověřena přítomnost platné XSRF-TOKEN cookie na /login')`
7. ⚙️ **Krok:** `self.register_page.navigate()`
8. ⚙️ **Krok:** `cookies_reg = page.context.cookies()` – *Získání hodnoty/stavu z aplikace*
9. ⚙️ **Krok:** `xsrf_cookie_reg = next((c for c in cookies_reg if c['name'] == 'XSRF-TOKEN'), None)` – *Příprava testovacích dat*
10. 🔍 **Kontrola:** Cookie XSRF-TOKEN nebyla na stránce /register nalezena
   - Technicky: `assert xsrf_cookie_reg is not None`
11. 🔍 **Kontrola:** Cookie XSRF-TOKEN je prázdná na /register
   - Technicky: `assert len(xsrf_cookie_reg['value']) > 0`
12. 🔍 **Kontrola:** Ověřena přítomnost platné XSRF-TOKEN cookie na /register
   - Technicky: `step('Ověřena přítomnost platné XSRF-TOKEN cookie na /register')`

#### `TestCsrfAndSessionIntegrity` -> `test_tc_us20_02_rejection_of_request_with_missing_or_invalid_csrf_token` (řádek 51) `[xfail(reason='Bezpečnostní defekt aplikace: Server neověřuje platnost CSRF tokenu a akceptuje POST požadavky s neplatným či chybějícím tokenem (vrací HTTP 200 namísto 419/403)', strict=False)]`

**Popis:** [TC-US20-02] Odmítnutí formulářového požadavku s chybějícím nebo neplatným CSRF tokenem.

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `response = page.request.post(f'{self.login_page.base_url}/login', data={'email': 'attacker@example.com', 'password': 'WrongPassword123!'}, headers={'X-XSRF-TOKEN': 'neplatny_podvrzeny_token_123'})` – *Získání hodnoty/stavu z aplikace*
3. 🔍 **Kontrola:** Požadavek s neplatným CSRF tokenem měl být odmítnut kódem 419 nebo 403, ale vrátil HTTP {response.status}
   - Technicky: `assert response.status in (403, 419)`
4. 🔍 **Kontrola:** Ověřeno bezpečné zamítnutí požadavku s neplatným CSRF tokenem
   - Technicky: `step('Ověřeno bezpečné zamítnutí požadavku s neplatným CSRF tokenem')`

#### `TestCsrfAndSessionIntegrity` -> `test_tc_us20_03_session_regeneration_on_login_and_logout` (řádek 73)

**Popis:** [TC-US20-03] Regenerace identifikátoru sezení při přihlášení a odhlášení (Session Fixation ochrana).

**Souhrn:** `9` akcí, `9` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate()`
2. ⚙️ **Krok:** `anon_cookies = page.context.cookies()` – *Získání hodnoty/stavu z aplikace*
3. ⚙️ **Krok:** `anon_session = next((c['value'] for c in anon_cookies if 'session' in c['name'].lower()), None)` – *Příprava testovacích dat*
4. ⚙️ **Krok:** `self.login_page.login(registered_user['email'], registered_user['password'])`
5. 🔍 **Kontrola:** `expect(page).to_have_url(f'{self.courses_page.base_url}/courses', timeout=10000)`
6. ⚙️ **Krok:** `auth_cookies = page.context.cookies()` – *Získání hodnoty/stavu z aplikace*
7. ⚙️ **Krok:** `auth_session = next((c['value'] for c in auth_cookies if 'session' in c['name'].lower()), None)` – *Příprava testovacích dat*
8. 🔍 **Kontrola:** Anonymní session cookie nebyla nalezena
   - Technicky: `assert anon_session is not None`
9. 🔍 **Kontrola:** Autentizovaná session cookie nebyla po přihlášení nalezena
   - Technicky: `assert auth_session is not None`
10. 🔍 **Kontrola:** Session cookie nebyla po přihlášení regenerována (Session Fixation riziko)
   - Technicky: `assert anon_session != auth_session`
11. 🔍 **Kontrola:** Ověřena úspěšná regenerace sezení při přihlášení uživatele
   - Technicky: `step('Ověřena úspěšná regenerace sezení při přihlášení uživatele')`
12. ⚙️ **Krok:** `self.login_page.logout()`
13. 🔍 **Kontrola:** `expect(self.login_page.nav_login_link).to_be_visible()`
14. ⚙️ **Krok:** `post_logout_cookies = page.context.cookies()` – *Získání hodnoty/stavu z aplikace*
15. ⚙️ **Krok:** `post_logout_session = next((c['value'] for c in post_logout_cookies if 'session' in c['name'].lower()), None)` – *Příprava testovacích dat*
16. 🔍 **Kontrola:** Session cookie po odhlášení nebyla nalezena
   - Technicky: `assert post_logout_session is not None`
17. 🔍 **Kontrola:** Session cookie nebyla po odhlášení změněna/zneplatněna
   - Technicky: `assert auth_session != post_logout_session`
18. 🔍 **Kontrola:** Ověřeno bezpečné zneplatnění sezení po odhlášení uživatele
   - Technicky: `step('Ověřeno bezpečné zneplatnění sezení po odhlášení uživatele')`

### Soubor: `tests/security/test_rbac.py`
> *Automatizované testy pro US-19: Řízení přístupu na základě rolí (RBAC a autorizace API).

Pokrývá test casy:
- [TC-US19-01] Dostupnost veřejných sekcí aplikace pro nepřihlášeného návštěvníka
- [TC-US19-02] Zamezení přístupu a automatické přesměrování neautentizovaného uživatele na katalog kurzů
- [TC-US19-03] Zpřístupnění lektorských akcí výhradně pro uživatele v roli Lektor
- [TC-US19-04] Zamezení přístupu běžného zákazníka k lektorským operacím v UI
- [TC-US19-05] Zamezení zápisu na běhy kurzů pro uživatele v roli Lektor (UI i API úroveň)
- [TC-US19-06] Nedostupnost servisních a údržbových rozhraní pro neautorizované návštěvníky
- [TC-US19-07] Přepnutí rolí a okamžitá aktualizace autorizačních oprávnění v sezení
- [TC-US19-08] Zamezení neoprávněné manipulace s daty přes přímé API / POST požadavky
- [TC-US19-09] Ochrana proti horizontální eskalaci práv (IDOR) mezi lektory*

#### `TestRoleBasedAccessControl` -> `test_tc_us19_01_public_sections_availability_for_guest` (řádek 55)

**Popis:** [TC-US19-01] Dostupnost veřejných sekcí aplikace pro nepřihlášeného návštěvníka.

**Souhrn:** `5` akcí, `9` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.login_page.navigate('/')`
2. 🔍 **Kontrola:** Ověřen přístup na rozcestník /
   - Technicky: `expect(page).to_have_url(re.compile('.*/$'))`
3. ⚙️ **Krok:** `self.courses_page.navigate()`
4. 🔍 **Kontrola:** `expect(page).to_have_url(self.courses_page.url)`
5. 🔍 **Kontrola:** `expect(self.courses_page.courses_section).to_be_visible()`
6. 🔍 **Kontrola:** Ověřen přístup do katalogu kurzů pro nepřihlášeného návštěvníka
   - Technicky: `expect(self.courses_page.navbar.login_link).to_be_visible()`
7. ⚙️ **Krok:** `self.courses_page.navigate_to_detail(1)`
8. 🔍 **Kontrola:** `expect(page).to_have_url(re.compile('.*/courses/1$'))`
9. 🔍 **Kontrola:** `expect(self.courses_page.course_detail).to_be_visible()`
10. 🔍 **Kontrola:** Ověřen přístup na detail kurzu a nepřítomnost privátních lektorských akcí
   - Technicky: `expect(self.courses_page.participants_buttons).not_to_be_visible()`
11. ⚙️ **Krok:** `self.login_page.navigate()`
12. 🔍 **Kontrola:** `expect(self.login_page.login_title).to_be_visible()`
13. ⚙️ **Krok:** `self.register_page.navigate()`
14. 🔍 **Kontrola:** Ověřen přístup na /login a /register
   - Technicky: `expect(self.register_page.register_button).to_be_visible()`

#### `TestRoleBasedAccessControl` -> `test_tc_us19_02_prevention_of_unauthenticated_access_to_private_routes` (řádek 89) `[xfail(reason='Defekt aplikace (RBAC): Nepřihlášený uživatel není při přístupu na chráněné URL přesměrován na /courses', strict=False)]`

**Popis:** [TC-US19-02] Zamezení přístupu a automatické přesměrování neautentizovaného uživatele na katalog kurzů.

**Souhrn:** `3` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self.profile_page.navigate()`
2. 🔍 **Kontrola:** `expect(page).to_have_url(self.courses_page.url)`
3. 🔍 **Kontrola:** Ověřeno přesměrování z /profile na /courses
   - Technicky: `expect(self.profile_page.name_input).not_to_be_visible()`
4. ⚙️ **Krok:** `self.my_courses_page.navigate()`
5. 🔍 **Kontrola:** Ověřeno přesměrování z /my-courses na /courses
   - Technicky: `expect(page).to_have_url(self.courses_page.url)`
6. ⚙️ **Krok:** `self.course_create_page.navigate()`
7. 🔍 **Kontrola:** Ověřeno přesměrování z /courses/create na /courses
   - Technicky: `expect(page).to_have_url(self.courses_page.url)`

#### `TestRoleBasedAccessControl` -> `test_tc_us19_03_lector_tools_accessibility_for_lector_role` (řádek 107)

**Popis:** [TC-US19-03] Zpřístupnění lektorských akcí výhradně pro uživatele v roli Lektor.

**Souhrn:** `5` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, lector_user)`
2. ⚙️ **Krok:** `self.courses_page.navigate()`
3. 🔍 **Kontrola:** Ověřena přítomnost tlačítka 'Přidat kurz' v katalogu pro lektora
   - Technicky: `expect(self.courses_page.add_course_button).to_be_visible()`
4. ⚙️ **Krok:** `self.course_create_page.navigate()`
5. 🔍 **Kontrola:** Ověřen přístup lektora k formuláři vytvoření kurzu
   - Technicky: `expect(self.course_create_page.heading).to_be_visible()`
6. ⚙️ **Krok:** `self.courses_page.navigate_to_detail(1)`
7. 🔍 **Kontrola:** `expect(self.courses_page.course_detail).to_be_visible()`
8. 🔍 **Kontrola:** `expect(self.courses_page.participants_buttons.first).to_be_visible()`
9. ⚙️ **Krok:** `self.courses_page.participants_buttons.first.click()`
10. 🔍 **Kontrola:** `expect(page).to_have_url(re.compile('.*/courses/\\d+/participants$'), timeout=10000)`
11. 🔍 **Kontrola:** Ověřen přístup lektora k seznamu účastníků běhu kurzu
   - Technicky: `expect(self.students_page.heading).to_be_visible()`

#### `TestRoleBasedAccessControl` -> `test_tc_us19_04_prevention_of_customer_access_to_lector_operations_ui` (řádek 135) `[xfail(reason='Defekt aplikace (RBAC): Zákazník má přímý přístup k lektorským formulářům /courses/create a /create-iteration', strict=False)]`

**Popis:** [TC-US19-04] Zamezení přístupu běžného zákazníka k lektorským operacím v UI.

**Souhrn:** `6` akcí, `6` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.courses_page.navigate()`
3. 🔍 **Kontrola:** `expect(self.courses_page.add_course_button).not_to_be_visible()`
4. 🔍 **Kontrola:** Ověřeno, že zákazník nevidí v katalogu lektorská tlačítka
   - Technicky: `expect(self.courses_page.add_iteration_buttons).not_to_be_visible()`
5. ⚙️ **Krok:** `self.courses_page.navigate_to_detail(1)`
6. 🔍 **Kontrola:** Ověřeno, že zákazník nevidí na detailu kurzu tlačítko 'Přihlášení'
   - Technicky: `expect(self.courses_page.participants_buttons).not_to_be_visible()`
7. ⚙️ **Krok:** `self.course_create_page.navigate()`
8. 🔍 **Kontrola:** Ověřeno odmítnutí přístupu na /courses/create pro zákazníka
   - Technicky: `expect(self.course_create_page.heading).not_to_be_visible()`
9. ⚙️ **Krok:** `self.iteration_create_page.open_for_course(1)`
10. 🔍 **Kontrola:** Ověřeno odmítnutí přístupu na /courses/1/create-iteration pro zákazníka
   - Technicky: `expect(self.iteration_create_page.container).not_to_be_visible()`
11. ⚙️ **Krok:** `self.students_page.open_for_iteration(1)`
12. 🔍 **Kontrola:** Ověřeno odmítnutí přístupu na /courses/1/participants pro zákazníka
   - Technicky: `expect(self.students_page.participants_table).not_to_be_visible()`

#### `TestRoleBasedAccessControl` -> `test_tc_us19_05_restriction_of_enrollment_for_lector_role` (řádek 169) `[xfail(reason='Defekt aplikace (RBAC): Lektor má přímý přístup na registrační formulář /courses/:id/register', strict=False)]`

**Popis:** [TC-US19-05] Zamezení zápisu na běhy kurzů pro uživatele v roli Lektor (UI i API úroveň).

**Souhrn:** `3` akcí, `3` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, lector_user)`
2. ⚙️ **Krok:** `self.courses_page.navigate_to_detail(1)`
3. 🔍 **Kontrola:** `expect(self.courses_page.course_detail).to_be_visible()`
4. 🔍 **Kontrola:** Ověřeno, že lektor nemá v detailu kurzu tlačítko zápisu 'Nezávazná registrace'
   - Technicky: `expect(self.courses_page.enroll_buttons).not_to_be_visible()`
5. ⚙️ **Krok:** `self.enroll_page.open_for_iteration(1)`
6. 🔍 **Kontrola:** Ověřeno, že přímý přístup na /courses/1/register byl lektorovi odmítnut
   - Technicky: `expect(self.enroll_page.heading).not_to_be_visible()`

#### `TestRoleBasedAccessControl` -> `test_tc_us19_06_unavailability_of_maintenance_interfaces` (řádek 189) `[xfail(reason='Defekt aplikace: Servisní trasy (např. /artisan, /system-cache, /_ignition) vracejí HTTP 200 místo 404/403 a /migrate vrací HTTP 500', strict=False)]`

**Popis:** [TC-US19-06] Nedostupnost servisních a údržbových rozhraní pro neautorizované návštěvníky.

**Souhrn:** `5` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `service_routes = ['/artisan', '/migrate', '/system-cache', '/_ignition', '/telescope']` – *Příprava testovacích dat*
2. ⚙️ **Krok:** `base_url = self.courses_page.base_url` – *Příprava testovacích dat*
3. ⚙️ **Krok:** `for:` – *Řídicí blok (for)*
4. ⚙️ **Krok:** `url = f'{base_url}{route}'` – *Příprava testovacích dat*
5. ⚙️ **Krok:** `status = 200` – *Získání hodnoty/stavu z aplikace*
6. 🔍 **Kontrola:** Servisní trasa '{route}' vrátila neočekávaný HTTP kód {status} (očekáváno 403 nebo 404)
   - Technicky: `assert status in (403, 404)`
7. 🔍 **Kontrola:** Ověřeno, že servisní trasy vrací 403 Forbidden nebo 404 Not Found
   - Technicky: `step('Ověřeno, že servisní trasy vrací 403 Forbidden nebo 404 Not Found')`

#### `TestRoleBasedAccessControl` -> `test_tc_us19_07_role_switching_and_immediate_permission_update` (řádek 208)

**Popis:** [TC-US19-07] Přepnutí rolí a okamžitá aktualizace autorizačních oprávnění v sezení.

**Souhrn:** `8` akcí, `4` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `self.courses_page.navigate()`
3. 🔍 **Kontrola:** Ověřeno, že zákazník nemá tlačítko 'Přidat kurz'
   - Technicky: `expect(self.courses_page.add_course_button).not_to_be_visible()`
4. ⚙️ **Krok:** `self.courses_page.navbar.logout()`
5. 🔍 **Kontrola:** Zákazník úspěšně odhlášen
   - Technicky: `expect(self.courses_page.navbar.login_link).to_be_visible()`
6. ⚙️ **Krok:** `self._login(page, lector_user)`
7. ⚙️ **Krok:** `self.courses_page.navigate()`
8. 🔍 **Kontrola:** Ověřeno, že po přihlášení lektora jsou lektorská oprávnění ihned aktivní
   - Technicky: `expect(self.courses_page.add_course_button).to_be_visible()`
9. ⚙️ **Krok:** `self.courses_page.navbar.logout()`
10. ⚙️ **Krok:** `self._login(page, registered_user)`
11. ⚙️ **Krok:** `self.courses_page.navigate()`
12. 🔍 **Kontrola:** Ověřeno správné vyčištění oprávnění lektora při opětovném přihlášení zákazníka
   - Technicky: `expect(self.courses_page.add_course_button).not_to_be_visible()`

#### `TestRoleBasedAccessControl` -> `test_tc_us19_08_prevention_of_unauthorized_data_manipulation_via_api` (řádek 240) `[xfail(reason='Defekt aplikace: Backend API postrádá serverovou autorizaci a umožní vytvoření kurzu i bez lektorské role', strict=False)]`

**Popis:** [TC-US19-08] Zamezení neoprávněné manipulace s daty přes přímé API / POST požadavky.

**Souhrn:** `2` akcí, `2` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, registered_user)`
2. ⚙️ **Krok:** `response = page.request.post(f'{self.courses_page.base_url}/api/courses', data={'name': 'Hacker Course Test', 'description': 'Unauthorized attempt', 'capacity': 10, 'price': 1000})` – *Získání hodnoty/stavu z aplikace*
3. 🔍 **Kontrola:** Požadavek běžného zákazníka na vytvoření kurzu měl být odmítnut (401/403), ale vrátil: {response.status}
   - Technicky: `assert response.status in (401, 403)`
4. 🔍 **Kontrola:** Ověřeno odmítnutí neoprávněného API požadavku zákazníka na vytvoření kurzu
   - Technicky: `step('Ověřeno odmítnutí neoprávněného API požadavku zákazníka na vytvoření kurzu')`

#### `TestRoleBasedAccessControl` -> `test_tc_us19_09_protection_against_horizontal_privilege_escalation_idor` (řádek 262)

**Popis:** [TC-US19-09] Ochrana proti horizontální eskalaci práv (IDOR) mezi lektory.

**Souhrn:** `2` akcí, `1` kontrol

**Postup kroků a kontrol testu:**

1. ⚙️ **Krok:** `self._login(page, lector_user)`
2. ⚙️ **Krok:** `self.students_page.open_for_iteration(999999)`
3. 🔍 **Kontrola:** Ověřeno, že lektor nemá přístup k účastníkům cizího kurzu (ochrana proti IDOR)
   - Technicky: `expect(self.students_page.participants_table).not_to_be_visible()`

---
