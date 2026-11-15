"""
Page Object Model pro úvodní navigační rozcestník portálu (Linktree na /).
Požadavek: US-01.
"""

from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage


class LinktreePage(BasePage):
    """Page Object Model pro úvodní rozcestník testovacích aplikací portálu Kitner."""

    PATH = "/"
    TITLE_TEXT = "Testování"
    HEADING_TEXT = "Dostupné testy"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading: Locator = page.get_by_role("heading", level=1)
        self.calculator_link: Locator = page.get_by_role("link", name="Kalkulacka")
        self.test_login_link: Locator = page.get_by_role("link", name="Testovací login")
        self.nextdate_link: Locator = page.get_by_role("link", name="NextDate")
        self.course_registration_link: Locator = page.get_by_role("link", name="Registrace na kurz")
        self.course_list_link: Locator = page.get_by_role("link", name="(výpis)")
        self.demo_login_link: Locator = page.get_by_role("link", name="Demo-login")

        # Fallback lokátory pro 404 chybovou stránku (požadavek US-01 / AC-1)
        # TODO(testid): chybějící data-testid pro 404 chybovou hlášku a odkaz zpět na rozcestník
        self.not_found_heading: Locator = page.get_by_role("heading", name="404")
        self.not_found_back_link: Locator = page.get_by_role("link", name="Zpět")

    def open_demo_login(self):
        """Klikne na odkaz 'Demo-login' pro vstup do aplikace kurzů."""
        self.demo_login_link.click()
        expect(self.page).to_have_url(f"{self.base_url}/courses")
