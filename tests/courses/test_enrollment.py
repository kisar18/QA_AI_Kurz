"""Automatizované testy pro US-12: Nezávazná registrace na běh kurzu s validací IČO a telefonu.

Pokrývá test casy:
- [TC-US12-01] Úspěšná nezávazná registrace na běh kurzu s platným IČO a telefonem
- [TC-US12-02] Validace povinného pole a minimální délky telefonního čísla
- [TC-US12-03] Validace formální platnosti IČO pomocí váženého kontrolního součtu modulo 11
- [TC-US12-04] Zamezení zápisu na kurz pro nepovolané role (Lektor a nepřihlášený host)
- [TC-US12-05] Úspěšný zápis na kurz bez vyplnění nepovinného pole IČO
"""

import re
import pytest
from playwright.sync_api import Page, expect

from helpers.step_helpers import step
from pages.courses_page import CoursesPage
from pages.course_enroll_page import CourseEnrollPage
from pages.login_page import LoginPage
from pages.my_courses_page import MyCoursesPage


class TestCourseEnrollment:
    """Testovací sada pro nezávaznou registraci na běh kurzu dle US-12."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.courses_page = CoursesPage(page)
        self.enroll_page = CourseEnrollPage(page)
        self.login_page = LoginPage(page)
        self.my_courses_page = MyCoursesPage(page)

    def _login_as_customer(self, page: Page, registered_user: dict):
        """Pomocná metoda pro přihlášení zákazníka."""
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])
        expect(page).to_have_url(f"{self.courses_page.base_url}/courses")
        step("Uživatel přihlášen v roli zákazníka")

    def test_tc_us12_01_successful_enrollment_with_ico_and_phone(self, page: Page, registered_user: dict):
        """[TC-US12-01] Úspěšná nezávazná registrace na běh kurzu s platným IČO a telefonem."""
        self._login_as_customer(page, registered_user)

        # Otevření detailu kurzu a přechod do formuláře registrace volného běhu
        self.courses_page.open_first_course_detail()
        expect(self.courses_page.iterations_heading).to_be_visible()

        # Vyhledání volného běhu
        cards = self.courses_page.iteration_cards
        card_count = cards.count()
        free_card = None
        for i in range(card_count):
            card = cards.nth(i)  # Iterace běhů pro nalezení termínu s volnou kapacitou
            text = card.inner_text()
            m = re.search(r"Kapacita:\s*(\d+)/(\d+)", text)
            if m and int(m.group(1)) < int(m.group(2)):
                free_card = card
                break

        assert free_card is not None, "V nabídce nebyl nalezen volný běh"
        enroll_btn = self.courses_page.get_iteration_enroll_button(free_card)
        with page.expect_navigation():
            enroll_btn.click()

        # Kontrola přítomnosti formulářových polí
        expect(self.enroll_page.registration_section).to_be_visible()
        expect(self.enroll_page.ico_input).to_be_visible()
        expect(self.enroll_page.phone_input).to_be_visible()
        step("Ověřena přítomnost formulářových polí pro IČO a telefon")

        # Vyplnění platného IČO a telefonu
        with page.expect_response(lambda r: "/api/courses/enroll" in r.url and r.status == 200):
            self.enroll_page.fill_and_submit("27082440", "+420777123456")

        # Ověření přesměrování do sekce Moje kurzy (/my-courses)
        expect(page).to_have_url(re.compile(r".*/my-courses"))
        expect(self.my_courses_page.title).to_be_visible()
        expect(self.my_courses_page.courses_section).to_be_visible()
        step("Ověřeno úspěšné odeslání registrace a přesměrování na /my-courses")

    def test_tc_us12_02_validation_of_required_phone_and_minimum_length(self, page: Page, registered_user: dict):
        """[TC-US12-02] Validace povinného pole a minimální délky telefonního čísla."""
        self._login_as_customer(page, registered_user)

        # Otevření formuláře registrace
        self.enroll_page.open_for_iteration(32)
        expect(self.enroll_page.registration_section).to_be_visible()

        # Test A: Prázdný telefon
        self.enroll_page.fill_and_submit(ico="27082440", phone="")
        expect(self.enroll_page.phone_error).to_be_visible()
        step("Ověřena validační chyba pro prázdné telefonní číslo")

        # Test B: Příliš krátké číslo (12345)
        self.enroll_page.fill_and_submit(ico="27082440", phone="12345")
        expect(self.enroll_page.phone_error).to_be_visible()
        expect(self.enroll_page.phone_error).to_contain_text("Telefonní číslo musí obsahovat alespoň 9 číslic")
        step("Ověřena validační chyba pro krátké telefonní číslo (méně než 9 číslic)")

    def test_tc_us12_03_validation_of_ico_checksum_modulo_11(self, page: Page, registered_user: dict):
        """[TC-US12-03] Validace formální platnosti IČO pomocí váženého kontrolního součtu modulo 11."""
        self._login_as_customer(page, registered_user)

        self.enroll_page.open_for_iteration(32)
        expect(self.enroll_page.registration_section).to_be_visible()

        # Odeslání s neplatným IČO (12345678 – neplatný kontrolní součet)
        self.enroll_page.fill_and_submit(ico="12345678", phone="+420777123456")
        expect(self.enroll_page.ico_error).to_be_visible()
        expect(self.enroll_page.ico_error).to_contain_text("Neplatné IČO")
        step("Ověřeno zamítnutí registrace při neplatném kontrolním součtu IČO (chyba 'Neplatné IČO')")

    def test_tc_us12_04_prevention_of_enrollment_for_unauthorized_roles(
        self, page: Page, lector_user: dict
    ):
        """[TC-US12-04] Zamezení zápisu na kurz pro nepovolané role (Lektor a nepřihlášený host)."""
        # 1. Nepřihlášený host na přímé URL registrace běhu
        self.enroll_page.open_for_iteration(32)
        expect(page).to_have_url(re.compile(r".*/courses"))
        step("Nepřihlášený návštěvník byl z přímé URL registrace přesměrován zpět")

        # 2. Lektor na detailu kurzu
        self.login_page.navigate()
        self.login_page.login(lector_user["email"], lector_user["password"])
        # Lektor po přihlášení přejde na detail kurzu
        self.courses_page.navigate_to_detail(1)
        expect(self.courses_page.iterations_heading).to_be_visible()

        # Lektorovi se tlačítka pro registraci vůbec nenabízí
        expect(self.courses_page.enroll_buttons.first).not_to_be_visible()
        step("Ověřeno, že lektorovi se tlačítka 'Nezávazná registrace' nezobrazují")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Pole IČO je v rozporu se specifikací validováno jako povinné (prázdné IČO vede na chybu 'Neplatné IČO')",
        strict=False,
    )
    def test_tc_us12_05_successful_enrollment_without_optional_ico(self, page: Page, registered_user: dict):
        """[TC-US12-05] Úspěšný zápis na kurz bez vyplnění nepovinného pole IČO."""
        self._login_as_customer(page, registered_user)

        # Otevření volného běhu 35 pro registraci bez IČO
        self.enroll_page.open_for_iteration(35)
        expect(self.enroll_page.registration_section).to_be_visible()

        # Vyplnění pouze platného telefonu bez IČO
        with page.expect_response(lambda r: "/api/courses/enroll" in r.url and r.status == 200, timeout=5000):
            self.enroll_page.fill_and_submit(ico="", phone="+420777987654")

        # Úspěšné dokončení registrace bez IČO
        expect(page).to_have_url(re.compile(r".*/my-courses"))
        expect(self.my_courses_page.title).to_be_visible()
        step("Ověřen úspěšný zápis na kurz bez vyplnění nepovinného pole IČO")
