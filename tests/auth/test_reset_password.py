import pytest
from playwright.sync_api import Page, expect
from pages.reset_password_page import ResetPasswordPage
from helpers.step_helpers import step


class TestDemoResetPassword:
    """Testovací sada pro dokončení změny hesla pomocí tokenu dle specifikace US-06."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.reset_page = ResetPasswordPage(page)

    @pytest.mark.xfail(
        reason="Defekt infrastruktury/aplikace: Nelze vygenerovat a doručit platný resetovací token kvůli vyčerpané kvótě Mailtrap (500 na /forgot-password)",
        strict=False,
    )
    def test_tc_us06_01_successful_password_reset_with_valid_token(
        self, page: Page, registered_user: dict
    ):
        """[TC-US06-01] Úspěšné nastavení nového hesla s platným tokenem."""
        # Simulace otevření s platným tokenem
        self.reset_page.open_with_token(token="platny-aktivni-token-2026", email=registered_user["email"])
        step("Otevřen formulář pro nastavení nového hesla s platným tokenem")

        expect(self.reset_page.password_input).to_be_visible()
        expect(self.reset_page.password_again_input).to_be_visible()
        expect(self.reset_page.submit_button).to_be_visible()
        step("Ověřena přítomnost polí pro nové heslo, potvrzení hesla a odesílacího tlačítka")

        self.reset_page.reset_password("NoveSilneHeslo2026!", "NoveSilneHeslo2026!")
        step("Zadáno nové silné heslo se shodným potvrzením a odesláno")

        expect(self.reset_page.status_div).to_be_visible()
        expect(self.reset_page.login_link).to_be_visible()
        step("Ověřeno potvrzení o úspěšné změně hesla a nabídka odkazu na přihlášení")

    def test_tc_us06_02_validation_password_mismatch(self, page: Page):
        """[TC-US06-02] Validace neshody nového hesla a kontrolního potvrzení."""
        self.reset_page.open_with_token(token="sample-token", email="test@example.com")
        step("Otevřen formulář resetu hesla")

        self.reset_page.reset_password("HesloABC123!", "HesloXYZ789!")
        step("Zadána odlišná hesla do pole pro nové heslo a potvrzení")

        expect(self.reset_page.password_error).to_be_visible()
        expect(self.reset_page.password_error).to_contain_text("The password field confirmation does not match.")
        step("Ověřeno zobrazení validační chyby při neshodě hesel")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Frontend na /password-reset nezobrazuje v UI chybovou hlášku neplatného tokenu ('This password reset token is invalid'), ačkoliv server správně vrací 422",
        strict=False,
    )
    def test_tc_us06_03_invalid_or_tampered_token_rejection(
        self, page: Page, registered_user: dict
    ):
        """[TC-US06-03] Pokus o nastavení hesla s neplatným nebo pozměněným tokenem."""
        self.reset_page.open_with_token(token="neplatny_token_12345", email=registered_user["email"])
        step("Otevřen formulář resetu hesla s neplatným/pozměněným tokenem")

        with page.expect_response(
            lambda r: "/reset-password" in r.url and r.request.method == "POST"
        ) as resp_info:
            self.reset_page.reset_password("NovePlatneHeslo123!", "NovePlatneHeslo123!")

        resp = resp_info.value
        assert resp.status == 422, f"Server nevrátil 422 pro neplatný token, ale: {resp.status}"
        body = resp.json()
        assert "password reset token is invalid" in body.get("message", "").lower() or any(
            "invalid" in err.lower() for err_list in body.get("errors", {}).values() for err in err_list
        )
        step("Ověřeno, že server striktně odmítl neplatný token s kódem 422")

        # Frontend by měl informovat uživatele o neplatnosti tokenu
        expect(self.reset_page.status_div).to_be_visible()
        step("Ověřeno zobrazení chybové zprávy pro uživatele v UI")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Frontend na /password-reset nezobrazuje v UI chybovou hlášku expirovaného/použitého tokenu, ačkoliv server správně vrací 422",
        strict=False,
    )
    def test_tc_us06_04_expired_or_already_used_token_rejection(
        self, page: Page, registered_user: dict
    ):
        """[TC-US06-04] Pokus o použití vypršeného nebo již jednou použitého tokenu."""
        self.reset_page.open_with_token(token="expired-token-session-999", email=registered_user["email"])
        step("Otevřen formulář s expirovaným/použitým tokenem")

        with page.expect_response(
            lambda r: "/reset-password" in r.url and r.request.method == "POST"
        ) as resp_info:
            self.reset_page.reset_password("DalsiNoveHeslo123!", "DalsiNoveHeslo123!")

        resp = resp_info.value
        assert resp.status == 422, f"Server nevrátil 422 pro expirovaný token, ale: {resp.status}"
        step("Ověřeno, že server odmítl expirovaný token se stavovým kódem 422")

        # Frontend by měl informovat uživatele o vypršení platnosti
        expect(self.reset_page.status_div).to_be_visible()
        step("Ověřeno zobrazení informace o vypršení platnosti odkazu v UI")

    def test_tc_us06_05_security_rules_minimum_password_strength(self, page: Page):
        """[TC-US06-05] Kontrola bezpečnostních pravidel pro minimální sílu hesla."""
        self.reset_page.open_with_token(token="sample-token", email="test@example.com")
        step("Otevřen formulář resetu hesla")

        self.reset_page.reset_password("123", "123")
        step("Zadáno příliš krátké heslo (3 znaky)")

        expect(self.reset_page.password_error).to_be_visible()
        expect(self.reset_page.password_error).to_contain_text("The password field must be at least 8 characters.")
        step("Ověřeno odmítnutí slabého hesla a zobrazení požadavku na minimálně 8 znaků")
