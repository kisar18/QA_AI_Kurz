from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class CoursesPage(BasePage):
    """Page Object Model pro katalog a detail kurzů (/courses)."""

    PATH = "/courses"

    def __init__(self, page: Page):
        super().__init__(page)
        self.title: Locator = page.get_by_test_id("courses_title")
        self.courses_section: Locator = page.get_by_test_id("courses_section")
        self.course_names: Locator = page.get_by_test_id("course_name")
        self.course_descriptions: Locator = page.get_by_test_id("course_description")
        self.course_prices: Locator = page.get_by_test_id("course_price")
        self.detail_buttons: Locator = page.get_by_test_id("registration_link")

        # Prvky na detailu kurzu (/courses/:id)
        self.course_detail: Locator = page.get_by_test_id("course_detail")
        self.iterations_heading: Locator = page.get_by_test_id("iterations_heading")
        self.enroll_buttons: Locator = page.get_by_role("button", name="Nezávazná registrace")

    def open_first_course_detail(self):
        """Proklikne na detail prvního kurzu v katalogu."""
        self.detail_buttons.first.click()
        self.page.wait_for_load_state("networkidle")
