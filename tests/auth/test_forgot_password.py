import pytest
from playwright.sync_api import Page, expect
from pages.forgot_password_page import ForgotPasswordPage
from helpers.step_helpers import step


class TestDemoForgotPassword:
    """Testovací sada pro žádost o obnovu hesla dle specifikace US-05."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Inicializuje Page Object a přejde na stránku před každým testem."""
        self.page = page
        self.forgot_page = ForgotPasswordPage(page)
        self.forgot_page.navigate()

    @pytest.mark.xfail(
        reason="Defekt aplikace: Backend testovani.kitner.cz selhává při odesílání e-mailu kvůli vyčerpané kvótě Mailtrap (500 Internal Server Error) nebo throttlingu (422)",
        strict=True,
    )
    def test_tc_us05_01_successful_password_reset_request_for_registered_email(
        self, page: Page, registered_user: dict
    ):
        """[TC-US05-01] Úspěšné odeslání žádosti o reset hesla pro registrovaný e-mail."""
        expect(self.forgot_page.email_input).to_be_visible()
        expect(self.forgot_page.submit_button).to_be_visible()
        step("Ověřena přítomnost pole pro e-mail a odesílacího tlačítka")

        self.forgot_page.request_password_reset(registered_user["email"])
        step(f"Odeslána žádost o reset hesla pro e-mail: {registered_user['email']}")

        expect(self.forgot_page.status_message).to_be_visible()
        expect(self.forgot_page.status_message).to_contain_text("Odkaz na obnovení hesla")
        step("Ověřeno zobrazení potvrzovací zprávy o odeslání resetovacího odkazu")

    def test_tc_us05_02_validation_mandatory_email_field(self, page: Page):
        """[TC-US05-02] Validace povinného pole při odeslání prázdného formuláře."""
        expect(self.forgot_page.email_input).to_be_visible()
        self.forgot_page.request_password_reset("")
        step("Odeslán prázdný formulář bez vyplněného e-mailu")

        # Ověření zobrazení validační chyby povinného pole
        expect(self.forgot_page.email_error).to_be_visible()
        expect(self.forgot_page.email_error).to_contain_text("The email field is required.")
        expect(page).to_have_url(self.forgot_page.url)
        step("Ověřena validace povinného pole: zobrazena chybová hláška a stránka zůstala na /forgot-password")

    def test_tc_us05_03_validation_invalid_email_format(self, page: Page, invalid_emails: list):
        """[TC-US05-03] Validace neplatného formátu e-mailové adresy."""
        invalid_sample = invalid_emails[0]
        self.forgot_page.request_password_reset(invalid_sample)
        step(f"Zadán syntakticky neplatný formát e-mailu: {invalid_sample}")

        expect(self.forgot_page.email_input).to_have_js_property("validity.valid", False)
        expect(page).to_have_url(self.forgot_page.url)
        step("Ověřena klientská validace formátu: formulář nebyl odeslán na server")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Prevence odhadování účtů (User Enumeration) selhává – systém vrací 'We can't find a user with that email address' namísto neutrálního potvrzení",
        strict=True,
    )
    def test_tc_us05_04_non_existent_email_user_enumeration_prevention(self, page: Page):
        """[TC-US05-04] Odeslání žádosti pro neexistující e-mail a prevence odhadování účtů."""
        non_existent_email = "zcela.neexistujici.konto999@example.com"
        self.forgot_page.request_password_reset(non_existent_email)
        step(f"Odeslána žádost s neexistujícím e-mailem: {non_existent_email}")

        # Bezpečnostní standard vyžaduje, aby systém nezveřejňoval neexistenci účtu
        expect(self.forgot_page.user_not_found_message).not_to_be_visible()
        expect(self.forgot_page.status_message).to_be_visible()
        step("Ověřeno zobrazení neutrálního hlášení a absence prozrazení neexistence účtu")
