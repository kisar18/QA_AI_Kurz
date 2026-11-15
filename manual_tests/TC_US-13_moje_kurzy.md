# Test Casy: US-13 Přehled mých zapsaných kurzů

**Zdrojová User Story:** US-13  
**Datum vytvoření:** 2026-11-15  
**Autor návrhu:** AI Agent + Nezávislý QA Kontrolor  

---

### [TC-US13-01] Zobrazení zapsaného kurzu a kompletních organizačních informací
- **Pokrývá kritérium:** AC-2, AC-3, AC-4, AC-5, AC-6, AC-7
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Aplikace běží na testovacím prostředí (`http://testovani.kitner.cz` nebo lokální instance).
  - Přihlášen uživatel v roli zákazníka, který má aktivní zápis na alespoň jeden běh kurzu (např. provedením zápisu podle US-12).
  - Otevřena stránka přehledu mých kurzů (`/my-courses`).
- **Testovací data:**
  - Zapsaný kurz s definovanými termíny konání:
    - Název kurzu, popis, cena
    - Datum zahájení a ukončení (datum první a poslední lekce)
    - Den v týdnu a čas konání lekcí (např. *Pondělí 18:00 - 20:00*)
    - Místo konání nebo forma výuky (např. prezenční adresa učebny nebo online odkaz)
- **Kroky:**
  1. Otevři stránku `/my-courses`.
  2. Zkontroluj přítomnost hlavní sekce zapsaných kurzů a její nadpis ("Mé zapsané kurzy").
  3. Ověř zobrazení karty zapsaného kurzu v seznamu.
  4. Zkontroluj přítomnost názvu kurzu, jeho textového popisu a uvedené ceny v Kč.
  5. Ověř zobrazení data zahájení a data ukončení běhu kurzu (první a poslední lekce).
  6. Ověř zobrazení informací o dni v týdnu a času konání lekcí.
  7. Ověř zobrazení místa konání / formy výuky kurzu.
- **Očekávaný výsledek:**
  - Všechny kurzy s aktivním zápisem uživatele jsou zobrazeny v přehledu.
  - U každého kurzu jsou kompletně a bez chyb zobrazeny všechny organizační náležitosti: název, popis, cena, data konání první a poslední lekce, den a čas výuky i místo konání / forma výuky.

---

### [TC-US13-02] Dostupnost odkazu v navigaci a přístup do sekce pro přihlášeného zákazníka
- **Pokrývá kritérium:** AC-1
- **Typ testu:** Pozitivní
- **Priorita:** High
- **Předpoklady:**
  - Uživatel v roli zákazníka je přihlášen do aplikace.
  - Uživatel se nachází na libovolné stránce portálu (např. `/courses` nebo `/home`).
- **Testovací data:**
  - Přihlášený zákaznický účet (např. `klient@example.com` / `Heslo123`).
- **Kroky:**
  1. Zkontroluj položky v horní navigační liště.
  2. Ověř přítomnost odkazu "Moje kurzy".
  3. Klikni na odkaz "Moje kurzy" v horní navigaci.
- **Očekávaný výsledek:**
  - Odkaz "Moje kurzy" je pro přihlášeného zákazníka zřetelně a trvale dostupný v navigaci.
  - Kliknutí provede plynulé přesměrování na URL `/my-courses`.
  - Stránka se úspěšně načte s nadpisem "Mé zapsané kurzy".

---

### [TC-US13-03] Přechod na podrobný detail kurzu z karty v přehledu
- **Pokrývá kritérium:** AC-8
- **Typ testu:** Pozitivní
- **Priorita:** Medium
- **Předpoklady:**
  - Přihlášený zákazník se nachází na stránce `/my-courses`.
  - V přehledu je zobrazen alespoň jeden zapsaný kurz.
- **Testovací data:**
  - Karta existujícího zapsaného kurzu s tlačítkem/odkazem pro zobrazení podrobností.
- **Kroky:**
  1. Na stránce `/my-courses` vyhledej kartu zapsaného kurzu.
  2. Klikni na tlačítko "Více informací" (nebo odkaz na detail kurzu) na kartě daného kurzu.
  3. Zkontroluj URL v adresním řádku prohlížeče a obsah zobrazené stránky.
  4. V detailu kurzu klikni v navigaci nebo prohlížeči zpět na "Moje kurzy".
- **Očekávaný výsledek:**
  - Dojde k přesměrování na detail odpovídajícího kurzu (URL odpovídající vzoru `/courses/<course_id>`).
  - Na zobrazené stránce se zobrazí kompletní detail kurzu se všemi informacemi a vypsanými termíny.
  - Uživatel se může bez problémů vrátit zpět do přehledu svých kurzů.

---

### [TC-US13-04] Zamezení přístupu do sekce 'Moje kurzy' pro nepřihlášeného návštěvníka
- **Pokrývá kritérium:** AC-1
- **Typ testu:** Negativní
- **Priorita:** High
- **Předpoklady:**
  - Návštěvník není přihlášen do systému (anonymní stav).
  - Otevřena libovolná veřejná stránka (např. `/courses` nebo `/`).
- **Testovací data:**
  - URL privátní sekce: `/my-courses`.
