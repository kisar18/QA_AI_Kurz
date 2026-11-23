"""Automatizované testy pro US-13: Přehled mých zapsaných kurzů.

Pokrývá test casy:
- [TC-US13-01] Zobrazení zapsaného kurzu a kompletních organizačních informací
- [TC-US13-02] Dostupnost odkazu v navigaci a přístup do sekce pro přihlášeného zákazníka
- [TC-US13-03] Přechod na podrobný detail kurzu z karty v přehledu
- [TC-US13-04] Zamezení přístupu do sekce 'Moje kurzy' pro nepřihlášeného návštěvníka
- [TC-US13-05] Zobrazení sekce 'Moje kurzy' pro zákazníka bez aktivních zápisů (Empty State)
- [TC-US13-06] Zobrazení více souběžně zapsaných kurzů a nezávislost organizačních údajů
- [TC-US13-07] Omezení přístupu do sekce 'Moje kurzy' pro roli Lektor (RBAC)
- [TC-US13-08] Rozlišení nadcházejících kurzů a chronologické řazení termínů
"""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
import pytest
from playwright.sync_api import Page, expect

from helpers.step_helpers import step
from pages.courses_page import CoursesPage
from pages.login_page import LoginPage
from pages.my_courses_page import MyCoursesPage
from pages.register_page import RegisterPage


