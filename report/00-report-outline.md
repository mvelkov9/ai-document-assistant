# Report Outline — Seminarska naloga (Word Document)

## Working title

Razvoj integrirane spletne storitve za varno upravljanje dokumentov z AI povzetki in dokumentnim Q&A v oblačni arhitekturi

## Production URL

**https://doc-ai-assist.com** — live deployment on Hetzner CX33 VPS with TLS

## Required document structure (chapters in Word)

1. Naslovnica
2. Povzetek in ključne besede v slovenščini
3. Abstract and keywords in English
4. Uvod
5. Problem in cilji
6. Poslovni scenarij uporabe
7. Arhitekturni opis rešitve
8. Analiza integracije in podatkovnih tokov
9. Analiza varnosti
10. Stroškovna analiza
11. Kritična ocena primernosti
12. Implementacijska validacija (s posnetki zaslona)
13. Zaključek
14. Seznam virov

## Suggested chapter expansion

### 1. Uvod

- predstavitev problema
- cilji naloge
- raziskovalni oziroma razvojni pristop
- metodologija dela

### 2. Problem in cilji

- opis problema neučinkovitega upravljanja dokumentov
- 6 glavnih ciljev razvoja

### 3. Poslovni scenarij uporabe

- profil ciljne organizacije
- potreba po varni hrambi dokumentov
- razlogi za integracijo AI funkcionalnosti
- večuporabniški vidik in arhitekturne zahteve

### 4. Arhitektura sistema

- logična arhitektura (diagram)
- deployment arhitektura na VPS
- opis komponent: Vue, FastAPI, PostgreSQL, MinIO, AI adapter, reverse proxy
- arhitekturni diagram
- podatkovni model (4 tabele)
- API zasnova (24 endpointov)

### 5. Analiza integracije in podatkovnih tokov

- prijava in avtorizacija
- upload dokumenta
- hramba v MinIO in metapodatki v bazi
- summary job tok (asinhroni)
- dokumentni Q&A tok (RAG-lite BM25)
- diagram podatkovnih tokov

### 6. Analiza varnosti

- JWT in upravljanje dostopa
- zasebnost dokumentov
- obravnava AI integracije in prompt tveganj
- varovanje skrivnosti in `.env` pristop
- rate limiting, security headers
- OWASP Top 10 mapping
- readiness, logging, backup in operativni minimum

### 7. Stroškovna analiza

- strošek VPS (Hetzner CX33 — €5,49/mesec)
- strošek domene (doc-ai-assist.com)
- strošek AI API klicev (Groq free tier)
- primerjava z managed alternativo
- scenariji: osnovni, razširjeni, skalirani

### 8. Kritična ocena primernosti

- prednosti izbrane rešitve
- slabosti in omejitve
- primernost za slovensko organizacijo
- primerjava z managed PaaS pristopom

### 9. Implementacijska validacija (s posnetki zaslona!)

- kratek opis dejanske implementacije
- predstavitev API in OpenAPI dokumentacije
- opis CI/CD, testov in deployment poti
- **POSNETKI ZASLONA** — see screenshot list below
- prikaz demo scenarija

### 10. Zaključek

- povzetek doseženih ciljev
- omejitve rešitve
- možnosti nadaljnjega razvoja

## Required figures and tables

- glavni arhitekturni diagram (Mermaid → slika)
- diagram podatkovnih tokov (Mermaid → slika)
- tabela glavnih API endpointov (24 endpointov)
- tabela varnostnih tveganj in mitigacij
- tabela stroškovnih scenarijev
- tabela uporabljenih tehnologij in verzij

## Final Word Blueprint

Spodnji načrt ni nov seznam vsebine, ampak predlog, kako naj bo obstoječa vsebina razporejena v končni Word-verziji, da bo dokument deloval kot urejena seminarska naloga in ne kot izvožen Markdown.

### Splošna postavitev

- pisava: Calibri 11 ali Times New Roman 12
- razmik med vrsticami: 1,15 ali 1,5
- poravnava: obojestranska
- robovi: standardni Word robovi (2,5 cm)
- naslovi poglavij: Heading 1
- podpoglavja: Heading 2
- podpodpoglavja: Heading 3
- oštevilčevanje slik: Slika 1, Slika 2, ...
- oštevilčevanje tabel: Tabela 1, Tabela 2, ...
- vsaka slika in tabela mora imeti naslov in po potrebi kratek vir
- po naslovnici vstavi samodejno kazalo
- po kazalu po želji vstavi še seznam slik in seznam tabel

### Priporočen prelom strani

- Naslovnica: samostojna stran
- Povzetek in ključne besede: nova stran
- Abstract and keywords: nova stran
- Uvod naj se začne na novi strani
- poglavji 7 in 12 naj se začneta na novi strani, ker vsebujeta več slik in tabel
- Seznam virov naj bo vedno na novi strani

