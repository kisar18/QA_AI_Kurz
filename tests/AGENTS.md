# Pravidla pro testy a standard kvality assertů

Při vytváření nových testů nebo úpravě stávajících testů a assertů v tomto adresáři se řiď skillovými pravidly **`assertion-quality-review`**:

### Základní cíl: Řízení kvality a schopnost odhalovat chyby (Fault Detection Power)
> **Nestačí, že test projde zelený nebo že obsahuje velké množství assertů.**
> Cílem je prokázat, že asserty **odhalí reálné defekty aplikace** a zabrání falešné pozitivitě.

1. **Pravidlo prokazatelnosti defektu:**
   - Každý navržený assert musí pokrývat konkrétní riziko selhání (např. rozpad session, tiché selhání uložení dat v DB, bypass validace).
2. **Kompletní ověření výsledného stavu (Post-conditions & Side-effects):**
   - **Přihlášení:** Ověřuj zobrazení tlačítka *Odhlásit se*, jméno/ikonu uživatele a zánik tlačítek pro nepřihlášené.
   - **Formuláře a ukládání dat:** Vždy ověřuj reálnou perzistenci nových dat po znovunačtení.
   - **Chybové stavy:** Ověřuj přesný text hlášky a setrvání na stránce formuláře.
3. **Výhradně Web-First Auto-Retrying asserty (Playwright):**
   - Vždy `expect(locator).to_be_visible()`, nikdy nestabilní `assert locator.is_visible()`.
4. **Zákaz oslabování assertů:**
   - Při změně aplikace nebo pádu testu neřeš problém smazáním assertu nebo zvágněním podmínky. Vždy zachovej plnou hloubku ověření odpovídající novému chování.


---

# Pravidla pro lokátory

Při práci s lokátory (tvorba, oprava, audit) se řiď skillem **`locator-strategy`**:

1. **Tvrdý zákaz lokátorů v testech:** v `tests/` nesmí být žádný lokátor (`page.locator()`, `page.get_by_*()`, CSS/XPath). Testy používají pouze atributy a metody Page Objectů.
2. **Priorita:** `get_by_test_id` první. Pokud `data-testid` chybí, povoleno `get_by_role` / label / placeholder s komentářem `# TODO(testid): ...` a požadavkem na vývojáře.
3. **Audit:** `python .agents/skills/locator-strategy/scripts/audit_locators.py pages tests`
