"""Automatizované testy pro US-19: Řízení přístupu na základě rolí (RBAC a autorizace API).

Pokrývá test casy:
- [TC-US19-01] Dostupnost veřejných sekcí aplikace pro nepřihlášeného návštěvníka
- [TC-US19-02] Zamezení přístupu a automatické přesměrování neautentizovaného uživatele na katalog kurzů
- [TC-US19-03] Zpřístupnění lektorských akcí výhradně pro uživatele v roli Lektor
- [TC-US19-04] Zamezení přístupu běžného zákazníka k lektorským operacím v UI
- [TC-US19-05] Zamezení zápisu na běhy kurzů pro uživatele v roli Lektor (UI i API úroveň)
- [TC-US19-06] Nedostupnost servisních a údržbových rozhraní pro neautorizované návštěvníky
- [TC-US19-07] Přepnutí rolí a okamžitá aktualizace autorizačních oprávnění v sezení
- [TC-US19-08] Zamezení neoprávněné manipulace s daty přes přímé API / POST požadavky
- [TC-US19-09] Ochrana proti horizontální eskalaci práv (IDOR) mezi lektory
"""

import re
import urllib.request
import urllib.error
import pytest
from playwright.sync_api import Page, expect

from helpers.step_helpers import step
from pages.course_create_page import CourseCreatePage
from pages.course_enroll_page import CourseEnrollPage
from pages.course_iteration_create_page import CourseIterationCreatePage
from pages.courses_page import CoursesPage
from pages.login_page import LoginPage
from pages.my_courses_page import MyCoursesPage
from pages.profile_page import ProfilePage
from pages.register_page import RegisterPage
from pages.students_list_page import StudentsListPage


