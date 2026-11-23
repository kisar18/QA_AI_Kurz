"""Automatizované testy pro US-14: Vytvoření nového kurzu s kontrolou poměru stran obrázku.

Pokrývá test casy:
- [TC-US14-01] Úspěšné vytvoření kurzu lektorem s obrázkem v poměru 16:9
- [TC-US14-02] Validace povinných polí a číselných hodnot kapacity a ceny
- [TC-US14-03] Odmítnutí náhledového obrázku s nevyhovujícím poměrem stran
- [TC-US14-04] Zamezení přístupu k tvorbě kurzu pro zákazníka a nepřihlášeného hosta (RBAC)
- [TC-US14-05] Akceptace obrázku v rámci povolené 5% odchylky poměru stran
"""

import re
import uuid
from pathlib import Path
import pytest
from playwright.sync_api import Page, expect

from helpers.step_helpers import step
from pages.course_create_page import CourseCreatePage
from pages.courses_page import CoursesPage
from pages.login_page import LoginPage
from utils.image_generator import create_png_image


class TestCourseCreate:
    """Testovací sada pro vytváření nových kurzů lektorem dle US-14."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.course_create_page = CourseCreatePage(page)
        self.courses_page = CoursesPage(page)
        self.login_page = LoginPage(page)

    def _login_as_lector(self, page: Page, lector_user: dict):
        """Pomocná metoda pro přihlášení v roli lektora."""
        self.login_page.navigate()
        self.login_page.login(lector_user["email"], lector_user["password"])
        expect(page).to_have_url(f"{self.courses_page.base_url}/courses", timeout=10000)
        step("Uživatel přihlášen v roli lektora")

    def _login_as_customer(self, page: Page, registered_user: dict):
        """Pomocná metoda pro přihlášení v roli zákazníka."""
        self.login_page.navigate()
        self.login_page.login(registered_user["email"], registered_user["password"])
        expect(page).to_have_url(f"{self.courses_page.base_url}/courses", timeout=10000)
        step("Uživatel přihlášen v roli zákazníka")

    def test_tc_us14_01_create_course_success_with_16_9_image(
        self, page: Page, lector_user: dict, tmp_path: Path
    ):
        """[TC-US14-01] Úspěšné vytvoření kurzu lektorem s obrázkem v poměru 16:9."""
        valid_img = create_png_image(tmp_path / "course_16_9.png", width=1920, height=1080)
        unique_suffix = uuid.uuid4().hex[:6]
        course_name = f"Playwright Kurz {unique_suffix}"
        course_desc = "Kompletní kurz zaměřený na Playwright a Pytest od základů po CI/CD."

        self._login_as_lector(page, lector_user)
        self.course_create_page.navigate()
        expect(page).to_have_url(self.course_create_page.url)
        expect(self.course_create_page.heading).to_be_visible()
        step("Otevřen formulář pro vytvoření kurzu /courses/create")

        # Dialog nesmí nastat
        dialog_messages = []
        page.on("dialog", lambda d: (dialog_messages.append(d.message), d.accept()))

        self.course_create_page.create_course(
            name=course_name,
            description=course_desc,
            capacity=15,
            price=7500,
            image_path=str(valid_img.resolve()),
        )

        assert len(dialog_messages) == 0, f"Při nahrání validního 16:9 obrázku se zobrazil neočekávaný dialog: {dialog_messages}"

        # Očekává se přesměrování do katalogu kurzů
        expect(page).to_have_url(re.compile(r".*/courses/?$"), timeout=10000)
        step("Ověřeno úspěšné odeslání a přesměrování do přehledu kurzů")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Formulář postrádá klientskou i serverovou validaci povinných polí a ukládá prázdný kurz",
        strict=True,
    )
    def test_tc_us14_02_validation_of_required_fields_and_numeric_values(
        self, page: Page, lector_user: dict
    ):
        """[TC-US14-02] Validace povinných polí a číselných hodnot kapacity a ceny."""
        self._login_as_lector(page, lector_user)
        self.course_create_page.navigate()

        # Test A: Ponechání prázdných polí
        self.course_create_page.create_course(name="", description="", capacity="", price="")

        # Systém nesmí formulář uložit ani přesměrovat na /courses
        expect(page).to_have_url(self.course_create_page.url)
        step("Ověřeno, že prázdný formulář nebyl odeslán")

        # Test B: Neplatná kapacita (-5) a nečíselná cena
        self.course_create_page.create_course(
            name="Test Neplatná Data",
            description="Popis",
            capacity=-5,
            price="zdarma",
        )
        expect(page).to_have_url(self.course_create_page.url)
        step("Ověřeno, že záporná kapacita a nečíselná cena jsou odmítnuty")

    def test_tc_us14_03_rejection_of_image_with_invalid_aspect_ratio(
        self, page: Page, lector_user: dict, tmp_path: Path
    ):
        """[TC-US14-03] Odmítnutí náhledového obrázku s nevyhovujícím poměrem stran."""
        # Čtvercový obrázek 1:1 (výrazně mimo 16:9)
        square_img = create_png_image(tmp_path / "square_img.png", width=800, height=800)

        alert_messages = []

        def handle_dialog(dialog):
            alert_messages.append(dialog.message)
            dialog.accept()

        page.on("dialog", handle_dialog)

        self._login_as_lector(page, lector_user)
        self.course_create_page.navigate()

        # Vyplnění údajů a nahrání nevyhovujícího obrázku
        self.course_create_page.name_input.fill("Kurz s chybným obrázkem")
        self.course_create_page.description_input.fill("Popis kurzu")
        self.course_create_page.capacity_input.fill("10")
        self.course_create_page.price_input.fill("5000")
        self.course_create_page.image_input.set_input_files(str(square_img.resolve()))

        # Systém vymaže input po detekci nesprávného poměru stran
        expect(self.course_create_page.image_input).to_have_value("")

        assert any("správný poměr stran" in msg for msg in alert_messages), (
            f"Očekávané varovné hlášení o poměru stran nebylo zobrazeno: {alert_messages}"
        )
        step("Ověřeno zamítnutí obrázku s poměrem stran 1:1 a zobrazení varovného alertu")

    @pytest.mark.xfail(
        reason="Defekt aplikace (RBAC): Zákazník má neomezený přístup na formulář /courses/create",
        strict=True,
    )
    def test_tc_us14_04_prevention_of_course_creation_for_customer_and_guest_rbac(
        self, page: Page, registered_user: dict
    ):
        """[TC-US14-04] Zamezení přístupu k tvorbě kurzu pro zákazníka a nepřihlášeného hosta (RBAC)."""
        # 1. Zákazník: nesmí vidět tlačítko pro přidání kurzu a nesmí mít přístup na /courses/create
        self._login_as_customer(page, registered_user)
        self.courses_page.navigate()
        expect(self.courses_page.add_course_button).not_to_be_visible()
        step("Ověřeno, že zákazník nevidí v přehledu tlačítko 'Přidat kurz'")

        self.course_create_page.navigate()
        # Zákazník musí být odmítnut (přesměrován nebo 403)
        expect(self.course_create_page.heading).not_to_be_visible()
        step("Ověřeno, že zákazník nemá přístup k formuláři vytvoření kurzu")

        # 2. Nepřihlášený host: přímý přístup na /courses/create
        page.context.clear_cookies()
        self.course_create_page.navigate()
        expect(self.course_create_page.heading).not_to_be_visible()
        step("Ověřeno, že nepřihlášený host nemá přístup k formuláři vytvoření kurzu")

    @pytest.mark.xfail(
        reason="Defekt aplikace: Kontrola poměru stran používá chybný vzorec Math.abs(g-w) < 0.05 místo relativní 5% tolerance, takže odmítá obrázek 1280x750 s relativní odchylkou ~4 %",
        strict=True,
    )
    def test_tc_us14_05_acceptance_of_image_within_5_percent_aspect_ratio_tolerance(
        self, page: Page, lector_user: dict, tmp_path: Path
    ):
        """[TC-US14-05] Akceptace obrázku v rámci povolené 5% odchylky poměru stran."""
        # 1280x750 = ~1.707 (16:9 = 1.778, odchylka ~4.0 %, což je v toleranci do 5 %)
        tolerated_img = create_png_image(tmp_path / "tolerated_img.png", width=1280, height=750)

        alert_messages = []

        def handle_dialog(dialog):
            alert_messages.append(dialog.message)
            dialog.accept()

        page.on("dialog", handle_dialog)

        self._login_as_lector(page, lector_user)
        self.course_create_page.navigate()

        self.course_create_page.image_input.set_input_files(str(tolerated_img.resolve()))
        # Obrázek musí zůstat nastaven v inputu
        expect(self.course_create_page.image_input).not_to_have_value("")

        assert len(alert_messages) == 0, (
            f"Pro obrázek v toleranci 5 % se neměl zobrazit žádný varovný alert: {alert_messages}"
        )
        step("Ověřeno, že obrázek v toleranci do 5 % odchylky byl úspěšně akceptován")