- **Kroky:**
  1. Zkontroluj horní navigační lištu nepřihlášeného uživatele.
  2. Ověř, zda je v navigaci přítomen odkaz "Moje kurzy".
  3. Zadej do adresního řádku prohlížeče přímou URL `/my-courses` a stiskni klávesu Enter.
  4. Zkontroluj reakci systému a stav zobrazené stránky.
- **Očekávaný výsledek:**
  - V horní navigační liště se odkaz "Moje kurzy" nepřihlášenému návštěvníkovi vůbec nezobrazuje.
  - Při pokusu o přímou navigaci na `/my-courses` systém přístup odmítne: nedojde k zobrazení privátních dat kurzů ani termínů; uživatel je přesměrován na `/login` nebo informován o nutnosti přihlášení.

---

### [TC-US13-05] Zobrazení sekce 'Moje kurzy' pro zákazníka bez aktivních zápisů (Empty State)
- **Pokrývá kritérium:** AC-1, AC-2
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Uživatel v roli zákazníka je přihlášen.
  - Uživatel je nově zaregistrován a nemá dosud proveden žádný zápis na kurz.
- **Testovací data:**
  - Nový zákaznický účet bez historie zápisů.
- **Kroky:**
  1. Přejdi v horní navigaci do sekce "Moje kurzy" (`/my-courses`).
  2. Zkontroluj zobrazení stránky a její stabilitu (nesmí dojít k chybě aplikace 500).
  3. Zkontroluj obsah sekce kurzů a přítomnost informativního hlášení a odkazu do katalogu kurzů.
- **Očekávaný výsledek:**
  - Stránka se korektně načte s nadpisem "Mé zapsané kurzy".
  - Aplikace nezpůsobí chybu zpracování; zobrazí se informativní sdělení o tom, že uživatel zatím nemá zapsané žádné kurzy, a přímý odkaz pro výběr kurzu z katalogu (`/courses`).

---

### [TC-US13-06] Zobrazení více souběžně zapsaných kurzů a nezávislost organizačních údajů
- **Pokrývá kritérium:** AC-2, AC-3
- **Typ testu:** Hraniční
- **Priorita:** High
- **Předpoklady:**
  - Přihlášený zákazník má aktivní zápis na minimálně 2 různé kurzy (nebo 2 různé termíny).
- **Testovací data:**
  - Kurz A: termín konání v pondělí, prezenční výuka.
  - Kurz B: termín konání v pátek, online výuka.
- **Kroky:**
  1. Otevři stránku `/my-courses`.
  2. Spočítej počet zobrazených karet kurzů v sekci.
  3. Porovnej organizační údaje (termíny od-do, den v týdnu, čas a místo konání) mezi kartou Kurzu A a Kurzu B.
- **Očekávaný výsledek:**
  - Všechny zapsané kurzy uživatele jsou zobrazeny v seznamu (počet odpovídá provedeným registracím).
  - Každý kurz má své vlastní, nezávislé organizační údaje a nedochází k prolínání či přepisování termínů mezi jednotlivými kurzy.

---

### [TC-US13-07] Omezení přístupu do sekce 'Moje kurzy' pro roli Lektor (RBAC)
- **Pokrývá kritérium:** AC-1
- **Typ testu:** Negativní
- **Priorita:** Medium
- **Předpoklady:**
  - Do aplikace je přihlášen uživatel v roli Lektor (účet s oprávněním pro správu kurzů).
- **Testovací data:**
  - Účet lektora (např. `lektor@example.com` / `HesloLektor123`).
- **Kroky:**
  1. Po přihlášení lektora zkontroluj položky v horní navigační liště.
  2. Zkontroluj, zda je v navigaci zobrazen zákaznický odkaz "Moje kurzy" nebo pouze lektorské položky (např. "Správa kurzů", "Vytvořit kurz").
  3. Zadej do adresního řádku prohlížeče přímou URL klientské sekce `/my-courses` a stiskni Enter.
- **Očekávaný výsledek:**
  - Horní navigace reflektuje roli lektora a nenabízí běžný zákaznický zápisový přehled.
  - Při pokusu o přímou navigaci systém lektora buď přesměruje do lektorského rozhraní, nebo zobrazí odpovídající informaci v souladu s pravidly oprávnění (RBAC).

---

### [TC-US13-08] Rozlišení nadcházejících kurzů a chronologické řazení termínů
- **Pokrývá kritérium:** AC-2, AC-5
- **Typ testu:** Hraniční
- **Priorita:** Medium
- **Předpoklady:**
  - Přihlášený zákazník má zapsáno více kurzů s různými daty zahájení (např. kurz začínající zítra a kurz začínající za měsíc).
- **Testovací data:**
  - Kurz 1: začátek za 2 dny.
  - Kurz 2: začátek za 30 dní.
- **Kroky:**
  1. Otevři stránku `/my-courses`.
  2. Zkontroluj pořadí zobrazených karet kurzů v seznamu.
  3. Ověř, zda jsou kurzy řazeny chronologicky podle data zahájení nejbližší lekce (od nejbližšího termínu po nejvzdálenější).
  4. Zkontroluj, zda jsou termíny zřetelně formátovány a čitelné.
- **Očekávaný výsledek:**
  - Kurzy jsou uspořádány přehledně a chronologicky, takže uživatel vidí nejbližší nadcházející kurz jako první.
  - Data zahájení a ukončení přesně odpovídají vybraným běhům a umožňují uživateli snadnou časovou orientaci.
