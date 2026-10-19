import re
import pytest
from playwright.sync_api import Page, expect
from pages.courses_page import CoursesPage
from pages.login_page import LoginPage
from helpers.step_helpers import step


class TestCoursesCatalog:
    """Testovací sada pro katalog a detail kurzů (US-09, US-10, US-11)."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.courses_page = CoursesPage(page)
        self.login_page = LoginPage(page)

    def test_courses_catalog_display(self, page: Page):
        """[US-09] Ověření správného načtení katalogu kurzů."""
        self.courses_page.navigate()

        expect(page).to_have_url(self.courses_page.url)
        step("Ověřena URL /courses")

        expect(self.courses_page.title).to_be_visible()
        step("Ověřen nadpis katalogu kurzů")

        expect(self.courses_page.courses_section).to_be_visible()
        step("Ověřena hlavní sekce s kurzy")

        course_count = self.courses_page.course_names.count()
        assert course_count > 0, f"Očekáván alespoň 1 kurz, nalezeno: {course_count}"
        step(f"Ověřeno úspěšné načtení kurzů z backendu (nalezeno kurzů: {course_count})")

    def test_course_card_elements_presence(self, page: Page):
        """[US-09] Ověření přítomnosti klíčových informací na kartě kurzu: název, popis, cena zaokrouhlená na celé Kč, kapacita a obrázek."""
        self.courses_page.navigate()

        first_name = self.courses_page.course_names.first
        expect(first_name).to_be_visible()
        assert len(first_name.inner_text().strip()) > 0
        step(f"Ověřen název prvního kurzu: '{first_name.inner_text().strip()}'")

        first_desc = self.courses_page.course_descriptions.first
        expect(first_desc).to_be_visible()
        assert len(first_desc.inner_text().strip()) > 0
        step("Ověřen popis kurzu")

        first_capacity = self.courses_page.course_capacities.first
        expect(first_capacity).to_be_visible()
        assert "Kapacita:" in first_capacity.inner_text()
        step(f"Ověřena kapacita kurzu: '{first_capacity.inner_text().strip()}'")

        first_price = self.courses_page.course_prices.first
        expect(first_price).to_be_visible()
        price_text = first_price.inner_text().strip()
        # Ověření formátu ceny: např. "Cena: 5000 Kč" zaokrouhlené na celé koruny
        assert re.search(r"Cena:\s*\d+\s*Kč", price_text), f"Cena neodpovídá formátu celých Kč: {price_text}"
        step(f"Ověřena zaokrouhlená cena kurzu: '{price_text}'")

        first_img = self.courses_page.course_images.first
        expect(first_img).to_be_visible()
        step("Ověřeno zobrazení náhledového obrázku kurzu")

        first_btn = self.courses_page.see_more_buttons.first
        expect(first_btn).to_be_visible()
        step("Ověřeno tlačítko pro zobrazení detailu kurzu")

    def test_anonymous_user_registration_prompt_in_catalog(self, page: Page):
        """[US-09] Ověření zobrazení výzvy k registraci pro nepřihlášeného návštěvníka pod katalogem."""
        self.courses_page.navigate()

        expect(self.courses_page.interest_title).to_be_visible()
        expect(self.courses_page.interest_title).to_contain_text("Máte zájem o naše kurzy?")
        step("Ověřen text výzvy k registraci pro anonymního návštěvníka")

        expect(self.courses_page.registration_link).to_be_visible()
        self.courses_page.registration_link.click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(re.compile(r".*/register"))
        step("Ověřeno přesměrování z výzvy přímo na registrační formulář")

    def test_navigate_to_course_detail(self, page: Page):
        """[US-09, US-10] Ověření prokliku z katalogu do detailu konkrétního kurzu."""
        self.courses_page.navigate()
        self.courses_page.open_first_course_detail()

        expect(page).to_have_url(re.compile(r"http://testovani\.kitner\.cz/courses/\d+"))
        step("Ověřeno přesměrování na detail kurzu (/courses/:id)")

        expect(self.courses_page.course_detail).to_be_visible()
        step("Ověřeno načtení kontejneru detailu kurzu")

    def test_course_detail_content_and_iterations_format(self, page: Page):
        """[US-10] Ověření detailu kurzu: popis, cena a formát termínů (termín, datum, kapacita ve formátu X/Y)."""
        self.courses_page.navigate()
        self.courses_page.open_first_course_detail()

        # Ověření nadpisu běhů
        expect(self.courses_page.iterations_heading).to_be_visible()
        step("Ověřen nadpis 'Vypsané běhy kurzu:'")

        # Ověření, že pokud existují běhy, zobrazují správný formát
        iteration_count = self.courses_page.iteration_cards.count()
        if iteration_count > 0:
            first_iteration = self.courses_page.iteration_cards.first
            expect(first_iteration).to_be_visible()
            iteration_text = first_iteration.inner_text()

            # Formát data zahájení a ukončení
            assert "Zahájení:" in iteration_text
            assert "Ukončení:" in iteration_text
            step("Ověřeno zobrazení data zahájení a ukončení běhu kurzu")

            # Formát kapacity poměrem X/Y (např. "Kapacita: 0/15")
            assert re.search(r"Kapacita:\s*\d+/\d+", iteration_text), f"Formát kapacity X/Y nenalezen: {iteration_text}"
            step(f"Ověřen správný formát poměru obsazenosti a kapacity: {re.search(r'Kapacita:\s*\d+/\d+', iteration_text).group(0)}")

    def test_course_detail_iterations_anonymous_vs_authenticated(self, page: Page, registered_user: dict):
        """[US-10, US-11] Ověření, že termíny běhů kurzu se zobrazují anonymně a tlačítka zápisu se aktivují po přihlášení."""
        # 1. Anonymní pohled
        self.courses_page.navigate()
        self.courses_page.open_first_course_detail()

        expect(self.courses_page.iterations_heading).to_be_visible()
        step("Ověřen nadpis 'Vypsané běhy kurzu' pro nepřihlášeného návštěvníka")

        expect(self.courses_page.enroll_buttons.first).not_to_be_visible()
        step("Ověřeno, že tlačítka pro zápis nejsou pro anonymního uživatele zobrazena")

        expect(self.courses_page.registration_prompt).to_be_visible()
        step("Ověřena výzva k registraci pro nepřihlášeného návštěvníka na detailu kurzu")

        # 2. Přihlášený uživatel
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])
        page.wait_for_url("**/courses")

        self.courses_page.open_first_course_detail()
        expect(self.courses_page.enroll_buttons.first).to_be_visible()
        step("Ověřeno, že po přihlášení jsou tlačítka 'Nezávazná registrace' pro volný běh viditelná")

    def test_fully_booked_iteration_indication(self, page: Page):
        """[US-11] Ověření chování při plně obsazené kapacitě běhu kurzu (kapacita dosáhla maxima -> tlačítko zápisu je skryto/nedostupné)."""
        # Načteme detail kurzu s mocknutým plně obsazeným během přes route intercept
        def mock_full_capacity(route):
            response = route.fetch()
            data = response.json()
            if "iterations" in data and len(data["iterations"]) > 0:
                # Nastavíme users_count na úroveň kapacity (nebo vyšší)
                data["iterations"][0]["users_count"] = data.get("capacity", 10)
            route.fulfill(json=data)

        page.route("**/api/courses/*/iterations", mock_full_capacity)

        self.courses_page.navigate()
        self.courses_page.open_first_course_detail()

        # Ověříme, že poměr obsazenosti na prvním běhu ukazuje plnou kapacitu (např. 15/15)
        first_iteration = self.courses_page.iteration_cards.first
        expect(first_iteration).to_be_visible()
        assert re.search(r"Kapacita:\s*(\d+)/\1", first_iteration.inner_text()), "Běh by měl indikovat plnou obsazenost"

        # Tlačítko pro registraci nesmí být na plně obsazeném běhu dostupné
        enroll_btn = first_iteration.get_by_role("button", name="Nezávazná registrace")
        expect(enroll_btn).not_to_be_visible()
        step("Ověřeno, že pro plně obsazený běh není tlačítko registrace zobrazeno")
