---
name: assertion-quality-review
description: >-
  Aktivuj a použij tento skill v následujících situacích:
  1. Implementace nebo tvorba nového testu a návrh assertů (zajištění ověření kompletního výsledného stavu a post-conditions od začátku).
  2. Úprava, refaktoring nebo oprava existujících testů a assertů (např. kvůli změně chování aplikace, novým UI prvkům nebo opravě chyb).
  3. Požadavek na analýzu, audit, revizi nebo ověření kvality assertů v konkrétním testu či testovací sadě (odhalení slabin, falešné pozitivity a flakiness).
---

# Assertion Quality Review Skill

Standard pro tvorbu, refaktoring a audit assertů v Playwright + pytest.

> **Klíčový cíl:**
> Asserty musí mít **vysokou schopnost odhalovat chyby (Fault Detection Power)**. Test nesmí projít zeleně, pokud v aplikaci nastala chyba (eliminace falešné pozitivity).

---

## 1. Pět nepřekročitelných pravidel pro asserty

1. **Výhradně Web-First auto-retrying asserty:**
   - Vždy používej `expect(locator).to_be_visible()`, `expect(page).to_have_url(...)`.
   - ❌ **ZÁKAZ:** statické `assert locator.is_visible()`, `assert page.url == ...` (nečekají na asynchronní DOM a způsobují flakiness).

2. **ZÁKAZ podmínek `if` / `else` kolem assertů:**
   - ❌ **ZÁKAZ:** `if count > 0: expect(...)` nebo větvení `if ...: expect(...) else: ...`.
   - Pokud podmínka neplatí, test tiše projde zeleně bez ověření. Asserty musí běžet **bezpodmínečně**.

3. **ZÁKAZ `time.sleep()` a `wait_for_timeout()`:**
   - ❌ **ZÁKAZ:** Umělé pauzy před asserty. Playwright `expect(...)` automaticky čeká na splnění podmínky.

4. **Ověření kompletního výsledného stavu (Post-conditions & Side-effects):**
   - Nestačí pouhé čekání na URL nebo HTTP kód.
   - **Login:** Ověř URL + viditelnost tlačítka Odhlásit + jméno/profil + zmizení tlačítek Přihlásit/Registrace.
   - **Formulář / Změna dat:** Ověř URL + potvrzovací hlášku + perzistenci (znovunačtení a ověření hodnot).
   - **Smazání:** Ověř, že prvek není viditelný (`not_to_be_visible()`) a počet položek klesl.

5. **ZÁKAZ oslabování kontrol:**
   - Nikdy nemaž assert ani nezvágňuj podmínku jen proto, aby test prošel. Při pádu testu zjisti příčinu v aplikaci.

---

## 2. Rychlý tahák: Správné vs. zakázané vzory

| Kontrola | ❌ Zakázaný vzor | ✔️ Správný vzor |
| :--- | :--- | :--- |
| **Viditelnost** | `assert locator.is_visible()` | `expect(locator).to_be_visible()` |
| **Skrytí prvku** | `assert not locator.is_visible()` | `expect(locator).not_to_be_visible()` |
| **Podmíněné ověření** | `if items.count() > 0: expect(...)` | `expect(items.first).to_be_visible()` |
| **Hodnota pole** | `assert locator.input_value() == "x"` | `expect(locator).to_have_value("x")` |
| **Text v prvku** | `assert "ok" in locator.inner_text()` | `expect(locator).to_contain_text("ok")` |
| **URL stránky** | `page.wait_for_timeout(1000)`<br>`assert page.url == "/target"` | `expect(page).to_have_url(re.compile(r"/target$"))` |

---

## 3. Postup při revizi existujících testů
1. **Identifikuj tichá selhání:** Hledej `if`, `is_visible()`, `count() > 0` bez následného striktního expectu.
2. **Odstraň umělá čekání:** Nahraď `wait_for_timeout` za web-first `expect`.
3. **Doplň chybějící post-conditions:** Ověř reálný dopad akce na data a UI.
4. Podrobný kontrolní checklist najdeš v [references/checklist.md](./references/checklist.md).
