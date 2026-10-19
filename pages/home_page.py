from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class HomePage(BasePage):
    """Page Object Model pro domovskou stránku (/home) po přihlášení či registraci."""

    PATH = "/home"

    def __init__(self, page: Page):
        super().__init__(page)
        self.welcome_section: Locator = page.get_by_test_id("home_section")
