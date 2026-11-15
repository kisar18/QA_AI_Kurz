# Test Casy: US-15 Vypsání nového běhu (termínu) kurzu

**Zdrojová User Story:** US-15  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + Nezávislý QA Kontrolor  

---

### [TC-US15-01] Úspěšné vypsání nového termínu kurzu lektorem a zobrazení v detailu
- **Pokrývá kritérium:** AC-1, AC-2, AC-4, AC-5
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - Přihlášen uživatel v roli lektora (účet s lektorským oprávněním pro správu kurzů).
  - V systému existuje alespoň jeden publikovaný kurz (např. kurz s ID 1).
- **Testovací data:**
  - Datum zahájení: `2026-12-01`
  - Datum ukončení: `2027-01-15`
  - Den konání v týdnu: `Pondělí`
  - Čas lekce: `18:00 - 20:00`
  - Místo / forma výuky: `Praha 1 - Školící centrum, Učebna B`
- **Kroky:**
  1. Otevři katalog kurzů (`/courses`) a ověř přítomnost volby/tlačítka pro přidání termínu u vybraného kurzu.
  2. Klikni na tlačítko "Přidat iteraci" / "Přidat termín" (URL `/courses/1/create-iteration`).
  3. Zkontroluj přítomnost všech polí formuláře: datum zahájení, datum ukončení, den v týdnu, čas a místo výuky.
  4. Vyplň platné datum zahájení a datum ukončení.
  5. Vyber den konání v týdnu z výběrového pole.
  6. Vyplň čas lekce a místo konání.
  7. Klikni na tlačítko pro uložení ("Přidat iteraci").
  8. Po přesměrování na detail kurzu `/courses/1` vyhledej nově přidanou kartu běhu a zkontroluj zobrazené údaje včetně jména lektora.
- **Očekávaný výsledek:**
  - Formulář je úspěšně odeslán a nový běh kurzu je vytvořen v systému.
  - Nový termín je automaticky přiřazen k danému kurzu a propojen s přihlášeným lektorem (v kartě termínu nebo detailu kurzu je uvedeno jméno přihlášeného lektora).
  - Lektor je přesměrován na detail kurzu (`/courses/1`).
  - V sekci vypsaných termínů detailu kurzu je nově vytvořený běh ihned viditelný se všemi zadanými údaji (termíny, čas, den, místo).

---

### [TC-US15-02] Validace povinných polí při odeslání prázdného nebo neúplného formuláře
- **Pokrývá kritérium:** AC-2, AC-3
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Přihlášen uživatel v roli lektora.
  - Otevřen formulář pro vypsání nového termínu kurzu (`/courses/1/create-iteration`).
- **Testovací data:**
  - Prázdné hodnoty v povinných polích.
- **Kroky:**
  1. Otevři formulář vypsání termínu `/courses/1/create-iteration`.
  2. Ponech všechna pole formuláře prázdná a klikni na tlačítko "Přidat iteraci".
  3. Zkontroluj reakci systému a přítomnost validačních hlášek.
  4. Vyplň pouze datum zahájení a ukončení, ale ponech nevyplněné místo a čas.
  5. Znovu klikni na tlačítko "Přidat iteraci".
- **Očekávaný výsledek:**
  - Formulář se neodešle a systém zabrání vytvoření neúplného termínu.
  - Stránka zůstává na formuláři vypsání termínu.
  - U všech nevyplněných povinných polí (datum zahájení, datum ukončení, den v týdnu, čas, místo výuky) se zobrazí srozumitelná validační chybová hlášení.

---

### [TC-US15-03] Zamezení přístupu k vypsání nového termínu pro běžného studenta a hosta (RBAC)
- **Pokrývá kritérium:** AC-1
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Uživatel je přihlášen v roli běžného zákazníka (studenta), nebo je nepřihlášeným hostem.
- **Testovací data:**
  - Zákaznický účet bez lektorských oprávnění.
  - URL formuláře: `/courses/1/create-iteration`.
- **Kroky:**
  1. Přihlas se jako běžný zákazník a otevři detail kurzu `/courses/1` i katalog `/courses`.
  2. Zkontroluj, zda je na stránce zobrazeno tlačítko pro přidání termínu kurzu.
  3. Do adresního řádku prohlížeče zadej přímou URL `/courses/1/create-iteration` a stiskni Enter.
  4. Odhlas se (anonymní stav) a zopakuj pokus o přímou navigaci na `/courses/1/create-iteration`.
- **Očekávaný výsledek:**
  - Tlačítko pro vypsání nového termínu není studentovi ani nepřihlášenému návštěvníkovi v rozhraní vůbec nabízeno.
  - Pokus o přímé otevření URL `/courses/1/create-iteration` je systémem zamítnut (vrácena chyba 403 Forbidden, přesměrování na login, nebo návrat do katalogu).
  - Nepovolaný uživatel nemůže vypisovat termíny kurzů.

---

### [TC-US15-04] Logická validace časové souslednosti termínu kurzu
- **Pokrývá kritérium:** AC-2, AC-3
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Přihlášen lektor na stránce `/courses/1/create-iteration`.
- **Testovací data:**
  - Test 1 (konec před začátkem): Datum zahájení: `2026-12-15`, datum ukončení: `2026-11-01`.
  - Test 2 (jednodenní kurz): Datum zahájení: `2026-12-15`, datum ukončení: `2026-12-15`.