class TestMyCourses:
    """Testovací sada pro sekci Moje kurzy (/my-courses) dle US-13."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.my_courses_page = MyCoursesPage(page)
        self.courses_page = CoursesPage(page)
        self.login_page = LoginPage(page)
        self.register_page = RegisterPage(page)

    def _login_as_customer(self, page: Page, registered_user: dict):
        """Pomocná metoda pro přihlášení zákazníka."""
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])
        expect(page).to_have_url(f"{self.courses_page.base_url}/courses", timeout=10000)
        step("Uživatel přihlášen v roli zákazníka")

    def _login_as_predefined_student(self, page: Page):
        """Pomocná metoda pro přihlášení předpřipraveného studenta se zapsanými kurzy."""
        data_path = Path("data/test_user.json")
        with open(data_path, encoding="utf-8") as f:
            student = json.load(f)
        self.login_page.navigate()
        self.login_page.login(student["email"], student["password"])
        expect(page).to_have_url(f"{self.courses_page.base_url}/courses", timeout=10000)
        step("Student s existujícími zápisy přihlášen")

    def _login_as_lector(self, page: Page):
        """Pomocná metoda pro přihlášení uživatele v roli lektora."""
        data_path = Path("data/lector_user.json")
        with open(data_path, encoding="utf-8") as f:
            lector = json.load(f)
        self.login_page.navigate()
        self.login_page.login(lector["email"], lector["password"])
        expect(page).to_have_url(f"{self.courses_page.base_url}/courses", timeout=10000)
        step("Lektor přihlášen")

    def test_tc_us13_01_enrolled_course_display_and_organizational_info(self, page: Page):
        """[TC-US13-01] Zobrazení zapsaného kurzu a kompletních organizačních informací."""
        self._login_as_predefined_student(page)

        self.my_courses_page.navigate()
        expect(page).to_have_url(self.my_courses_page.url)
        step("Otevřena stránka /my-courses")

        # Ověření nadpisu sekce
        expect(self.my_courses_page.title).to_be_visible()
        step("Ověřen nadpis sekce 'Moje kurzy'")

        # Ověření kontejneru kurzů
        expect(self.my_courses_page.courses_section).to_be_visible()
        step("Ověřena hlavní sekce zapsaných kurzů")

        # Ověření organizačních náležitostí na kartě prvního zapsaného kurzu
        first_name = self.my_courses_page.course_names.first
        expect(first_name).to_be_visible()
        name_text = first_name.inner_text().strip()
        assert len(name_text) > 0, "Název zapsaného kurzu nesmí být prázdný"
        step(f"Ověřen název kurzu v mých kurzech: '{name_text}'")

        # Popis kurzu
        first_desc = self.my_courses_page.course_descriptions.first
        expect(first_desc).to_be_visible()
        assert len(first_desc.inner_text().strip()) > 0, "Popis kurzu nesmí být prázdný"
        step("Ověřen popis kurzu")

        # Cena kurzu
        first_price = self.my_courses_page.course_prices.first
        expect(first_price).to_be_visible()
        price_text = first_price.inner_text().strip()
        assert re.search(r"Cena:\s*\d+\s*Kč", price_text), f"Cena neodpovídá celým Kč: '{price_text}'"
        step(f"Ověřena cena kurzu: '{price_text}'")

        # Data zahájení a ukončení
        first_from = self.my_courses_page.date_time_from.first
        expect(first_from).to_be_visible()
        step("Ověřeno datum zahájení kurzu (date_time_from)")

        first_to = self.my_courses_page.date_time_to.first
        expect(first_to).to_be_visible()
        step("Ověřeno datum ukončení kurzu (date_time_to)")

        # Informace o dnu v týdnu a místu konání
        first_day = self.my_courses_page.day_information.first
        expect(first_day).to_be_visible()
        step("Ověřen den v týdnu / čas konání lekcí")

        first_place = self.my_courses_page.place_information.first
        expect(first_place).to_be_visible()
        step("Ověřeno místo konání / forma výuky")

    def test_tc_us13_02_navbar_link_availability_for_customer(self, page: Page, registered_user: dict):
        """[TC-US13-02] Dostupnost odkazu v navigaci a přístup do sekce pro přihlášeného zákazníka."""
        self._login_as_customer(page, registered_user)

        # Kontrola, že odkaz 'Moje kurzy' je v navigaci přítomen
        expect(self.courses_page.navbar.my_courses_link).to_be_visible()
        step("Ověřena přítomnost odkazu 'Moje kurzy' v horní navigaci")

        # Proklik přes navigaci
        self.courses_page.navbar.my_courses_link.click()

        expect(page).to_have_url(self.my_courses_page.url)
        expect(self.my_courses_page.title).to_be_visible()
        step("Ověřeno úspěšné přesměrování z navigace na /my-courses")

    def test_tc_us13_03_navigate_to_course_detail_from_my_courses(self, page: Page):
        """[TC-US13-03] Přechod na podrobný detail kurzu z karty v přehledu."""
        self._login_as_predefined_student(page)
        self.my_courses_page.navigate()

        # Proklik na detail kurzu z karty v přehledu
        first_detail_btn = self.my_courses_page.detail_buttons.first
        expect(first_detail_btn).to_be_visible()

        first_detail_btn.click()

        expect(page).to_have_url(re.compile(r".*/courses/\d+"))
        expect(self.courses_page.course_detail).to_be_visible()
        step("Ověřeno přesměrování z mých kurzů na detail odpovídajícího kurzu")

        # Návrat zpět přes navigaci
        self.courses_page.navbar.my_courses_link.click()

        expect(page).to_have_url(self.my_courses_page.url)
        step("Ověřen úspěšný návrat zpět do přehledu 'Moje kurzy'")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Nepřihlášený návštěvník při přístupu na /my-courses není přesměrován na /login ani informován o nutnosti přihlášení",
        strict=True,
    )
    def test_tc_us13_04_prevention_of_unauthenticated_access_to_my_courses(self, page: Page):
        """[TC-US13-04] Zamezení přístupu do sekce 'Moje kurzy' pro nepřihlášeného návštěvníka."""
        # 1. Kontrola navigace nepřihlášeného uživatele na veřejné stránce
        self.courses_page.navigate()
        expect(self.courses_page.navbar.my_courses_link).not_to_be_visible()
        step("Ověřeno, že nepřihlášenému návštěvníkovi se odkaz 'Moje kurzy' v navigaci nezobrazuje")

        # 2. Přímý pokus o přístup na /my-courses
        self.my_courses_page.navigate()
        expect(page).to_have_url(re.compile(r".*/login|.*/courses$"))
        step("Ověřeno, že systém zamezil neautorizovanému přístupu a přesměroval návštěvníka na /login nebo /courses")

    def test_tc_us13_05_empty_state_for_customer_without_enrollments(self, page: Page):
        """[TC-US13-05] Zobrazení sekce 'Moje kurzy' pro zákazníka bez aktivních zápisů (Empty State)."""
        # Registrace nového unikátního uživatele, který nemá žádné zapsané kurzy
        unique_id = uuid.uuid4().hex[:6]
        user_email = f"empty_{unique_id}@example.com"
        user_pass = "EmptyPass123!"

        self.register_page.navigate()
        self.register_page.register(
            name=f"Empty User {unique_id}",
            email=user_email,
            password=user_pass,
            password_again=user_pass,
        )
        expect(page).to_have_url(re.compile(r".*/home|.*/courses"))
        step(f"Zaregistrován nový uživatel bez zapsaných kurzů: {user_email}")

        # Otevření /my-courses pro nového uživatele
        self.my_courses_page.navigate()
        expect(page).to_have_url(self.my_courses_page.url)
        expect(self.my_courses_page.title).to_be_visible()

        # Ověření, že uživatel bez zápisů nemá zobrazenou žádnou kartu kurzu
        course_count = self.my_courses_page.course_names.count()
        assert course_count == 0, f"Očekáván prázdný přehled (0 kurzů), nalezeno: {course_count}"
        step("Ověřen správný stav Empty State (žádný zapsaný kurz)")

    def test_tc_us13_06_multiple_enrolled_courses_independent_data(self, page: Page):
        """[TC-US13-06] Zobrazení více souběžně zapsaných kurzů a nezávislost organizačních údajů."""
        self._login_as_predefined_student(page)
        self.my_courses_page.navigate()

        course_count = self.my_courses_page.course_names.count()
        assert course_count >= 2, f"Očekávány alespoň 2 zapsané kurzy pro ověření nezávislosti, nalezeno: {course_count}"
        step(f"Ověřen počet zapsaných kurzů: {course_count}")

        # Získání organizačních informací obou kurzů
        name_1 = self.my_courses_page.course_names.nth(0).inner_text().strip()
        name_2 = self.my_courses_page.course_names.nth(1).inner_text().strip()
        assert name_1 != name_2, f"Kurzy by měly mít různé názvy: '{name_1}' vs '{name_2}'"

        date_from_1 = self.my_courses_page.date_time_from.nth(0).inner_text().strip()
        date_from_2 = self.my_courses_page.date_time_from.nth(1).inner_text().strip()
        assert date_from_1 != date_from_2, f"Kurzy by měly mít nezávislá data zahájení: '{date_from_1}' vs '{date_from_2}'"
        step(f"Ověřena nezávislost údajů mezi '{name_1}' ({date_from_1}) a '{name_2}' ({date_from_2})")

    @pytest.mark.xfail(
        reason="Defekt aplikace (RBAC): Lektor má v navigaci zákaznický odkaz 'Moje kurzy' a sekce pro něj není omezena ani přesměrována",
        strict=True,
    )
    def test_tc_us13_07_restriction_of_my_courses_for_lector_rbac(self, page: Page):
        """[TC-US13-07] Omezení přístupu do sekce 'Moje kurzy' pro roli Lektor (RBAC)."""
        self._login_as_lector(page)

        # Lektor by neměl mít v klientské navigaci odkaz 'Moje kurzy'
        expect(self.courses_page.navbar.my_courses_link).not_to_be_visible()
        step("Ověřeno, že lektor nemá v navigaci zákaznický odkaz 'Moje kurzy'")

        # Přímý pokus o přístup na /my-courses by měl lektora přesměrovat do lektorské zóny nebo odmítnout přístup
        self.my_courses_page.navigate()
        expect(page).not_to_have_url(self.my_courses_page.url)
        step("Ověřeno, že lektor byl z /my-courses přesměrován pryč")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Zapsané kurzy na /my-courses nejsou řazeny vzestupně chronologicky od nejbližšího data",
        strict=True,
    )
    def test_tc_us13_08_upcoming_courses_chronological_ordering(self, page: Page):
        """[TC-US13-08] Rozlišení nadcházejících kurzů a chronologické řazení termínů."""
        self._login_as_predefined_student(page)
        self.my_courses_page.navigate()

        dates_text = self.my_courses_page.date_time_from.all_inner_texts()
        assert len(dates_text) >= 2, f"Pro ověření chronologického řazení jsou potřeba alespoň 2 kurzy, nalezeno: {len(dates_text)}"

        parsed_dates = []
        for dt_str in dates_text:
            match = re.search(r"(\d+)\.\s*(\d+)\.\s*(\d{4})", dt_str)
            assert match, f"Nelze parsovat datum zahájení z textu: '{dt_str}'"
            day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
            parsed_dates.append(datetime(year, month, day))

        # Ověření vzestupného chronologického řazení (nejbližší termín jako první)
        for i in range(len(parsed_dates) - 1):
            assert parsed_dates[i] <= parsed_dates[i + 1], (
                f"Kurzy nejsou řazeny chronologicky vzestupně: "
                f"{parsed_dates[i].strftime('%d.%m.%Y')} předchází {parsed_dates[i + 1].strftime('%d.%m.%Y')}"
            )
        step("Ověřeno chronologické řazení kurzů na /my-courses")
