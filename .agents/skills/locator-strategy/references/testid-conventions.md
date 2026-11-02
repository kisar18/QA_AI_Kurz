# Konvence `data-testid`

## Pojmenování
- `snake_case`, anglicky, bez diakritiky.
- Vzor `<entita>_<prvek>`: `course_name_input`, `login_button`.
- Chyby polí: `<pole>_error` (např. `ico_error`, `phone_error`).
- Sekce a kontejnery: `<entita>_section`, `<entita>_container`.
- Prvky seznamu: obecný testid pro všechny (`course_name`) a vždy se vybírají přes `filter`, ne přes pořadí.

## Příklady z projektu (pro zachování konzistence)
| Oblast | Příklady |
| :--- | :--- |
| Přihlášení | `email_input`, `password_input`, `login_button`, `forgot_password_link` |
| Kurzy | `courses_title`, `course_name`, `course_price`, `registration_link` |
| Vytvoření kurzu | `course_name_input`, `course_capacity_input`, `course_price_input` |
| Registrace na kurz | `ico_input`, `ico_error`, `phone_input`, `phone_error` |
| Navigace | `login_link`, `logout_button`, `courses_link`, `home_link` |

## Šablona požadavku na vývojáře
```
Stránka: <URL / název obrazovky>
Prvek: <popis prvku>
Navržený testid: <název dle konvence>
Důvod: <proč dnešní lokátor nestačí>
```