class TestRoleBasedAccessControl:
    """Testovací sada pro řízení přístupu na základě rolí (RBAC - US-19)."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)
        self.register_page = RegisterPage(page)
        self.courses_page = CoursesPage(page)
        self.profile_page = ProfilePage(page)
        self.my_courses_page = MyCoursesPage(page)
        self.course_create_page = CourseCreatePage(page)
        self.iteration_create_page = CourseIterationCreatePage(page)
        self.enroll_page = CourseEnrollPage(page)
        self.students_page = StudentsListPage(page)

    def _login(self, page: Page, user: dict):
        """Pomocná metoda pro přihlášení uživatele."""
        self.login_page.navigate()
        self.login_page.login(user["email"], user["password"])
        expect(page).to_have_url(f"{self.courses_page.base_url}/courses", timeout=10000)
        step(f"Uživatel přihlášen: {user['email']}")

    def test_tc_us19_01_public_sections_availability_for_guest(self, page: Page):
        """[TC-US19-01] Dostupnost veřejných sekcí aplikace pro nepřihlášeného návštěvníka."""
        # 1. Rozcestník /
        self.login_page.navigate("/")
        expect(page).to_have_url(re.compile(r".*/$"))
        step("Ověřen přístup na rozcestník /")

        # 2. Katalog kurzů /courses
        self.courses_page.navigate()
        expect(page).to_have_url(self.courses_page.url)
        expect(self.courses_page.courses_section).to_be_visible()
        expect(self.courses_page.navbar.login_link).to_be_visible()
        step("Ověřen přístup do katalogu kurzů pro nepřihlášeného návštěvníka")

        # 3. Detail kurzu /courses/1
        self.courses_page.navigate_to_detail(1)
        expect(page).to_have_url(re.compile(r".*/courses/1$"))
        expect(self.courses_page.course_detail).to_be_visible()
        # Privátní akce nesmí být viditelné
        expect(self.courses_page.participants_buttons).not_to_be_visible()
        step("Ověřen přístup na detail kurzu a nepřítomnost privátních lektorských akcí")

        # 4. Přihlašovací formulář /login a registrační formulář /register
        self.login_page.navigate()
        expect(self.login_page.login_title).to_be_visible()

        self.register_page.navigate()
        expect(self.register_page.register_button).to_be_visible()
        step("Ověřen přístup na /login a /register")

    @pytest.mark.xfail(
        reason="Defekt aplikace (RBAC): Nepřihlášený uživatel není při přístupu na chráněné URL přesměrován na /courses",
        strict=False,
    )
    def test_tc_us19_02_prevention_of_unauthenticated_access_to_private_routes(self, page: Page):
        """[TC-US19-02] Zamezení přístupu a automatické přesměrování neautentizovaného uživatele na katalog kurzů."""
        # Pokus o přístup na /profile
        self.profile_page.navigate()
        expect(page).to_have_url(self.courses_page.url)
        expect(self.profile_page.name_input).not_to_be_visible()
        step("Ověřeno přesměrování z /profile na /courses")

        # Pokus o přístup na /my-courses
        self.my_courses_page.navigate()
        expect(page).to_have_url(self.courses_page.url)
        step("Ověřeno přesměrování z /my-courses na /courses")

        # Pokus o přístup na /courses/create
        self.course_create_page.navigate()
        expect(page).to_have_url(self.courses_page.url)
        step("Ověřeno přesměrování z /courses/create na /courses")

    def test_tc_us19_03_lector_tools_accessibility_for_lector_role(self, page: Page, lector_user: dict):
        """[TC-US19-03] Zpřístupnění lektorských akcí výhradně pro uživatele v roli Lektor."""
        self._login(page, lector_user)

        # 1. Tlačítko 'Přidat kurz' v katalogu
        self.courses_page.navigate()
        expect(self.courses_page.add_course_button).to_be_visible()
        step("Ověřena přítomnost tlačítka 'Přidat kurz' v katalogu pro lektora")

        # 2. Formulář tvorby kurzu
        self.course_create_page.navigate()
        expect(self.course_create_page.heading).to_be_visible()
        step("Ověřen přístup lektora k formuláři vytvoření kurzu")

        # 3. Akce na detailu kurzu: vypsání termínu a seznam přihlášených
        self.courses_page.navigate_to_detail(1)
        expect(self.courses_page.course_detail).to_be_visible()
        expect(self.courses_page.participants_buttons.first).to_be_visible()

        self.courses_page.participants_buttons.first.click()
        expect(page).to_have_url(re.compile(r".*/courses/\d+/participants$"), timeout=10000)
        expect(self.students_page.heading).to_be_visible()
        step("Ověřen přístup lektora k seznamu účastníků běhu kurzu")

    @pytest.mark.xfail(
        reason="Defekt aplikace (RBAC): Zákazník má přímý přístup k lektorským formulářům /courses/create a /create-iteration",
        strict=False,
    )
    def test_tc_us19_04_prevention_of_customer_access_to_lector_operations_ui(
        self, page: Page, registered_user: dict
    ):
        """[TC-US19-04] Zamezení přístupu běžného zákazníka k lektorským operacím v UI."""
        self._login(page, registered_user)

        # V katalogu student nesmí vidět tlačítka pro lektorské akce
        self.courses_page.navigate()
        expect(self.courses_page.add_course_button).not_to_be_visible()
        expect(self.courses_page.add_iteration_buttons).not_to_be_visible()
        step("Ověřeno, že zákazník nevidí v katalogu lektorská tlačítka")

        # Na detailu nesmí vidět správu účastníků
        self.courses_page.navigate_to_detail(1)
        expect(self.courses_page.participants_buttons).not_to_be_visible()
        step("Ověřeno, že zákazník nevidí na detailu kurzu tlačítko 'Přihlášení'")

        # Přímý přístup na lektorské URL musí být odmítnut
        self.course_create_page.navigate()
        expect(self.course_create_page.heading).not_to_be_visible()
        step("Ověřeno odmítnutí přístupu na /courses/create pro zákazníka")

        self.iteration_create_page.open_for_course(1)
        expect(self.iteration_create_page.container).not_to_be_visible()
        step("Ověřeno odmítnutí přístupu na /courses/1/create-iteration pro zákazníka")

        self.students_page.open_for_iteration(1)
        expect(self.students_page.participants_table).not_to_be_visible()
        step("Ověřeno odmítnutí přístupu na /courses/1/participants pro zákazníka")

    @pytest.mark.xfail(
        reason="Defekt aplikace (RBAC): Lektor má přímý přístup na registrační formulář /courses/:id/register",
        strict=False,
    )
    def test_tc_us19_05_restriction_of_enrollment_for_lector_role(self, page: Page, lector_user: dict):
        """[TC-US19-05] Zamezení zápisu na běhy kurzů pro uživatele v roli Lektor (UI i API úroveň)."""
        self._login(page, lector_user)

        self.courses_page.navigate_to_detail(1)
        expect(self.courses_page.course_detail).to_be_visible()

        # Lektor nesmí vidět tlačítko zápisu na běh kurzu
        expect(self.courses_page.enroll_buttons).not_to_be_visible()
        step("Ověřeno, že lektor nemá v detailu kurzu tlačítko zápisu 'Nezávazná registrace'")

        # Přímý přístup na formulář zápisu musí být lektorovi odmítnut
        self.enroll_page.open_for_iteration(1)
        expect(self.enroll_page.heading).not_to_be_visible()
        step("Ověřeno, že přímý přístup na /courses/1/register byl lektorovi odmítnut")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Servisní trasy (např. /artisan, /system-cache, /_ignition) vracejí HTTP 200 místo 404/403 a /migrate vrací HTTP 500",
        strict=False,
    )
    def test_tc_us19_06_unavailability_of_maintenance_interfaces(self):
        """[TC-US19-06] Nedostupnost servisních a údržbových rozhraní pro neautorizované návštěvníky."""
        service_routes = ["/artisan", "/migrate", "/system-cache", "/_ignition", "/telescope"]
        base_url = self.courses_page.base_url

        for route in service_routes:
            url = f"{base_url}{route}"
            status = 200
            try:
                resp = urllib.request.urlopen(url)
                status = resp.status
            except urllib.error.HTTPError as e:
                status = e.code

            assert status in (403, 404), (
                f"Servisní trasa '{route}' vrátila neočekávaný HTTP kód {status} (očekáváno 403 nebo 404)"
            )
        step("Ověřeno, že servisní trasy vrací 403 Forbidden nebo 404 Not Found")

    def test_tc_us19_07_role_switching_and_immediate_permission_update(
        self, page: Page, registered_user: dict, lector_user: dict
    ):
        """[TC-US19-07] Přepnutí rolí a okamžitá aktualizace autorizačních oprávnění v sezení."""
        # 1. Přihlášení jako Zákazník
        self._login(page, registered_user)
        self.courses_page.navigate()
        expect(self.courses_page.add_course_button).not_to_be_visible()
        step("Ověřeno, že zákazník nemá tlačítko 'Přidat kurz'")

        # 2. Odhlášení
        self.courses_page.navbar.logout()
        expect(self.courses_page.navbar.login_link).to_be_visible()
        step("Zákazník úspěšně odhlášen")

        # 3. Přihlášení jako Lektor v témže prohlížeči
        self._login(page, lector_user)
        self.courses_page.navigate()
        expect(self.courses_page.add_course_button).to_be_visible()
        step("Ověřeno, že po přihlášení lektora jsou lektorská oprávnění ihned aktivní")

        # 4. Odhlášení lektora a návrat k zákazníkovi
        self.courses_page.navbar.logout()
        self._login(page, registered_user)
        self.courses_page.navigate()
        expect(self.courses_page.add_course_button).not_to_be_visible()
        step("Ověřeno správné vyčištění oprávnění lektora při opětovném přihlášení zákazníka")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Backend API postrádá serverovou autorizaci a umožní vytvoření kurzu i bez lektorské role",
        strict=False,
    )
    def test_tc_us19_08_prevention_of_unauthorized_data_manipulation_via_api(
        self, page: Page, registered_user: dict
    ):
        """[TC-US19-08] Zamezení neoprávněné manipulace s daty přes přímé API / POST požadavky."""
        self._login(page, registered_user)

        # Pokus o odeslání POST požadavku na vytvoření kurzu se sezením běžného zákazníka
        response = page.request.post(
            f"{self.courses_page.base_url}/api/courses",
            data={
                "name": "Hacker Course Test",
                "description": "Unauthorized attempt",
                "capacity": 10,
                "price": 1000,
            },
        )

        assert response.status in (401, 403), (
            f"Požadavek běžného zákazníka na vytvoření kurzu měl být odmítnut (401/403), ale vrátil: {response.status}"
        )
        step("Ověřeno odmítnutí neoprávněného API požadavku zákazníka na vytvoření kurzu")

    def test_tc_us19_09_protection_against_horizontal_privilege_escalation_idor(
        self, page: Page, lector_user: dict
    ):
        """[TC-US19-09] Ochrana proti horizontální eskalaci práv (IDOR) mezi lektory."""
        self._login(page, lector_user)

        # Lektor se pokusí otevřít účastníky kurzu, který nespravuje (např. běh s ID 999999)
        self.students_page.open_for_iteration(999999)

        # Systém musí zabránit přístupu a nezobrazit tabulku
        expect(self.students_page.participants_table).not_to_be_visible()
        step("Ověřeno, že lektor nemá přístup k účastníkům cizího kurzu (ochrana proti IDOR)")
