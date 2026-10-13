from playwright.sync_api import Page, Locator


class ProfilePage:
    """Page Object Model pro profil uživatele (/profile)."""

    URL = "http://testovani.kitner.cz/profile"

    def __init__(self, page: Page):
        self.page = page
        self.heading: Locator = page.get_by_test_id("profile_heading")
        self.name_input: Locator = page.get_by_test_id("profile_name_input")
        self.email_input: Locator = page.get_by_test_id("profile_email_input")
        self.phone_input: Locator = page.get_by_test_id("profile_phone_input")
        self.ico_input: Locator = page.get_by_test_id("profile_ico_input")
        self.button_container: Locator = page.get_by_test_id("profile_button_container")
        self.save_button: Locator = self.button_container.get_by_role("button", name="Uložit")
        self.ico_error: Locator = page.get_by_text("Neplatné IČO")
        self.phone_error: Locator = page.get_by_text("Neplatné telefonní číslo")
        self.email_error: Locator = page.get_by_text("Neplatný email")

    def navigate(self):
        """Otevře přímo URL profilu."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")

    def update_profile(self, name: str = None, email: str = None, phone: str = None, ico: str = None):
        """Vyplní formulář profilu a klikne na Uložit."""
        if name is not None:
            self.name_input.fill(name)
        if email is not None:
            self.email_input.fill(email)
        if phone is not None:
            self.phone_input.fill(phone)
        if ico is not None:
            self.ico_input.fill(ico)
        self.save_button.click()
