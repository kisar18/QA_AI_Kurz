import logging

logger = logging.getLogger("QA_STEP")


def step(message: str):
    """Vypíše a zaloguje kontrolní krok/assert do testovacího výstupu."""
    print(f"\n   [ASSERT OK] {message}")
    logger.info(f"[ASSERT OK] {message}")
