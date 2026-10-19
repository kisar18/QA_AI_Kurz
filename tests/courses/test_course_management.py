import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.course_create_page import CourseCreatePage
from helpers.step_helpers import step


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

    def test_course_create_form_elements_presence(self, page: Page, lector_user: dict):
        """Ověření zobrazení formuláře pro vytvoření kurzu a jeho polí (pod účtem lektora)."""
        self._login(page, lector_user)
        self.course_create_page.navigate()

        expect(page).to_have_url(self.course_create_page.url)
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

    def test_course_create_submission_flow(self, page: Page, lector_user: dict):
        """Ověření vyplnění a odeslání formuláře nového kurzu lektorem s přesměrováním do přehledu."""
        self._login(page, lector_user)
        self.course_create_page.navigate()

        course_name = "Automatizovaný QA Kurz"
        description = "Testovací popis pro ověření odeslání kurzu"

        self.course_create_page.create_course(
            name=course_name,
            description=description,
            capacity=12,
            price=1990,
        )

        expect(page).to_have_url(f"{self.course_create_page.base_url}/courses/")
        step("Ověřeno úspěšné odeslání formuláře a přesměrování na přehled kurzů (/courses/)")

    def test_course_create_image_aspect_ratio_validation(self, page: Page, lector_user: dict):
        """[US-14] Ověření validace poměru stran náhledového obrázku kurzu (požadován 16:9 s tolerancí 5 %)."""
        from utils.image_generator import create_png_image

        invalid_img = create_png_image("data/test_1_1.png", width=100, height=100)
        valid_img = create_png_image("data/test_16_9.png", width=160, height=90)

        self._login(page, lector_user)
        self.course_create_page.navigate()

        # 1. Neplatný poměr stran (1:1) -> vyvolá alert a vyčistí input
        alert_messages = []

        def handle_dialog(dialog):
            alert_messages.append(dialog.message)
            dialog.accept()

        page.on("dialog", handle_dialog)

        self.course_create_page.image_input.set_input_files(str(invalid_img.resolve()))
        page.wait_for_timeout(1000)

        assert any("správný poměr stran" in msg for msg in alert_messages), f"Očekávané chybové hlášení v alertu se nezobrazilo: {alert_messages}"
        assert self.course_create_page.image_input.input_value() == "", "Input souboru měl být po neplatném poměru stran vymazán"
        step("Ověřeno zamítnutí obrázku s neplatným poměrem stran (1:1) a zobrazení varovného alertu")

        # 2. Platný poměr stran (16:9) -> alert se nezobrazí a soubor zůstane nastaven
        alert_messages.clear()
        self.course_create_page.image_input.set_input_files(str(valid_img.resolve()))
        page.wait_for_timeout(1000)

        assert len(alert_messages) == 0, f"Pro platný poměr stran 16:9 se neměl zobrazit žádný alert: {alert_messages}"
        assert self.course_create_page.image_input.input_value() != "", "Platný obrázek 16:9 měl zůstat v inputu nastaven"
        step("Ověřeno úspěšné přijetí obrázku s poměrem stran 16:9")
