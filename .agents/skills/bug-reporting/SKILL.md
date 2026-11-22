---
name: bug-reporting
description: >-
  Aktivuj tento skill, když je požadováno spuštění automatizovaných testů, identifikace chyb
  a vytvoření přehledného HTML reportu pro všechny padající testy se všemi povinnými poli
  (kroky k reprodukci, očekávaný a skutečný výsledek, prostředí a odkaz na screenshot/trace).
---

# Pracovní postup: Běh testů -> Analýza chyb -> HTML Bug Report

Tento skill slouží k automatizovanému spuštění testů, zachycení důkazních materiálů (screenshotů a traces) a vygenerování standardizovaného HTML přehledu vad (`reports/bug_overview.html`).

Kvalita a úplnost výstupu je **striktně vynucena hookem `Stop`**: agent nemůže ukončit práci, dokud není přehled vygenerován a neobsahuje kompletní report pro každý padající test.

---

## Povinná pole každého bug reportu
Každý zaznamenaný pád testu musí v reportu obsahovat:
1. **Kroky k reprodukci** (`steps_to_reproduce`): Číslovaný seznam konkrétních kroků vedoucích k chybě.
2. **Očekávaný výsledek** (`expected_result`): Přesný popis správného chování dle specifikace.
3. **Skutečný výsledek** (`actual_result`): Konkrétní chybové chování aplikace (např. chybová hláška, timeout).
4. **Prostředí** (`environment`): Operační systém, prohlížeč, URL testované aplikace.
5. **Odkaz na důkaz** (`evidence`): Relativní cesta k existujícímu souboru screenshotu (`.png`) nebo Playwright trace (`.zip`) v `reports/evidence/`.

> [!WARNING]
> Zákaz placeholderů typu `TODO`, `TBD`, `DOPLNIT`, `N/A`. Hook `Stop` kontroluje skutečný obsah a tyto zástupné texty odmítne!

---

## Pracovní postup v krocích

1. **Spuštění testovací sady se sběrem důkazů:**
   Spusť runner, který zajistí uložení screenshotů/traces při pádu:
   ```powershell
   python .agents/skills/bug-reporting/scripts/run_tests_with_evidence.py
   ```
   *Výstup:* Vznikne `reports/test_run_data.json` a výchozí návrh `reports/bug_reports.json`.

2. **Analýza pádů a doplnění bug reportů:**
   - Prohlédni nalezené pády v `reports/test_run_data.json`.
   - Zkontroluj a upřesni `reports/bug_reports.json` pro každý padající test:
     - Zkontroluj kroky k reprodukci (aby byly jasné a lidsky čitelné).
     - Upřesni očekávaný a skutečný výsledek.
     - Ověř, že soubor v poli `evidence` skutečně existuje v `reports/evidence/`.

3. **Vygenerování HTML přehledu chyb:**
   Vygeneruj vizuální a strojově validovatelný přehled:
   ```powershell
   python .agents/skills/bug-reporting/scripts/generate_bug_overview.py
   ```
   *Výstup:* Vytvoří se `reports/bug_overview.html`.

4. **Předběžná kontrola Definice hotovo (DoD):**
   Spusť ověřovací skript:
   ```powershell
   python .agents/skills/bug-reporting/scripts/verify_bug_reports.py
   ```
   - Pokud skript skončí s kódem `0` (`HOTOVO`), můžeš práci ukončit a předat uživateli.
   - Pokud skončí s kódem `1` (`NENÍ HOTOVO`), oprav hlášené nedostatky. Jinak tě hook `Stop` nepustí odpověď dokončit.

5. **Předání výsledku uživateli:**
   Uživateli sděl souhrnné statistiky (počet testů celkem, úspěšných a selhaných) a předej klikací odkaz na vygenerovaný soubor [reports/bug_overview.html](file:///c:/Users/marti/Documents/VyvojAplikaci/QA_AI_kurz/Lekce1/reports/bug_overview.html).
