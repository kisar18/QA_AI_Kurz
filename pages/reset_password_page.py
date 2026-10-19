from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class ResetPasswordPage(BasePage):
    """Page Object Model pro stránku resetu hesla (/password-reset/:token)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.section: Locator = page.get_by_test_id("reset_password_section")
        self.password_input: Locator = page.get_by_test_id("password_input")
        self.password_again_input: Locator = page.get_by_test_id("password_again_input")
        self.submit_button: Locator = page.get_by_test_id("submit_button")
        self.password_error: Locator = page.get_by_test_id("password_input_errors")
        self.status_div: Locator = page.get_by_test_id("status_div")
        self.login_link: Locator = page.get_by_test_id("login_link")

    def open_with_token(self, token: str, email: str = "") -> None:
        """Otevře stránku pro reset hesla s daným tokenem a volitelným e-mailem v query."""
        url = f"/password-reset/{token}"
        if email:
            url += f"?email={email}"
        self.navigate(url)

    def reset_password(self, password: str, password_confirmation: str) -> None:
        """Vyplní formulář pro změnu hesla a odešle jej."""
        if password:
            self.password_input.fill(password)
        else:
            self.password_input.clear()

        if password_confirmation:
            self.password_again_input.fill(password_confirmation)
        else:
            self.password_again_input.clear()

        self.submit_button.click()
