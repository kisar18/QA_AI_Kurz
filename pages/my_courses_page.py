from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class MyCoursesPage(BasePage):
    """Page Object Model pro stránku 'Moje kurzy' (/my-courses)."""

    PATH = "/my-courses"

    def __init__(self, page: Page):
        super().__init__(page)
        self.title: Locator = page.get_by_test_id("courses_title")
        self.courses_section: Locator = page.get_by_test_id("courses_section")
        self.date_time_from: Locator = page.get_by_test_id("date_time_from")
        self.date_time_to: Locator = page.get_by_test_id("date_time_to")
        self.day_information: Locator = page.get_by_test_id("day_information")
        self.place_information: Locator = page.get_by_test_id("place_information")
        self.see_more_buttons: Locator = page.get_by_test_id("see_more_button")
