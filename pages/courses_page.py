import re
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
        self.course_images: Locator = page.get_by_test_id("course_image")
        self.course_capacities: Locator = page.get_by_test_id("course_capacity")
        self.detail_buttons: Locator = page.locator("button[data-testid='registration_link']")
        self.see_more_buttons: Locator = self.detail_buttons  # Tlačítka 'Chci vidět více'

        # Výzva k registraci pro nepřihlášené v katalogu i na detailu
        self.interest_title: Locator = page.get_by_test_id("interest_title")
        self.registration_link: Locator = page.locator("a[data-testid='registration_link']")
        self.registration_prompt: Locator = page.get_by_test_id("registration_prompt")

        # Prvky na detailu kurzu (/courses/:id)
        self.course_detail: Locator = page.get_by_test_id("course_detail")
        self.iterations_heading: Locator = page.get_by_test_id("iterations_heading")
        self.iteration_cards: Locator = page.locator("[data-testid^='iteration_']")
        self.enroll_buttons: Locator = page.get_by_role("button", name="Nezávazná registrace")

        # Lektorská akční tlačítka
        self.add_course_button: Locator = page.get_by_role("button", name="Přidat kurz")
        self.add_iteration_buttons: Locator = page.get_by_test_id("add_iteration_button")
        self.participants_buttons: Locator = page.get_by_role("button", name="Přihlášení")

    def open_first_course_detail(self):
        """Proklikne na detail prvního kurzu v katalogu."""
        self.detail_buttons.first.click()
        self.page.wait_for_url(re.compile(r".*/courses/\d+"))
        self.page.wait_for_load_state("networkidle")
