from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class CourseIterationCreatePage(BasePage):
    """Page Object Model pro vypsání nového běhu kurzu (/courses/:id/create-iteration)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.container: Locator = page.get_by_test_id("create_course_iteration_container")
        self.start_input: Locator = page.get_by_test_id("course_start_input")
        self.end_input: Locator = page.get_by_test_id("course_end_input")
        self.day_select: Locator = page.get_by_test_id("course_day_select")
        self.time_input: Locator = page.get_by_test_id("course_time_input")
        self.location_input: Locator = page.get_by_test_id("course_location_input")
        self.submit_button: Locator = page.get_by_role("button", name="Přidat iteraci")
        self.error_message: Locator = page.get_by_test_id("course_iteration_error")

    def open_for_course(self, course_id: int | str):
        """Otevře stránku pro vytvoření termínu pro daný kurz."""
        self.navigate(f"/courses/{course_id}/create-iteration")

    def fill_and_submit(
        self,
        start_date: str,
        end_date: str,
        day_of_week: str,
        time_str: str,
        location: str,
    ):
        """Vyplní formulář pro nový termín kurzu a odešle jej."""
        if start_date:
            self.start_input.fill(start_date)
        if end_date:
            self.end_input.fill(end_date)
        if day_of_week:
            self.day_select.select_option(value=day_of_week)
        if time_str:
            self.time_input.fill(time_str)
        if location:
            self.location_input.fill(location)

        self.submit_button.click()
