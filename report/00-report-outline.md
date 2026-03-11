# Report Outline

## Working title

Razvoj integrirane spletne storitve za varno upravljanje dokumentov z AI povzetki in dokumentnim Q&A v oblacni arhitekturi

## Required document structure

1. Naslovnica
2. Povzetek in kljucne besede v slovenscini
3. Abstract and keywords in English
4. Uvod
5. Arhitekturni opis resitve
6. Analiza integracije in podatkovnih tokov
7. Analiza varnosti
8. Stroskovna analiza
9. Kriticna ocena primernosti
10. Zakljucek
11. Seznam virov

## Suggested chapter expansion

### 1. Uvod

- predstavitev problema
- cilji naloge
- raziskovalni oziroma razvojni pristop
- metodologija dela

### 2. Poslovni in tehnicni scenarij

- profil ciljne organizacije
- potreba po varni hrambi dokumentov
- razlogi za integracijo AI funkcionalnosti
- vecuporabniski vidik in arhitekturne zahteve

### 3. Arhitektura sistema

- logicna arhitektura
- deployment arhitektura na VPS
- opis komponent: Vue, FastAPI, PostgreSQL, MinIO, AI adapter, reverse proxy
- arhitekturni diagram

### 4. Analiza integracije in podatkovnih tokov

- prijava in avtorizacija
- upload dokumenta
- hramba v MinIO in metapodatki v bazi
- summary job tok
- dokumentni Q&A tok
- diagram podatkovnih tokov

### 5. Analiza varnosti

- JWT in upravljanje dostopa
- zasebnost dokumentov
- obravnava AI integracije in prompt tveganj
- varovanje skrivnosti in `.env` pristop
- readiness, logging, backup in operativni minimum

### 6. Stroskovna analiza

- strosek VPS
- strosek domene in TLS
- strosek AI API klicev
- primerjava z managed alternativo
- scenariji: osnovni, razsirjeni, skalirani

### 7. Kriticna ocena primernosti

- prednosti izbrane resitve
- slabosti in omejitve
- primernost za slovensko organizacijo
- primerjava z managed PaaS pristopom

### 8. Implementacija in rezultati

- kratek opis dejanske implementacije
- predstavitev API in OpenAPI dokumentacije
- opis CI/CD, testov in deployment poti
- prikaz demo scenarija

### 9. Zakljucek

- povzetek dosezenih ciljev
- omejitve resitve
- moznosti nadaljnjega razvoja

## Required figures and tables

- glavni arhitekturni diagram
- diagram podatkovnih tokov
- tabela glavnih API endpointov
- tabela varnostnih tveganj in mitigacij
- tabela stroškovnih scenarijev

## Recommended appendices

- primer `.env.example`
- primer demo scenarija
- povezava do repozitorija
- seznam uporabljenih tehnologij in verzij
