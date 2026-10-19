import pytest
from playwright.sync_api import Page, expect
from pages.linktree_page import LinktreePage
from helpers.step_helpers import step


class TestPortalLinktree:
    """Testovací sada pro úvodní navigační rozcestník portálu (US-01)."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.linktree_page = LinktreePage(page)

    def test_portal_linktree_elements_presence(self, page: Page):
        """Ověření, že úvodní stránka / obsahuje všechny klíčové navigační odkazy portálu (US-01)."""
        self.linktree_page.navigate()

        expect(page).to_have_url(f"{self.linktree_page.base_url}/")
        step("Ověřena úvodní URL portálu (/)")

        expect(self.linktree_page.calculator_link).to_be_visible()
        step("Ověřen odkaz na aplikaci Kalkulačka")

        expect(self.linktree_page.test_login_link).to_be_visible()
        step("Ověřen odkaz na Testovací login")

        expect(self.linktree_page.nextdate_link).to_be_visible()
        step("Ověřen odkaz na NextDate")

        expect(self.linktree_page.course_registration_link).to_be_visible()
        step("Ověřen odkaz na Registraci na kurz")

        expect(self.linktree_page.course_list_link).to_be_visible()
        step("Ověřen odkaz na (výpis) kurzu")

        expect(self.linktree_page.demo_login_link).to_be_visible()
        step("Ověřen odkaz na 'Demo-login' pro vstup do aplikace kurzů")

    def test_portal_linktree_navigation_to_courses(self, page: Page):
        """Ověření, že kliknutí na 'Demo-login' nasměruje návštěvníka přímo do katalogu kurzů (US-01)."""
        self.linktree_page.navigate()
        self.linktree_page.open_demo_login()

        expect(page).to_have_url(f"{self.linktree_page.base_url}/courses")
        step("Ověřeno úspěšné přesměrování z rozcestníku do katalogu kurzů (/courses)")
