---
name: ust-to-manual-tc
description: >-
  Aktivuj tento skill, když uživatel požaduje vytvoření manuálních test casů z User Story (UST),
  analýzu akceptačních kritérií a jejich převedení na testovací scénáře, nebo ověření kvality
  manuálních testů pomocí skriptu Definice hotovo (DoD).
---

# Pracovní postup: User Story -> Manuální Test Casy

Tento skill definuje standardizovaný postup tvorby a validace manuálních testovacích scénářů na základě akceptačních kritérií (AC) ze zadané User Story (UST).

Proces se řídí **zásadami proti falešnému hotovo**: o výsledku rozhoduje deterministický skript, agent nesmí domýšlet chybějící zadání a při nejasnostech hlásí stav `BLOKOVÁNO`.

---

## Tři stavy výsledku procesu

| Stav | Návratový kód | Popis |
| :--- | :---: | :--- |
| **`HOTOVO`** | `0` | Všechna AC jsou 100% pokryta, struktura TC je kompletní bez placeholderů a QA schválilo sadu. |
| **`NENÍ HOTOVO`** | `1` | Chybí pokrytí některého AC, chybí povinná pole nebo sada postrádá negativní scénáře. Agent musí nedostatky opravit. |
| **`BLOKOVÁNO`** | - | Zadání US je nejednoznačné, chybí klíčové hraniční podmínky nebo si kritéria protiřečí. **Agent nesmí chybějící požadavky domýšlet.** Práci zastaví a předloží konkrétní dotazy člověku. |

---

## Pracovní postup v krocích

| Krok | Název | Kdo dělá | Vstup | Výstup | Popis činnosti & Pojistka |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Review User Story** | **Agent + Uživatel** | Text US / odkaz na `user stories/` | Vyjasněná US a seznam AC (nebo `BLOKOVÁNO`) | Agent zkontroluje testovatelnost, nejasnosti a hraniční stavy. **Pojistka:** Pokud US postrádá podstatné informace, agent nedomýšlí zadání a ohlásí `BLOKOVÁNO` s dotazy na uživatele. |
| **2** | **Návrh test casů** | **Agent** | Potvrzená US + šablona v `templates/` | `manual_tests/TC_<US_ID>.md` | Agent navrhne kompletní sadu TC (Happy path, negativní i hraniční). Každý TC odkazuje na konkrétní AC. |
| **3** | **Nezávislý audit v čistém kontextu** | **Nezávislý AI Kontrolor (Čistý kontext)** | Navržený Markdown soubor + zdrojová US | Seznam chybějících aspektů a rizik | **Pojistka čistého kontextu:** Kontrola neprobíhá ve stejné konverzační session. Kontrolor dostane pouze US a navržené TC s otázkou: *"Co v test casích chybí a jaké hraniční případy nejsou pokryty?"*. |
| **4** | **Spuštění skriptu "Definice hotovo"** | **Agent** | Soubor TC + zdrojová US | Výsledek validátoru (Exit code 0/1) | **Pojistka stroje:** Agent spustí validační skript `verify_test_cases.py`. Skript zkontroluje integritu zdrojové US, 100% pokrytí AC a formát. |
| **5** | **Finální schválení** | **Uživatel (QA Lead)** | Výstup skriptu (PASS) + hotové TC | Schválená sada test casů | Uživatel zkontroluje byznys logiku a formálně potvrdí převzetí. |

---

## Pravidla pro tvorbu Test Casů
1. **Identifikace:** Každý test case musí mít unikátní ID (např. `TC-US02-01`), název, odkaz na kritérium (`**Pokrývá kritérium:** AC-X`), typ testu, předpoklady, očíslované kroky a očekávaný výsledek.
2. **Diverzita testů:** Sada musí obsahovat jak pozitivní scénáře (Happy Path), tak alespoň jeden negativní nebo hraniční scénář.
3. **Zákaz placeholderů:** Žádné nevyplněné zástupné texty (`TODO`, `TBD`, `DOPLNIT`).
4. **Read-Only ochrana:** Agent nesmí modifikovat zdrojový soubor s User Stories (např. odmazávat AC) ani upravovat validační skript, aby testy prošly.
5. **Cílové umístění:** Soubory se ukládají výhradně do `manual_tests/` (např. `manual_tests/TC_US-02_registrace.md`).

---

## Spuštění skriptu Definice hotovo (Krok 4)

Před předáním uživateli agent **vždy** spustí kontrolní skript:
```powershell
python .agents/skills/ust-to-manual-tc/scripts/verify_test_cases.py manual_tests/TC_<US_ID>.md
```
- **Exit code 0 (`HOTOVO`):** Všechna AC jsou pokryta, integrita je zachována a struktura je v pořádku.
- **Exit code 1 (`NENÍ HOTOVO`):** Chybí pokrytí některého AC, chybí povinná sekce nebo byl modifikován zdrojový soubor. Agent musí chyby opravit a spustit test znovu.
