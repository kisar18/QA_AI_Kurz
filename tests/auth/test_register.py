import uuid
import pytest
from playwright.sync_api import Page, expect
from pages.register_page import RegisterPage
from pages.home_page import HomePage
from helpers.step_helpers import step


class TestDemoRegister:
    """Testovací sada pro ověření funkčnosti registrace na testovani.kitner.cz."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.register_page = RegisterPage(page)

    def test_register_form_elements_presence(self, page: Page):
        """Ověření přítomnosti prvků formuláře registrace."""
        self.register_page.navigate()

        expect(self.register_page.name_input).to_be_visible()
        step("Ověřeno pole pro jméno")

        expect(self.register_page.email_input).to_be_visible()
        step("Ověřeno pole pro e-mail")

        expect(self.register_page.password_input).to_be_visible()
        step("Ověřeno pole pro heslo")

        expect(self.register_page.password_again_input).to_be_visible()
        step("Ověřeno pole pro potvrzení hesla")

        expect(self.register_page.register_button).to_be_visible()
        step("Ověřeno tlačítko 'Registrovat'")

    def test_successful_registration(self, page: Page):
        """Ověření úspěšné registrace nového uživatele."""
        unique_id = uuid.uuid4().hex[:8]
        name = f"User {unique_id}"
        email = f"test_reg_{unique_id}@example.com"
        password = "Password123!"

        self.register_page.navigate()
        self.register_page.register(name, email, password, password)

        expect(page).to_have_url(f"{self.register_page.base_url}/home")
        step("Ověřeno přesměrování po registraci na /home")

        home_page = HomePage(page)
        expect(home_page.welcome_section).to_contain_text(f"Vítej uživateli {name}!")
        step(f"Ověřena uvítací zpráva pro uživatele {name}")

    def test_registration_password_mismatch(self, page: Page):
        """Ověření zobrazení chyby při zadání neshodných hesel."""
        self.register_page.navigate()
        self.register_page.register(
            name="Mismatch User",
            email="mismatch_user@example.com",
            password="Password123!",
            password_again="DifferentPassword456!",
        )

        expect(page).to_have_url(f"{self.register_page.base_url}/register")
        step("Ověřeno, že stránka zůstala na /register")

        expect(self.register_page.password_error).to_be_visible()
        expect(self.register_page.password_error).to_contain_text("The password field confirmation does not match.")
        step("Ověřena chybová hláška 'The password field confirmation does not match.'")

    def test_registration_duplicate_email(self, page: Page, registered_user: dict):
        """Ověření chybové hlášky při pokusu o registraci s již obsazeným e-mailem."""
        self.register_page.navigate()
        self.register_page.register(
            name="Duplicate Tester",
            email=registered_user["email"],
            password="Password123!",
            password_again="Password123!",
        )

        expect(page).to_have_url(f"{self.register_page.base_url}/register")
        step("Ověřeno, že registrace nebyla dokončena a zůstává na /register")

        expect(self.register_page.email_error).to_be_visible()
        expect(self.register_page.email_error).to_contain_text("The email has already been taken.")
        step("Ověřena chybová hláška 'The email has already been taken.'")

    def test_registration_html5_email_validation(self, page: Page, invalid_emails: list):
        """Ověření HTML5 validace při zadání neplatného formátu e-mailu (z data/invalid_emails.json)."""
        self.register_page.navigate()
        self.register_page.register(
            name="Valid Name",
            email=invalid_emails[0],
            password="Password123!",
            password_again="Password123!",
        )

        validation_message = self.register_page.email_input.evaluate("el => el.validationMessage")
        assert len(validation_message) > 0
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

    def test_registration_empty_form_validation(self, page: Page):
        """Ověření zobrazení chybových hlášek pro povinná pole při odeslání prázdného formuláře."""
        self.register_page.navigate()
        self.register_page.register_button.click()

        expect(page).to_have_url(f"{self.register_page.base_url}/register")
        step("Ověřeno, že prázdný formulář se neodeslal a stránka zůstává na /register")

        expect(self.register_page.name_error).to_be_visible()
        expect(self.register_page.name_error).to_contain_text("The name field is required.")
        step("Ověřena chybová hláška pro povinné jméno: 'The name field is required.'")

        expect(self.register_page.email_error).to_be_visible()
        expect(self.register_page.email_error).to_contain_text("The email field is required.")
        step("Ověřena chybová hláška pro povinný e-mail: 'The email field is required.'")

        expect(self.register_page.password_error).to_be_visible()
        expect(self.register_page.password_error).to_contain_text("The password field is required.")
        step("Ověřena chybová hláška pro povinné heslo: 'The password field is required.'")
