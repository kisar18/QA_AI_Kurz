import re
import base64
import json
import os
import uuid
import pytest
from playwright.sync_api import Browser
from pytest_html import extras
from pages.register_page import RegisterPage

CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_user.json")


@pytest.fixture(scope="session")
def registered_user(browser: Browser) -> dict:
    """
    Vrátí existující uložené testovací údaje z test_user.json.
    Pokud soubor neexistuje, automaticky zaregistruje nového uživatele a údaje uloží.
    """
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "email" in data and "password" in data:
                    return data
        except Exception:
            pass

    # Registrace nového uživatele
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "name": f"QA Tester {unique_id}",
        "email": f"qa_auto_{unique_id}@example.com",
        "password": "Password123!",
    }

    page = browser.new_page()
    reg_page = RegisterPage(page)
    reg_page.navigate()
    reg_page.register(
        name=user_data["name"],
        email=user_data["email"],
        password=user_data["password"],
        password_again=user_data["password"],
    )
    page.wait_for_url("**/home")
    page.wait_for_load_state("networkidle")
    page.close()

    # Uložení údajů pro další běhy
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2, ensure_ascii=False)

    return user_data


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook zachytí výsledek testu a při selhání automaticky pořídí screenshot obrazovky
    a přiloží jej do HTML reportu.
    """
    outcome = yield
    report = outcome.get_result()

    if not hasattr(report, "extras"):
        report.extras = []

    # Screenshot a vyčištění chybového výpisu pouze pokud test selže ve fázi samotného provádění ('call')
    if report.when == "call" and report.failed:
        # 1. Zkrácení chybového výpisu – odstranění dlouhého Aria snapshotu
        if report.longrepr:
            longrepr_str = str(report.longrepr)
            if "Aria snapshot:" in longrepr_str:
                cleaned_str = re.sub(
                    r"(\n\s*(?:E\s+)?)Aria snapshot:[\s\S]*?(?=\n(?:tests[\\/]|\w+.*\.py:\d+:|\S+\.py|\Z))",
                    "",
                    longrepr_str,
                )
                report.longrepr = cleaned_str

        # 2. Získání instance page z fixture nebo z testovací třídy a pořízení screenshotu
        page = item.funcargs.get("page")
        if not page and hasattr(item, "instance"):
            if hasattr(item.instance, "page"):
                page = getattr(item.instance, "page")
            elif hasattr(item.instance, "login_page") and hasattr(item.instance.login_page, "page"):
                page = getattr(item.instance.login_page, "page")
            elif hasattr(item.instance, "register_page") and hasattr(item.instance.register_page, "page"):
                page = getattr(item.instance.register_page, "page")

        if page:
            try:
                screenshot_bytes = page.screenshot(full_page=True)
                encoded = base64.b64encode(screenshot_bytes).decode("utf-8")
                report.extras.append(extras.png(encoded, name="Failure Screenshot"))
            except Exception as e:
                print(f"\n[Screenshot Error] Nepodařilo se pořídit screenshot: {e}")


def pytest_html_results_summary(prefix, summary, postfix):
    """
    Vloží do HTML reportu plnohodnotný Lightbox modal pro pohodlné zobrazení screenshotů
    v plné velikosti po kliknutí (včetně možnosti otevření na nové záložce).
    """
    lightbox_code = """
    <div id="screenshot-lightbox" class="lightbox-modal hidden">
        <div class="lightbox-backdrop"></div>
        <div class="lightbox-content">
            <div class="lightbox-header">
                <span class="lightbox-title">📸 Failure Screenshot (Full Size)</span>
                <div class="lightbox-actions">
                    <button id="lightbox-open-tab-btn" class="lightbox-btn" type="button">Otevřít na nové záložce ↗</button>
                    <button id="lightbox-close-btn" class="lightbox-btn lightbox-close-btn" type="button">✕ Zavřít</button>
                </div>
            </div>
            <div class="lightbox-body">
                <img id="lightbox-img" src="" alt="Screenshot" />
            </div>
        </div>
    </div>
    <script>
    (function() {
        function initLightbox() {
            var modal = document.getElementById('screenshot-lightbox');
            if (!modal) return;
            var imgEl = document.getElementById('lightbox-img');
            var closeBtn = document.getElementById('lightbox-close-btn');
            var openTabBtn = document.getElementById('lightbox-open-tab-btn');
            var backdrop = modal.querySelector('.lightbox-backdrop');

            function closeModal() {
                modal.classList.add('hidden');
                imgEl.src = '';
            }

            closeBtn.addEventListener('click', closeModal);
            backdrop.addEventListener('click', closeModal);
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') closeModal();
            });

            openTabBtn.addEventListener('click', function() {
                if (!imgEl.src) return;
                fetch(imgEl.src)
                    .then(function(res) { return res.blob(); })
                    .then(function(blob) {
                        var blobUrl = URL.createObjectURL(blob);
                        window.open(blobUrl, '_blank');
                    })
                    .catch(function() {
                        var w = window.open('');
                        if (w) {
                            w.document.write('<img src="' + imgEl.src + '" style="max-width:100%; height:auto;" />');
                        }
                    });
            });

            // Zachytí kliknutí na náhled screenshotu ještě před výchozím window.open
            document.addEventListener('click', function(e) {
                var target = e.target;
                if (target.tagName === 'IMG' && target.closest('.media-container__viewport')) {
                    e.stopImmediatePropagation();
                    e.preventDefault();
                    imgEl.src = target.src;
                    modal.classList.remove('hidden');
                }
            }, true);
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initLightbox);
        } else {
            initLightbox();
        }
    })();
    </script>
    """
    postfix.append(lightbox_code)


