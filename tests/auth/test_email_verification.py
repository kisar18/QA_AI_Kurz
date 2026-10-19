import pytest
from playwright.sync_api import Page, APIRequestContext
from config.settings import BASE_URL
from pages.login_page import LoginPage


class TestEmailVerification:
    """Testovací sada pro ověření e-mailové adresy (US-07)."""

    def test_unauthenticated_verification_notification_rejected(self, page: Page):
        """Ověření, že neautentizovaný požadavek na zaslání ověřovacího odkazu je zamítnut (401)."""
        response = page.request.post(
            f"{BASE_URL}/email/verification-notification",
            headers={"Accept": "application/json"},
        )
        assert response.status == 401
        data = response.json()
        assert data.get("message") == "Unauthenticated."

    def test_invalid_or_tampered_verification_link_rejected(self, page: Page):
        """Ověření, že neplatný nebo podvržený ověřovací odkaz není akceptován jako platné ověření."""
        response = page.request.get(
            f"{BASE_URL}/verify-email/99999/invalidhash?expires=1234567890&signature=tampered_signature",
            headers={"Accept": "application/json"},
        )
        # Neautentizovaný nebo neplatný podpis musí vrátit 401 Unauthenticated nebo 403 Forbidden
        assert response.status in (401, 403)

    def test_authenticated_user_verification_endpoint_available(self, page: Page, registered_user: dict):
        """Ověření, že přihlášený uživatel má přístup k endpointu pro znovuzaslání ověření."""
        login_page = LoginPage(page)
        login_page.navigate()
        login_page.login(registered_user["email"], registered_user["password"])
        page.wait_for_url("**/courses")

        # Znovuzaslání s platnými cookies a XSRF tokenem
        res = page.evaluate("""async () => {
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
        # Buď 200/202 (odesláno / již ověřeno) nebo 429 (rate limited / throttled)
        assert res in (200, 202, 204, 302, 429)
