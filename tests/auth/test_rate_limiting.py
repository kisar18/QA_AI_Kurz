import re
import uuid
import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from helpers.step_helpers import step


class TestDemoRateLimiting:
    """Testovací sada pro ochranu proti útokům hrubou silou na přihlášení dle specifikace US-08."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.login_page = LoginPage(page)
        self.navbar = self.login_page.navbar

    def _register_user(self, page: Page, email: str, password: str):
        reg_page = RegisterPage(page)
        reg_page.navigate()
        reg_page.register("Rate User", email, password, password)
        expect(page).to_have_url(re.compile(r"/(courses|home)$"))

    def test_tc_us08_01_attempts_1_to_5_allowed_without_blocking(self, page: Page):
        """[TC-US08-01] Průchod povoleného limitu 1 až 5 neúspěšných pokusů o přihlášení."""
        self.login_page.navigate()
        probe_email = f"rate_probe1_{uuid.uuid4().hex[:6]}@example.com"
        wrong_pass = "SpatneHeslo123!"

        for attempt in range(1, 6):
            resp = self.login_page.login_with_response(probe_email, wrong_pass)
            assert resp.status in (302, 422)
            expect(self.login_page.error_message).to_be_visible()
            expect(self.login_page.error_message).to_contain_text("These credentials do not match our records.")
            step(f"Pokus {attempt}/5: Zobrazena standardní chybová hláška o neplatných údajích")

    def test_tc_us08_02_blocking_on_6th_attempt_and_countdown_display(self, page: Page):
        """[TC-US08-02] Dočasná blokace při 6. neúspěšném pokusu a zobrazení odpočtu sekund."""
        self.login_page.navigate()
        probe_email = f"rate_probe2_{uuid.uuid4().hex[:6]}@example.com"
        wrong_pass = "SpatneHeslo123!"

        for attempt in range(1, 6):
            self.login_page.login_with_response(probe_email, wrong_pass)

        # 6. pokus musí narazit na blokaci
        resp = self.login_page.login_with_response(probe_email, wrong_pass)
        assert resp.status in (302, 422, 429)
        expect(self.login_page.error_message).to_be_visible()
        expect(self.login_page.error_message).to_contain_text("Too many login attempts")
        expect(self.login_page.error_message).to_contain_text(re.compile(r"try again in \d+ seconds", re.IGNORECASE))
        step("Pokus 6: Zablokován – zobrazena výstraha Too many login attempts s odpočtem sekund")

    def test_tc_us08_03_counter_reset_after_successful_login(self, page: Page):
        """[TC-US08-03] Automatické vynulování počítadla neúspěšných pokusů po úspěšném přihlášení."""
        user_email = f"rate_reset_{uuid.uuid4().hex[:6]}@example.com"
        valid_pass = "SpravneHeslo123!"
        self._register_user(page, user_email, valid_pass)
        self.navbar.logout()

        self.login_page.navigate()
        wrong_pass = "ChybneHeslo999!"

        # 4 neúspěšné pokusy
        for attempt in range(1, 5):
            self.login_page.login_with_response(user_email, wrong_pass)
            expect(self.login_page.error_message).to_contain_text("These credentials do not match our records.")
            step(f"Neúspěšný pokus {attempt}/4")

        # 5. pokus se správným heslem -> úspěšné přihlášení
        with page.expect_response(lambda r: "/login" in r.url and r.request.method == "POST"):
            self.login_page.login(user_email, valid_pass)
        expect(page).to_have_url(f"{self.login_page.base_url}/courses", timeout=15000)
        step("5. pokus se správným heslem: Uživatel úspěšně přihlášen (čítač vynulován)")

        # Odhlášení a 1 nový neúspěšný pokus
        self.navbar.logout()
        self.login_page.navigate()
        expect(self.login_page.email_input).to_be_visible()
        resp = self.login_page.login_with_response(user_email, wrong_pass)
        assert resp.status in (302, 422)
        expect(self.login_page.error_message).to_contain_text(
            "These credentials do not match our records.", timeout=15000
        )
        expect(self.login_page.error_message).not_to_contain_text("Too many login attempts")
        step("Nový neúspěšný pokus po přihlášení: Čítač byl vynulován, nedošlo k blokaci")

    def test_tc_us08_04_restoration_of_login_after_throttle_expiration(self, page: Page):
        """[TC-US08-04] Obnovení možnosti přihlášení po vypršení časového limitu blokace."""
        # 1. Registrace legitimního uživatele
        user_email = f"rate_expire_{uuid.uuid4().hex[:6]}@example.com"
        valid_pass = "ValidPass2026!"
        self._register_user(page, user_email, valid_pass)
        self.navbar.logout()

        self.login_page.navigate()

        # 2. Vyvolání blokace 6 neúspěšnými pokusy
        for _ in range(6):
            self.login_page.login_with_response(user_email, "WrongPass123!")

        expect(self.login_page.error_message).to_contain_text("Too many login attempts")
        step("Účet byl zablokován rate limiterem po 6 neúspěšných pokusech")

        # 3. Zjištění zbývajících sekund a vyčkání na expiraci
        m = re.search(r"in (\d+) seconds", self.login_page.error_message.inner_text())
        wait_seconds = int(m.group(1)) if m else 60
        step(f"Zaznamenána doba blokace: {wait_seconds} s, vyčkávám na automatickou expiraci")
        # Asynchronní vyčkání na vypršení časového limitu (+ 2 s rezerva pro synchronizaci serveru)
        page.wait_for_function(f"() => new Promise(r => setTimeout(r, {(wait_seconds + 2) * 1000}))", timeout=75000)

        # 4. Úspěšné přihlášení se správným heslem po vypršení blokace
        with page.expect_response(lambda r: "/login" in r.url and r.request.method == "POST"):
            self.login_page.login(user_email, valid_pass)
        expect(page).to_have_url(f"{self.login_page.base_url}/courses", timeout=15000)
        expect(self.navbar.logout_button).to_be_visible()
        step("Ověřeno úspěšné přihlášení po automatickém vypršení doby blokace")

    def test_tc_us08_05_rate_limit_isolation_per_account(self, page: Page):
        """[TC-US08-05] Izolace počítadla neúspěšných pokusů na konkrétní e-mailovou adresu."""
        email_b = f"rate_user_b_{uuid.uuid4().hex[:6]}@example.com"
        pass_b = "HesloBeta123!"
        self._register_user(page, email_b, pass_b)
        self.navbar.logout()

        self.login_page.navigate()
        email_a = f"rate_user_a_{uuid.uuid4().hex[:6]}@example.com"

        # Zablokování Účtu A
        for _ in range(6):
            self.login_page.login_with_response(email_a, "WrongPassA123!")
        expect(self.login_page.error_message).to_contain_text("Too many login attempts")
        step("Účet A byl úspěšně zablokován rate limiterem")

        # Přihlášení Účtu B na téže stránce/IP musí projít
        self.login_page.login(email_b, pass_b)
        expect(page).to_have_url(f"{self.login_page.base_url}/courses", timeout=15000)
        expect(self.navbar.logout_button).to_be_visible()
        step("Účet B se úspěšně přihlásil: Rate limiter izoluje pokusy per účet a nezpůsobuje DoS")

    def test_tc_us08_06_case_sensitivity_and_normalization_unification(self, page: Page):
        """[TC-US08-06] Sjednocení počítadla při různé velikosti písmen v e-mailu (Case Sensitivity & Normalizace)."""
        self.login_page.navigate()
        base_name = f"caselimit_{uuid.uuid4().hex[:6]}"
        variants = [
            f"{base_name}@example.com",
            f"{base_name.upper()}@example.com",
            f"{base_name.capitalize()}@EXAMPLE.COM",
            f"  {base_name}@example.com  ",
            f"{base_name.swapcase()}@Example.Com",
        ]

        for idx, email_variant in enumerate(variants, start=1):
            self.login_page.login_with_response(email_variant, "WrongPassword123!")
            expect(self.login_page.error_message).to_contain_text("These credentials do not match our records.")
            step(f"Pokus {idx}/5 s variantou zápisu: '{email_variant}'")

        # 6. pokus se základní variantou musí narazit na sjednocenou blokaci
        self.login_page.login_with_response(f"{base_name}@example.com", "WrongPassword123!")
        expect(self.login_page.error_message).to_contain_text("Too many login attempts")
        step("Pokus 6: Počítadlo správně sjednotilo normalizované varianty e-mailu a aktivovalo blokaci")

    def test_tc_us08_07_brute_force_protection_on_non_existent_accounts(self, page: Page):
        """[TC-US08-07] Ochrana proti útokům hrubou silou na neexistující účty (Prevence User Enumeration)."""
        self.login_page.navigate()
        non_existent_email = f"nonexistent_{uuid.uuid4().hex[:8]}@example.com"
        wrong_pass = "ArbitraryPassword123!"

        for attempt in range(1, 6):
            self.login_page.login_with_response(non_existent_email, wrong_pass)
            expect(self.login_page.error_message).to_contain_text("These credentials do not match our records.")
            step(f"Pokus {attempt}/5 s neexistujícím e-mailem")

        # 6. pokus pro neexistující e-mail musí také vyvolat blokaci
        self.login_page.login_with_response(non_existent_email, wrong_pass)
        expect(self.login_page.error_message).to_contain_text("Too many login attempts")
        step("Pokus 6: Rate Limiting aktivován i pro neexistující e-mail – prevence User Enumeration splněna")

    def test_tc_us08_08_submission_during_active_block_and_countdown_check(self, page: Page):
        """[TC-US08-08] Pokus o odeslání přihlášení uprostřed doby aktivní blokace a kontrola odpočtu."""
        self.login_page.navigate()
        probe_email = f"rate_countdown_{uuid.uuid4().hex[:6]}@example.com"
        wrong_pass = "WrongPass123!"

        for _ in range(6):
            self.login_page.login_with_response(probe_email, wrong_pass)

        # 1. blokace
        expect(self.login_page.error_message).to_contain_text(
            re.compile(r"Too many login attempts\. Please try again in (\d+) seconds\.")
        )
        initial_text = self.login_page.error_message.inner_text()
        m1 = re.search(r"in (\d+) seconds", initial_text)
        initial_seconds = int(m1.group(1)) if m1 else 60
        step(f"Zaznamenán výchozí čas blokace: {initial_seconds} s")

        # Fyzické uplynutí 2.5 s pro posun odpočtu na backendu
        page.wait_for_function("() => new Promise(r => setTimeout(r, 2500))")

        # Opakované odeslání během trvání blokace
        resp = self.login_page.login_with_response(probe_email, wrong_pass)
        assert resp.status in (302, 422, 429)
        expect(self.login_page.error_message).to_contain_text("Too many login attempts")
        updated_text = self.login_page.error_message.inner_text()
        m2 = re.search(r"in (\d+) seconds", updated_text)
        updated_seconds = int(m2.group(1)) if m2 else initial_seconds
        assert updated_seconds < initial_seconds, (
            f"Čas odpočtu se nesnížil: původní {initial_seconds} s, nový {updated_seconds} s"
        )
        step(f"Ověřeno setrvání blokace a reálný odpočet zbývajícího času ({updated_seconds} s < {initial_seconds} s)")
