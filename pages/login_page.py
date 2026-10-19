from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page Object Model pro přihlašovací stránku."""

    PATH = "/login"

    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input: Locator = page.get_by_test_id("email_input")
        self.password_input: Locator = page.get_by_test_id("password_input")
        self.login_button: Locator = page.get_by_test_id("login_button")
        self.login_title: Locator = page.get_by_test_id("login_text")
        self.error_message: Locator = page.get_by_test_id("email_input_errors")
        self.forgot_password_link: Locator = page.get_by_test_id("forgot_password_link")
        self.register_link: Locator = page.get_by_test_id("register_link")
        self.nav_login_link: Locator = page.get_by_test_id("login_link")
        self.nav_courses_link: Locator = page.get_by_test_id("courses_link")
        self.logout_button: Locator = page.get_by_test_id("logout_button")
        self.profile_link: Locator = page.get_by_test_id("courses_profile")

    def navigate_via_courses(self):
        """Přejde na /courses a odtud klikne na odkaz 'Přihlásit se' v navigaci."""
        self.page.goto(f"{self.base_url}/courses")
        self.page.wait_for_load_state("networkidle")
        self.nav_login_link.click()
        self.page.wait_for_url("**/login")

    def login(self, email: str, password: str):
        """Vyplní formulář zadanými údaji a odešle jej."""
        if email:
            self.email_input.fill(email)
        else:
            self.email_input.clear()

        if password:
            self.password_input.fill(password)
        else:
            self.password_input.clear()

        self.login_button.click()

    def login_with_response(self, email: str, password: str):
        """Vyplní formulář, odešle jej a počká na síťovou odpověď z endpointu /login."""
        if email:
            self.email_input.fill(email)
        else:
            self.email_input.clear()

        if password:
            self.password_input.fill(password)
        else:
            self.password_input.clear()

        with self.page.expect_response(lambda res: "/login" in res.url and res.request.method == "POST"):
            self.login_button.click()

    def logout(self):
        """Odhlásí přihlášeného uživatele kliknutím na 'Odhlásit se'."""
        self.logout_button.click()
        self.nav_login_link.wait_for(state="visible")

    def get_error_message(self) -> str:
        """Vrátí text zobrazené chybové hlášky."""
        self.error_message.wait_for(state="visible", timeout=5000)
        return self.error_message.inner_text().strip()
