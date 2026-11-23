import re
import pytest
from playwright.sync_api import Page, expect
from pages.components.navbar import Navbar
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from pages.my_courses_page import MyCoursesPage
from pages.courses_page import CoursesPage
from helpers.step_helpers import step


class TestDemoLogout:
    """Testovací sada pro bezpečné odhlášení ze systému dle specifikace US-04."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)
        self.profile_page = ProfilePage(page)
        self.my_courses_page = MyCoursesPage(page)
        self.courses_page = CoursesPage(page)
        self.navbar = self.login_page.navbar

    def _login(self, page: Page, user: dict):
        self.login_page.navigate()
        with page.expect_response(
            lambda r: "/login" in r.url and r.request.method == "POST",
            timeout=15000,
        ):
            self.login_page.login(user["email"], user["password"])
        expect(page).to_have_url(f"{self.login_page.base_url}/courses", timeout=15000)

    def test_tc_us04_01_successful_logout_via_navbar(self, page: Page, registered_user: dict):
        """[TC-US04-01] Úspěšné odhlášení přihlášeného uživatele přes horní navigaci."""
        self._login(page, registered_user)
        step("Uživatel úspěšně přihlášen")

        expect(self.navbar.logout_button).to_be_visible()
        expect(self.navbar.profile_link).to_be_visible()
        expect(self.navbar.login_link).not_to_be_visible()
        step("Ověřena přítomnost tlačítka pro odhlášení v navigaci")

        self.navbar.logout()
        step("Kliknuto na tlačítko 'Odhlásit se'")

        expect(page).to_have_url(re.compile(r"/(courses|login)?$"))
        expect(self.navbar.login_link).to_be_visible()
        expect(self.navbar.logout_button).not_to_be_visible()
        expect(self.navbar.profile_link).not_to_be_visible()
        step("Ověřeno úspěšné odhlášení: zobrazen odkaz 'Přihlásit se', skryty privátní prvky a veřejná URL")

    def test_tc_us04_02_session_invalidation_and_storage_cleanup(self, page: Page, registered_user: dict):
        """[TC-US04-02] Okamžité zneplatnění uživatelského sezení a smazání klientského úložiště."""
        self._login(page, registered_user)
        context = page.context

        cookies_before = context.cookies()
        session_cookie_before = next((c for c in cookies_before if "session" in c["name"].lower()), None)
        assert session_cookie_before is not None, "Před odhlášením nebyla nalezena session cookie"
        step("Zaznamenána platná session cookie před odhlášením")

        self.navbar.logout()
        step("Uživatel se odhlásil")

        # Kontrola stavu cookies a úložiště po odhlášení
        cookies_after = context.cookies()
        session_cookie_after = next((c for c in cookies_after if "session" in c["name"].lower()), None)
        assert session_cookie_after is None or session_cookie_after["value"] != session_cookie_before["value"], (
            "Session cookie nebyla po odhlášení nahrazena anonymní relací ani smazána"
        )
        token_storage = page.evaluate("() => localStorage.getItem('token') || sessionStorage.getItem('token')")
        assert not token_storage, "V klientském úložišti zůstal citlivý autentizační token"
        step("Ověřeno nahrazení/vymazání session cookie a absence citlivých tokenů v Web Storage")

        # Ověření, že s původní session cookie nelze provádět autorizované volání
        res = page.request.post(
            f"{self.login_page.base_url}/api/users/edit",
            headers={"Cookie": f"{session_cookie_before['name']}={session_cookie_before['value']}"},
            data={"name": "Hacked Session"},
            max_redirects=0,
        )
        assert res.status in (302, 401, 419) or res.url.endswith("/login"), (
            f"Stará session cookie nebyla odmítnuta, status: {res.status}, url: {res.url}"
        )
        step("Ověřeno, že server striktně odmítl požadavek se starou session cookie (stav 302/401/419)")

    def test_tc_us04_03_restricted_private_routes_access_after_logout(self, page: Page, registered_user: dict):
        """[TC-US04-03] Zamezení přístupu k privátním funkcím a profilu po odhlášení přes přímou URL."""
        self._login(page, registered_user)
        self.navbar.logout()
        step("Uživatel přihlášen a následně odhlášen")

        # Pokus o otevření /profile
        self.profile_page.navigate()
        expect(self.profile_page.name_input).not_to_be_visible()
        expect(self.profile_page.heading).not_to_be_visible()
        expect(self.navbar.login_link).to_be_visible()
        step("Ověřeno, že odhlášený uživatel nemá přístup k datům profilu na /profile")

        # Pokus o otevření /my-courses
        self.my_courses_page.navigate()
        expect(self.my_courses_page.date_time_from).not_to_be_visible()
        expect(self.navbar.login_link).to_be_visible()
        step("Ověřeno, že odhlášený uživatel nevidí seznam zapsaných kurzů na /my-courses")

    def test_tc_us04_04_browser_back_button_security(self, page: Page, registered_user: dict):
        """[TC-US04-04] Zabezpečení proti neoprávněnému návratu pomocí tlačítka Zpět v prohlížeči."""
        self._login(page, registered_user)
        self.profile_page.navigate()
        expect(self.profile_page.name_input).to_be_visible()
        step("Otevřen profil v přihlášeném stavu")

        self.navbar.logout()
        expect(self.navbar.login_link).to_be_visible()
        step("Uživatel odhlášen")

        # Stisk tlačítka Zpět v prohlížeči
        page.go_back()
        expect(self.profile_page.name_input).not_to_be_visible()
        step("Ověřeno, že návrat tlačítkem Zpět nezobrazí data profilu")

        # Obnovení stránky (F5)
        page.reload()
        expect(self.profile_page.name_input).not_to_be_visible()
        expect(self.navbar.logout_button).not_to_be_visible()
        expect(self.navbar.login_link).to_be_visible()
        step("Ověřeno, že ani po obnovení stránky nedošlo k obnovení sezení")

    def test_tc_us04_05_permanent_availability_of_logout_button(self, page: Page, registered_user: dict):
        """[TC-US04-05] Trvalá dostupnost tlačítka odhlášení na všech typech stránek a rozlišení."""
        self._login(page, registered_user)

        # 1. Desktop: /courses
        self.courses_page.navigate()
        expect(self.navbar.logout_button).to_be_visible()
        step("Desktop: Tlačítko odhlášení viditelné na /courses")

        # 2. Desktop: Detail kurzu
        self.courses_page.open_first_course_detail()
        expect(self.navbar.logout_button).to_be_visible()
        step("Desktop: Tlačítko odhlášení viditelné na detailu kurzu")

        # 3. Desktop: /profile
        self.profile_page.navigate()
        expect(self.navbar.logout_button).to_be_visible()
        step("Desktop: Tlačítko odhlášení viditelné na /profile")

        # 4. Desktop: /my-courses
        self.my_courses_page.navigate()
        expect(self.navbar.logout_button).to_be_visible()
        step("Desktop: Tlačítko odhlášení viditelné na /my-courses")

        # 5. Mobilní rozlišení (375x667)
        page.set_viewport_size({"width": 375, "height": 667})
        self.courses_page.navigate()
        expect(self.navbar.hamburger_menu).to_be_visible()
        self.navbar.open_mobile_menu()
        expect(self.navbar.logout_button).to_be_visible()
        step("Mobil: Tlačítko odhlášení dostupné v rozbaleném hamburger menu")

        self.navbar.logout()
        expect(self.navbar.hamburger_menu).to_be_visible()
        self.navbar.open_mobile_menu()
        expect(self.navbar.login_link).to_be_visible()
        step("Mobil: Úspěšné odhlášení z mobilního menu")

    def test_tc_us04_06_concurrent_tabs_logout_invalidation(self, page: Page, registered_user: dict):
        """[TC-US04-06] Odhlášení v jedné záložce a souběžná interakce v druhé otevřené záložce."""
        context = page.context

        # Záložka A
        page_a = page
        self._login(page_a, registered_user)

        # Záložka B (souběžně otevřený profil)
        page_b = context.new_page()
        profile_b = ProfilePage(page_b)
        profile_b.navigate()
        expect(profile_b.name_input).to_be_visible()
        step("Otevřeny dvě záložky: Záložka A (kurzy) a Záložka B (profil)")

        # Odhlášení v Záložce A
        navbar_a = Navbar(page_a)
        navbar_a.logout()
        expect(navbar_a.login_link).to_be_visible()
        step("V Záložce A provedeno odhlášení")

        # Pokus o změnu profilu v Záložce B – server musí odmítnout požadavek
        with page_b.expect_response(lambda r: "/api/users/edit" in r.url) as resp_info:
            profile_b.update_profile(name="NeopravnenaZmena")

        edit_response = resp_info.value
        assert edit_response.status in (401, 419), (
            f"Server v Záložce B nevrátil 401/419, ale: {edit_response.status}"
        )
        step("Ověřeno, že server v Záložce B striktně zamítl požadavek se stavem 401/419")

        # Pokus o navigaci na privátní sekci v Záložce B
        navbar_b = Navbar(page_b)
        page_b.reload()
        expect(navbar_b.login_link).to_be_visible()
        expect(navbar_b.logout_button).not_to_be_visible()
        step("Ověřeno, že po obnovení v Záložce B je uživatel odhlášen")

        # Ověření na čisté záložce C, že nedošlo k uložení neoprávněné změny do DB
        page_c = context.new_page()
        login_c = LoginPage(page_c)
        profile_c = ProfilePage(page_c)
        login_c.navigate()
        with page_c.expect_response(lambda r: "/login" in r.url and r.request.method == "POST"):
            login_c.login(registered_user["email"], registered_user["password"])
        expect(page_c).to_have_url(f"{login_c.base_url}/courses", timeout=15000)
        profile_c.navigate()
        expect(profile_c.name_input).not_to_have_value("NeopravnenaZmena")
        step("Ověřeno v čistém sezení, že neoprávněná změna se neuložila do databáze")

        page_b.close()
        page_c.close()
