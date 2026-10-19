import pytest
from playwright.sync_api import Page, expect
from config.settings import BASE_URL
from pages.login_page import LoginPage
from helpers.step_helpers import step


class TestCsrfAndSessionIntegrity:
    """Testovací sada pro CSRF ochranu a integritu sezení (US-20)."""

    def test_csrf_cookie_present_on_app_initialization(self, page: Page):
        """[US-20] Ověření, že aplikace po inicializaci získá platnou CSRF cookie (XSRF-TOKEN)."""
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state("networkidle")

        cookies = page.context.cookies()
        xsrf_cookie = next((c for c in cookies if c["name"] == "XSRF-TOKEN"), None)

        assert xsrf_cookie is not None, "Cookie XSRF-TOKEN nebyla po načtení stránky nalezena"
        assert len(xsrf_cookie["value"]) > 0, "Cookie XSRF-TOKEN je prázdná"
        step(f"Ověřena přítomnost CSRF tokenu v cookies: {xsrf_cookie['name']}")

    def test_unauthorized_state_changing_request_rejected(self, page: Page):
        """[US-20] Ověření, že neautentizovaný požadavek na změnu stavu bez platného sezení a tokenu je zamítnut."""
        response = page.request.post(
            f"{BASE_URL}/api/courses",
            headers={
                "Accept": "application/json",
            },
            data={"name": "Útočný kurz", "price": 1000},
        )
        assert response.status in (401, 403, 419), f"Očekáváno zamítnutí neautorizovaného požadavku, obdrženo: {response.status}"
        step(f"Ověřeno bezpečné zamítnutí neoprávněného POST požadavku (HTTP {response.status})")

    def test_session_regeneration_on_login_and_logout(self, page: Page, registered_user: dict):
        """[US-20] Ověření regenerace sezení po přihlášení a odhlášení (ochrana proti Session Fixation)."""
        login_page = LoginPage(page)
        login_page.navigate()

        # 1. Zachycení výchozí session cookie před přihlášením
        anon_cookies = page.context.cookies()
        anon_session = next((c["value"] for c in anon_cookies if "session" in c["name"].lower()), None)

        # 2. Přihlášení
        login_page.login(registered_user["email"], registered_user["password"])
        page.wait_for_url("**/courses")

        # 3. Session po přihlášení musí být nově regenerována
        auth_cookies = page.context.cookies()
        auth_session = next((c["value"] for c in auth_cookies if "session" in c["name"].lower()), None)

        if anon_session and auth_session:
            assert anon_session != auth_session, "Session cookie nebyla po přihlášení regenerována (Session Fixation riziko)"
            step("Ověřena úspěšná regenerace sezení při přihlášení uživatele")

        # 4. Bezpečné odhlášení
        login_page.logout()
        expect(login_page.nav_login_link).to_be_visible()

        post_logout_cookies = page.context.cookies()
        post_logout_session = next((c["value"] for c in post_logout_cookies if "session" in c["name"].lower()), None)

        if auth_session and post_logout_session:
            assert auth_session != post_logout_session, "Session cookie nebyla po odhlášení změněna/zneplatněna"
            step("Ověřeno zneplatnění sezení po odhlášení uživatele")