### Natančna razporeditev po poglavjih

#### 1. Naslovnica

- brez številke strani ali z izklopljeno prikazano številko
- brez odvečnih povezav kot surov URL v prvi polovici strani; URL in repozitorij naj bosta spodaj, manj poudarjeno

#### 2. Povzetek in ključne besede

- naj vsebuje 1 strnjen akademski odstavek
- takoj pod povzetkom vrstica: Ključne besede: oblak, FastAPI, ...

#### 3. Abstract and Keywords

- angleška različica naj bo enako dolga in podobno strukturirana kot slovenski povzetek
- takoj pod abstractom vrstica: Keywords: cloud, FastAPI, ...

#### 4. Uvod

- 3 do 5 odstavkov
- brez slik
- zaključi naj se z jasno navedbo cilja naloge in metodologije

#### 5. Problem in cilji

- podpoglavje 5.1 Problem: 1 do 2 odstavka
- podpoglavje 5.2 Cilji: oštevilčen seznam ciljev

#### 6. Poslovni scenarij uporabe

- 2 do 3 odstavki
- poudari realen organizacijski kontekst in večuporabniško naravo sistema

#### 7. Arhitekturni opis rešitve

- 7.1 Logična arhitektura
- takoj za uvodnim odstavkom vstavi Slika 1
- pod sliko: "Slika 1: Logična arhitektura sistema"
- po sliki sledi razlaga glavnih komponent
- 7.2 Deployment arhitektura: tabela s podatki o VPS
- 7.3 Arhitekturne odločitve: 3 do 5 odstavkov
- 7.4 Podatkovni model: seznam tabel ali kratka tabela
- 7.5 API zasnova: tukaj vstavi Tabela 1 s skupinami endpointov
- po želji dodaj 7.6 Frontend arhitektura in 7.7 Odzivna zasnova

#### 8. Analiza integracije in podatkovnih tokov

- najprej kratek uvod, kaj prikazuje poglavje
- nato Slika 2
- pod sliko: "Slika 2: Podatkovni tokovi sistema"
- po sliki sledi razlaga tokov po podpoglavjih: registracija, upload, summary, Q&A

#### 9. Analiza varnosti

- razdeli na jasna podpoglavja: identiteta, zaščita gesel, zaščita dokumentov, rate limiting, varnostne glave, validacija, logiranje, OWASP, AI tveganja, znane omejitve
- tabelo tveganj vstavi kot Tabela 2
- naslov tabele: "Tabela 2: Povzetek varnostnih tveganj in ukrepov"

#### 10. Stroškovna analiza

- najprej Tabela 3: konkretna stroškovna tabela
- nato Tabela 4: primerjava z managed alternativo
- pod tabelami dodaj razlago osnovnega, razširjenega in skaliranega scenarija

#### 11. Kritična ocena primernosti

- 11.1 Prednosti rešitve
- 11.2 Slabosti in omejitve
- 11.3 Razlikovanje od neposredne uporabe AI-orodij
- 11.4 Primernost za slovensko organizacijo
- to poglavje naj bo bolj analitično in manj opisno; tu profesor vidi kritično presojo

#### 12. Implementacijska validacija

- 12.1 Uporabljena tehnologija: Tabela 5
- 12.2 Razvojna validacija: opis testov, coverage, CI
- 12.3 Operativna validacija: produkcijski deployment, TLS, healthy containers
- 12.4 CI/CD pipeline: 1 do 2 odstavka
- 12.5 End-to-end validacija: zaporedno prikaži uporabniške tokove
- slike 3 do 16 naj bodo tukaj, razdeljene v logične skupine
- priporočilo: 1 slika na polovico strani ali največ 2 manjši sliki na stran

#### 13. Zaključek

- 3 do 5 odstavkov
- povzetek doseženih ciljev
- strokovno utemeljena omejitev rešitve
- realne nadaljnje nadgradnje

#### 14. Seznam virov

- vire poenoti v en slog
- priporočilo: "Naslov. Dostopno na: URL. Datum dostopa: marec 2026."
- če boš imel čas, poenoti vse vire na isti bibliografski slog in dodaj datum dostopa

### Priporočen vrstni red slik

- Slika 1: Logična arhitektura sistema
- Slika 2: Podatkovni tokovi sistema
- Slika 3: Začetna stran aplikacije
- Slika 4: Registracija oziroma prijava
- Slika 5: Pregled dokumentov
- Slika 6: Nalaganje dokumenta
- Slika 7: AI-generiran povzetek
- Slika 8: Dokumentni Q&A
- Slika 9: Administracijska plošča
- Slika 10: Uporabniški profil
- Slika 11: Swagger UI
- Slika 12: ReDoc
- Slika 13: Varnostne glave HTTP-odgovora
- Slika 14: Stanje Docker-vsebnikov na VPS
- Slika 15: Uspešen deployment na VPS
- Slika 16: CI pipeline v GitHub Actions
- Slika 17: Vgrajen PDF-pregledovalnik
- Slika 18: Pogovorni vmesnik za dokumentni Q&A
- Slika 19: Analitična plošča z grafi
- Slika 20: Odzivna mobilna postavitev

