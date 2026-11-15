import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage
from pages.my_courses_page import MyCoursesPage
from helpers.step_helpers import step


class TestUserProfile:
    """Testovací sada pro profil klienta (/profile) dle specifikace US-18."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)
        self.profile_page = ProfilePage(page)

    def _login(self, page: Page, user: dict):
        self.login_page.navigate()
        self.login_page.login(user["email"], user["password"])
        expect(page).to_have_url(f"{self.login_page.base_url}/courses")

    def test_tc_us18_01_prefilled_data_and_successful_update(self, page: Page, registered_user: dict):
        """[TC-US18-01] Předvyplnění existujících údajů a úspěšná aktualizace profilu."""
        self._login(page, registered_user)
        self.profile_page.navigate()

        expect(self.profile_page.heading).to_be_visible()
        expect(self.profile_page.heading).to_have_text("Profil")
        step("Ověřen nadpis 'Profil'")

        # Kontrola předvyplnění aktuálních dat uživatele (AC-1)
        expect(self.profile_page.name_input).to_be_visible()
        expect(self.profile_page.name_input).not_to_have_value("")
        step("Ověřeno, že pole pro jméno je předvyplněno aktuální hodnotou")

        expect(self.profile_page.email_input).to_be_visible()
        expect(self.profile_page.email_input).to_have_value(registered_user["email"])
        step(f"Ověřen předvyplněný e-mail: {registered_user['email']}")

        expect(self.profile_page.phone_input).to_be_visible()
        step("Ověřeno pole pro telefon")

        expect(self.profile_page.ico_input).to_be_visible()
        step("Ověřeno pole pro IČO")

        expect(self.profile_page.save_button).to_be_visible()
        step("Ověřeno tlačítko 'Uložit'")

        # Aktualizace na nové platné údaje (AC-3, AC-6)
        import uuid
        updated_name = f"QA Tester {uuid.uuid4().hex[:6]}"
        valid_phone = "+420777123456"
        valid_ico = "27082440"  # Platné IČO s kontrolním součtem modulo 11

        self.profile_page.update_profile(name=updated_name, phone=valid_phone, ico=valid_ico)

        expect(page).to_have_url(f"{self.profile_page.base_url}/home")
        step("Ověřeno přesměrování na /home po úspěšném uložení profilu (AC-6)")

        # Ověření perzistence změn
        self.profile_page.navigate()
        expect(self.profile_page.name_input).to_have_value(updated_name)
        expect(self.profile_page.phone_input).to_have_value(valid_phone)
        expect(self.profile_page.ico_input).to_have_value(valid_ico)
        step("Ověřena perzistence aktualizovaných údajů po znovunačtení profilu")

    def test_tc_us18_02_email_format_and_empty_email_validation(self, page: Page, registered_user: dict):
        """[TC-US18-02] Validace povinných polí jména a e-mailu a kontrola formátu e-mailu - neplatný e-mail."""
        self._login(page, registered_user)
        self.profile_page.navigate()

        # Neplatný formát e-mailu
        self.profile_page.update_profile(email="email-bez-zavinace")
        expect(page).to_have_url(f"{self.profile_page.base_url}/profile")
        expect(self.profile_page.email_error).to_be_visible()
        expect(self.profile_page.email_error).to_have_text(self.profile_page.EMAIL_ERROR_TEXT)
        step("Ověřeno odmítnutí neplatného formátu e-mailu a zobrazení chybové hlášky")

        # Prázdný e-mail (povinné pole dle AC-2)
        self.profile_page.update_profile(email="")
        expect(page).to_have_url(f"{self.profile_page.base_url}/profile")
        expect(self.profile_page.email_error).to_be_visible()
        step("Ověřeno odmítnutí prázdného pole e-mailu")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Chybí klientská validace povinného pole Jméno; aplikace při prázdném jménu chybně přesměruje na /home i přes 422 z backendu",
        strict=False,
    )
    def test_tc_us18_02_mandatory_name_validation(self, page: Page, registered_user: dict):
        """[TC-US18-02] Validace povinných polí jména a e-mailu a kontrola formátu e-mailu - prázdné jméno."""
        self._login(page, registered_user)
        self.profile_page.navigate()

        self.profile_page.update_profile(name="")

        expect(page).to_have_url(f"{self.profile_page.base_url}/profile")
        expect(self.profile_page.name_error).to_be_visible()
        step("Ověřeno zamezení uložení formuláře s prázdným jménem a zobrazení chybové hlášky")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Při pokusu o uložení obsazeného e-mailu jiného uživatele frontend chybně přesměruje na /home místo zobrazení chybové hlášky na /profile",
        strict=False,
    )
    def test_tc_us18_03_duplicate_email_collision(self, page: Page, registered_user: dict, lector_user: dict):
        """[TC-US18-03] Zamezení změny e-mailu na adresu již obsazenou jiným uživatelem."""
        self._login(page, registered_user)
        self.profile_page.navigate()

        # Pokus o změnu na e-mail existujícího uživatele B (lektor)
        self.profile_page.update_profile(email=lector_user["email"])

        expect(page).to_have_url(f"{self.profile_page.base_url}/profile")
        expect(self.profile_page.email_collision_error).to_be_visible()
        step("Ověřeno odmítnutí duplicitního e-mailu a zobrazení validační hlášky")

    def test_tc_us18_04_invalid_ico_validation(self, page: Page, registered_user: dict):
        """[TC-US18-04] Validace formální platnosti IČO pomocí kontrolního součtu na profilu."""
        self._login(page, registered_user)
        self.profile_page.navigate()

        # Neplatné IČO s nevyhovujícím kontrolním součtem
        self.profile_page.update_profile(phone="+420777123456", ico="12345678")

        expect(page).to_have_url(f"{self.profile_page.base_url}/profile")
        step("Ověřeno, že formulář se neodeslal a stránka zůstává na /profile")

        expect(self.profile_page.ico_error).to_be_visible()
        expect(self.profile_page.ico_error).to_have_text(self.profile_page.ICO_ERROR_TEXT)
        step("Ověřena validační hláška 'Neplatné IČO'")

    def test_tc_us18_05_invalid_phone_validation(self, page: Page, registered_user: dict):
        """[TC-US18-05] Validace formátu telefonního čísla na profilu."""
        self._login(page, registered_user)
        self.profile_page.navigate()

        # Neplatný telefon s platným IČO
        self.profile_page.update_profile(phone="12", ico="27082440")

        expect(page).to_have_url(f"{self.profile_page.base_url}/profile")
        step("Ověřeno, že formulář se neodeslal při neplatném telefonu")

        expect(self.profile_page.phone_error).to_be_visible()
        expect(self.profile_page.phone_error).to_have_text(self.profile_page.PHONE_ERROR_TEXT)
        step("Ověřena validační hláška 'Neplatné telefonní číslo'")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Klientská validace IČO a telefonu nepovoluje prázdné hodnoty a brání smazání nepovinných polí (AC-3)",
        strict=False,
    )
    def test_tc_us18_06_clear_optional_ico_and_phone(self, page: Page, registered_user: dict):
        """[TC-US18-06] Úspěšné uložení profilu s vymazáním nepovinných údajů (IČO a telefon)."""
        self._login(page, registered_user)
        self.profile_page.navigate()

        # Vymazání doplňkových nepovinných údajů (AC-3)
        self.profile_page.update_profile(ico="", phone="")

        expect(page).to_have_url(f"{self.profile_page.base_url}/home")
        step("Ověřeno přesměrování po vymazání nepovinných údajů")

        self.profile_page.navigate()
        expect(self.profile_page.ico_input).to_have_value("")
        expect(self.profile_page.phone_input).to_have_value("")
        step("Ověřeno, že doplňkové údaje IČO a telefon jsou na profilu prázdné")

    def test_profile_unauthenticated_access_denied(self, page: Page):
        """Ověření, že bez přihlášení není formulář profilu zobrazen."""
        self.profile_page.navigate()

        expect(self.profile_page.name_input).not_to_be_visible()
        expect(self.profile_page.heading).not_to_be_visible()
        step("Ověřeno, že nepřihlášený uživatel nemá přístup k datům profilu")


class TestMyCourses:
    """Testovací sada pro sekci zapsaných kurzů zákazníka (/my-courses) – US-13."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.login_page = LoginPage(page)
        self.my_courses_page = MyCoursesPage(page)

    def _login(self, page: Page, user: dict):
        self.login_page.navigate()
        self.login_page.login(user["email"], user["password"])
        expect(page).to_have_url(f"{self.login_page.base_url}/courses")

    def test_my_courses_page_display(self, page: Page, registered_user: dict):
        """Ověření načtení stránky zapsaných kurzů přihlášeného klienta (/my-courses)."""
        self._login(page, registered_user)
        self.my_courses_page.navigate()

        expect(page).to_have_url(f"{self.login_page.base_url}/my-courses")
        step("Ověřena URL /my-courses")

        expect(self.my_courses_page.title).to_be_visible()
        expect(self.my_courses_page.title).to_have_text("Mé zapsané kurzy")
        step("Ověřen nadpis sekce 'Mé zapsané kurzy'")

        expect(self.my_courses_page.courses_section).to_be_visible()
        step("Ověřena sekce pro zobrazení kurzů uživatele")
