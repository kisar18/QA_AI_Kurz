# Rychlý checklist lokátorů

## 1. Kontrolní otázky pro každý lokátor
- [ ] Je to `get_by_test_id`? Pokud ne, má `data-testid` opravdu chybět (ověřeno v DOM)?
- [ ] Najde lokátor právě **1** prvek (`to_have_count(1)`), nebo záměrně celý seznam?
- [ ] Nezávisí na pořadí prvků, CSS třídách ani jazyce?
- [ ] Je lokátor definován v Page Objectu, ne v testu?
- [ ] Text v lokátoru je pojmenovaná konstanta?
- [ ] Fallback má značku `# TODO(testid): ...` a požadavek na vývojáře?
- [ ] `.first` / `.nth()` má komentář s důvodem?

## 2. Tahák Playwright API

| Cíl | Použití |
| :--- | :--- |
| Podle testid | `page.get_by_test_id("email_input")` |
| Podle role | `page.get_by_role("button", name="Uložit")` |
| Podle labelu | `page.get_by_label("E-mail")` |
| Podle placeholderu | `page.get_by_placeholder("Zadejte e-mail")` |
| Podle textu | `page.get_by_text("Vítej")` |
| Zúžení do kontejneru | `container.get_by_role("button")` |
| Filtr podle textu | `cards.filter(has_text="Python")` |
| Filtr podle potomka | `cards.filter(has=page.get_by_test_id("badge"))` |
| Kombinace (AND) | `locator.and_(other)` |
| Alternativa (OR) | `locator.or_(other)` |
| Počet | `expect(locator).to_have_count(1)` |

## 3. Co dělat při chybě
| Chyba | Příčina | Řešení |
| :--- | :--- | :--- |
| `strict mode violation` | Lokátor najde více prvků | Zpřesnit (`filter`, kontejner), ne `.first` |
| `Timeout` na lokátoru | Prvek neexistuje / změnil se testid | Zkontrolovat DOM, opravit lokátor |
| Test zelený jen s `.first` | Pořadí prvků | Lokátor vázaný na obsah (`filter`) |