### Pripravljeni podnapisi slik

- Slika 1: Logična arhitektura sistema z glavnimi komponentami in zunanjimi integracijami.
- Slika 2: Podatkovni tokovi sistema od prijave uporabnika do asinhrone obdelave dokumenta.
- Slika 3: Začetna stran aplikacije za neprijavljenega uporabnika.
- Slika 4: Obrazec za registracijo oziroma prijavo v sistem.
- Slika 5: Pregled dokumentov prijavljenega uporabnika.
- Slika 6: Uporabniški vmesnik za nalaganje PDF-dokumentov.
- Slika 7: Primer AI-generiranega povzetka izbranega dokumenta.
- Slika 8: Primer dokumentnega Q&A nad vsebino naloženega dokumenta.
- Slika 9: Administracijska plošča s statistiko sistema in upravljanjem uporabnikov.
- Slika 10: Uporabniški profil s ključnimi informacijami o računu in aktivnosti.
- Slika 11: OpenAPI-dokumentacija aplikacije v okolju Swagger UI.
- Slika 12: OpenAPI-dokumentacija aplikacije v okolju ReDoc.
- Slika 13: Primer varnostnih glav v HTTP-odzivu produkcijske aplikacije.
- Slika 14: Stanje Docker-vsebnikov na produkcijskem VPS-strežniku.
- Slika 15: Uspešen produkcijski deployment z uporabo skripte `deploy.sh`.
- Slika 16: CI/CD pipeline v GitHub Actions po uspešno izvedenem preverjanju.
- Slika 17: Vgrajeni PDF-pregledovalnik v uporabniškem vmesniku.
- Slika 18: Pogovorni vmesnik za dokumentni Q&A z zgodovino vprašanj in odgovorov.
- Slika 19: Analitična plošča z grafičnim prikazom stanja dokumentov in aktivnosti.
- Slika 20: Odzivna mobilna postavitev aplikacije na manjšem zaslonu.

### Priporočen vrstni red tabel

- Tabela 1: Skupine API-endpointov
- Tabela 2: Povzetek varnostnih tveganj in ukrepov
- Tabela 3: Konkretna stroškovna tabela
- Tabela 4: Primerjava z managed alternativo
- Tabela 5: Uporabljene tehnologije in namen

### Kaj odstrani iz končne Word-verzije

- vse vrstice tipa "POSNETEK X" kot delovne opombe
- surove Markdown code blocke, če bodo diagrami že vstavljeni kot slike
- tehnične opombe zase, ki niso namenjene bralcu
- podvojene razlage istih funkcionalnosti v več poglavjih

### Kaj doda profesionalen vtis

- enotna velikost in poravnava vseh slik
- podnapisi pod vsako sliko in tabelo
- sklicevanje v besedilu: "kot prikazuje Slika 1" ali "iz Tabele 3 je razvidno"
- brez preveč dolgih alinej; daljše sezname pretvori v odstavke ali tabele
- dosledna raba strokovnih izrazov: rešitev, arhitektura, podatkovna baza, objektna hramba, avtentikacija, avtorizacija

## SCREENSHOT LIST — zajeti in vstaviti v Word dokument

Spodaj je natančen seznam posnetkov zaslona, ki jih morate zajeti in vstaviti v Word dokument.
Za vsak posnetek je navedena **lokacija v Word dokumentu** (poglavje) in **navodilo kako ga zajeti**.

### Poglavje 7 — Arhitektura

