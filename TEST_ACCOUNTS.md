# Testovací účty a role

Dokumentace a přehled testovacích účtů pro aplikaci [http://testovani.kitner.cz](http://testovani.kitner.cz).

---

## 1. Lektor (Lector)
Účet s oprávněním pro **správu kurzů** (přidání kurzu, přidání termínu / iterace kurzu).

* **Login (Email):** `lector@lector.com`
* **Heslo:** `lector@lector.com`
* **Oprávnění:** Přidávání kurzů, správa termínů/iterací

---

## 2. Běžný student / registrovaný uživatel (Dynamic QA Tester)
Dynamicky generovaný / cachovaný účet uložený v `test_user.json`.

* **Login (Email):** Uložen v `test_user.json` (automaticky generován fixtures)
* **Heslo:** `Password123!`
* **Oprávnění:** Prohlížení kurzů, profil, běžný uživatel
