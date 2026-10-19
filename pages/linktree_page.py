"""
Page Object Model pro úvodní navigační rozcestník portálu (Linktree na /).
Požadavek: US-01.
"""

from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class LinktreePage(BasePage):
    """Page Object Model pro úvodní rozcestník testovacích aplikací portálu Kitner."""

    PATH = "/"

    def __init__(self, page: Page):
        super().__init__(page)
        self.calculator_link: Locator = page.get_by_role("link", name="Kalkulacka")
        self.test_login_link: Locator = page.get_by_role("link", name="Testovací login")
        self.nextdate_link: Locator = page.get_by_role("link", name="NextDate")
        self.course_registration_link: Locator = page.get_by_role("link", name="Registrace na kurz")
        self.course_list_link: Locator = page.get_by_role("link", name="(výpis)")
        self.demo_login_link: Locator = page.get_by_role("link", name="Demo-login")

    def open_demo_login(self):
        """Klikne na odkaz 'Demo-login' pro vstup do aplikace kurzů."""
        self.demo_login_link.click()
        self.page.wait_for_url("**/courses")
        self.page.wait_for_load_state("networkidle")
