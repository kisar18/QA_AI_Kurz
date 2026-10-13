from playwright.sync_api import Page, Locator


class ForgotPasswordPage:
    """Page Object Model pro stránku zapomenutého hesla (/forgot-password)."""

    URL = "http://testovani.kitner.cz/forgot-password"

    def __init__(self, page: Page):
        self.page = page
        self.email_input: Locator = page.get_by_test_id("email_input")
        self.submit_button: Locator = page.get_by_test_id("submit_button")

    def navigate(self):
        """Otevře přímo URL stránky pro obnovu hesla."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")

    def request_password_reset(self, email: str):
        """Vyplní e-mail a odešle žádost o obnovení hesla."""
        if email:
            self.email_input.fill(email)
        else:
            self.email_input.clear()
        self.submit_button.click()
