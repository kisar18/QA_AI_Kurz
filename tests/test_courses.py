import re
import pytest
from playwright.sync_api import Page, expect
from pages.courses_page import CoursesPage
from pages.login_page import LoginPage
from pages.helpers import step


class TestCoursesCatalog:
    """Testovací sada pro katalog a detail kurzů (/courses)."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.courses_page = CoursesPage(page)
        self.login_page = LoginPage(page)

    def test_courses_catalog_display(self, page: Page):
        """Ověření správného načtení katalogu kurzů."""
        self.courses_page.navigate()

        expect(page).to_have_url("http://testovani.kitner.cz/courses")
        step("Ověřena URL /courses")

        expect(self.courses_page.title).to_be_visible()
        step("Ověřen nadpis katalogu kurzů")

        expect(self.courses_page.courses_section).to_be_visible()
        step("Ověřena hlavní sekce s kurzy")

        course_count = self.courses_page.course_names.count()
        assert course_count > 0, f"Očekáván alespoň 1 kurz, nalezeno: {course_count}"
        step(f"Ověřeno úspěšné načtení kurzů z backendu (nalezeno kurzů: {course_count})")

    def test_course_card_elements_presence(self, page: Page):
        """Ověření přítomnosti klíčových informací na kartě kurzu."""
        self.courses_page.navigate()

        first_name = self.courses_page.course_names.first
        expect(first_name).to_be_visible()
        assert len(first_name.inner_text().strip()) > 0
        step(f"Ověřen název prvního kurzu: '{first_name.inner_text().strip()}'")

        first_price = self.courses_page.course_prices.first
        expect(first_price).to_be_visible()
        step(f"Ověřena cena kurzu: '{first_price.inner_text().strip()}'")

        first_btn = self.courses_page.detail_buttons.first
        expect(first_btn).to_be_visible()
        step("Ověřeno tlačítko pro zobrazení detailu kurzu")

    def test_navigate_to_course_detail(self, page: Page):
        """Ověření prokliku z katalogu do detailu konkrétního kurzu."""
        self.courses_page.navigate()
        self.courses_page.open_first_course_detail()

        expect(page).to_have_url(re.compile(r"http://testovani\.kitner\.cz/courses/\d+"))
        step("Ověřeno přesměrování na detail kurzu (/courses/:id)")

        expect(self.courses_page.course_detail).to_be_visible()
        step("Ověřeno načtení kontejneru detailu kurzu")

    def test_course_detail_iterations_anonymous_vs_authenticated(self, page: Page, registered_user: dict):
        """Ověření, že termíny běhů kurzu se zobrazují anonymně a tlačítka zápisu se aktivují po přihlášení."""
        # 1. Anonymní pohled
        self.courses_page.navigate()
        self.courses_page.open_first_course_detail()

        expect(self.courses_page.iterations_heading).to_be_visible()
        step("Ověřen nadpis 'Vypsané běhy kurzu' pro nepřihlášeného návštěvníka")

        expect(self.courses_page.enroll_buttons.first).not_to_be_visible()
        step("Ověřeno, že tlačítka pro zápis nejsou pro anonymního uživatele zobrazena")

        # 2. Přihlášený uživatel
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])
        page.wait_for_url("**/courses")

        self.courses_page.open_first_course_detail()
        expect(self.courses_page.enroll_buttons.first).to_be_visible()
        step("Ověřeno, že po přihlášení jsou tlačítka 'Nezávazná registrace' viditelná")
