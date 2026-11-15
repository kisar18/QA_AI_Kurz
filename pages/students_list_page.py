import re
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class StudentsListPage(BasePage):
    """Page Object Model pro seznam přihlášených studentů kurzu (/courses/:id/participants)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading: Locator = page.get_by_test_id("header_title")
        self.participants_table: Locator = page.get_by_test_id("participants_table")
        self.table_header: Locator = page.get_by_test_id("table_header")
        self.name_header: Locator = page.get_by_test_id("name_header")
        self.email_header: Locator = page.get_by_test_id("email_header")
        self.phone_header: Locator = page.get_by_test_id("phone_header")
        self.ico_header: Locator = page.get_by_test_id("ico_header")

        # Dynamické řádky a buňky účastníků
        self.participant_rows: Locator = page.get_by_test_id(re.compile(r"^participant_row_"))
        self.participant_names: Locator = page.get_by_test_id(re.compile(r"^participant_name_"))
        self.participant_emails: Locator = page.get_by_test_id(re.compile(r"^participant_email_"))
        self.participant_phones: Locator = page.get_by_test_id(re.compile(r"^participant_phone_"))
        self.participant_icos: Locator = page.get_by_test_id(re.compile(r"^participant_ico_"))

        # Zástupný prvek pro prázdný stav
        # TODO(testid): aplikace nemá data-testid pro hlášení prázdné tabulky účastníků
        self.empty_state_message: Locator = page.get_by_text("nejsou přihlášeni žádní studenti")

    def open_for_iteration(self, iteration_id: int | str):
        """Otevře seznam přihlášených studentů pro daný termín kurzu."""
        self.navigate(f"/courses/{iteration_id}/participants")
