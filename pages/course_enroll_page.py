from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class CourseEnrollPage(BasePage):
    """Page Object Model pro formulář nezávazné registrace na běh kurzu (/courses/:id/register)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.registration_section: Locator = page.get_by_test_id("registration_section")
        self.registration_title: Locator = page.get_by_test_id("registration_title")
        self.ico_input: Locator = page.get_by_test_id("ico_input")
        self.ico_error: Locator = page.get_by_test_id("ico_error")
        self.phone_input: Locator = page.get_by_test_id("phone_input")
        self.phone_error: Locator = page.get_by_test_id("phone_error")
        self.submit_button: Locator = page.get_by_role("button", name="Nezávazná registrace")

    def open_for_iteration(self, iteration_id: int | str):
        """Otevře registrační formulář pro konkrétní běh kurzu."""
        self.navigate(f"/courses/{iteration_id}/register")

    def fill_and_submit(self, ico: str, phone: str):
        """Vyplní formulář zápisu a klikne na tlačítko registrace."""
        if ico:
            self.ico_input.fill(ico)
        else:
            self.ico_input.clear()

        if phone:
            self.phone_input.fill(phone)
        else:
            self.phone_input.clear()

        self.submit_button.click()
