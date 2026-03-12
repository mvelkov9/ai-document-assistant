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
- API zasnova (21 endpointov)

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
- tabela glavnih API endpointov (21 endpointov)
- tabela varnostnih tveganj in mitigacij
- tabela stroškovnih scenarijev
- tabela uporabljenih tehnologij in verzij

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
- Appendix B: API endpoint tabela (vseh 21 endpointov)
- Appendix C: Tabela uporabljenih tehnologij in verzij
- Appendix D: Povezava do repozitorija (https://github.com/mvelkov9/ai-document-assistant)
- Appendix E: Povezava do produkcijskega URL-ja (https://doc-ai-assist.com)

## Report improvement notes (v1.5.0 additions)

Ko bodo implementirane v1.5.0 faze, je treba v report dodati naslednje:

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
- To naslovi uporabnikovo skrb, da "na GUI ni ravno veliko za početi" — z v1.5.0 bo GUI postal osrednji del izkušnje

### Razširitev poglavja 12 (Implementacijska validacija)

- Dodaj sekcijo **12.6 Frontend validacija** s posnetki zaslona vseh novih funkcionalnosti

### Posodobitev poglavja 13 (Zaključek)

- Posodobi seznam realiziranih elementov za višjo oceno z novimi funkcionalnostmi
