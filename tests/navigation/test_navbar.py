import pytest
from playwright.sync_api import Page, expect
from pages.courses_page import CoursesPage
from pages.login_page import LoginPage
from pages.components.navbar import Navbar
from helpers.step_helpers import step


class TestNavigationNavbar:
    """Testy navigace a odkazů v horní navigační liště (Navbar)."""

    def test_navigation_between_courses_and_login(self, page: Page):
        """Ověření navigace mezi katalogem kurzů a přihlášením přes navbar."""
        courses_page = CoursesPage(page)
        login_page = LoginPage(page)
        navbar = Navbar(page)

        courses_page.navigate()
        expect(navbar.courses_link).to_be_visible()
        expect(navbar.login_link).to_be_visible()
        step("Navbar prvky v katalogu kurzů jsou viditelné")

        navbar.login_link.click()
        page.wait_for_url("**/login")
        expect(login_page.login_title).to_be_visible()
        step("Úspěšná navigace z katalogu kurzů do přihlášení")

        navbar.courses_link.click()
        page.wait_for_url("**/courses")
        expect(courses_page.title).to_be_visible()
        step("Úspěšná zpětná navigace z přihlášení do katalogu kurzů")
