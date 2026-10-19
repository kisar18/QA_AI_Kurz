"""
Page Object pro sdílenou navigační lištu (navbar) přítomnou na všech stránkách.
"""

from playwright.sync_api import Page, Locator


class Navbar:
    """Komponenta navigační lišty – sdílená na všech stránkách."""

    def __init__(self, page: Page):
        self.page = page
        self.login_link: Locator = page.get_by_test_id("login_link")
        self.logout_button: Locator = page.get_by_test_id("logout_button")
        self.courses_link: Locator = page.get_by_test_id("courses_link")
        self.home_link: Locator = page.get_by_test_id("home_link")
        self.my_courses_link: Locator = page.get_by_role("link", name="Moje kurzy")
        self.profile_link: Locator = page.get_by_test_id("courses_profile")

    def logout(self):
        """Odhlásí přihlášeného uživatele kliknutím na 'Odhlásit se'."""
        self.logout_button.click()
        self.login_link.wait_for(state="visible")

    def is_logged_in(self) -> bool:
        """Vrátí True, pokud je uživatel přihlášen (tlačítko Odhlásit je viditelné)."""
        return self.logout_button.is_visible()
