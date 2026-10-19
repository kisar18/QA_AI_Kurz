from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class RegisterPage(BasePage):
    """Page Object Model pro registrační stránku."""

    PATH = "/register"

    def __init__(self, page: Page):
        super().__init__(page)
        self.name_input: Locator = page.get_by_test_id("name_input")
        self.email_input: Locator = page.get_by_test_id("email_input")
        self.password_input: Locator = page.get_by_test_id("password_input")
        self.password_again_input: Locator = page.get_by_test_id("password_again_input")
        self.register_button: Locator = page.get_by_test_id("register_button")
        self.login_link: Locator = page.get_by_test_id("login_link")
        self.name_error: Locator = page.get_by_test_id("name_input_errors")
        self.password_error: Locator = page.get_by_test_id("password_input_errors")
        self.email_error: Locator = page.get_by_test_id("email_input_errors")

    def register(self, name: str, email: str, password: str, password_again: str):
        """Vyplní formulář a odešle registraci."""
        if name:
            self.name_input.fill(name)
        else:
            self.name_input.clear()

        if email:
            self.email_input.fill(email)
        else:
            self.email_input.clear()

        if password:
            self.password_input.fill(password)
        else:
            self.password_input.clear()

        if password_again:
            self.password_again_input.fill(password_again)
        else:
            self.password_again_input.clear()

        self.register_button.click()
