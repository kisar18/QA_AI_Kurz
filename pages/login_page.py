from playwright.sync_api import Page, Locator


class LoginPage:
    """Page Object Model pro přihlašovací stránku."""

    URL = "http://testovani.kitner.cz/login"
    COURSES_URL = "http://testovani.kitner.cz/courses"

    def __init__(self, page: Page):
        self.page = page
        self.email_input: Locator = page.locator("[data-testid='email_input']")
        self.password_input: Locator = page.locator("[data-testid='password_input']")
        self.login_button: Locator = page.locator("[data-testid='login_button']")
        self.login_title: Locator = page.locator("[data-testid='login_text']")
        self.error_message: Locator = page.locator("[data-testid='email_input_errors']")
        self.forgot_password_link: Locator = page.locator("[data-testid='forgot_password_link']")
        self.register_link: Locator = page.locator("[data-testid='register_link']")
        self.nav_login_link: Locator = page.locator("[data-testid='login_link']")
        self.nav_courses_link: Locator = page.locator("[data-testid='courses_link']")
        self.logout_button: Locator = page.locator("[data-testid='logout_button']")
        self.profile_link: Locator = page.locator("[data-testid='courses_profile']")

    def navigate(self):
        """Otevře přímo URL přihlašovací stránky."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")

    def navigate_via_courses(self):
        """Přejde na /courses a odtud klikne na odkaz 'Přihlásit se' v navigaci."""
        self.page.goto(self.COURSES_URL)
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

    def logout(self):
        """Odhlásí přihlášeného uživatele kliknutím na 'Odhlásit se'."""
        self.logout_button.click()
        self.nav_login_link.wait_for(state="visible")

    def get_error_message(self) -> str:
        """Vrátí text zobrazené chybové hlášky."""
        self.error_message.wait_for(state="visible", timeout=5000)
        return self.error_message.inner_text().strip()
