import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from pages.helpers import step


class TestUserProfile:
    """Testovací sada pro profil klienta (/profile)."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)
        self.profile_page = ProfilePage(page)

    def _login(self, page: Page, user: dict):
        self.login_page.navigate()
        self.login_page.login(user["email"], user["password"])
        page.wait_for_url("**/courses")

    def test_profile_elements_presence_and_prefilled_data(self, page: Page, registered_user: dict):
        """Ověření zobrazení prvků profilu a předvyplněných údajů přihlášeného klienta."""
        self._login(page, registered_user)
        self.profile_page.navigate()

        expect(self.profile_page.heading).to_be_visible()
        expect(self.profile_page.heading).to_have_text("Profil")
        step("Ověřen nadpis 'Profil'")

        expect(self.profile_page.name_input).to_be_visible()
        assert self.profile_page.name_input.input_value() == registered_user["name"]
        step(f"Ověřeno předvyplněné jméno: {registered_user['name']}")

        expect(self.profile_page.email_input).to_be_visible()
        assert self.profile_page.email_input.input_value() == registered_user["email"]
        step(f"Ověřen předvyplněný e-mail: {registered_user['email']}")

        expect(self.profile_page.phone_input).to_be_visible()
        step("Ověřeno pole pro telefon")

        expect(self.profile_page.ico_input).to_be_visible()
        step("Ověřeno pole pro IČO")

        expect(self.profile_page.save_button).to_be_visible()
        step("Ověřeno tlačítko 'Uložit'")

    def test_profile_successful_update(self, page: Page, registered_user: dict):
        """Ověření úspěšné aktualizace údajů profilu (platný telefon a platné IČO s kontrolním součtem)."""
        self._login(page, registered_user)
        self.profile_page.navigate()

        # Platné IČO s korektním kontrolním součtem ARES modulo 11: 27082440 (Alza.cz a.s.)
        valid_ico = "27082440"
        valid_phone = "+420777123456"

        self.profile_page.update_profile(phone=valid_phone, ico=valid_ico)

        expect(page).to_have_url("http://testovani.kitner.cz/home")
        step("Ověřeno přesměrování na /home po úspěšném uložení profilu")

    def test_profile_invalid_ico_validation(self, page: Page, registered_user: dict):
        """Ověření odmítnutí neplatného IČO (nevyhovující kontrolní součet)."""
        self._login(page, registered_user)
        self.profile_page.navigate()

        # Neplatné IČO s platným telefonem
        self.profile_page.update_profile(phone="+420777123456", ico="12345678")

        expect(page).to_have_url("http://testovani.kitner.cz/profile")
        step("Ověřeno, že formulář se neodeslal a stránka zůstává na /profile")

        expect(self.profile_page.ico_error).to_be_visible()
        step("Ověřena validační hláška 'Neplatné IČO'")

    def test_profile_invalid_phone_validation(self, page: Page, registered_user: dict):
        """Ověření odmítnutí neplatného telefonního čísla."""
        self._login(page, registered_user)
        self.profile_page.navigate()

        # Neplatný telefon s platným IČO
        self.profile_page.update_profile(phone="12", ico="27082440")

        expect(page).to_have_url("http://testovani.kitner.cz/profile")
        step("Ověřeno, že formulář se neodeslal při neplatném telefonu")

        expect(self.profile_page.phone_error).to_be_visible()
        step("Ověřena validační hláška 'Neplatné telefonní číslo'")

    def test_profile_unauthenticated_access_denied(self, page: Page):
        """Ověření, že bez přihlášení není formulář profilu zobrazen."""
        self.profile_page.navigate()

        expect(self.profile_page.name_input).not_to_be_visible()
        expect(self.profile_page.heading).not_to_be_visible()
        step("Ověřeno, že nepřihlášený uživatel nemá přístup k datům profilu")
