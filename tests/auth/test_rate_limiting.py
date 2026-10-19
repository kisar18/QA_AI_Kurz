import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from helpers.step_helpers import step
from utils.data_generator import generate_random_email


class TestRateLimiting:
    """Testovací sada pro ochranu proti útokům hrubou silou na přihlášení (US-08)."""

    def test_brute_force_login_triggers_rate_limiting(self, page: Page):
        """Ověření, že po 5 po sobě jdoucích neúspěšných pokusech systém dočasně zablokuje další přihlášení (US-08)."""
        login_page = LoginPage(page)
        login_page.navigate()

        probe_email = generate_random_email("probe_rate_limit")
        wrong_password = "InvalidPassword999!"

        # Prvních 5 pokusů musí vracet standardní chybu o neshodě údajů
        for attempt in range(1, 6):
            login_page.login(probe_email, wrong_password)
            page.wait_for_timeout(1000)
            expect(login_page.error_message).to_be_visible()
            expect(login_page.error_message).to_contain_text("These credentials do not match our records.")
            step(f"Pokus {attempt}/5: Zobrazena standardní chybová hláška o neplatných údajích")

        # 6. pokus musí narazit na ochranu proti hrubé síle (Rate Limiting)
        login_page.login(probe_email, wrong_password)
        page.wait_for_timeout(1000)
        expect(login_page.error_message).to_be_visible()
        expect(login_page.error_message).to_contain_text("Too many login attempts")
        step("Pokus 6: Úspěšně zachycena blokace – zobrazena hláška 'Too many login attempts. Please try again in ... seconds.'")
