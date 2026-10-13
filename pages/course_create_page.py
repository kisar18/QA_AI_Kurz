from playwright.sync_api import Page, Locator


class CourseCreatePage:
    """Page Object Model pro formulář vytvoření nového kurzu (/courses/create)."""

    URL = "http://testovani.kitner.cz/courses/create"

    def __init__(self, page: Page):
        self.page = page
        self.heading: Locator = page.get_by_test_id("create_course_title")
        self.name_input: Locator = page.get_by_test_id("course_name_input")
        self.description_input: Locator = page.get_by_test_id("course_description_input")
        self.capacity_input: Locator = page.get_by_test_id("course_capacity_input")
        self.price_input: Locator = page.get_by_test_id("course_price_input")
        self.submit_button: Locator = page.get_by_role("button", name="Vytvořit kurz")

    def navigate(self):
        """Otevře přímo URL pro vytvoření kurzu."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")

    def create_course(self, name: str, description: str, capacity: int, price: int):
        """Vyplní formulář a odešle vytvoření nového kurzu."""
        if name:
            self.name_input.fill(name)
        if description:
            self.description_input.fill(description)
        if capacity is not None:
            self.capacity_input.fill(str(capacity))
        if price is not None:
            self.price_input.fill(str(price))
        self.submit_button.click()
