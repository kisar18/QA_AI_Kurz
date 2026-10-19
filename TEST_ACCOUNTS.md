# Testovací účty a role

Dokumentace a přehled testovacích účtů pro aplikaci [http://testovani.kitner.cz](http://testovani.kitner.cz).

---

## 1. Lektor (Lector)
Účet s oprávněním pro **správu kurzů** (přidání kurzu, přidání termínu / iterace kurzu).

* **Datový soubor:** [`data/lector_user.json`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/data/lector_user.json)
* **Login (Email):** `lector@lector.com`
* **Heslo:** `lector@lector.com`
* **Oprávnění:** Přidávání kurzů, správa termínů/iterací
* **Pytest fixture:** `lector_user` v [`tests/conftest.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/conftest.py)

---

## 2. Běžný student / registrovaný uživatel (Dynamic QA Tester)
Dynamicky generovaný / cachovaný účet uložený v [`data/test_user.json`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/data/test_user.json).

* **Datový soubor:** [`data/test_user.json`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/data/test_user.json)
* **Login (Email):** Uložen v `data/test_user.json` (automaticky generován / ověřen fixture)
* **Heslo:** `Password123!`
* **Oprávnění:** Prohlížení kurzů, zápis na kurz, profil klienta
* **Pytest fixture:** `registered_user` v [`tests/conftest.py`](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/tests/conftest.py)
