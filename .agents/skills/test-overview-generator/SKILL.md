---
name: test-overview-generator
description: >-
  Aktivuj a použij tento skill v následujících situacích:
  1. Tvorba, aktualizace nebo generování katalogu automatizovaných testů (TEST_OVERVIEW.md) a přehledu pokrytí (docs/coverage_overview.html).
  2. Audit a revize pokrytí User Stories a manuálních test casů automatizovanými testy (Traceability Matrix).
  3. Ověření stavu Definition of Done (check_done.py) pro přehledy testů, 1:1 mapování a Zero-Unmapped-Tests.
---

# Test Overview & Coverage Generator Skill

Tento skill slouží k automatickému generování technického katalogu testů i přehledu pokrytí User Stories a test casů automatizovanými testy.

## Proces generování přehledu a pokrytí

1. **Spusť generátor:**
   Spusť generování přehledu i HTML reportu pokrytí jedním příkazem:
   ```powershell
   # Vygeneruje katalog testů (TEST_OVERVIEW.md) i HTML report pokrytí (docs/coverage_overview.html)
   python .agents/skills/test-overview-generator/scripts/generate_test_overview.py --html

   # Nebo samostatně pouze HTML report pokrytí schválených Test Casů (z manual_tests/):
   python .agents/skills/test-overview-generator/scripts/generate_coverage_report.py
   ```

2. **Automatická analýza a mapování testů (čistě na manuální test casy):**
   Skripty staticky analyzují projekt a provádí:
   - **Manuální Test Casy:** Projdou výhradně `manual_tests/` a extrahují všechny schválené manuální Test Casy (`[TC-USxx-yy]`). Mapování se neprovádí proti obecným akceptačním kritériím, ale striktně proti konkrétním manuálním scénářům.
   - **Testy:** Projdou `tests/` pomocí AST a extrahují kroky, kontroly a párují testy přímo na konkrétní `[TC-USxx-yy]`.
   - **Výpočet pokrytí:** Porovná stav pokrytí pro každý jednotlivý manuální Test Case (🟢 Pokryto / 🔴 Nepokryto) a pro každou User Story (podíl pokrytých manuálních TC).
   - **Výstupy:** Vygenerují `TEST_OVERVIEW.md` (katalog testů) a `docs/coverage_overview.html` (Traceability Matrix: manuální TC ➔ automatizované testy).

3. **Rozhodnutí, zda je hotovo (Definition of Done):**
   Spusť validační skript pro ověření stavu:
   ```powershell
   python .agents/skills/test-overview-generator/scripts/check_done.py
   ```
   - Ověřuje existenci, aktuálnost, konzistenci statistik, kvalitu testů, **100% pokrytí schválených manuálních TC** i HTML report pokrytí (`docs/coverage_overview.html`).
   - Návratový kód: `0` = **HOTOVO**, `1` = **NENÍ HOTOVO** (přepínač `--fix` automaticky vše přegeneruje).

4. **Předání výsledku uživateli:**
   Informuj uživatele o výsledku rozhodnutí (`HOTOVO`), souhrnných metrikách (% pokrytých US, celkem TC a AT) a odkaž na vygenerované soubory `TEST_OVERVIEW.md` a `docs/coverage_overview.html`.
