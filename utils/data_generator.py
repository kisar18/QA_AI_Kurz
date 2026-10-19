"""
Nezávislé pomocné utility pro dynamické generování testovacích dat.
Zajišťuje generování unikátních e-mailů, hesel, názvů kurzů a validních/nevalidních IČO.
"""

import random
import string
import uuid


def generate_random_string(length: int = 8) -> str:
    """Vygeneruje náhodný alfanumerický řetězec."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_random_email(prefix: str = "qa_user") -> str:
    """Vygeneruje unikátní platnou e-mailovou adresu."""
    uid = uuid.uuid4().hex[:8]
    return f"{prefix}_{uid}@example.com"


def generate_valid_ico() -> str:
    """
    Vygeneruje platné 8místné české IČO podle algoritmu modulo 11.
    Váhy pro prvních 7 číslic jsou [8, 7, 6, 5, 4, 3, 2].
    Kontrolní číslice k:
    zbytek = součet % 11
    pokud zbytek == 0: k = 1
    pokud zbytek == 1: k = 0
    jinak k = 11 - zbytek
    """
    weights = [8, 7, 6, 5, 4, 3, 2]
    first_7 = [random.randint(0, 9) for _ in range(7)]
    if first_7[0] == 0:
        first_7[0] = random.randint(1, 9)

    checksum = sum(d * w for d, w in zip(first_7, weights))
    remainder = checksum % 11

    if remainder == 0:
        check_digit = 1
    elif remainder == 1:
        check_digit = 0
    else:
        check_digit = 11 - remainder

    return "".join(map(str, first_7)) + str(check_digit)


def generate_invalid_ico() -> str:
    """Vrátí prokazatelně neplatné IČO (nevyhovující modulo 11 nebo špatný počet číslic)."""
    valid = generate_valid_ico()
    # Změníme poslední číslici tak, aby kontrolní součet neprošel
    last_digit = int(valid[-1])
    invalid_last = (last_digit + 1) % 10
    return valid[:-1] + str(invalid_last)


def generate_random_course_data() -> dict:
    """Vygeneruje data pro nový kurz s unikátním názvem."""
    uid = uuid.uuid4().hex[:6]
    return {
        "name": f"Automatizovaný kurz {uid}",
        "description": f"Testovací popis kurzu {uid} vytvořený přes automatizovaný E2E test.",
        "capacity": random.randint(5, 30),
        "price": random.randint(1000, 15000),
    }
