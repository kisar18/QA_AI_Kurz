"""Automatizované testy pro US-15: Vypsání nového běhu (termínu) kurzu.

Pokrývá test casy:
- [TC-US15-01] Úspěšné vypsání nového termínu kurzu lektorem a zobrazení v detailu
- [TC-US15-02] Validace povinných polí při odeslání prázdného nebo neúplného formuláře
- [TC-US15-03] Zamezení přístupu k vypsání nového termínu pro běžného studenta a hosta (RBAC)
- [TC-US15-04] Logická validace časové souslednosti termínu kurzu
- [TC-US15-05] Vypsání termínu s online formou výuky a kontrola zobrazení formátu
- [TC-US15-06] Vypsání více nezávislých termínů k jednomu kurzu a souběžné zobrazení
- [TC-US15-07] Validace data zahájení v minulosti
- [TC-US15-08] Omezení vypsání termínu k cizímu kurzu (Autorská oprávnění lektora)
"""

import re
import pytest
from playwright.sync_api import Page, expect

from helpers.step_helpers import step
from pages.course_iteration_create_page import CourseIterationCreatePage
from pages.courses_page import CoursesPage
from pages.login_page import LoginPage


class TestCourseIterations:
    """Testovací sada pro vypsání a správu běhů kurzu dle US-15."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.iteration_create_page = CourseIterationCreatePage(page)
        self.courses_page = CoursesPage(page)
        self.login_page = LoginPage(page)

    def _login_as_lector(self, page: Page, lector_user: dict):
        """Pomocná metoda pro přihlášení lektora."""
        self.login_page.navigate()
        self.login_page.login(lector_user["email"], lector_user["password"])
        expect(page).to_have_url(f"{self.courses_page.base_url}/courses", timeout=10000)
        step("Uživatel přihlášen v roli lektora")

    def _login_as_customer(self, page: Page, registered_user: dict):
        """Pomocná metoda pro přihlášení zákazníka."""
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])
        expect(page).to_have_url(f"{self.courses_page.base_url}/courses", timeout=10000)
        step("Uživatel přihlášen v roli zákazníka")

    def test_tc_us15_01_create_new_iteration_success(self, page: Page, lector_user: dict):
        """[TC-US15-01] Úspěšné vypsání nového termínu kurzu lektorem a zobrazení v detailu."""
        self._login_as_lector(page, lector_user)

        # Otevření formuláře pro vytvoření termínu pro kurz 1
        self.iteration_create_page.open_for_course(1)
        expect(self.iteration_create_page.container).to_be_visible()
        step("Otevřen formulář pro vytvoření termínu (/courses/1/create-iteration)")

        # Kontrola přítomnosti polí formuláře
        expect(self.iteration_create_page.start_input).to_be_visible()
        expect(self.iteration_create_page.end_input).to_be_visible()
        expect(self.iteration_create_page.day_select).to_be_visible()
        expect(self.iteration_create_page.time_input).to_be_visible()
        expect(self.iteration_create_page.location_input).to_be_visible()
        expect(self.iteration_create_page.submit_button).to_be_visible()
        step("Ověřena přítomnost všech polí formuláře pro nový termín")

        # Vyplnění a odeslání platných dat (input type=time vyžaduje formát HH:MM)
        self.iteration_create_page.fill_and_submit(
            start_date="2026-12-01",
            end_date="2027-01-15",
            day_of_week="Pondělí",
            time_str="18:00",
            location="Praha 1 - Školící centrum, Učebna B",
        )

        # Očekává se přesměrování na detail kurzu /courses/1
        expect(page).to_have_url(re.compile(r".*/courses/1$"), timeout=10000)
        expect(self.courses_page.course_detail).to_be_visible()
        expect(self.courses_page.iterations_heading).to_be_visible()
        step("Ověřeno úspěšné uložení termínu a přesměrování na detail kurzu /courses/1")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Formulář vypsání termínu postrádá validaci povinných polí a odešle i prázdný termín",
        strict=True,
    )
    def test_tc_us15_02_validation_of_required_fields_empty_form(self, page: Page, lector_user: dict):
        """[TC-US15-02] Validace povinných polí při odeslání prázdného nebo neúplného formuláře."""
        self._login_as_lector(page, lector_user)
        self.iteration_create_page.open_for_course(1)

        # Odeslání prázdného formuláře
        self.iteration_create_page.fill_and_submit(
            start_date="",
            end_date="",
            day_of_week="",
            time_str="",
            location="",
        )

        # Systém musí zabránit uložení a zůstat na formuláři
        expect(self.iteration_create_page.container).to_be_visible()
        expect(page).to_have_url(re.compile(r".*/create-iteration$"))
        step("Ověřeno, že prázdný formulář termínu nebyl odeslán")

    @pytest.mark.xfail(
        reason="Defekt aplikace (RBAC): Běžný zákazník má přístup k formuláři vypsání nového termínu běhu kurzu",
        strict=True,
    )
    def test_tc_us15_03_prevention_of_iteration_creation_for_student_and_guest_rbac(
        self, page: Page, registered_user: dict
    ):
        """[TC-US15-03] Zamezení přístupu k vypsání nového termínu pro běžného studenta a hosta (RBAC)."""
        # 1. Zákazník: nesmí vidět formulář pro přidání termínu
        self._login_as_customer(page, registered_user)
        self.iteration_create_page.open_for_course(1)
        expect(self.iteration_create_page.container).not_to_be_visible()
        step("Ověřeno, že běžnému zákazníkovi se formulář vytvoření termínu nezobrazí")

        # 2. Nepřihlášený host
        page.context.clear_cookies()
        self.iteration_create_page.open_for_course(1)
        expect(self.iteration_create_page.container).not_to_be_visible()
        step("Ověřeno, že nepřihlášenému hostovi se formulář vytvoření termínu nezobrazí")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Formulář postrádá logickou validaci časové souslednosti (umožní konec před začátkem)",
        strict=True,
    )
    def test_tc_us15_04_logical_validation_of_chronological_sequence(self, page: Page, lector_user: dict):
        """[TC-US15-04] Logická validace časové souslednosti termínu kurzu."""
        self._login_as_lector(page, lector_user)
        self.iteration_create_page.open_for_course(1)

        # Test 1: Datum ukončení před datem zahájení
        self.iteration_create_page.fill_and_submit(
            start_date="2026-12-15",
            end_date="2026-11-01",
            day_of_week="Úterý",
            time_str="18:00",
            location="Praha",
        )

        # Systém musí zabránit uložení obráceného termínu
        expect(self.iteration_create_page.container).to_be_visible()
        expect(page).to_have_url(re.compile(r".*/create-iteration$"))
        step("Ověřeno, že termín s datem ukončení před zahájením byl odmítnut")

    def test_tc_us15_05_create_iteration_online_format(self, page: Page, lector_user: dict):
        """[TC-US15-05] Vypsání termínu s online formou výuky a kontrola zobrazení formátu."""
        self._login_as_lector(page, lector_user)
        self.iteration_create_page.open_for_course(1)

        self.iteration_create_page.fill_and_submit(
            start_date="2027-02-01",
            end_date="2027-03-01",
            day_of_week="Středa",
            time_str="17:30",
            location="Online výuka (Google Meet / Zoom)",
        )

        expect(page).to_have_url(re.compile(r".*/courses/1$"), timeout=10000)
        expect(self.courses_page.course_detail).to_be_visible()
        step("Ověřeno vypsání online termínu kurzu a zobrazení v detailu")

    def test_tc_us15_06_multiple_independent_iterations_for_single_course(
        self, page: Page, lector_user: dict
    ):
        """[TC-US15-06] Vypsání více nezávislých termínů k jednomu kurzu a souběžné zobrazení."""
        self._login_as_lector(page, lector_user)

        # Vytvoření dalšího termínu pro tentýž kurz
        self.iteration_create_page.open_for_course(1)
        self.iteration_create_page.fill_and_submit(
            start_date="2027-04-10",
            end_date="2027-05-15",
            day_of_week="Sobota",
            time_str="09:00",
            location="Praha - Víkendová učebna",
        )

        expect(page).to_have_url(re.compile(r".*/courses/1$"), timeout=10000)
        expect(self.courses_page.course_detail).to_be_visible()

        # Ověření, že na detailu kurzu je zobrazeno více karet běhů
        expect(self.courses_page.iteration_cards.nth(1)).to_be_visible()
        iteration_count = self.courses_page.iteration_cards.count()
        assert iteration_count >= 2, f"Očekávány alespoň 2 vypsané termíny, nalezeno: {iteration_count}"
        step(f"Ověřena přítomnost {iteration_count} nezávislých termínů na detailu kurzu")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Systém nevaliduje datum zahájení a umožní vypsat termín v minulosti",
        strict=True,
    )
    def test_tc_us15_07_validation_of_past_start_date(self, page: Page, lector_user: dict):
        """[TC-US15-07] Validace data zahájení v minulosti."""
        self._login_as_lector(page, lector_user)
        self.iteration_create_page.open_for_course(1)

        # Termín v minulosti
        self.iteration_create_page.fill_and_submit(
            start_date="2020-01-01",
            end_date="2020-02-01",
            day_of_week="Pondělí",
            time_str="10:00",
            location="Minulost",
        )

        # Systém musí zabránit uložení termínu v minulosti
        expect(self.iteration_create_page.container).to_be_visible()
        expect(page).to_have_url(re.compile(r".*/create-iteration$"))
        step("Ověřeno, že termín s datem v minulosti byl odmítnut")

    @pytest.mark.xfail(
        reason="Defekt aplikace / nepodporováno: V aplikaci neexistuje rozlišení vlastnictví kurzu mezi lektory a chybí autorizační kontrola",
        strict=True,
    )
    def test_tc_us15_08_restriction_of_iteration_creation_for_foreign_course(
        self, page: Page, lector_user: dict
    ):
        """[TC-US15-08] Omezení vypsání termínu k cizímu kurzu (Autorská oprávnění lektora)."""
        self._login_as_lector(page, lector_user)

        # Pokus o vypsání termínu ke kurzu s vysokým ID (např. 999999), který lektor nevlastní
        self.iteration_create_page.open_for_course(999999)

        # Systém by měl přístup zamítnout (403, 404 nebo přesměrování s chybou)
        expect(self.iteration_create_page.container).not_to_be_visible()
        step("Ověřeno, že lektor nemá přístup k vypsání termínu u cizího / neexistujícího kurzu")
