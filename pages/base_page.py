"""
Abstraktní bázová třída pro všechny Page Object Models.
Zajišťuje jednotnou inicializaci a sdílené metody navigace i přístup k navigační liště.
"""

from playwright.sync_api import Page
from config.settings import BASE_URL
from pages.components.navbar import Navbar


class BasePage:
    """Bázová třída, od které dědí všechny Page Objects.

    Attributes:
        page: Instance Playwright Page.
        base_url: Základní URL aplikace (z konfigurace).
        navbar: Sdílená komponenta navigace (Navbar).
    """

    PATH: str = ""  # relativní cesta – přepsat v podtřídě

    def __init__(self, page: Page):
        self.page = page
        self.base_url = BASE_URL
        self.navbar = Navbar(page)

    @property
    def url(self) -> str:
        """Sestaví absolutní URL z BASE_URL a PATH."""
        return f"{self.base_url}{self.PATH}"

    def navigate(self, path: str | None = None):
        """Otevře přímo URL dané stránky (nebo volitelné specifikované cesty) a počká na síťový klid."""
        target_url = f"{self.base_url}{path}" if path else self.url
        self.page.goto(target_url)
        self.page.wait_for_load_state("networkidle")
