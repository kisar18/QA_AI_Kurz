from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class EmailVerificationPage(BasePage):
    """Page Object Model pro stránku a proces ověření e-mailové adresy (/email/verify)."""

    PATH = "/email/verify"

    def __init__(self, page: Page):
        super().__init__(page)
        # TODO(testid): aplikace prozatím postrádá data-testid na komponentě ověření e-mailu
        self.resend_button: Locator = page.get_by_role("button", name="Znovu odeslat ověřovací e-mail")
        self.status_message: Locator = page.get_by_test_id("verification_status")
        # Chybová stránka neplatného podpisu (403 Invalid Signature)
        self.forbidden_heading: Locator = page.get_by_text("403")
        self.invalid_signature_text: Locator = page.get_by_text("INVALID SIGNATURE.")

    def open_verification_link(self, user_id: str | int, token_hash: str, signature: str, expires: int = 1777777777):
        """Otevře podepsaný ověřovací odkaz."""
        url = f"/verify-email/{user_id}/{token_hash}?expires={expires}&signature={signature}"
        return self.page.goto(f"{self.base_url}{url}")

    def send_resend_notification(self) -> int:
        """Odešle POST požadavek na znovuzaslání ověřovacího e-mailu přes klientský fetch s XSRF tokenem."""
        return self.page.evaluate("""async () => {
            const xsrf = decodeURIComponent(
                document.cookie.split('; ')
                    .find(row => row.startsWith('XSRF-TOKEN='))
                    ?.split('=')[1] || ''
            );
            const resp = await fetch('/email/verification-notification', {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'X-XSRF-TOKEN': xsrf
                }
            });
            return resp.status;
        }""")
