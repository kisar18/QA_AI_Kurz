"""Automatizované testy pro US-11: Vizuální indikace a zamezení zápisu při naplněné kapacitě.

Pokrývá test casy:
- [TC-US11-01] Zobrazení tlačítka registrace u běhu s volnou kapacitou a přesměrování
- [TC-US11-02] Skrytí registrace a indikace plné obsazenosti u vyčerpané kapacity
- [TC-US11-03] Zamezení přímého zápisu na plně obsazený běh přes přímou URL
"""

import re
import pytest
from playwright.sync_api import Page, expect

from helpers.step_helpers import step
from pages.courses_page import CoursesPage
from pages.course_enroll_page import CourseEnrollPage
from pages.login_page import LoginPage


class TestCourseCapacity:
    """Testovací sada pro indikaci a kontrolu kapacity běhů kurzu dle US-11."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.courses_page = CoursesPage(page)
        self.enroll_page = CourseEnrollPage(page)
        self.login_page = LoginPage(page)

    def _login_as_customer(self, page: Page, registered_user: dict):
        """Pomocná metoda pro přihlášení zákazníka."""
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])
        expect(page).to_have_url(f"{self.courses_page.base_url}/courses")
        step("Uživatel přihlášen v roli zákazníka")

    def test_tc_us11_01_enroll_button_for_available_capacity(self, page: Page, registered_user: dict):
        """[TC-US11-01] Zobrazení tlačítka registrace u běhu s volnou kapacitou a přesměrování."""
        self._login_as_customer(page, registered_user)

        self.courses_page.open_first_course_detail()
        expect(self.courses_page.iterations_heading).to_be_visible()

        # Vyhledání karty běhu s volnou kapacitou
        cards = self.courses_page.iteration_cards
        card_count = cards.count()
        assert card_count > 0, "Detail kurzu musí obsahovat alespoň jeden běh"

        free_card = None
        free_iteration_id = None
        for i in range(card_count):
            card = cards.nth(i)  # Iterace běhů pro nalezení termínu s volnou kapacitou
            text = card.inner_text()
            m = re.search(r"Kapacita:\s*(\d+)/(\d+)", text)
            if m and int(m.group(1)) < int(m.group(2)):
                free_card = card
                # Extrakce ID běhu z data-testid (např. iteration_31 -> 31)
                tid = card.get_attribute("data-testid") or ""
                free_iteration_id = tid.replace("iteration_", "")
                break

        assert free_card is not None, "V nabídce nebyl nalezen žádný běh s volnou kapacitou"
        step(f"Nalezen běh s volnou kapacitou: ID {free_iteration_id}")

        # Ověření přítomnosti tlačítka 'Nezávazná registrace' u volného běhu
        enroll_btn = self.courses_page.get_iteration_enroll_button(free_card)
        expect(enroll_btn).to_be_visible()
        step("Ověřeno zobrazení tlačítka 'Nezávazná registrace' u termínu s volnou kapacitou")

        # Kliknutí na tlačítko a ověření přesměrování na registrační formulář běhu
        with page.expect_navigation():
            enroll_btn.click()

        expect(page).to_have_url(re.compile(r".*/courses/\d+/register"))
        expect(self.enroll_page.registration_section).to_be_visible()
        step("Ověřeno přesměrování do objednávkového formuláře (/courses/<iteration_id>/register)")

    def test_tc_us11_02_fully_booked_iteration_indication(self, page: Page, registered_user: dict):
        """[TC-US11-02] Skrytí registrace a indikace plné obsazenosti u vyčerpané kapacity."""
        self._login_as_customer(page, registered_user)

        self.courses_page.open_first_course_detail()
        expect(self.courses_page.iterations_heading).to_be_visible()

        # Vyhledání karty plně obsazeného běhu (obsazeno >= kapacita)
        cards = self.courses_page.iteration_cards
        card_count = cards.count()
        assert card_count > 0, "Detail kurzu musí obsahovat alespoň jeden běh"

        full_card = None
        for i in range(card_count):
            card = cards.nth(i)  # Iterace pro vyhledání plně obsazeného termínu
            text = card.inner_text()
            m = re.search(r"Kapacita:\s*(\d+)/(\d+)", text)
            if m and int(m.group(1)) >= int(m.group(2)):
                full_card = card
                step(f"Nalezen plně obsazený běh: {m.group(0)}")
                break

        assert full_card is not None, "V nabídce nebyl nalezen žádný plně obsazený běh pro ověření"

        # Tlačítko pro registraci se u plně obsazeného běhu nesmí nabízet
        enroll_btn = self.courses_page.get_iteration_enroll_button(full_card)
        expect(enroll_btn).not_to_be_visible()
        step("Ověřeno, že tlačítko pro registraci je pro plně obsazený běh skryto")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Backend neověřuje kapacitu a umožní odeslat registraci na plně obsazený běh bez zamítnutí",
        strict=True,
    )
    def test_tc_us11_03_direct_url_access_to_fully_booked_iteration(self, page: Page, registered_user: dict):
        """[TC-US11-03] Zamezení přímého zápisu na plně obsazený běh přes přímou URL."""
        self._login_as_customer(page, registered_user)

        # ID 1 odpovídá plně obsazenému běhu s kapacitou 12/12 (resp. 127/12)
        full_iteration_id = "1"
        self.enroll_page.open_for_iteration(full_iteration_id)

        # Pokud se formulář načte, odeslání musí skončit chybovou hláškou o vyčerpané kapacitě
        self.enroll_page.fill_and_submit("27082440", "+420777123456")

        # Systém nesmí povolit přihlášení a musí informovat o vyčerpané kapacitě
        expect(self.enroll_page.capacity_error).to_be_visible(timeout=5000)
        step("Ověřeno zamezení registrace na plně obsazený běh")
