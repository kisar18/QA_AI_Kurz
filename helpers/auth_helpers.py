"""
Sdílené akce pro autentizaci uživatelů (přihlášení, registrace, odhlášení).
Zapouzdřuje opakující se byznysové kroky pro testy.
"""

from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.register_page import RegisterPage


def login_user(page: Page, email: str, password: str) -> LoginPage:
    """Provede kompletní přihlášení uživatele a počká na načtení."""
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(email, password)
    page.wait_for_load_state("networkidle")
    return login_page


def register_user(page: Page, name: str, email: str, password: str) -> RegisterPage:
    """Provede registraci nového uživatele."""
    register_page = RegisterPage(page)
    register_page.navigate()
    register_page.register(name=name, email=email, password=password, password_again=password)
    page.wait_for_load_state("networkidle")
    return register_page


def logout_user(page: Page):
    """Odhlásí aktuálně přihlášeného uživatele."""
    login_page = LoginPage(page)
    login_page.logout()
