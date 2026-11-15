"""Automatizované testy pro US-17: Domovská uvítací nástěnka po přihlášení.

Pokrývá test casy:
- [TC-US17-01] Zobrazení personalizované uvítací zprávy se jménem uživatele po přihlášení
- [TC-US17-02] Trvalá dostupnost volby 'Domů' v horní navigaci pro přihlášeného uživatele
- [TC-US17-03] Zamezení přístupu na domovskou nástěnku pro nepřihlášeného návštěvníka
- [TC-US17-04] Zobrazení uvítací zprávy pro uživatele s českou diakritikou ve jméně
"""

import re
import uuid
import pytest
from playwright.sync_api import Page, expect

from helpers.step_helpers import step
from pages.courses_page import CoursesPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from pages.register_page import RegisterPage


class TestHomeDashboard:
    """Testovací sada pro domovskou nástěnku (/home) dle US-17."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.home_page = HomePage(page)
        self.courses_page = CoursesPage(page)
        self.login_page = LoginPage(page)
        self.profile_page = ProfilePage(page)
        self.register_page = RegisterPage(page)

    def _login_user(self, page: Page, user: dict):
        """Pomocná metoda pro přihlášení uživatele."""
        self.login_page.navigate()
        self.login_page.login(user["email"], user["password"])
        expect(page).to_have_url(f"{self.courses_page.base_url}/courses", timeout=10000)
        step("Uživatel úspěšně přihlášen")

    def test_tc_us17_01_personalized_welcome_message_display(self, page: Page):
        """[TC-US17-01] Zobrazení personalizované uvítací zprávy se jménem uživatele po přihlášení."""
        unique_suffix = uuid.uuid4().hex[:6]
        user_name = f"Petr Svoboda {unique_suffix}"
        user_email = f"petr_{unique_suffix}@example.com"
        user_pass = "Heslo123!"

        # Každý test si připraví vlastní stav (registrace nového uživatele)
        self.register_page.navigate()
        self.register_page.register(
            name=user_name,
            email=user_email,
            password=user_pass,
            password_again=user_pass,
        )
        expect(page).to_have_url(re.compile(r".*/home|.*/courses"), timeout=10000)

        # Přechod na domovskou stránku /home
        self.home_page.navigate()
        expect(page).to_have_url(self.home_page.url)
        step("Otevřena stránka /home")

        # Ověření přítomnosti uvítacího prvku a personalizovaného textu se jménem uživatele
        expect(self.home_page.welcome_section).to_be_visible()
        expect(self.home_page.welcome_section).to_contain_text(user_name)
        welcome_text = self.home_page.get_welcome_text()
        assert user_name in welcome_text, f"Uvítací zpráva neobsahuje jméno uživatele: '{welcome_text}'"
        step(f"Ověřena personalizovaná uvítací zpráva: '{welcome_text}'")

    def test_tc_us17_02_persistent_home_navigation_link(self, page: Page, registered_user: dict):
        """[TC-US17-02] Trvalá dostupnost volby 'Domů' v horní navigaci pro přihlášeného uživatele."""
        self._login_user(page, registered_user)

        # 1. Kontrola na stránce profilu
        self.profile_page.navigate()
        expect(page).to_have_url(self.profile_page.url)
        expect(self.home_page.home_link).to_be_visible()
        step("Ověřena dostupnost odkazu 'Domů' na stránce profilu")

        # Proklik přes odkaz 'Domů'
        self.home_page.home_link.click()
        expect(page).to_have_url(self.home_page.url)
        expect(self.home_page.welcome_section).to_be_visible()
        step("Ověřeno úspěšné přesměrování z profilu na /home")

        # 2. Kontrola na stránce katalogu kurzů
        self.courses_page.navigate()
        expect(self.home_page.home_link).to_be_visible()
        self.home_page.home_link.click()
        expect(page).to_have_url(self.home_page.url)
        expect(self.home_page.welcome_section).to_be_visible()
        step("Ověřeno úspěšné přesměrování z katalogu kurzů na /home")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Nepřihlášený návštěvník při vstupu na /home není přesměrován na /login ani /courses, obsah katalogu se vykreslí přímo na URL /home",
        strict=False,
    )
    def test_tc_us17_03_prevention_of_unauthenticated_access_to_dashboard(self, page: Page):
        """[TC-US17-03] Zamezení přístupu na domovskou nástěnku pro nepřihlášeného návštěvníka."""
        # Pokus o přímou navigaci nepřihlášeného uživatele na /home
        self.home_page.navigate()

        # Osobní nástěnka nesmí být nepřihlášenému návštěvníkovi zobrazena
        expect(self.home_page.welcome_section).not_to_be_visible()
        step("Ověřeno, že nepřihlášenému návštěvníkovi se nezobrazuje uvítací sekce s privátními daty")

        # Očekává se přesměrování na /login nebo katalog /courses
        expect(page).to_have_url(re.compile(r".*/login|.*/courses$"))
        step("Ověřeno přesměrování nepřihlášeného návštěvníka na přihlášení nebo katalog")

    def test_tc_us17_04_welcome_message_with_czech_diacritics(self, page: Page):
        """[TC-US17-04] Zobrazení uvítací zprávy pro uživatele s českou diakritikou ve jméně."""
        unique_suffix = uuid.uuid4().hex[:6]
        diacritics_name = f"Eliška Řehořová-Žáčková {unique_suffix}"
        user_email = f"eliska_{unique_suffix}@example.com"
        user_pass = "Diakritika123!"

        # Registrace uživatele s komplexní českou diakritikou
        self.register_page.navigate()
        self.register_page.register(
            name=diacritics_name,
            email=user_email,
            password=user_pass,
            password_again=user_pass,
        )

        # Po registraci probíhá přesměrování na /home
        expect(page).to_have_url(re.compile(r".*/home|.*/courses"), timeout=10000)
        self.home_page.navigate()

        # Ověření bezchybného vykreslení českých znaků bez poškození kódování
        expect(self.home_page.welcome_section).to_be_visible()
        expect(self.home_page.welcome_section).to_contain_text(diacritics_name)

        welcome_text = self.home_page.get_welcome_text()
        assert diacritics_name in welcome_text, (
            f"Jméno s diakritikou nebylo správně nalezeno v uvítacím textu: '{welcome_text}'"
        )
        step(f"Ověřeno bezchybné zobrazení jména s diakritikou v uvítání: '{welcome_text}'")
