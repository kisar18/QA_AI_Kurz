from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class StudentsListPage(BasePage):
    """Page Object Model pro seznam přihlášených studentů kurzu (/courses/:id/participants)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading: Locator = page.get_by_test_id("header_title")
        self.participants_table: Locator = page.get_by_test_id("participants_table")
        self.table_rows: Locator = page.locator("[data-testid='participants_table'] tbody tr")
        self.name_header: Locator = page.get_by_test_id("name_header")

    def open_for_iteration(self, iteration_id: int | str):
        """Otevře seznam přihlášených studentů pro daný termín kurzu."""
        self.navigate(f"/courses/{iteration_id}/participants")
