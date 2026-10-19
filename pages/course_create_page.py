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
        self.image_input: Locator = page.locator("input[type='file']")
        self.submit_button: Locator = page.get_by_role("button", name="Vytvořit kurz")

    def create_course(self, name: str, description: str, capacity: int, price: int, image_path: str = None):
        """Vyplní formulář a odešle vytvoření nového kurzu.

        Args:
            name: Název kurzu.
            description: Popis kurzu.
            capacity: Maximální kapacita účastníků (kladné celé číslo).
            price: Cena kurzu v Kč.
            image_path: Volitelná absolutní cesta k souboru náhledového obrázku.
        """
        if name:
            self.name_input.fill(name)
        if description:
            self.description_input.fill(description)
        if capacity is not None:
            self.capacity_input.fill(str(capacity))
        if price is not None:
            self.price_input.fill(str(price))
        if image_path:
            self.image_input.set_input_files(image_path)
        self.submit_button.click()
