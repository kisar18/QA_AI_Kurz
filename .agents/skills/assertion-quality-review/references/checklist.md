# Rychlý kontrolní checklist kvality assertů (Assertion Quality Checklist)

Tento checklist slouží jako rychlé vodítko při hodnocení assertů v testech.

---

## 1. Základní kontrolní otázky pro každý test

Před schválením testu si polož následující otázky:

1. **„Může tento test projít (být zelený), i když daná funkcionalita ve skutečnosti nefunguje?“**
   - *Příklad:* Pokud test pouze čeká na URL nebo ověří, že formulář zmizel, ale data se neuložila.
2. **„Ověřuje test reálný dopad akce na systém, nebo jen to, že kliknutí nespadlo?“**
   - Test musí ověřovat důsledky (stav UI, perzistence dat, zprávy uživateli).
3. **„Je v testu dostatečné množství assertů na klíčové stavy?“**
   - Ideální je ověřit: změnu URL + stav UI (ikony/tlačítka) + zpětnou vazbu (toast/hláška).
4. **„Používáme web-first auto-retrying asserty?“**
   - V Playwrightu vždy preferovat `expect(locator).to_be_visible()` před `assert locator.is_visible()`.

---

## 2. Kontrolní matice podle typu scénáře

| Typ scénáře | Minimální nutné asserty | Častá slepá místa (Anti-patterns) |
| :--- | :--- | :--- |
| **Přihlášení (Login)** | 1. URL po přihlášení<br>2. Tlačítko **Odhlásit se** je viditelné<br>3. Jméno/ikona uživatele je zobrazena<br>4. Tlačítko **Přihlásit se** zmizelo | Pouze `to_have_url()` nebo `wait_for_url()` bez kontroly stavu přihlášení v hlavičce. |
| **Odhlášení (Logout)** | 1. URL login stránky<br>2. Tlačítko **Přihlásit se** je viditelné<br>3. Chráněná stránka je nepřístupná | Neověření, zda se po kliknutí na Zpět v prohlížeči nebo přímé navigaci na chráněnou URL znovu neotevře profil. |
| **Vytvoření / Uložení (Create / Update)** | 1. Úspěšná hláška / toast<br>2. Přesměrování na přehled / domov<br>3. Znovunačtení a ověření uložení nových dat v polích | Pouhé ověření, že kliknutí na 'Uložit' přesměrovalo, bez kontroly, co se uložilo. |
| **Smazání (Delete)** | 1. Prvek není viditelný (`not_to_be_visible()`)<br>2. Počet položek klesl o 1<br>3. Potvrzení o smazání | Test ověří pouze zavření dialogu, nikoliv reálné zmizení položky ze seznamu. |
| **Nevalidní vstup (Validation Error)** | 1. Zobrazení konkrétní chybové hlášky u pole<br>2. URL se nezměnila (formulář se neodeslal)<br>3. Data ve formuláři zůstala zachována | Ověření pouze obecného `error.is_visible()` bez kontroly textu hlášky nebo ověření, že se formulář neodeslal. |
| **Filtrování / Hledání** | 1. Správné výsledky jsou viditelné<br>2. Nesouvisející výsledky nejsou v seznamu<br>3. Počet nalezených položek odpovídá | Ověření jen prvního prvku, nikoliv vyřazení neplatných. |

---

## 3. Playwright Web-First Asserty – Rychlý tahák

| Cíl kontroly | ❌ Vyvarovat se (statické / bez auto-retry) | ✔️ Doporučený web-first assert |
| :--- | :--- | :--- |
| **Viditelnost** | `assert locator.is_visible()` | `expect(locator).to_be_visible()` |
| **Skrytí prvku** | `assert not locator.is_visible()` | `expect(locator).not_to_be_visible()` |
| **Hodnota v inputu** | `assert locator.input_value() == "text"` | `expect(locator).to_have_value("text")` |
| **Text v prvku** | `assert "text" in locator.inner_text()` | `expect(locator).to_contain_text("text")` |
| **Přesný text** | `assert locator.inner_text() == "text"` | `expect(locator).to_have_text("text")` |
| **Počet prvků** | `assert locator.count() == 3` | `expect(locator).to_have_count(3)` |
| **URL stránky** | `assert page.url == expected_url` | `expect(page).to_have_url(expected_url)` |
| **Aktivní / Disabled** | `assert locator.is_enabled()` | `expect(locator).to_be_enabled()` |
