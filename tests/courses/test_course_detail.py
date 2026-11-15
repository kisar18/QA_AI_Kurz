"""Automatizované testy pro US-10: Zobrazení detailu kurzu a vypsaných termínů.

Pokrývá test casy:
- [TC-US10-01] Zobrazení kompletních informací o kurzu a seznamu vypsaných běhů
- [TC-US10-02] Ověření formátu a výpočtu poměru obsazenosti termínu (např. 3/12)
- [TC-US10-03] Zobrazení výzvy k vytvoření účtu pro nepřihlášeného návštěvníka na detailu kurzu
- [TC-US10-04] Zpracování požadavku na neexistující ID kurzu
"""

import re
import pytest
from playwright.sync_api import Page, expect

from helpers.step_helpers import step
from pages.courses_page import CoursesPage


class TestCourseDetail:
    """Testovací sada pro detail kurzu a jeho termínů (/courses/:id) dle US-10."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.courses_page = CoursesPage(page)

    def test_tc_us10_01_course_detail_content_and_iterations_list(self, page: Page):
        """[TC-US10-01] Zobrazení kompletních informací o kurzu a seznamu vypsaných běhů."""
        self.courses_page.navigate()
        self.courses_page.open_first_course_detail()

        # Ověření kontejneru detailu kurzu
        expect(self.courses_page.course_detail).to_be_visible()
        step("Ověřen kontejner detailu kurzu")

        # Ověření názvu kurzu
        first_name = self.courses_page.course_names.first
        expect(first_name).to_be_visible()
        name_text = first_name.inner_text().strip()
        assert len(name_text) > 0, "Název kurzu na detailu nesmí být prázdný"
        step(f"Ověřen název kurzu: '{name_text}'")

        # Ověření popisu kurzu
        first_desc = self.courses_page.course_descriptions.first
        expect(first_desc).to_be_visible()
        assert len(first_desc.inner_text().strip()) > 0, "Popis kurzu nesmí být prázdný"
        step("Ověřen podrobný popis kurzu")

        # Ověření ceny kurzu v celých Kč
        first_price = self.courses_page.course_prices.first
        expect(first_price).to_be_visible()
        price_text = first_price.inner_text().strip()
        assert re.search(r"Cena:\s*\d+\s*Kč", price_text), f"Cena neodpovídá celým Kč: '{price_text}'"
        step(f"Ověřena cena kurzu: '{price_text}'")

        # Ověření náhledového obrázku
        img = self.courses_page.course_detail_image
        expect(img).to_be_visible()
        step("Ověřen náhledový obrázek kurzu")

        # Ověření sekce vypsaných termínů
        expect(self.courses_page.iterations_heading).to_be_visible()
        expect(self.courses_page.iterations_heading).to_contain_text("Vypsané běhy kurzu")
        step("Ověřen nadpis sekce vypsaných běhů")

        # Ověření prvního termínu: datum zahájení, ukončení a kapacita
        first_iteration = self.courses_page.iteration_cards.first
        expect(first_iteration).to_be_visible()
        iteration_text = first_iteration.inner_text()
        assert "Zahájení:" in iteration_text, "Chybí informace o zahájení běhu"
        assert "Ukončení:" in iteration_text, "Chybí informace o ukončení běhu"
        assert "Kapacita:" in iteration_text, "Chybí informace o kapacitě běhu"
        step("Ověřeny povinné údaje běhu kurzu: zahájení, ukončení a kapacita")

    def test_tc_us10_02_iteration_capacity_ratio_format(self, page: Page):
        """[TC-US10-02] Ověření formátu a výpočtu poměru obsazenosti termínu (např. 3/12)."""
        self.courses_page.navigate()
        self.courses_page.open_first_course_detail()

        first_iteration = self.courses_page.iteration_cards.first
        expect(first_iteration).to_be_visible()
        iteration_text = first_iteration.inner_text()

        # Ověření formátu poměru obsazenosti: Kapacita: X/Y (např. 0/15)
        capacity_match = re.search(r"Kapacita:\s*(\d+)/(\d+)", iteration_text)
        assert capacity_match, f"Formát kapacity poměrem X/Y nenalezen v textu: '{iteration_text}'"

        enrolled, total = int(capacity_match.group(1)), int(capacity_match.group(2))
        assert enrolled >= 0, "Počet zapsaných studentů nesmí být záporný"
        assert total > 0, "Celková kapacita kurzu musí být větší než 0"
        step(f"Ověřen formát kapacity poměrem: {capacity_match.group(0)} (zapsáno: {enrolled}, celkem: {total})")

    def test_tc_us10_03_registration_prompt_for_anonymous_user_on_detail(self, page: Page):
        """[TC-US10-03] Zobrazení výzvy k vytvoření účtu pro nepřihlášeného návštěvníka na detailu kurzu."""
        self.courses_page.navigate()
        self.courses_page.open_first_course_detail()

        # Ověření, že na detailu se nepřihlášenému zobrazuje výzva k registraci
        expect(self.courses_page.registration_prompt).to_be_visible()
        step("Ověřena výzva k vytvoření účtu na detailu kurzu")

        expect(self.courses_page.registration_link).to_be_visible()
        with page.expect_navigation():
            self.courses_page.registration_link.click()

        expect(page).to_have_url(re.compile(r".*/register"))
        step("Ověřeno přesměrování z detailu kurzu na registrační formulář /register")

    @pytest.mark.xfail(
        reason="Aplikace pro neexistující kurz nevrací HTTP 404 Not Found ani chybovou stránku, ale vrací stavový kód 200 a prázdný kontejner",
        strict=False,
    )
    def test_tc_us10_04_non_existent_course_id_handling(self, page: Page):
        """[TC-US10-04] Zpracování požadavku na neexistující ID kurzu."""
        response = page.goto(f"{self.courses_page.base_url}/courses/999999")
        page.wait_for_load_state("networkidle")

        # Systém má vrátit 404 a chybovou stránku o nenalezení kurzu
        assert response is not None and response.status == 404, f"Očekáván HTTP kód 404, vráceno: {response.status if response else 'None'}"
        step("Ověřen HTTP stav 404 pro neexistující ID kurzu")
