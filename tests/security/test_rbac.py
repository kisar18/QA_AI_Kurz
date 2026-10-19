import re
import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.courses_page import CoursesPage
from helpers.step_helpers import step


class TestRoleBasedAccessControl:
    """Testovací sada pro řízení přístupu na základě rolí (RBAC - US-19)."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)
        self.courses_page = CoursesPage(page)

    def _login(self, page: Page, user: dict):
        self.login_page.navigate()
        self.login_page.login(user["email"], user["password"])
        page.wait_for_url("**/courses")

    def test_anonymous_access_to_private_routes_is_restricted(self, page: Page):
        """[US-19] Ověření, že nepřihlášený návštěvník nemá přístup k privátním sekcím (/profile a /my-courses)."""
        # Pokus o otevření /profile bez přihlášení
        page.goto(f"{self.login_page.base_url}/profile")
        page.wait_for_load_state("networkidle")
        # Anonymní uživatel nesmí vidět formulář profilu
        expect(page.get_by_test_id("profile_name_input")).not_to_be_visible()
        step("Ověřeno, že nepřihlášený uživatel nevidí profil")

        # Pokus o otevření /my-courses bez přihlášení
        page.goto(f"{self.login_page.base_url}/my-courses")
        page.wait_for_load_state("networkidle")
        # Bez přihlášení nesmí být k dispozici privátní zapsané kurzy
        expect(page.get_by_test_id("date_time_from")).not_to_be_visible()
        step("Ověřeno, že nepřihlášený uživatel nevidí zapsané kurzy")

    def test_student_cannot_access_lector_create_course(self, page: Page, registered_user: dict):
        """[US-19] Ověření, že běžný student nemá v navigaci tlačítko pro přidání kurzu ani oprávnění pro lektorské rozhraní."""
        self._login(page, registered_user)

        # V katalogu student nesmí vidět tlačítko 'Přidat kurz'
        self.courses_page.navigate()
        expect(page.get_by_role("button", name="Přidat kurz")).not_to_be_visible()
        step("Ověřeno, že student nemá v přehledu kurzů tlačítko 'Přidat kurz'")

        # V katalogu student nesmí vidět tlačítka 'Přidat iteraci'
        expect(page.get_by_test_id("add_iteration_button")).not_to_be_visible()
        step("Ověřeno, že student nemá tlačítka 'Přidat iteraci'")

    def test_lector_cannot_enroll_in_course_as_customer(self, page: Page, lector_user: dict):
        """[US-19] Ověření, že lektor nemá možnost se zapsat na běh kurzu (místo tlačítka zápisu vidí tlačítko přihlášených studentů)."""
        self._login(page, lector_user)

        self.courses_page.navigate("/courses/1")
        expect(self.courses_page.course_detail).to_be_visible()

        # Lektor nesmí vidět tlačítko 'Nezávazná registrace' (zápis je vyhrazen zákazníkům)
        expect(page.get_by_role("button", name="Nezávazná registrace")).not_to_be_visible()
        step("Ověřeno, že role lektora nemá možnost registrovat se na kurz jako zákazník")

        # Lektor vidí tlačítko 'Přihlášení' pro zobrazení přehledu studentů
        expect(page.get_by_role("button", name="Přihlášení").first).to_be_visible()
        step("Ověřeno, že role lektora vidí tlačítko pro správu účastníků")