| # | Posnetek | Kako zajeti | Kam v Word |
|---|----------|-------------|------------|
| 1 | **Arhitekturni diagram** | Render Mermaid iz `docs/diagrams/architecture.mmd` v PNG (https://mermaid.live/) | Slika 1 v poglavju 7.1 |
| 2 | **Podatkovni tok diagram** | Render Mermaid iz `docs/diagrams/data-flow.mmd` v PNG | Slika 2 v poglavju 8 |

### Poglavje 12 — Implementacijska validacija

| # | Posnetek | Kako zajeti | Kam v Word |
|---|----------|-------------|------------|
| 3 | **Landing page** | Odpri https://doc-ai-assist.com (nisi prijavljen) | Slika 3 — „Začetna stran aplikacije" |
| 4 | **Registracija / Prijava** | Klikni Registracija ali Prijava na landing page | Slika 4 — „Registracijski obrazec" |
| 5 | **Dashboard z dokumenti** | Po prijavi — stran Dokumenti z naloženim PDF | Slika 5 — „Preglednica dokumentov" |
| 6 | **Upload stran** | Klikni „Naloži" v sidebar-u | Slika 6 — „Nalaganje dokumenta" |
| 7 | **AI povzetek** | Na dokumentu klikni Povzemi in počakaj rezultat | Slika 7 — „AI-generiran povzetek dokumenta" |
| 8 | **Q&A primer** | Postavi vprašanje nad dokumentom | Slika 8 — „Dokumentni Q&A — vprašanje in odgovor" |
| 9 | **Admin panel** | Klikni Admin v sidebar-u (kot admin uporabnik) | Slika 9 — „Administracijska plošča" |
| 10 | **User profil** | Klikni Profil v sidebar-u | Slika 10 — „Uporabniški profil" |
| 11 | **Swagger UI** | Odpri https://doc-ai-assist.com/docs | Slika 11 — „OpenAPI dokumentacija (Swagger UI)" |
| 12 | **ReDoc** | Odpri https://doc-ai-assist.com/redoc | Slika 12 — „OpenAPI dokumentacija (ReDoc)" |

### Poglavje 12.3 — Operativna validacija

| # | Posnetek | Kako zajeti | Kam v Word |
|---|----------|-------------|------------|
| 13 | **Security headers** | V terminalu: `curl -I https://doc-ai-assist.com` | Slika 13 — „Varnostne glave HTTP odgovorov" |
| 14 | **docker compose ps** | Na VPS: `docker compose -f ... ps` | Slika 14 — „Stanje Docker containerjev na VPS" |
| 15 | **Deploy script output** | Na VPS: `bash infrastructure/scripts/deploy.sh` (ali screencapture prejšnjega) | Slika 15 — „Uspešen deployment na VPS" |
| 16 | **GitHub Actions CI** | Odpri GitHub repo → Actions → zadnji zeleni pipeline | Slika 16 — „CI pipeline (GitHub Actions)" |

## Recommended appendices za Word dokument

- Appendix A: `.env.production.example` (primer konfiguracije)
- Appendix B: API endpoint tabela (vseh 24 endpointov)
- Appendix C: Tabela uporabljenih tehnologij in verzij
- Appendix D: Povezava do repozitorija (https://github.com/mvelkov9/ai-document-assistant)
- Appendix E: Povezava do produkcijskega URL-ja (https://doc-ai-assist.com)

## Report improvement notes (v1.5.x additions already implemented)

Naslednje točke so smiselne za končno Word verzijo, ker pomagajo nasloviti pomislek, da je GUI preveč skromen:

### Dodatni posnetki zaslona (Slika 17–20)

| # | Posnetek | Kako zajeti | Kam v Word |
|---|----------|-------------|------------|
| 17 | **In-app PDF viewer** | Odpri dokument v aplikaciji in prikaži PDF | Slika 17 — „Vgrajen PDF pregledovalnik" |
| 18 | **Chat Q&A vmesnik** | Prikaži pogovorni tok z AI nad dokumentom | Slika 18 — „Pogovorni vmesnik za dokumentni Q&A" |
| 19 | **Dashboard grafikoni** | Prikaži analitično stran z grafi | Slika 19 — „Analitična plošča z grafi" |
| 20 | **Mobilni pogled** | Odpri aplikacijo na mobilnem ali v emulatoru | Slika 20 — „Odzivna mobilna postavitev" |

### Razširitev poglavja 7 (Arhitektura)

- Dodaj sekcijo **7.6 Frontend arhitektura** z opisom komponentne strukture, PDF.js integracije, chat vmesnika in Chart.js vizualizacije
- Dodaj sekcijo **7.7 Odzivna zasnova** z opisom breakpointov in mobilne izkušnje

### Razširitev poglavja 11 (Kritična ocena)

- V sekcijo 11.1 (Prednosti) dodaj: bogat uporabniški vmesnik z vgrajenim PDF pregledovalnikom, pogovornim Q&A vmesnikom in analitičnimi grafi
- To neposredno naslovi pomislek, da "na GUI ni ravno veliko za početi". V resnici ima aplikacija več ločenih uporabniških tokov: prijava, nalaganje, pregled dokumentov, PDF ogled, AI povzetek, Q&A, oznake, download, admin statistika in upravljanje vlog.

### Razširitev poglavja 12 (Implementacijska validacija)

- Dodaj sekcijo **12.6 Frontend validacija** s posnetki zaslona vseh novih funkcionalnosti

### Posodobitev poglavja 13 (Zaključek)

- Posodobi seznam realiziranih elementov za višjo oceno z novimi funkcionalnostmi
