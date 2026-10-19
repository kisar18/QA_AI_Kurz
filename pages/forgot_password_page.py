from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class ForgotPasswordPage(BasePage):
    """Page Object Model pro stránku zapomenutého hesla (/forgot-password)."""

    PATH = "/forgot-password"

    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input: Locator = page.get_by_test_id("email_input")
        self.submit_button: Locator = page.get_by_test_id("submit_button")

    def request_password_reset(self, email: str):
        """Vyplní e-mail a odešle žádost o obnovení hesla."""
        if email:
            self.email_input.fill(email)
        else:
            self.email_input.clear()
        self.submit_button.click()
