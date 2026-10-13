import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.course_create_page import CourseCreatePage
from pages.helpers import step


class TestCourseManagement:
    """Testovací sada pro správu a životní cyklus kurzů (/courses/create a /my-courses)."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)
        self.course_create_page = CourseCreatePage(page)

    def _login(self, page: Page, user: dict):
        self.login_page.navigate()
        self.login_page.login(user["email"], user["password"])
        page.wait_for_url("**/courses")

    def test_course_create_form_elements_presence(self, page: Page, registered_user: dict):
        """Ověření zobrazení formuláře pro vytvoření kurzu a jeho polí."""
        self._login(page, registered_user)
        self.course_create_page.navigate()

        expect(page).to_have_url("http://testovani.kitner.cz/courses/create")
        step("Ověřena URL /courses/create")

        expect(self.course_create_page.heading).to_be_visible()
        step("Ověřen nadpis 'Vytvořit kurz'")

        expect(self.course_create_page.name_input).to_be_visible()
        step("Ověřeno pole pro název kurzu")

        expect(self.course_create_page.description_input).to_be_visible()
        step("Ověřeno pole pro popis kurzu")

        expect(self.course_create_page.capacity_input).to_be_visible()
        step("Ověřeno pole pro kapacitu")

        expect(self.course_create_page.price_input).to_be_visible()
        step("Ověřeno pole pro cenu")

        expect(self.course_create_page.submit_button).to_be_visible()
        step("Ověřeno tlačítko 'Vytvořit kurz'")

    def test_course_create_submission_flow(self, page: Page, registered_user: dict):
        """Ověření vyplnění a odeslání formuláře nového kurzu s přesměrováním do přehledu."""
        self._login(page, registered_user)
        self.course_create_page.navigate()

        course_name = "Automatizovaný QA Kurz"
        description = "Testovací popis pro ověření odeslání kurzu"

        self.course_create_page.create_course(
            name=course_name,
            description=description,
            capacity=12,
            price=1990,
        )

        expect(page).to_have_url("http://testovani.kitner.cz/courses/")
        step("Ověřeno úspěšné odeslání formuláře a přesměrování na přehled kurzů (/courses/)")

    def test_my_courses_page_display(self, page: Page, registered_user: dict):
        """Ověření načtení stránky zapsaných kurzů přihlášeného klienta (/my-courses)."""
        self._login(page, registered_user)
        page.goto("http://testovani.kitner.cz/my-courses")
        page.wait_for_load_state("networkidle")

        expect(page).to_have_url("http://testovani.kitner.cz/my-courses")
        step("Ověřena URL /my-courses")

        expect(page.get_by_test_id("courses_title")).to_be_visible()
        expect(page.get_by_test_id("courses_title")).to_have_text("Mé zapsané kurzy")
        step("Ověřen nadpis sekce 'Mé zapsané kurzy'")

        expect(page.get_by_test_id("courses_section")).to_be_visible()
        step("Ověřena sekce pro zobrazení kurzů uživatele")
