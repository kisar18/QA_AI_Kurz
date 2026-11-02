# Příklady Před vs Po (reálné případy z projektu)

## 1. CSS selektor s testid
```python
# ❌ Před
self.detail_buttons = page.locator("button[data-testid='registration_link']")
# ✔️ Po (pokud je testid jedinečný pro prvek)
self.detail_buttons = page.get_by_test_id("registration_link")
# Pokud stejný testid sdílí <a> i <button>, zpřesnit rolí:
self.detail_buttons = page.get_by_test_id("registration_link").and_(page.get_by_role("button"))
```

## 2. Prefixový selektor
```python
# ❌ Před
self.iteration_cards = page.locator("[data-testid^='iteration_']")
# ✔️ Po: požádat o jednotný testid karty (např. iteration_card)
# TODO(testid): chybí společný testid karty iterace; dočasně prefixový selektor
```

## 3. `.first` místo konkrétní položky
```python
# ❌ Před
self.detail_buttons.first.click()
# ✔️ Po: lokátor vázaný na konkrétní kurz
def course_card(self, name: str) -> Locator:
    return self.course_cards.filter(has_text=name)

def open_detail(self, name: str):
    self.course_card(name).get_by_test_id("registration_link").click()
```

## 4. Text závislý na jazyce backendu
```python
# ❌ Před
self.user_not_found_message = page.get_by_text("We can't find a user with that email address.")
# ✔️ Po: text jako konstanta, nebo testid, pokud existuje
USER_NOT_FOUND_TEXT = "We can't find a user with that email address."
self.user_not_found_message = page.get_by_text(USER_NOT_FOUND_TEXT)  # TODO(testid): chybí testid hlášky
```

## 5. Atributový selektor bez testid
```python
# ❌ Před
self.image_input = page.locator("input[type='file']")
# ✔️ Po
self.image_input = page.get_by_test_id("course_image_input")  # po doplnění testid
# Do té doby: page.get_by_label(IMAGE_LABEL) s TODO(testid)
```

## 6. Lokátor v testu (tvrdý zákaz)
```python
# ❌ V testu
expect(page.get_by_test_id("email_input")).to_be_visible()
# ✔️ V testu
expect(login_page.email_input).to_be_visible()
```

