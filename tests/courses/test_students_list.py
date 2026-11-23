"""Automatizované testy pro US-16: Zobrazení seznamu přihlášených účastníků pro lektora.

Pokrývá test casy:
- [TC-US16-01] Zobrazení tabulky účastníků běhu kurzu lektorem a kompletní údaje
- [TC-US16-02] Zobrazení zástupné hodnoty 'Neuvedeno' při nevyplněném IČO studenta
- [TC-US16-03] Zamezení přístupu k seznamu účastníků pro běžného zákazníka a hosta (Ochrana soukromí)
- [TC-US16-04] Zobrazení seznamu pro běh kurzu bez dosud přihlášených studentů (Empty State)
"""

import re
import pytest
from playwright.sync_api import Page, expect

from helpers.step_helpers import step
from pages.courses_page import CoursesPage
from pages.login_page import LoginPage
from pages.students_list_page import StudentsListPage


class TestStudentsList:
    """Testovací sada pro seznam přihlášených studentů kurzu lektorem dle US-16."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.students_page = StudentsListPage(page)
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

    def test_tc_us16_01_view_participants_table_and_complete_data(
        self, page: Page, lector_user: dict
    ):
        """[TC-US16-01] Zobrazení tabulky účastníků běhu kurzu lektorem a kompletní údaje."""
        self._login_as_lector(page, lector_user)

        # Otevření detailu kurzu 1
        self.courses_page.navigate_to_detail(1)
        expect(self.courses_page.course_detail).to_be_visible()

        # Proklik přes tlačítko 'Přihlášení' u prvního běhu
        participants_btn = self.courses_page.participants_buttons.first
        expect(participants_btn).to_be_visible()
        participants_btn.click()

        expect(page).to_have_url(re.compile(r".*/courses/\d+/participants$"), timeout=10000)
        expect(self.students_page.heading).to_be_visible()
        expect(self.students_page.heading).to_have_text("Seznam přihlášených")
        step("Otevřena stránka se seznamem přihlášených účastníků")

        # Ověření přítomnosti tabulky a jejích sloupců
        expect(self.students_page.participants_table).to_be_visible()
        expect(self.students_page.name_header).to_be_visible()
        expect(self.students_page.email_header).to_be_visible()
        expect(self.students_page.phone_header).to_be_visible()
        expect(self.students_page.ico_header).to_be_visible()
        step("Ověřeny hlavičky tabulky (Jméno, Email, Telefon, IČO)")

        # Ověření kompletních údajů na prvním řádku
        expect(self.students_page.participant_rows.first).to_be_visible()
        name = self.students_page.participant_names.first.inner_text().strip()
        email = self.students_page.participant_emails.first.inner_text().strip()
        phone = self.students_page.participant_phones.first.inner_text().strip()
        ico = self.students_page.participant_icos.first.inner_text().strip()

        assert len(name) > 0, "Jméno účastníka nesmí být prázdné"
        assert len(email) > 0 and "@" in email, f"E-mail účastníka je neplatný: '{email}'"
        assert len(phone) > 0, "Telefon účastníka nesmí být prázdný"
        assert len(ico) > 0, "IČO účastníka nesmí být prázdné (má obsahovat IČO nebo 'Neuvedeno')"
        step(f"Ověřeny kompletní údaje prvního účastníka: {name}, {email}, {phone}, IČO: {ico}")

    @pytest.mark.xfail(
        reason="Důsledek defektu US-12: Formulář přihlášky na kurz nedovolí odeslání bez IČO, v seznamu účastníků nelze ověřit hodnotu 'Neuvedeno'",
        strict=True,
    )
    def test_tc_us16_02_placeholder_neuvedeno_for_empty_ico(self, page: Page, lector_user: dict):
        """[TC-US16-02] Zobrazení zástupné hodnoty 'Neuvedeno' při nevyplněném IČO studenta."""
        self._login_as_lector(page, lector_user)
        self.students_page.open_for_iteration(1)

        expect(self.students_page.participants_table).to_be_visible()
        expect(self.students_page.participant_rows.first).to_be_visible()

        icos = self.students_page.participant_icos.all_inner_texts()
        assert any(ico.strip() == "Neuvedeno" for ico in icos), (
            f"V seznamu IČO účastníků se nenachází zástupný text 'Neuvedeno': {icos[:5]}"
        )
        step("Ověřena přítomnost zástupného textu 'Neuvedeno' u účastníka bez IČO")

    def test_tc_us16_03_prevention_of_participants_access_for_customer_and_guest_privacy(
        self, page: Page, registered_user: dict
    ):
        """[TC-US16-03] Zamezení přístupu k seznamu účastníků pro běžného zákazníka a hosta (Ochrana soukromí)."""
        # 1. Zákazník: nesmí vidět tlačítko v detailu ani tabulku účastníků na URL
        self._login_as_customer(page, registered_user)
        self.courses_page.navigate_to_detail(1)
        expect(self.courses_page.course_detail).to_be_visible()
        expect(self.courses_page.participants_buttons).not_to_be_visible()
        step("Ověřeno, že zákazník nevidí na detailu kurzu tlačítko 'Přihlášení'")

        # Přímý pokus o přístup na /courses/1/participants
        self.students_page.open_for_iteration(1)
        expect(self.students_page.participants_table).not_to_be_visible()
        expect(self.students_page.heading).not_to_be_visible()
        step("Ověřeno, že zákazník nemá přístup k tabulce účastníků (ochrana osobních údajů)")

        # 2. Nepřihlášený host
        page.context.clear_cookies()
        self.students_page.open_for_iteration(1)
        expect(self.students_page.participants_table).not_to_be_visible()
        expect(self.students_page.heading).not_to_be_visible()
        step("Ověřeno, že nepřihlášený host nemá přístup k tabulce účastníků")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Aplikace postrádá informativní empty state hlášení při 0 přihlášených studentech a zobrazuje pouze prázdný tbody",
        strict=True,
    )
    def test_tc_us16_04_empty_state_for_iteration_without_students(
        self, page: Page, lector_user: dict
    ):
        """[TC-US16-04] Zobrazení seznamu pro běh kurzu bez dosud přihlášených studentů (Empty State)."""
        self._login_as_lector(page, lector_user)

        # Otevření seznamu účastníků pro běh bez studentů (např. vysoké ID běhu nebo nově vytvořený)
        self.students_page.open_for_iteration(999999)

        # Očekává se informativní hlášení o prázdném běhu
        expect(self.students_page.empty_state_message).to_be_visible()
        step("Ověřeno informativní sdělení empty state při nulovém počtu přihlášených studentů")
