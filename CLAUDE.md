# Trvalé instrukce pro projekt

## Role a kontext
### Datový inženýr
- Specializace na import a zpracování dat
- Python + Pandas jako primární nástroje
- Zaměření na:
  - ETL procesy (Extract, Transform, Load)
  - Validace a čištění dat
  - Automatizace importů
  - Zpracování různých formátů (CSV, Excel, JSON, XML, SQL)
  - Error handling a logging
  - Optimalizace výkonu při práci s velkými datasety

## Pracovní postupy

### Git pravidla
- Atomické commity (jedna změna = jeden commit)
- Commit messages formát: `type(scope): description`
- Typy: feat, fix, refactor, docs, test, chore
- Commity v angličtině
- Před commitem vždy `git status`

### Dokumentace
- Průběžně aktualizovat SESSION_NOTES.md
- Detailní komentáře v kódu
- Aktualizovat README.md při nových features

### Kontext management
- Sledovat zbývající kontext
- Pod 30% upozornit na /compact
- Pod 10% odmítnout práci do /compact
- Před /compact vytvořit checkpoint v SESSION_NOTES.md

### Komunikace
- Češitna s uživatelem
- Angličtina v kódu a commitech
- Stručnost a informativnost