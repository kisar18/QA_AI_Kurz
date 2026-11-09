---
name: ust-to-manual-tc
description: >-
  Aktivuj tento skill, když uživatel požaduje vytvoření manuálních test casů z User Story (UST),
  analýzu akceptačních kritérií a jejich převedení na testovací scénáře, nebo ověření kvality
  manuálních testů pomocí skriptu Definice hotovo (DoD).
---

# Pracovní postup: User Story -> Manuální Test Casy

Tento skill definuje standardizovaný postup tvorby a validace manuálních testovacích scénářů na základě akceptačních kritérií (AC) ze zadané User Story (UST).

## Pracovní postup v krocích

| Krok | Název | Kdo dělá | Vstup | Výstup | Popis činnosti |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Review User Story** | **Agent + Uživatel** | Text US / odkaz na `user stories/` | Vyjasněná US a seznam AC (AC-1..n) | Agent zkontroluje testovatelnost, nejasnosti a hraniční stavy. Při pochybnostech se doptá. Uživatel potvrdí zadání. |
| **2** | **Návrh test casů** | **Agent** | Potvrzená US + šablona v `templates/` | `manual_tests/TC_<US_ID>.md` | Agent navrhne kompletní sadu TC (Happy path, negativní i hraniční). Každý TC odkazuje na konkrétní AC. |
| **3** | **Review uživatelem** | **Uživatel (QA)** | Navržený Markdown soubor | Připomínky / odsouhlasení | Uživatel zkontroluje byznys logiku a reálnost kroků. Agent zapracuje případné úpravy. |
| **4** | **Skript "Definice hotovo"** | **Agent** | Soubor TC + zdrojová US | Výsledek validátoru (Exit code 0/1) | Agent spustí validační skript, který zkontroluje 100% pokrytí AC a strukturu TC. Pokud skript selže, agent chyby opraví. |
| **5** | **Finální schválení** | **Uživatel** | Výstup skriptu (PASS) + hotové TC | Schválená sada test casů | Uživatel formálně potvrdí převzetí hotových manuálních test casů. |

## Pravidla pro tvorbu Test Casů
- Každý test case musí mít unikátní ID (např. `TC-US02-01`), název, odkaz na kritérium (`**Pokrývá kritérium:** AC-X`), typ testu, předpoklady, očíslované kroky a očekávaný výsledek.
- Sada musí obsahovat jak pozitivní scénáře, tak alespoň jeden negativní nebo chybový scénář.
- Cílové umístění souborů je adresář `manual_tests/` (např. `manual_tests/TC_US-02_registrace.md`).

## Spuštění skriptu Definice hotovo (Krok 4)
Před předáním uživateli agent **vždy** spustí kontrolní skript:
```powershell
python .agents/skills/ust-to-manual-tc/scripts/verify_test_cases.py manual_tests/TC_<US_ID>.md
```
- **Exit code 0 (`HOTOVO`):** Všechna AC jsou pokryta, struktura je v pořádku. Agent prezentuje výsledek uživateli.
- **Exit code 1 (`NENÍ HOTOVO`):** Chybí pokrytí některého AC nebo chybí povinná sekce. Agent musí nedostatky opravit a spustit test znovu.

