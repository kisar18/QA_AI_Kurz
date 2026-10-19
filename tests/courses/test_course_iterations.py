import re
import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.courses_page import CoursesPage
from pages.course_iteration_create_page import CourseIterationCreatePage
from pages.students_list_page import StudentsListPage
from helpers.step_helpers import step


class TestCourseIterations:
    """Testovací sada pro správu termínů (běhů) kurzů a seznam studentů lektorem (US-15, US-16)."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)
        self.courses_page = CoursesPage(page)
        self.iteration_create_page = CourseIterationCreatePage(page)
        self.students_page = StudentsListPage(page)

    def _login(self, page: Page, user: dict):
        self.login_page.navigate()
        self.login_page.login(user["email"], user["password"])
        page.wait_for_url("**/courses")

    def test_lector_can_create_new_iteration(self, page: Page, lector_user: dict):
        """[US-15] Ověření vytvoření nového termínu (běhu) kurzu lektorem."""
        self._login(page, lector_user)

        # Otevřeme formulář vypsání termínu pro kurz 1
        self.iteration_create_page.open_for_course(1)

        expect(self.iteration_create_page.container).to_be_visible()
        expect(self.iteration_create_page.start_input).to_be_visible()
        expect(self.iteration_create_page.end_input).to_be_visible()
        expect(self.iteration_create_page.day_select).to_be_visible()
        expect(self.iteration_create_page.time_input).to_be_visible()
        expect(self.iteration_create_page.location_input).to_be_visible()
        step("Ověřeny všechny formulářové prvky pro vypsání nového běhu kurzu")

        # Vyplnění a odeslání termínu
        self.iteration_create_page.fill_and_submit(
            start_date="2026-11-01",
            end_date="2026-12-01",
            day_of_week="Pondělí",
            time_str="18:00",
            location="Praha - Školicí centrum / Online",
        )

        # Po odeslání je lektor přesměrován na detail kurzu (/courses/1)
        page.wait_for_url(re.compile(r".*/courses/1$"))
        expect(self.courses_page.course_detail).to_be_visible()
        step("Ověřeno úspěšné vypsání termínu a přesměrování na detail kurzu")

    def test_lector_can_view_participants_list(self, page: Page, lector_user: dict):
        """[US-16] Ověření, že lektor má přístup k seznamu účastníků běhu kurzu."""
        self._login(page, lector_user)

        self.courses_page.navigate("/courses/1")
        expect(self.courses_page.course_detail).to_be_visible()

        # Lektor má u běhů tlačítko 'Přihlášení'
        participants_button = page.get_by_role("button", name="Přihlášení").first
        if participants_button.count() > 0 and participants_button.is_visible():
            participants_button.click()
            page.wait_for_url(re.compile(r".*/courses/\d+/participants"))

            expect(self.students_page.heading).to_be_visible()
            expect(self.students_page.heading).to_have_text("Seznam přihlášených")
            expect(self.students_page.participants_table).to_be_visible()
            step("Ověřeno zobrazení tabulky přihlášených účastníků pro roli lektora")
        else:
            # Přímá navigace na endpoint účastníků
            self.students_page.open_for_iteration(1)
            expect(self.students_page.heading).to_be_visible()
            expect(self.students_page.heading).to_have_text("Seznam přihlášených")
            expect(self.students_page.participants_table).to_be_visible()
            step("Ověřeno zobrazení tabulky účastníků na /courses/:id/participants")

    def test_student_cannot_access_participants_management(self, page: Page, registered_user: dict):
        """[US-16] Ověření, že běžný zákazník/student nemá přístup k lektorskému seznamu účastníků."""
        self._login(page, registered_user)

        self.courses_page.navigate("/courses/1")
        expect(self.courses_page.course_detail).to_be_visible()

        # Tlačítko 'Přihlášení' (účastníci) nesmí být pro studenta zobrazeno
        expect(page.get_by_role("button", name="Přihlášení")).not_to_be_visible()
        step("Ověřeno, že tlačítko 'Přihlášení' (seznam účastníků) není studentovi nabízeno")
