import pytest
from playwright.sync_api import Page, expect
from pages.forgot_password_page import ForgotPasswordPage


class TestForgotPassword:
    """Testy pro stránku obnovy hesla (/forgot-password)."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Inicializuje Page Object a přejde na stránku před každým testem."""
        self.page = page
        self.forgot_page = ForgotPasswordPage(page)
        self.forgot_page.navigate()

    # -----------------------------------------------------------------------
    # TC-FP-01: Zobrazení formuláře a jeho prvků
    # -----------------------------------------------------------------------
    def test_form_elements_are_visible(self):
        """Ověří, že formulář pro obnovu hesla obsahuje vstupní pole pro e-mail
        a tlačítko pro odeslání žádosti."""
        expect(self.forgot_page.email_input).to_be_visible()
        expect(self.forgot_page.submit_button).to_be_visible()

    # -----------------------------------------------------------------------
    # TC-FP-02: HTML5 validace formátu e-mailu
    # -----------------------------------------------------------------------
    def test_invalid_email_format_prevented(self, invalid_emails: list):
        """Ověří, že prohlížečová HTML5 validace zabrání odeslání formuláře
        při zadání řetězce bez znaku '@' (neplatný e-mail z data/invalid_emails.json)."""
        invalid_sample = invalid_emails[0]
        self.forgot_page.email_input.fill(invalid_sample)
        self.forgot_page.submit_button.click()

        # HTML5 validace nedovolí odeslání – stránka zůstane na /forgot-password
        expect(self.page).to_have_url(self.forgot_page.url)

        # Pole e-mailu musí být stále vyplněné (formulář nebyl odeslán)
        expect(self.forgot_page.email_input).to_have_value(invalid_sample)

    # -----------------------------------------------------------------------
    # TC-FP-03: Odeslání žádosti o obnovu hesla s platným e-mailem
    # -----------------------------------------------------------------------
    def test_submit_valid_email_shows_feedback(self, page: Page, registered_user: dict):
        """Ověří, že odeslání formuláře s platným registrovaným e-mailem zobrazí potvrzovací zprávu (US-05)."""
        # Zachytíme /forgot-password pro deterministický test zobrazení UI hlášky
        # (reálný Mailtrap na serveru testovani.kitner.cz pravidelně vyčerpává měsíční limit a vrací 500 TransportException)
        page.route(
            "**/forgot-password",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                json={"status": "Odkaz na obnovení hesla byl odeslán."},
            ),
        )
        self.forgot_page.request_password_reset(registered_user["email"])

        expect(self.forgot_page.status_message).to_be_visible()
        expect(self.forgot_page.status_message).to_contain_text("Odkaz na obnovení hesla")

    # -----------------------------------------------------------------------
    # TC-FP-04: Neexistující e-mail zobrazí chybovou hlášku
    # -----------------------------------------------------------------------
    def test_non_existent_email_shows_user_not_found_message(self):
        """Ověří, že zadání neexistujícího e-mailu zobrazí chybovou hlášku (US-05)."""
        self.forgot_page.request_password_reset("non_existent_user_99999@example.com")
        self.page.wait_for_timeout(1000)

        expect(self.forgot_page.user_not_found_message).to_be_visible()
