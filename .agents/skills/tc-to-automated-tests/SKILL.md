---
name: tc-to-automated-tests
description: >-
  Aktivuj tento skill, když uživatel požaduje převod schválených test casů (např. z manual_tests/TC_*.md)
  do automatizovaných Playwright + pytest testů, revizi a ověření kvality generovaných testů,
  nebo spuštění skriptu Definice hotovo (DoD) pro automatizované testy.
---

# Pracovní postup: Schválené Test Casy -> Automatizované Testy

Tento skill definuje standardizovaný proces převodu schválených manuálních test casů (TC) do automatizovaných E2E testů (Playwright + pytest) s Page Object Modelem.

Proces je striktně řízen **6 pojistkami proti falešnému hotovo**: o výsledku nerozhoduje tvrzení modelu, ale deterministický skript, testy musí projít 3× za sebou a v případě nepřekonatelné překážky má agent povinnost nahlásit stav `BLOKOVÁNO`.

---

## Tři stavy výsledku procesu

| Stav | Návratový kód | Popis |
| :--- | :---: | :--- |
| **`HOTOVO`** | `0` | Všechny TC mají implementovaný test, audit lokátorů/assertů je čistý, testy prošly **3× po sobě** v pytestu a QA schválilo kód. |
| **`NENÍ HOTOVO`** | `1` | Chybí některý test case, v testu jsou inline lokátory či `time.sleep`, nebo test v některém z běhů selhal. Agent musí chyby opravit a spustit ověření znovu. |
| **`BLOKOVÁNO`** | - | V UI chybí prvek, nelze vytvořit jednoznačný lokátor bez porušení pravidel, chybí data nebo padá backend. **Agent nesmí překážku obcházet mockem ani křehkým selektorem.** Zastaví práci a popíše blokaci člověku. |

---

## Pracovní postup v krocích

| Krok | Název kroku | Kdo dělá | Vstup | Výstup | Popis činnosti & Pojistka |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Příprava vstupů & Analýza** | **Uživatel + Agent** | Schválené TC (`manual_tests/TC_*.md`) | Mapa mapování (TC ID -> testy, POM) | Uživatel zadá zdrojové TC. Agent analyzuje existující POM třídy v `pages/`, fixtures a data v `data/`. Pokud chybí prostředí nebo data, hlásí `BLOKOVÁNO`. |
| **2** | **Příprava Page Objectů** | **Agent** | Chybějící prvky z analýzy | Upravené POM v `pages/` (nebo `BLOKOVÁNO`) | Doplnění lokátorů/metod. **Pojistka:** Žádný XPath, `:nth-child` ani CSS třídy. Chybí-li `data-testid` a nelze zacílit čistě dle skillu `locator-strategy`, ohlásí `BLOKOVÁNO`. |
| **3** | **Generování testů** | **Agent** | Schválené TC + POM + `tests/AGENTS.md` | Soubor `tests/<oblast>/test_*.py` | Implementace testů 1:1 pro každý TC. Každý test obsahuje v docstringu ID (např. `[TC-US02-01]`), logování `step()` a web-first `expect()`. |
| **4** | **Nezávislý audit lokátorů a assertů** | **Nezávislý AI Kontrolor (Čistý kontext)** | Kód v `pages/` a `tests/` + zdrojové TC | Seznam nálezů (co chybí, slabiny) | **Pojistka čistého kontextu:** Kontrola neprobíhá s historií chatu. Kontrolor dostane pouze kód a TC s otázkou: *"Co v testech chybí, jaké chyby se mohou zamaskovat a kde chybí asserty?"*. |
| **5** | **Skript "Definice hotovo"** | **Agent** | Soubor TC + testovací soubor | Protokol DoD skriptu (Exit 0/1) | **Pojistka stroje:** Spuštění `verify_automated_tests.py`. Skript ověří: 100% pokrytí TC, Zero-Inline-Locators v testech, zákaz pevných sleepů a **3× úspěšný běh v pytestu**. |
| **6** | **Review & Akceptace** | **Uživatel (QA)** | Výstup DoD (PASS) + pytest report + kód | Schválení k merge | Uživatel provede závěrečnou kontrolu a schválí začlenění kódu. |
| **7** | **Commit** | **Agent + Uživatel** | Schválený kód | Git commit | Agent vytvoří commit dle pravidel repozitáře (nikdy necommitovat `.env` ani složku `reports/`). |

---

## Pravidla tvorby automatizovaných testů
1. **Párování s TC:** Každá testovací funkce musí v docstringu obsahovat přesné ID test casu (např. `"""[TC-US02-01] Úspěšná registrace..."""`).
2. **Zero-Inline-Locators:** V souborech v `tests/` nesmí být `page.locator()`, `page.get_by_*()` ani `xpath=`. Všechny selektory patří do `pages/`.
3. **Žádná pevná čekání:** Přísný zákaz `time.sleep()` i `page.wait_for_timeout()`. Využívat výhradně auto-retrying web-first `expect(locator)...`.
4. **Zákaz oslabování assertů:** Vždy ověřovat kompletní post-conditions a chybové stavy. Zákaz `assert locator.is_visible()`.
5. **Read-Only ochrana:** Agent nesmí svévolně upravovat validační skript ani soubor se schválenými TC.

---

## Spuštění skriptu "Definice hotovo" (Krok 5)

Před předáním práce uživateli agent **vždy** spustí kontrolní skript:

```powershell
python .agents/skills/tc-to-automated-tests/scripts/verify_automated_tests.py --tc-file manual_tests/TC_<ID>.md --test-file tests/<oblast>/test_<tema>.py --runs 3
```

- **Exit code 0 (`HOTOVO`):** Všechna TC jsou pokryta, kód splňuje pravidla projektu a testy 3× po sobě prošly.
- **Exit code 1 (`NENÍ HOTOVO`):** Skript vypíše nalezené chyby. Agent musí nedostatky opravit a skript spustit znovu.

