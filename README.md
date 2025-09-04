# Projekt - TCM Převod Studenti

## O projektu
Projekt pro import a zpracování dat studentů z Excel souborů do databáze.
Specializace na ETL procesy, validaci dat a správu vztahů mezi studenty a kurzy.

## Struktura projektu
```
studenti/
├── src/
│   ├── importers/     # Moduly pro import různých formátů dat
│   ├── validators/    # Validace dat
│   └── transformers/  # Transformace dat
├── data/
│   ├── raw/          # Surová vstupní data
│   └── processed/    # Zpracovaná data
├── tests/            # Testy
├── config/           # Konfigurace
├── logs/             # Logy
├── requirements.txt  # Python závislosti
├── CLAUDE.md         # Trvalé instrukce pro AI asistenta
├── SESSION_NOTES.md  # Průběžná dokumentace práce
├── README.md         # Dokumentace projektu
└── .gitignore        # Seznam ignorovaných souborů
```

## Instalace

### Požadavky
- Python 3.8+
- pip

### Kroky instalace

1. Vytvořte virtuální prostředí:
```bash
python -m venv venv
```

2. Aktivujte virtuální prostředí:
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Nainstalujte závislosti:
```bash
pip install -r requirements.txt
```

## Použití

### Import dat studentů z Excel

```python
from src.importers import ExcelImporter

# Inicializace importeru
importer = ExcelImporter('data/raw/Flox_persons.xlsx')

# Import dat
df = importer.import_data()

# Získání metadat
metadata = importer.get_metadata()
```

### Datový model

#### Tabulka: students
- ID studenta
- Jméno a příjmení
- Email
- Další kontaktní údaje

#### Tabulka: groups (kurzy)
- ID skupiny/kurzu
- Název skupiny
- Popis
- Metadata

#### Tabulka: student_groups (vazební tabulka)
- ID studenta
- ID skupiny
- Datum přiřazení

## Vývoj
Projekt využívá Claude AI asistenta pro vývoj s následujícími pravidly:
- Atomické commity
- Detailní dokumentace
- Průběžné testování

## Licence
*Bude doplněno*