from playwright.sync_api import Page, Locator


class HomePage:
    """Page Object Model pro domovskou stránku (/home) po přihlášení či registraci."""

    URL = "http://testovani.kitner.cz/home"

    def __init__(self, page: Page):
        self.page = page
        self.welcome_section: Locator = page.get_by_test_id("home_section")

    def navigate(self):
        """Otevře přímo URL domovské stránky."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")
