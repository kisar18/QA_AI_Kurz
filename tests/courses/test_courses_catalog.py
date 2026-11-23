"""Automatizované testy pro US-09: Prohlížení katalogu kurzů.

Pokrývá test casy:
- [TC-US09-01] Přehledné zobrazení katalogu kurzů a povinných údajů na kartách
- [TC-US09-02] Zobrazení neutrálního výchozího obrázku u kurzu bez vlastního náhledu
- [TC-US09-03] Přechod na podrobný detail kurzu z karty v katalogu
- [TC-US09-04] Zobrazení výzvy k registraci pro nepřihlášeného návštěvníka
- [TC-US09-05] Absence výzvy k registraci pro již přihlášeného uživatele
"""

import re
import pytest
from playwright.sync_api import Page, expect

from helpers.step_helpers import step
from pages.courses_page import CoursesPage
from pages.login_page import LoginPage


class TestCoursesCatalog:
    """Testovací sada pro katalog kurzů (/courses) dle US-09."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.courses_page = CoursesPage(page)
        self.login_page = LoginPage(page)

    def test_tc_us09_01_courses_catalog_display_and_card_elements(self, page: Page):
        """[TC-US09-01] Přehledné zobrazení katalogu kurzů a povinných údajů na kartách."""
        self.courses_page.navigate()

        expect(page).to_have_url(self.courses_page.url)
        step("Ověřena URL /courses")

        expect(self.courses_page.title).to_be_visible()
        step("Ověřen nadpis katalogu kurzů")

        expect(self.courses_page.courses_section).to_be_visible()
        step("Ověřena hlavní sekce s kurzy")

        # Ověření počtu kurzů
        course_count = self.courses_page.course_names.count()
        assert course_count > 0, f"Očekáván alespoň 1 kurz v nabídce, nalezeno: {course_count}"
        step(f"Nalezeno celkem {course_count} kurzů v katalogu")

        # Ověření povinných údajů na první kartě kurzu
        # Výběr první karty kurzu pro kontrolu povinných prvků v katalogu
        first_name = self.courses_page.course_names.first
        expect(first_name).to_be_visible()
        name_text = first_name.inner_text().strip()
        assert len(name_text) > 0, "Název kurzu nesmí být prázdný"
        step(f"Ověřen název kurzu: '{name_text}'")

        # Výběr popisu první karty kurzu
        first_desc = self.courses_page.course_descriptions.first
        expect(first_desc).to_be_visible()
        assert len(first_desc.inner_text().strip()) > 0, "Popis kurzu nesmí být prázdný"
        step("Ověřen stručný popis kurzu")

        # Výběr kapacity první karty kurzu
        first_capacity = self.courses_page.course_capacities.first
        expect(first_capacity).to_be_visible()
        capacity_text = first_capacity.inner_text().strip()
        assert re.search(r"Kapacita:\s*\d+", capacity_text), f"Formát kapacity neodpovídá: '{capacity_text}'"
        step(f"Ověřena maximální kapacita: '{capacity_text}'")

        # Výběr ceny první karty kurzu
        first_price = self.courses_page.course_prices.first
        expect(first_price).to_be_visible()
        price_text = first_price.inner_text().strip()
        assert re.search(r"Cena:\s*\d+\s*Kč", price_text), f"Cena neodpovídá formátu celých Kč: '{price_text}'"
        step(f"Ověřena cena zaokrouhlená na celé Kč: '{price_text}'")

        # Výběr náhledu první karty kurzu
        first_img = self.courses_page.course_images.first
        expect(first_img).to_be_visible()
        step("Ověřen grafický náhled kurzu")

    @pytest.mark.xfail(
        reason="Aplikace neobsahuje fallback na výchozí neutrální obrázek při chybějícím souboru v úložišti (storage/app/public/... 404 vede na broken image)",
        strict=True,
    )
    def test_tc_us09_02_default_image_for_course_without_thumbnail(self, page: Page):
        """[TC-US09-02] Zobrazení neutrálního výchozího obrázku u kurzu bez vlastního náhledu."""
        self.courses_page.navigate()

        images = self.courses_page.course_images
        img_count = images.count()
        assert img_count > 0, "V katalogu musí být alespoň jeden obrázek kurzu"

        # Ověření, že obrázek kurzu má platný zdroj (není broken image ikona)
        for i in range(img_count):
            img = images.nth(i)  # Iterace přes obrázky pro kontrolu platnosti zdroje
            expect(img).to_be_visible()
            src = img.get_attribute("src")
            assert src is not None and len(src) > 0, f"Obrázek na indexu {i} postrádá atribut src"
            # Obrázek nesmí být prázdný a musí mít přirozenou šířku větší než 0 (není poškozen)
            is_loaded = page.evaluate("(el) => el.complete && el.naturalWidth > 0", img.element_handle())
            assert is_loaded, f"Obrázek na indexu {i} nebyl korektně načten (broken image)"

        step(f"Ověřeno všech {img_count} obrázků v katalogu – žádný není rozbitý (broken image)")

    def test_tc_us09_03_navigate_to_course_detail(self, page: Page):
        """[TC-US09-03] Přechod na podrobný detail kurzu z karty v katalogu."""
        self.courses_page.navigate()
        self.courses_page.open_first_course_detail()

        expect(page).to_have_url(re.compile(rf"^{re.escape(self.courses_page.base_url)}/courses/\d+$"))
        step("Ověřeno přesměrování na URL detailu kurzu (/courses/<id>)")

        expect(self.courses_page.course_detail).to_be_visible()
        step("Ověřeno načtení kontejneru detailu kurzu")

    def test_tc_us09_04_anonymous_user_registration_prompt(self, page: Page):
        """[TC-US09-04] Zobrazení výzvy k registraci pro nepřihlášeného návštěvníka."""
        self.courses_page.navigate()

        expect(self.courses_page.interest_title).to_be_visible()
        expect(self.courses_page.interest_title).to_contain_text("Máte zájem o naše kurzy?")
        step("Ověřena výzva k registraci pro anonymního návštěvníka")

        expect(self.courses_page.registration_link).to_be_visible()
        with page.expect_navigation():
            self.courses_page.registration_link.click()

        expect(page).to_have_url(re.compile(r".*/register"))
        step("Ověřeno přesměrování na registrační formulář /register")

    def test_tc_us09_05_absence_of_registration_prompt_for_authenticated_user(
        self, page: Page, registered_user: dict
    ):
        """[TC-US09-05] Absence výzvy k registraci pro již přihlášeného uživatele."""
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])
        expect(page).to_have_url(f"{self.courses_page.base_url}/courses")
        step("Uživatel úspěšně přihlášen a přesměrován do katalogu kurzů")

        expect(self.courses_page.interest_title).not_to_be_visible()
        expect(self.courses_page.registration_link).not_to_be_visible()
        step("Ověřeno, že výzva k registraci se přihlášenému uživateli nezobrazuje")
