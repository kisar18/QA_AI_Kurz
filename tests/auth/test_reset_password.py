import pytest
from playwright.sync_api import Page, expect
from pages.reset_password_page import ResetPasswordPage


class TestResetPassword:
    """Testovací sada pro dokončení změny hesla pomocí tokenu (US-06)."""

    def test_reset_password_form_elements_present(self, page: Page):
        """Ověření, že stránka pro reset hesla obsahuje všechny formulářové prvky."""
        reset_page = ResetPasswordPage(page)
        reset_page.open_with_token(token="sample-test-token", email="test@example.com")

        expect(reset_page.section).to_be_visible()
        expect(reset_page.password_input).to_be_visible()
        expect(reset_page.password_again_input).to_be_visible()
        expect(reset_page.submit_button).to_be_visible()
        expect(reset_page.submit_button).to_have_text("Změnit heslo")

    def test_reset_password_passwords_mismatch(self, page: Page):
        """Ověření zobrazení validační chyby při zadání neshodujících se hesel."""
        reset_page = ResetPasswordPage(page)
        reset_page.open_with_token(token="sample-test-token", email="test@example.com")

        reset_page.reset_password("Secret123!", "Different123!")

        expect(reset_page.password_error).to_be_visible()
        expect(reset_page.password_error).to_contain_text("password field confirmation does not match")

    def test_reset_password_invalid_token_rejected(self, page: Page, registered_user: dict):
        """Ověření odmítnutí neplatného tokenu pro existujícího uživatele."""
        reset_page = ResetPasswordPage(page)
        reset_page.open_with_token(token="invalid-expired-token", email=registered_user["email"])

        with page.expect_response(lambda r: "/reset-password" in r.url and r.status == 422) as response_info:
            reset_page.reset_password("NewPassword123!", "NewPassword123!")

        resp = response_info.value
        body = resp.json()
        assert "password reset token is invalid" in body.get("message", "").lower() or any(
            "invalid" in err.lower() for err_list in body.get("errors", {}).values() for err in err_list
        )
