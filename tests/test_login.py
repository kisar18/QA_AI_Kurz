import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.helpers import step


class TestDemoLogin:
    """Testovací sada pro ověření funkčnosti Demo Login na testovani.kitner.cz."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)

    def test_navigate_from_courses_to_login(self, page: Page):
        """Ověření prokliku z hlavní stránky kurzů do formuláře přihlášení."""
        self.login_page.navigate_via_courses()

        expect(page).to_have_url("http://testovani.kitner.cz/login")
        step("Ověřeno přesměrování na URL /login")

        expect(self.login_page.login_title).to_be_visible()
        step("Ověřena viditelnost nadpisu formuláře")

        expect(self.login_page.login_title).to_have_text("Přihlášení")
        step("Ověřen text nadpisu 'Přihlášení'")

    def test_login_form_elements_presence(self, page: Page):
        """Ověření přítomnosti a viditelnosti všech klíčových prvků formuláře."""
        self.login_page.navigate()

        expect(self.login_page.email_input).to_be_visible()
        step("Ověřeno pole pro zadání e-mailu")

        expect(self.login_page.password_input).to_be_visible()
        step("Ověřeno pole pro zadání hesla")

        expect(self.login_page.login_button).to_be_visible()
        step("Ověřeno tlačítko pro přihlášení")

        expect(self.login_page.forgot_password_link).to_be_visible()
        step("Ověřen odkaz 'Zapomněli jste heslo?'")

        expect(self.login_page.register_link).to_be_visible()
        step("Ověřen odkaz na registraci")

    def test_successful_login_and_logout(self, page: Page, registered_user: dict):
        """Ověření úspěšného přihlášení s platným účtem a následného odhlášení."""
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])

        # Po úspěšném přihlášení:
        expect(page).to_have_url("http://testovani.kitner.cz/courses")
        step("Ověřeno přesměrování na stránku kurzů (/courses)")

        expect(self.login_page.logout_button).to_be_visible()
        step(f"Ověřeno úspěšné přihlášení uživatele ({registered_user['email']}) – v menu je viditelné tlačítko 'Odhlásit se'")

        expect(self.login_page.profile_link).to_be_visible()
        step("Ověřeno, že v menu je viditelný odkaz na 'Můj Profil'")

        expect(self.login_page.nav_login_link).not_to_be_visible()
        step("Ověřeno, že odkaz 'Přihlásit se' již v menu NENÍ zobrazen")

        # Ověření odhlášení:
        self.login_page.logout()

        expect(self.login_page.nav_login_link).to_be_visible()
        step("Ověřeno úspěšné odhlášení uživatele – v menu se znovu objevil odkaz 'Přihlásit se'")

        expect(self.login_page.logout_button).not_to_be_visible()
        step("Ověřeno, že tlačítko 'Odhlásit se' po odhlášení zmizelo")

        expect(self.login_page.profile_link).not_to_be_visible()
        step("Ověřeno, že odkaz 'Můj Profil' po odhlášení zmizel")

    def test_html5_validation_on_invalid_email_format(self, page: Page):
        """Ověření nativní HTML5 validace pro neplatný formát e-mailu (formulář se neodešle)."""
        self.login_page.navigate()
        self.login_page.login("neplatny_format_emailu", "TajneHeslo123")

        validation_message = self.login_page.email_input.evaluate("el => el.validationMessage")
        assert len(validation_message) > 0
        step("Ověřeno spuštění HTML5 validace pro neplatný formát e-mailu")

        expect(page).to_have_url("http://testovani.kitner.cz/login")
        step("Ověřeno, že stránka zůstala na /login a formulář se neodeslal")

        expect(self.login_page.error_message).not_to_be_visible()
        step("Ověřeno, že se nezobrazila serverová chyba")

        expect(self.login_page.login_button).to_be_visible()
        step("Ověřeno, že tlačítko 'Přihlásit' zůstává připraveno k odeslání")

    def test_login_with_invalid_credentials(self, page: Page):
        """Ověření zobrazení chybové hlášky při zadání neexistujícího uživatele."""
        self.login_page.navigate()
        self.login_page.login("neplatny_uzivatel@example.com", "SpatneHeslo123")

        expect(self.login_page.error_message).to_be_visible()
        step("Ověřena viditelnost chybové hlášky")

        expect(self.login_page.error_message).to_contain_text("These credentials do not match our records.")
        step("Ověřen text chybové hlášky 'These credentials do not match our records.'")

        expect(page).to_have_url("http://testovani.kitner.cz/login")
        step("Ověřeno, že uživatel zůstal na stránce /login")

        expect(self.login_page.nav_login_link).to_be_visible()
        step("Ověřeno, že v navigaci stále svítí 'Přihlásit se'")

        expect(self.login_page.logout_button).not_to_be_visible()
        step("Ověřeno, že v navigaci NENÍ 'Odhlásit se'")

    @pytest.mark.parametrize(
        "email, password",
        [
            ("test.user@domena.cz", "wrong_password_xyz"),
            ("admin@unknown.test", "123456"),
            ("jan.novak@seznam.cz", "spatneHeslo"),
        ],
        ids=["wrong_password", "unknown_admin", "czech_domain_user"],
    )
    def test_login_invalid_credentials_matrix(self, page: Page, email: str, password: str):
        """Parametrizovaný test pro různé kombinace neexistujících/neplatných přihlašovacích údajů."""
        self.login_page.navigate()
        self.login_page.login(email, password)

        expect(self.login_page.error_message).to_be_visible()
        step(f"Ověřena chybová hláška pro e-mail: {email}")

        assert len(self.login_page.get_error_message()) > 0
        step("Ověřeno, že text chybové hlášky není prázdný")

        expect(page).to_have_url("http://testovani.kitner.cz/login")
        step("Ověřeno zachování URL /login")

        expect(self.login_page.logout_button).not_to_be_visible()
        step("Ověřeno, že uživatel nebyl přihlášen")

    def test_password_field_is_masked(self, page: Page):
        """Ověření, že pole pro heslo má type='password' (maskovaný vstup)."""
        self.login_page.navigate()

        expect(self.login_page.password_input).to_have_attribute("type", "password")
        step("Ověřen atribut type='password' u pole pro heslo")

    def test_forgot_password_link(self, page: Page):
        """Ověření funkčnosti odkazu 'Zapomněli jste heslo?'."""
        self.login_page.navigate()
        self.login_page.forgot_password_link.click()

        expect(page).to_have_url("http://testovani.kitner.cz/forgot-password")
        step("Ověřeno přesměrování na /forgot-password")

        expect(page.locator("[data-testid='email_input']")).to_be_visible()
        step("Ověřena přítomnost pole pro zadání resetovacího e-mailu")

        expect(page.locator("button")).to_be_visible()
        step("Ověřena přítomnost odesílacího tlačítka")

    def test_register_link(self, page: Page):
        """Ověření funkčnosti odkazu na registraci."""
        self.login_page.navigate()
        self.login_page.register_link.click()

        expect(page).to_have_url("http://testovani.kitner.cz/register")
        step("Ověřeno přesměrování na /register")

        expect(page.locator("[data-testid='name_input']")).to_be_visible()
        step("Ověřeno pole pro jméno na stránce registrace")

        expect(page.locator("[data-testid='register_button']")).to_be_visible()
        step("Ověřeno tlačítko 'Registrovat'")
