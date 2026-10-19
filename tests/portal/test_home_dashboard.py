import pytest
from playwright.sync_api import Page, expect
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.components.navbar import Navbar
from helpers.step_helpers import step


class TestHomeDashboard:
    """Testovací sada pro domovskou uvítací nástěnku po přihlášení (US-17)."""

    def test_authenticated_user_sees_personalized_welcome(self, page: Page, registered_user: dict):
        """Ověření, že po přihlášení se uživateli zobrazí personalizované uvítání se jménem (US-17)."""
        login_page = LoginPage(page)
        home_page = HomePage(page)

        login_page.navigate()
        login_page.login(registered_user["email"], registered_user["password"])
        page.wait_for_url("**/courses")
        page.wait_for_load_state("networkidle")

        # Přejdeme na domovskou stránku /home
        home_page.navigate()

        expect(page).to_have_url(home_page.url)
        step("Ověřena URL domovské stránky (/home)")

        expect(home_page.welcome_section).to_be_visible()
        expect(home_page.welcome_section).to_contain_text(f"Vítej uživateli {registered_user['name']}!")
        step(f"Ověřeno personalizované uvítání uživatele: 'Vítej uživateli {registered_user['name']}!'")

    def test_navbar_home_link_navigates_to_dashboard(self, page: Page, registered_user: dict):
        """Ověření, že volba 'Domů' v horní navigaci spolehlivě přepne na domovskou nástěnku (US-17)."""
        login_page = LoginPage(page)
        navbar = Navbar(page)
        home_page = HomePage(page)

        login_page.navigate()
        login_page.login(registered_user["email"], registered_user["password"])

        # Uživatel je na /courses, klikne na odkaz 'Domů' v menu
        expect(navbar.home_link).to_be_visible()
        navbar.home_link.click()
        page.wait_for_url("**/home")

        expect(page).to_have_url(home_page.url)
        expect(home_page.welcome_section).to_be_visible()
        step("Ověřen úspěšný přechod na domovskou stránku přes odkaz 'Domů' v navigaci")
