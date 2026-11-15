"""Automatizované testy pro US-20: Ochrana proti podvržení požadavků (CSRF) a integrita sezení.

Pokrývá test casy:
- [TC-US20-01] Přítomnost platného bezpečnostního CSRF tokenu ve formulářích
- [TC-US20-02] Odmítnutí formulářového požadavku s chybějícím nebo neplatným CSRF tokenem
- [TC-US20-03] Regenerace identifikátoru sezení při přihlášení a odhlášení (Session Fixation ochrana)
"""

import pytest
from playwright.sync_api import Page, expect

from helpers.step_helpers import step
from pages.courses_page import CoursesPage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage


class TestCsrfAndSessionIntegrity:
    """Testovací sada pro CSRF ochranu a integritu sezení (US-20)."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)
        self.register_page = RegisterPage(page)
        self.courses_page = CoursesPage(page)

    def test_tc_us20_01_presence_of_valid_csrf_token(self, page: Page):
        """[TC-US20-01] Přítomnost platného bezpečnostního CSRF tokenu ve formulářích."""
        # 1. Kontrola na přihlašovací stránce /login
        self.login_page.navigate()
        cookies = page.context.cookies()
        xsrf_cookie = next((c for c in cookies if c["name"] == "XSRF-TOKEN"), None)

        assert xsrf_cookie is not None, "Cookie XSRF-TOKEN nebyla na stránce /login nalezena"
        assert len(xsrf_cookie["value"]) > 0, "Cookie XSRF-TOKEN je prázdná"
        step("Ověřena přítomnost platné XSRF-TOKEN cookie na /login")

        # 2. Kontrola na registrační stránce /register
        self.register_page.navigate()
        cookies_reg = page.context.cookies()
        xsrf_cookie_reg = next((c for c in cookies_reg if c["name"] == "XSRF-TOKEN"), None)

        assert xsrf_cookie_reg is not None, "Cookie XSRF-TOKEN nebyla na stránce /register nalezena"
        assert len(xsrf_cookie_reg["value"]) > 0, "Cookie XSRF-TOKEN je prázdná na /register"
        step("Ověřena přítomnost platné XSRF-TOKEN cookie na /register")

    @pytest.mark.xfail(
        reason="Bezpečnostní defekt aplikace: Server neověřuje platnost CSRF tokenu a akceptuje POST požadavky s neplatným či chybějícím tokenem (vrací HTTP 200 namísto 419/403)",
        strict=False,
    )
    def test_tc_us20_02_rejection_of_request_with_missing_or_invalid_csrf_token(self, page: Page):
        """[TC-US20-02] Odmítnutí formulářového požadavku s chybějícím nebo neplatným CSRF tokenem."""
        self.login_page.navigate()

        # Odeslání požadavku s podvrženým / neplatným CSRF tokenem v hlavičce
        response = page.request.post(
            f"{self.login_page.base_url}/login",
            data={
                "email": "attacker@example.com",
                "password": "WrongPassword123!",
            },
            headers={
                "X-XSRF-TOKEN": "neplatny_podvrzeny_token_123",
            },
        )

        # Očekává se odmítnutí stavovým kódem 419 (Page Expired) nebo 403 (Forbidden)
        assert response.status in (403, 419), (
            f"Požadavek s neplatným CSRF tokenem měl být odmítnut kódem 419 nebo 403, ale vrátil HTTP {response.status}"
        )
        step("Ověřeno bezpečné zamítnutí požadavku s neplatným CSRF tokenem")

    def test_tc_us20_03_session_regeneration_on_login_and_logout(
        self, page: Page, registered_user: dict
    ):
        """[TC-US20-03] Regenerace identifikátoru sezení při přihlášení a odhlášení (Session Fixation ochrana)."""
        self.login_page.navigate()

        # 1. Zachycení výchozí session cookie anonymního uživatele
        anon_cookies = page.context.cookies()
        anon_session = next((c["value"] for c in anon_cookies if "session" in c["name"].lower()), None)

        # 2. Úspěšné přihlášení
        self.login_page.login(registered_user["email"], registered_user["password"])
        expect(page).to_have_url(f"{self.courses_page.base_url}/courses", timeout=10000)

        # 3. Session po přihlášení musí být nově vygenerována (jiné ID)
        auth_cookies = page.context.cookies()
        auth_session = next((c["value"] for c in auth_cookies if "session" in c["name"].lower()), None)

        assert anon_session is not None, "Anonymní session cookie nebyla nalezena"
        assert auth_session is not None, "Autentizovaná session cookie nebyla po přihlášení nalezena"
        assert anon_session != auth_session, (
            "Session cookie nebyla po přihlášení regenerována (Session Fixation riziko)"
        )
        step("Ověřena úspěšná regenerace sezení při přihlášení uživatele")

        # 4. Odhlášení
        self.login_page.logout()
        expect(self.login_page.nav_login_link).to_be_visible()

        # 5. Session cookie po odhlášení musí být opět změněna / zneplatněna
        post_logout_cookies = page.context.cookies()
        post_logout_session = next((c["value"] for c in post_logout_cookies if "session" in c["name"].lower()), None)

        assert post_logout_session is not None, "Session cookie po odhlášení nebyla nalezena"
        assert auth_session != post_logout_session, (
            "Session cookie nebyla po odhlášení změněna/zneplatněna"
        )
        step("Ověřeno bezpečné zneplatnění sezení po odhlášení uživatele")
