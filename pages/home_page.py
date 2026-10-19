from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class HomePage(BasePage):
    """Page Object Model pro domovskou stránku (/home) po přihlášení či registraci.
    Požadavek: US-17.
    """

    PATH = "/home"

    def __init__(self, page: Page):
        super().__init__(page)
        self.welcome_section: Locator = page.get_by_test_id("home_section")

    def get_welcome_text(self) -> str:
        """Vrátí uvítací text zobrazený na domovské stránce."""
        return self.welcome_section.inner_text().strip()
