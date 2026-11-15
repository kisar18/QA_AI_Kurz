import uuid
import pytest
from playwright.sync_api import Page, expect
from pages.register_page import RegisterPage
from pages.home_page import HomePage
from helpers.step_helpers import step


class TestDemoRegister:
    """Testovací sada pro ověření funkčnosti registrace dle specifikace US-02."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.register_page = RegisterPage(page)

    def test_tc_us02_01_successful_registration(self, page: Page):
        """[TC-US02-01] Úspěšná registrace nového uživatele a automatické přihlášení."""
        self.register_page.navigate()
        step("Otevřena stránka registrace (/register)")

        # Kontrola přítomnosti všech polí formuláře
        expect(self.register_page.name_input).to_be_visible()
        expect(self.register_page.email_input).to_be_visible()
        expect(self.register_page.password_input).to_be_visible()
        expect(self.register_page.password_again_input).to_be_visible()
        expect(self.register_page.register_button).to_be_visible()
        step("Ověřena přítomnost všech polí registračního formuláře")

        unique_id = uuid.uuid4().hex[:8]
        name = f"User {unique_id}"
        email = f"test_reg_{unique_id}@example.com"
        password = "Password123!"

        self.register_page.register(name, email, password, password)
        step(f"Vyplněn formulář novými údaji (e-mail: {email}) a odeslán")

        expect(page).to_have_url(f"{self.register_page.base_url}/home")
        step("Ověřeno automatické přihlášení a přesměrování na /home (AC-1, AC-7)")

        home_page = HomePage(page)
        expect(home_page.welcome_section).to_contain_text(f"Vítej uživateli {name}!")
        expect(self.register_page.navbar.logout_button).to_be_visible()
        expect(self.register_page.navbar.login_link).not_to_be_visible()
        step(f"Ověřena uvítací zpráva pro uživatele {name}, tlačítko odhlášení a zánik odkazu pro přihlášení")

    def test_tc_us02_02_empty_form_validation(self, page: Page):
        """[TC-US02-02] Validace povinných polí při odeslání prázdného formuláře."""
        self.register_page.navigate()
        step("Otevřena stránka registrace")

        self.register_page.register_button.click()
        step("Kliknuto na tlačítko registrace bez vyplnění údajů")

        expect(page).to_have_url(f"{self.register_page.base_url}/register")
        step("Ověřeno setrvání na stránce /register")

        expect(self.register_page.name_error).to_be_visible()
        expect(self.register_page.name_error).to_contain_text("The name field is required.")
        step("Ověřena chybová hláška pro povinné jméno")

        expect(self.register_page.email_error).to_be_visible()
        expect(self.register_page.email_error).to_contain_text("The email field is required.")
        step("Ověřena chybová hláška pro povinný e-mail")

        expect(self.register_page.password_error).to_be_visible()
        expect(self.register_page.password_error).to_contain_text("The password field is required.")
        step("Ověřena chybová hláška pro povinné heslo")

    def test_tc_us02_03_registration_duplicate_email(self, page: Page, registered_user: dict):
        """[TC-US02-03] Pokus o registraci s již existujícím e-mailem."""
        self.register_page.navigate()
        step("Otevřena stránka registrace")

        self.register_page.register(
            name="Duplicate Tester",
            email=registered_user["email"],
            password="Password123!",
            password_again="Password123!",
        )
        step(f"Odeslán formulář s existujícím e-mailem: {registered_user['email']}")

        expect(page).to_have_url(f"{self.register_page.base_url}/register")
        step("Ověřeno zamítnutí registrace a setrvání na /register")

        expect(self.register_page.email_error).to_be_visible()
        expect(self.register_page.email_error).to_contain_text("The email has already been taken.")
        step("Ověřena chybová hláška 'The email has already been taken.'")

    def test_tc_us02_04_duplicate_email_case_insensitive_and_whitespace(self, page: Page, registered_user: dict):
        """[TC-US02-04] Normalizace e-mailu a case-insensitivity unikátnosti."""
        self.register_page.navigate()
        step("Otevřena stránka registrace")

        raw_email = f"  {registered_user['email'].upper()}  "
        self.register_page.register(
            name="Upper Case Tester",
            email=raw_email,
            password="Password123!",
            password_again="Password123!",
        )
        step(f"Odeslán formulář s e-mailem s mezerami a velkými písmeny: '{raw_email}'")

        expect(page).to_have_url(f"{self.register_page.base_url}/register")
        step("Ověřeno, že registrace byla odmítnuta a stránka zůstává na /register")

        expect(self.register_page.email_error).to_be_visible()
        expect(self.register_page.email_error).to_contain_text("The email has already been taken.")
        step("Ověřeno odmítnutí registrace z důvodu duplicity normalizovaného e-mailu (AC-4)")

    def test_tc_us02_05_password_mismatch(self, page: Page):
        """[TC-US02-05] Neshoda hesla a potvrzení hesla."""
        self.register_page.navigate()
        step("Otevřena stránka registrace")

        self.register_page.register(
            name="Mismatch User",
            email="mismatch_user@example.com",
            password="Password123!",
            password_again="DifferentPassword456!",
        )
        step("Vyplněn formulář s rozdílnými hesly")

        expect(page).to_have_url(f"{self.register_page.base_url}/register")
        step("Ověřeno setrvání na /register")

        expect(self.register_page.password_error).to_be_visible()
        expect(self.register_page.password_error).to_contain_text("The password field confirmation does not match.")
        step("Ověřena chybová hláška 'The password field confirmation does not match.'")

    def test_tc_us02_06_navigation_links(self, page: Page):
        """[TC-US02-06] Ověření navigačních odkazů na stránce registrace."""
        self.register_page.navigate()
        step("Otevřena stránka registrace")

        # 1. Odkaz na přihlášení
        expect(self.register_page.login_link).to_be_visible()
        self.register_page.login_link.click()
        expect(page).to_have_url(f"{self.register_page.base_url}/login")
        step("Ověřen odkaz na přihlášení a úspěšné přesměrování na /login")

        # 2. Odkaz na zapomenuté heslo
        self.register_page.navigate()
        expect(self.register_page.forgot_password_link).to_be_visible()
        self.register_page.forgot_password_link.click()
        expect(page).to_have_url(f"{self.register_page.base_url}/forgot-password")
        step("Ověřen odkaz pro obnovu hesla a přesměrování na /forgot-password")

    def test_registration_html5_email_validation(self, page: Page, invalid_emails: list):
        """Ověření HTML5 validace při zadání neplatného formátu e-mailu (z data/invalid_emails.json)."""
        self.register_page.navigate()
        self.register_page.register(
            name="Valid Name",
            email=invalid_emails[0],
            password="Password123!",
            password_again="Password123!",
        )

        expect(self.register_page.email_input).not_to_have_js_property("validationMessage", "")
        step("Ověřeno spuštění nativní HTML5 validace e-mailu")

        expect(page).to_have_url(f"{self.register_page.base_url}/register")
        step("Ověřeno, že formulář se neodeslal")

    def test_registration_passwords_are_masked(self, page: Page):
        """Ověření, že obě pole pro heslo mají atribut type='password'."""
        self.register_page.navigate()

        expect(self.register_page.password_input).to_have_attribute("type", "password")
        step("Ověřen atribut type='password' u prvního pole pro heslo")

        expect(self.register_page.password_again_input).to_have_attribute("type", "password")
        step("Ověřen atribut type='password' u potvrzovacího pole pro heslo")
