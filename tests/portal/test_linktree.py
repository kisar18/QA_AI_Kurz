import re
import pytest
from playwright.sync_api import Page, expect
from pages.linktree_page import LinktreePage
from pages.courses_page import CoursesPage
from helpers.step_helpers import step


class TestPortalLinktree:
    """Testovací sada pro úvodní navigační rozcestník portálu dle US-01."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.linktree_page = LinktreePage(page)
        self.courses_page = CoursesPage(page)

    def test_tc_us01_01_linktree_elements_and_metadata_display(self, page: Page):
        """[TC-US01-01] Zobrazení rozcestníku, metadat stránky a přítomnost všech navigačních odkazů."""
        self.linktree_page.navigate()
        step("Otevřena úvodní stránka rozcestníku (/)")

        res = page.request.get(self.linktree_page.url)
        assert res.status == 200
        step("Ověřen úspěšný stavový kód HTTP 200 OK")

        expect(page).to_have_url(f"{self.linktree_page.base_url}/")
        step("Ověřena cílová URL rozcestníku (/)")

        expect(page).to_have_title(self.linktree_page.TITLE_TEXT)
        step(f"Ověřen titulek stránky v záložce prohlížeče: '{self.linktree_page.TITLE_TEXT}'")

        expect(self.linktree_page.heading).to_be_visible()
        expect(self.linktree_page.heading).to_have_text(self.linktree_page.HEADING_TEXT)
        step(f"Ověřen hlavní nadpis H1: '{self.linktree_page.HEADING_TEXT}'")

        # Ověření viditelnosti všech odkazů rozcestníku (AC-2, AC-3)
        expect(self.linktree_page.calculator_link).to_be_visible()
        step("Ověřen odkaz na aplikaci Kalkulačka")

        expect(self.linktree_page.test_login_link).to_be_visible()
        step("Ověřen odkaz na Testovací login")

        expect(self.linktree_page.nextdate_link).to_be_visible()
        step("Ověřen odkaz na NextDate")

        expect(self.linktree_page.course_registration_link).to_be_visible()
        step("Ověřen odkaz na Registraci na kurz")

        expect(self.linktree_page.course_list_link).to_be_visible()
        step("Ověřen doplňkový odkaz '(výpis)' kurzu")

        expect(self.linktree_page.demo_login_link).to_be_visible()
        step("Ověřen dominantní odkaz 'Demo-login' pro vstup do aplikace kurzů")

    def test_tc_us01_02_demo_login_navigation_to_courses(self, page: Page):
        """[TC-US01-02] Navigace přes odkaz 'Demo-login' přímo do katalogu kurzů."""
        self.linktree_page.navigate()
        step("Otevřena úvodní stránka rozcestníku")

        self.linktree_page.open_demo_login()
        step("Kliknuto na odkaz 'Demo-login'")

        expect(page).to_have_url(f"{self.linktree_page.base_url}/courses")
        step("Ověřeno okamžité přesměrování do katalogu kurzů (/courses)")

        expect(self.courses_page.title).to_be_visible()
        expect(self.courses_page.courses_section).to_be_visible()
        step("Ověřeno úspěšné načtení sekce katalogu kurzů")

    def test_tc_us01_03_external_links_functionality_and_attributes(self, page: Page):
        """[TC-US01-03] Funkčnost, cílové adresy a bezpečnostní atributy externích odkazů."""
        self.linktree_page.navigate()
        step("Otevřena úvodní stránka rozcestníku")

        links_to_verify = [
            (self.linktree_page.calculator_link, re.compile(r"/kalkulacka/kalkulacka\.html$"), "/kalkulacka/kalkulacka.html", "Kalkulačka"),
            (self.linktree_page.test_login_link, re.compile(r"/login_app/?$"), "/login_app/", "Testovací login"),
            (self.linktree_page.nextdate_link, re.compile(r"/nextdate/?$"), "/nextdate/", "NextDate"),
            (self.linktree_page.course_registration_link, re.compile(r"/regkurz/?$"), "/regkurz/", "Registrace na kurz"),
            (self.linktree_page.course_list_link, re.compile(r"/regkurz/list\.php$"), "/regkurz/list.php", "(výpis)"),
        ]

        for link_locator, pattern, _, link_name in links_to_verify:
            expect(link_locator).to_have_attribute("href", pattern)
            step(f"Ověřen atribut href odkazu '{link_name}'")

            target_attr = link_locator.get_attribute("target")
            if target_attr == "_blank":
                expect(link_locator).to_have_attribute("rel", "noopener noreferrer")
                step(f"Ověřen bezpečnostní atribut rel='noopener noreferrer' pro odkaz '{link_name}'")

        # Ověření dostupnosti externích endpointů (HTTP 200)
        for _, _, path, name in links_to_verify:
            full_url = f"{self.linktree_page.base_url}{path}"
            res = page.request.get(full_url)
            assert res.status == 200, f"Odkaz na {name} ({full_url}) vrátil chybový status {res.status}"
            step(f"Ověřena funkčnost a dostupnost endpointu pro '{name}' (HTTP 200 OK)")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Aplikace nemá implementovanou chybovou stránku 404 pro neznámé routy; vykreslí prázdnou bílou stránku se stavovým kódem 200",
        strict=False,
    )
    def test_tc_us01_04_handling_non_existent_subpage(self, page: Page):
        """[TC-US01-04] Zpracování neexistující podstránky z rozcestníku."""
        non_existent_url = f"{self.linktree_page.base_url}/neexistujici-nastroj-12345"
        response = page.goto(non_existent_url)
        step(f"Zadán požadavek na neexistující adresu {non_existent_url}")

        assert response is not None and response.status == 404
        step("Ověřen stavový kód 404 Not Found")

        expect(self.linktree_page.not_found_heading).to_be_visible()
        step("Ověřena přítomnost 404 chybové hlášky na stránce")

        expect(self.linktree_page.not_found_back_link).to_be_visible()
        self.linktree_page.not_found_back_link.click()
        expect(page).to_have_url(f"{self.linktree_page.base_url}/")
        step("Ověřena možnost návratu z chybové stránky zpět na rozcestník")

    def test_tc_us01_05_responsive_mobile_viewport(self, page: Page):
        """[TC-US01-05] Responzivní zobrazení a čitelnost rozcestníku na mobilním zařízení."""
        page.set_viewport_size({"width": 375, "height": 667})
        self.linktree_page.navigate()
        step("Nastaven mobilní viewport (375x667) a načten rozcestník")

        # Ověření, že nevzniká nežádoucí horizontální posuvník
        scroll_width = page.evaluate("() => document.documentElement.scrollWidth")
        client_width = page.evaluate("() => document.documentElement.clientWidth")
        assert scroll_width <= client_width, "Stránka na mobilním rozlišení přetéká horizontálně"
        step("Ověřeno, že stránka nepřetéká horizontálně")

        # Ověření viditelnosti odkazů a funkčnosti Demo-login na mobilním zobrazení
        expect(self.linktree_page.demo_login_link).to_be_visible()
        self.linktree_page.open_demo_login()
        expect(page).to_have_url(f"{self.linktree_page.base_url}/courses")
        step("Ověřena funkčnost tlačítka 'Demo-login' a přechod do katalogu na mobilním viewportu")

    def test_tc_us01_06_keyboard_accessibility_and_navigation(self, page: Page):
        """[TC-US01-06] Přístupnost a navigace rozcestníku pomocí klávesnice."""
        self.linktree_page.navigate()
        step("Načtena úvodní stránka rozcestníku")

        # Postupné procházení odkazů pomocí Tab klávesy
        page.keyboard.press("Tab")
        expect(self.linktree_page.calculator_link).to_be_focused()
        step("Klávesa Tab: Focus na odkaz Kalkulacka")

        page.keyboard.press("Tab")
        expect(self.linktree_page.test_login_link).to_be_focused()
        step("Klávesa Tab: Focus na odkaz Testovací login")

        page.keyboard.press("Tab")
        expect(self.linktree_page.nextdate_link).to_be_focused()
        step("Klávesa Tab: Focus na odkaz NextDate")

        page.keyboard.press("Tab")
        expect(self.linktree_page.course_registration_link).to_be_focused()
        step("Klávesa Tab: Focus na odkaz Registrace na kurz")

        page.keyboard.press("Tab")
        expect(self.linktree_page.course_list_link).to_be_focused()
        step("Klávesa Tab: Focus na odkaz (výpis)")

        page.keyboard.press("Tab")
        expect(self.linktree_page.demo_login_link).to_be_focused()
        step("Klávesa Tab: Focus na dominantní odkaz Demo-login")

        # Odeslání odkazu stiskem klávesy Enter
        page.keyboard.press("Enter")
        expect(page).to_have_url(f"{self.linktree_page.base_url}/courses")
        step("Klávesa Enter: Úspěšné přesměrování do katalogu kurzů (/courses)")
