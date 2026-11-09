---
name: test-overview-generator
description: >-
  Aktivuj tento skill, když uživatel požaduje přehled, katalog, soupis nebo revizi automatizovaných testů,
  jejich kroků a kontrol, nebo přehled pokrytí User Stories a test casů v projektu (včetně HTML reportu).
---

# Test Overview & Coverage Generator Skill

Tento skill slouží k automatickému generování technického katalogu testů i přehledu pokrytí User Stories a test casů automatizovanými testy.

## Proces generování přehledu a pokrytí

1. **Spusť generátor:**
   Spusť generování přehledu i HTML reportu pokrytí jedním příkazem:
   ```powershell
   # Vygeneruje katalog testů (TEST_OVERVIEW.md) i HTML report pokrytí (reports/coverage_overview.html)
   python .agents/skills/test-overview-generator/scripts/generate_test_overview.py --html

   # Nebo samostatně pouze HTML report pokrytí User Stories:
   python .agents/skills/test-overview-generator/scripts/generate_coverage_report.py
   ```

2. **Automatická analýza a mapování požadavků na testy:**
   Skripty staticky analyzují projekt a provádí:
   - **User Stories:** Projdou `user stories/` a extrahují všechny User Stories (US-01 až US-20) a jejich akceptační kritéria (test casy).
   - **Testy:** Projdou `tests/` pomocí AST a extrahují kroky, kontroly a mapování na `US-xx`.
   - **Výpočet pokrytí:** Porovnají počet test casů a počet AT pro každou US a určí stav (🟢 Plně pokryto, 🟡 Částečně, 🔴 Nepokryto).
   - **Výstupy:** Vygenerují `TEST_OVERVIEW.md` (katalog testů) a `reports/coverage_overview.html` (interaktivní HTML přehled).

3. **Rozhodnutí, zda je hotovo (Definition of Done):**
   Spusť validační skript pro ověření stavu:
   ```powershell
   python .agents/skills/test-overview-generator/scripts/check_done.py
   ```
   - Ověřuje existenci, aktuálnost, konzistenci statistik, kvalitu testů i HTML report pokrytí.
   - Návratový kód: `0` = **HOTOVO**, `1` = **NENÍ HOTOVO** (přepínač `--fix` automaticky vše přegeneruje).

4. **Předání výsledku uživateli:**
   Informuj uživatele o výsledku rozhodnutí (`HOTOVO`), souhrnných metrikách (% pokrytých US, celkem TC a AT) a odkaž na vygenerované soubory `TEST_OVERVIEW.md` a `reports/coverage_overview.html`.
