"""
Centrální konfigurace prostředí pro testovací projekt.
Všechny globální nastavení (URL, timeouty, browser options) jsou definovány zde.
"""

import os

# -------------------------------------------------------------------
# Základní URL testované aplikace
# Lze přepsat proměnnou prostředí BASE_URL (pro CI/CD nebo jiná prostředí)
# -------------------------------------------------------------------
BASE_URL: str = os.getenv("BASE_URL", "http://testovani.kitner.cz").rstrip("/")

# -------------------------------------------------------------------
# Nastavení prohlížeče
# -------------------------------------------------------------------
HEADLESS: bool = os.getenv("HEADLESS", "true").lower() in ("true", "1", "yes")
BROWSER_SLOWMO: int = int(os.getenv("BROWSER_SLOWMO", "0"))

# -------------------------------------------------------------------
# Časové limity (ms)
# -------------------------------------------------------------------
DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30000"))  # timeout pro lokátory
NETWORK_IDLE_TIMEOUT: int = 10_000                                 # timeout pro wait_for_load_state

# -------------------------------------------------------------------
# Cesty k datovým souborům a výstupům
# -------------------------------------------------------------------
ROOT_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR: str = os.path.join(ROOT_DIR, "data")
REPORTS_DIR: str = os.path.join(ROOT_DIR, "reports")
CREDENTIALS_FILE: str = os.path.join(DATA_DIR, "test_user.json")
LECTOR_CREDENTIALS_FILE: str = os.path.join(DATA_DIR, "lector_user.json")
INVALID_EMAILS_FILE: str = os.path.join(DATA_DIR, "invalid_emails.json")
