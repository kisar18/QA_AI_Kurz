import re
import pytest
from playwright.sync_api import Page, expect
from pages.courses_page import CoursesPage
from pages.course_enroll_page import CourseEnrollPage
from pages.my_courses_page import MyCoursesPage
from pages.login_page import LoginPage
from utils.data_generator import generate_valid_ico, generate_invalid_ico
from helpers.step_helpers import step


class TestCourseEnrollment:
    """Testovací sada pro zápis na běh kurzu a zobrazení zapsaných kurzů (US-12, US-13)."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.courses_page = CoursesPage(page)
        self.enroll_page = CourseEnrollPage(page)
        self.my_courses_page = MyCoursesPage(page)
        self.login_page = LoginPage(page)

    def test_enrollment_form_elements_presence(self, page: Page, registered_user: dict):
        """[US-12] Ověření přítomnosti formulářových prvků pro zápis na kurz."""
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])
        page.wait_for_url("**/courses")

        self.courses_page.open_first_course_detail()
        expect(self.courses_page.enroll_buttons.first).to_be_visible()
        self.courses_page.enroll_buttons.first.click()
        page.wait_for_url(re.compile(r".*/courses/\d+/register"))

        expect(self.enroll_page.registration_section).to_be_visible()
        expect(self.enroll_page.registration_title).to_be_visible()
        expect(self.enroll_page.ico_input).to_be_visible()
        expect(self.enroll_page.phone_input).to_be_visible()
        expect(self.enroll_page.submit_button).to_be_visible()
        step("Ověřena přítomnost všech prvků formuláře pro zápis na kurz")

    def test_enrollment_ico_validation(self, page: Page, registered_user: dict):
        """[US-12] Ověření validace IČO pomocí váženého kontrolního součtu modulo 11."""
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])
        page.wait_for_url("**/courses")

        self.courses_page.open_first_course_detail()
        self.courses_page.enroll_buttons.first.click()
        page.wait_for_url(re.compile(r".*/courses/\d+/register"))

        invalid_ico = generate_invalid_ico()
        self.enroll_page.fill_and_submit(ico=invalid_ico, phone="+420777123456")

        expect(self.enroll_page.ico_error).to_be_visible()
        expect(self.enroll_page.ico_error).to_have_text("Neplatné IČO")
        step(f"Ověřeno odmítnutí neplatného IČO '{invalid_ico}' a zobrazení chybové hlášky")

    def test_enrollment_phone_validation(self, page: Page, registered_user: dict):
        """[US-12] Ověření validace telefonního čísla (minimálně 9 číslic)."""
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])
        page.wait_for_url("**/courses")

        self.courses_page.open_first_course_detail()
        self.courses_page.enroll_buttons.first.click()
        page.wait_for_url(re.compile(r".*/courses/\d+/register"))

        valid_ico = generate_valid_ico()
        self.enroll_page.fill_and_submit(ico=valid_ico, phone="12345")

        expect(self.enroll_page.phone_error).to_be_visible()
        expect(self.enroll_page.phone_error).to_have_text("Telefonní číslo musí obsahovat alespoň 9 číslic.")
        step("Ověřeno zobrazení validační chyby při zadání krátkého telefonního čísla")

    def test_successful_enrollment_and_my_courses_display(self, page: Page, registered_user: dict):
        """[US-12, US-13] Úspěšné odeslání zápisu na kurz a ověření zobrazení v 'Moje kurzy'."""
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])
        page.wait_for_url("**/courses")

        self.courses_page.open_first_course_detail()
        expect(self.courses_page.enroll_buttons.first).to_be_visible()
        self.courses_page.enroll_buttons.first.click()
        page.wait_for_url(re.compile(r".*/courses/\d+/register"))

        valid_ico = generate_valid_ico()
        valid_phone = "+420777888999"

        # Přijmeme vyskakovací alert prohlížeče ("proběhla úspěšná registrace")
        page.on("dialog", lambda dialog: dialog.accept())

        self.enroll_page.fill_and_submit(ico=valid_ico, phone=valid_phone)

        # Ověření přesměrování na /my-courses (US-12)
        page.wait_for_url("**/my-courses")
        expect(self.my_courses_page.title).to_be_visible()
        expect(self.my_courses_page.title).to_have_text("Mé zapsané kurzy")
        step("Ověřeno přesměrování po úspěšném zápisu na stránku /my-courses")

        # Ověření informací o zapsaném kurzu (US-13)
        expect(self.my_courses_page.courses_section).to_be_visible()
        if self.my_courses_page.date_time_from.count() > 0:
            expect(self.my_courses_page.date_time_from.first).to_be_visible()
            expect(self.my_courses_page.date_time_to.first).to_be_visible()
            expect(self.my_courses_page.day_information.first).to_be_visible()
            expect(self.my_courses_page.place_information.first).to_be_visible()
            step("Ověřeno zobrazení termínů lekcí, dne a místa konání zapsaného kurzu")
