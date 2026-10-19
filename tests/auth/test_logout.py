import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.components.navbar import Navbar
from helpers.step_helpers import step


class TestDemoLogout:
    """Testovací sada pro bezpečné odhlášení ze systému (US-04)."""

    def test_user_can_logout_successfully(self, page: Page, registered_user: dict):
        """Ověření, že přihlášený uživatel se může úspěšně odhlásit přes navbar."""
        login_page = LoginPage(page)
        navbar = Navbar(page)

        login_page.navigate()
        login_page.login(registered_user["email"], registered_user["password"])

        # Uživatel je přihlášen
        expect(navbar.logout_button).to_be_visible()
        step("Uživatel je přihlášen – tlačítko Odhlásit se je viditelné")

        # Provedení odhlášení
        navbar.logout()

        # Ověření stavu po odhlášení
        expect(navbar.login_link).to_be_visible()
        expect(navbar.logout_button).not_to_be_visible()
        step("Uživatel byl úspěšně odhlášen – odkaz Přihlásit se je znovu zobrazen")
