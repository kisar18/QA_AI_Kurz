from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class CourseCreatePage(BasePage):
    """Page Object Model pro formulář vytvoření nového kurzu (/courses/create)."""

    PATH = "/courses/create"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading: Locator = page.get_by_test_id("create_course_title")
        self.name_input: Locator = page.get_by_test_id("course_name_input")
        self.description_input: Locator = page.get_by_test_id("course_description_input")
        self.capacity_input: Locator = page.get_by_test_id("course_capacity_input")
        self.price_input: Locator = page.get_by_test_id("course_price_input")
        self.image_input: Locator = page.get_by_test_id("course_file_input")
        # TODO(testid): submit button sdílí obecný role button
        self.submit_button: Locator = page.get_by_role("button", name="Vytvořit kurz")

    def create_course(
        self,
        name: str = "",
        description: str = "",
        capacity: int | str | None = None,
        price: int | str | None = None,
        image_path: str = None,
    ):
        """Vyplní formulář a odešle vytvoření nového kurzu."""
        if name:
            self.name_input.fill(name)
        else:
            self.name_input.clear()

        if description:
            self.description_input.fill(description)
        else:
            self.description_input.clear()

        if capacity is not None:
            self.capacity_input.fill(str(capacity))
        else:
            self.capacity_input.clear()

        if price is not None:
            self.price_input.fill(str(price))
        else:
            self.price_input.clear()

        if image_path:
            self.image_input.set_input_files(image_path)

        self.submit_button.click()