- **Kroky:**
  1. Na formuláři zadej datum zahájení `2026-12-15` a dřívější datum ukončení `2026-11-01`.
  2. Vyplň ostatní pole a klikni na "Přidat iteraci".
  3. Zkontroluj zobrazenou validační chybu.
  4. Následně otestuj hraniční jednodenní kurz: zadej stejné datum pro zahájení i ukončení (`2026-12-15`) a odešli formulář.
- **Očekávaný výsledek:**
  - V 1. případě systém odmítne obrácené datum (datum ukončení nesmí předcházet zahájení) a zobrazí validační chybu.
  - V 2. případě systém povolí uložení jednodenního kurzu (stejné datum zahájení a ukončení je platný hraniční stav).

---

### [TC-US15-05] Vypsání termínu s online formou výuky a kontrola zobrazení formátu
- **Pokrývá kritérium:** AC-2, AC-4, AC-5
- **Typ testu:** Pozitivní
- **Priorita:** Medium
- **Předpoklady:**
  - Přihlášen lektor na stránce `/courses/1/create-iteration`.
- **Testovací data:**
  - Datum zahájení: `2027-02-01`
  - Datum ukončení: `2027-03-01`
  - Den konání: `Středa`
  - Čas konání: `17:30 - 19:30`
  - Forma výuky: `Online výuka (Google Meet / Zoom)`
- **Kroky:**
  1. Vyplň formulář s uvedenou online formou výuky a večerním časem.
  2. Odešli formulář kliknutím na "Přidat iteraci".
  3. Po přesměrování na detail kurzu vyhledej nově přidaný běh.
- **Očekávaný výsledek:**
  - Termín je úspěšně vytvořen.
  - V detailu kurzu je zřetelně uvedena forma výuky `Online výuka (Google Meet / Zoom)` i správný den a čas lekcí.

---

### [TC-US15-06] Vypsání více nezávislých termínů k jednomu kurzu a souběžné zobrazení
- **Pokrývá kritérium:** AC-4, AC-5
- **Typ testu:** Hraniční
- **Priorita:** High
- **Předpoklady:**
  - U vybraného kurzu již existuje alespoň jeden vypsaný termín.
  - Přihlášen lektor.
- **Testovací data:**
  - Druhý nezávislý termín: datum zahájení za 3 měsíce, jiný den v týdnu (např. `Sobota 09:00 - 13:00`).
- **Kroky:**
  1. Otevři formulář vypsání termínu pro tentýž kurz (`/courses/1/create-iteration`).
  2. Vyplň parametry druhého termínu a odešli formulář.
  3. Zkontroluj detail kurzu `/courses/1`.
- **Očekávaný výsledek:**
  - V detailu kurzu jsou přehledně zobrazeny oba vypsané termíny (běhy).
  - Každý běh má své vlastní nezávislé parametry (data, den, čas, obsazenost 0/kapacita) a nedochází k přepsání dříve vytvořeného termínu.

---

### [TC-US15-07] Validace data zahájení v minulosti
- **Pokrývá kritérium:** AC-2, AC-3
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Přihlášen uživatel v roli lektora.
  - Otevřen formulář pro vypsání termínu `/courses/1/create-iteration`.
- **Testovací data:**
  - Datum zahájení v minulosti: např. datum o 30 dní dříve než dnešní den.
  - Datum ukončení v minulosti: např. datum o 10 dní dříve než dnešní den.
  - Platný den v týdnu, čas a místo.
- **Kroky:**
  1. Zadej do pole data zahájení datum z minulosti.
  2. Zadej do pole data ukončení datum z minulosti.
  3. Vyplň zbývající povinná pole a klikni na "Přidat iteraci".
  4. Zkontroluj reakci formuláře.
- **Očekávaný výsledek:**
  - Systém nepovolí vypsat nový termín do minulosti.
  - Formulář se neuloží a uživatel je upozorněn validační chybou (např. "Datum zahájení nesmí být v minulosti").

---

### [TC-US15-08] Omezení vypsání termínu k cizímu kurzu (Autorská oprávnění lektora)
- **Pokrývá kritérium:** AC-1, AC-4
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - V systému existují dva různí lektoři: Lektor A a Lektor B.
  - Lektor A je autorem a správcem Kurzu 1.
  - Do aplikace je přihlášen Lektor B.
- **Testovací data:**
  - Účet Lektora B (např. `lektor.beta@example.com` / `HesloBeta123`).
  - ID kurzu patřícího Lektoru A (např. `/courses/1`).
- **Kroky:**
  1. Po přihlášení Lektora B otevři katalog kurzů `/courses`.
  2. Zkontroluj, zda se u cizího Kurzu 1 zobrazuje tlačítko pro vypsání termínu.
  3. Zadej do adresního řádku prohlížeče přímou URL pro vypsání termínu k cizímu kurzu `/courses/1/create-iteration` a stiskni Enter.
  4. Zkontroluj reakci systému a oprávnění.
- **Očekávaný výsledek:**
  - Lektor B nemá oprávnění spravovat ani vypisovat termíny k cizímu kurzu jiného lektora.
  - Tlačítko pro vypsání termínu se u cizího kurzu nenabízí a přímý přístup na URL je zamítnut (stav 403 Forbidden nebo přesměrování s chybovou zprávou o nepovolené akci).
