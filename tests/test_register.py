import uuid
import pytest
from playwright.sync_api import Page, expect
from pages.register_page import RegisterPage
from pages.home_page import HomePage
from pages.helpers import step


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

        expect(page).to_have_url("http://testovani.kitner.cz/home")
        step("Ověřeno přesměrování po registraci na /home")

        home_page = HomePage(page)
        expect(home_page.welcome_section).to_contain_text(f"Vítej uživateli {name}!")
        step(f"Ověřena uvítací zpráva pro uživatele {name}")
