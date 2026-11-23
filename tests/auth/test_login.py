import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.forgot_password_page import ForgotPasswordPage
from helpers.step_helpers import step


class TestDemoLogin:
    """Testovací sada pro ověření funkčnosti přihlášení dle specifikace US-03."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)

    def test_tc_us03_01_successful_login_and_role_navigation_adaptation(
        self, page: Page, registered_user: dict, lector_user: dict
    ):
        """[TC-US03-01] Úspěšné přihlášení s platnými údaji a adaptace horní navigace podle role."""
        # 1. Přihlášení v roli Zákazník
        self.login_page.navigate()
        step("Otevřena stránka přihlášení (/login)")

        self.login_page.login(registered_user["email"], registered_user["password"])
        expect(page).to_have_url(f"{self.login_page.base_url}/courses")
        step("Ověřeno přesměrování zákazníka na /courses")

        expect(self.login_page.logout_button).to_be_visible()
        expect(self.login_page.profile_link).to_be_visible()
        expect(self.login_page.nav_login_link).not_to_be_visible()
        step("Ověřena adaptace navigace pro zákazníka: tlačítko Odhlásit se, Můj profil a zánik Přihlásit se")

        # 2. Odhlášení
        self.login_page.logout()
        expect(self.login_page.nav_login_link).to_be_visible()
        expect(self.login_page.logout_button).not_to_be_visible()
        step("Ověřeno úspěšné odhlášení")

        # 3. Přihlášení v roli Lektor
        self.login_page.navigate()
        self.login_page.login(lector_user["email"], lector_user["password"])
        expect(page).to_have_url(f"{self.login_page.base_url}/courses")
        step("Ověřeno přesměrování lektora na /courses")

        expect(self.login_page.logout_button).to_be_visible()
        expect(self.login_page.nav_login_link).not_to_be_visible()
        step("Ověřeno úspěšné přihlášení lektora a přítomnost tlačítka Odhlásit se")

    def test_tc_us03_02_validation_mandatory_fields_and_invalid_email_format(
        self, page: Page, invalid_emails: list
    ):
        """[TC-US03-02] Validace povinných polí a neplatného formátu e-mailu."""
        self.login_page.navigate()
        step("Otevřena stránka přihlášení")

        # 1. Prázdný formulář (povinná pole na straně serveru)
        self.login_page.login("", "")
        expect(page).to_have_url(f"{self.login_page.base_url}/login")
        expect(self.login_page.error_message).to_be_visible()
        expect(self.login_page.error_message).to_contain_text("The email field is required.")
        step("Ověřeno setrvání na /login a zobrazení chybové hlášky pro povinný e-mail")

        # 2. Neplatný formát e-mailu (klientská HTML5 validace type='email')
        self.login_page.navigate()
        self.login_page.login(invalid_emails[0], "BezpecneHeslo123")
        expect(page).to_have_url(f"{self.login_page.base_url}/login")
        expect(self.login_page.email_input).not_to_have_js_property("validationMessage", "")
        step("Ověřeno spuštění HTML5 validace pro syntakticky neplatný formát e-mailu")

    def test_tc_us03_03_case_insensitivity_and_whitespace_trimming(self, page: Page, registered_user: dict):
        """[TC-US03-03] Tolerance k velikosti písmen a automatické ořezávání mezer v e-mailu."""
        self.login_page.navigate()
        step("Otevřena stránka přihlášení")

        raw_email = f"   {registered_user['email'].upper()}   "
        self.login_page.login(raw_email, registered_user["password"])

        expect(page).to_have_url(f"{self.login_page.base_url}/courses")
        expect(self.login_page.logout_button).to_be_visible()
        step("Ověřeno úspěšné přihlášení s normalizovaným e-mailem (velká písmena + okrajové mezery)")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Po neúspěšném pokusu o přihlášení nedochází k bezpečnostnímu vymazání pole hesla",
        strict=True,
    )
    def test_tc_us03_04_unified_error_message_and_password_clearing(
        self, page: Page, registered_user: dict
    ):
        """[TC-US03-04] Jednotná chybová hláška a bezpečnostní vyčištění pole hesla."""
        expected_error = "These credentials do not match our records."

        # Scénář A: Neexistující e-mail
        self.login_page.navigate()
        self.login_page.login("zcela.neexistujici.adresa999@example.com", "Heslo123")

        expect(page).to_have_url(f"{self.login_page.base_url}/login")
        expect(self.login_page.error_message).to_be_visible()
        expect(self.login_page.error_message).to_contain_text(expected_error)
        step(f"Scénář A: Ověřena chybová hláška pro neexistující účet: '{expected_error}'")

        # Scénář B: Existující účet s chybným heslem
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], "SpatneHeslo999!")

        expect(page).to_have_url(f"{self.login_page.base_url}/login")
        expect(self.login_page.error_message).to_be_visible()
        expect(self.login_page.error_message).to_contain_text(expected_error)
        expect(self.login_page.email_input).to_have_value(registered_user["email"])
        step("Scénář B: Ověřena identická chybová zpráva a zachování předvyplněného e-mailu")

        # Bezpečnostní vymazání pole hesla (selhává na defektu aplikace)
        expect(self.login_page.password_input).to_have_value("")
        step("Ověřeno automatické bezpečnostní vymazání pole hesla po chybě přihlášení")

    def test_tc_us03_05_keyboard_accessibility_and_navigation(self, page: Page, registered_user: dict):
        """[TC-US03-05] Přístupné ovládání přihlašovacího formuláře z klávesnice."""
        self.login_page.navigate()
        step("Otevřena stránka přihlášení")

        # Přechod do formuláře a focus pole E-mail
        self.login_page.email_input.focus()
        expect(self.login_page.email_input).to_be_focused()
        self.login_page.email_input.fill(registered_user["email"])
        step("Focus na pole E-mail a vyplnění e-mailu")

        # Klávesa Tab do hesla
        page.keyboard.press("Tab")
        expect(self.login_page.password_input).to_be_focused()
        self.login_page.password_input.fill(registered_user["password"])
        step("Focus na pole Heslo a vyplnění hesla")

        # Odeslání klávesou Enter z pole hesla
        page.keyboard.press("Enter")
        expect(page).to_have_url(f"{self.login_page.base_url}/courses")
        expect(self.login_page.logout_button).to_be_visible()
        step("Klávesa Enter: Úspěšné odeslání přihlašovacího formuláře a přechod na /courses")

    def test_tc_us03_06_password_masking_and_navigation_links(self, page: Page):
        """[TC-US03-06] Maskování zadaného hesla a doprovodné navigační odkazy formuláře."""
        self.login_page.navigate()
        step("Otevřena stránka přihlášení")

        expect(self.login_page.password_input).to_have_attribute("type", "password")
        step("Ověřeno maskování hesla (atribut type='password')")

        expect(self.login_page.register_link).to_be_visible()
        step("Ověřen odkaz pro registraci")

        expect(self.login_page.forgot_password_link).to_be_visible()
        self.login_page.forgot_password_link.click()
        expect(page).to_have_url(f"{self.login_page.base_url}/forgot-password")
        step("Ověřen odkaz pro obnovu hesla a funkční přesměrování na /forgot-password")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Přihlášený uživatel není automaticky přesměrován z /login zpět do aplikace; aplikace umožní opětovné zobrazení formuláře přihlášení",
        strict=True,
    )
    def test_tc_us03_07_authenticated_user_access_to_login_page_redirects(
        self, page: Page, registered_user: dict
    ):
        """[TC-US03-07] Chování při pokusu o otevření stránky přihlášení již přihlášeným uživatelem."""
        # Přihlášení
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])
        expect(page).to_have_url(f"{self.login_page.base_url}/courses")
        step("Uživatel úspěšně přihlášen")

        # Pokus o otevření /login v přihlášeném stavu
        self.login_page.navigate()
        expect(page).not_to_have_url(f"{self.login_page.base_url}/login")
        expect(page).to_have_url(f"{self.login_page.base_url}/courses")
        step("Ověřeno přesměrování přihlášeného uživatele z /login zpět do katalogu kurzů")
