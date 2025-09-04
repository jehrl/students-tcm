# Session Notes

## Datum: 2025-09-04

### Inicializace projektu
- Vytvořen nový git repository
- Nastaveny pracovní postupy v CLAUDE.md
- Vytvořena základní struktura projektu
- Nastavena role datového inženýra se specializací na Python/Pandas

### Analýza dat Flox_persons.xlsx
- **Struktura souboru:**
  - 2 listy: persons (2905 záznamů) a addresses (3749 záznamů)
  - 23 sloupců v persons listu
  - 149 unikátních skupin/kurzů
  
- **Klíčové zjištění:**
  - 70% studentů má přiřazené skupiny (2040 z 2905)
  - Průměrně 3.31 skupin na studenta
  - Největší skupina: "ČLENOVÉ TCM Servis" (1079 studentů)
  - Duplicitní adresní pole (strukturované vs. spojené)
  - Problém s roky ve skupinách (obsahují divné hodnoty)
  
- **Kategorie skupin:**
  - STUDIUM: 41 skupin
  - SEMINÁŘ: 35 skupin
  - LEKTOŘI: 34 skupin
  - KURZ: 35 skupin
  - ČLENOVÉ: 3 skupiny
  - ADMIN: 1 skupina

### Implementované moduly
- `src/importers/` - base_importer, csv_importer, excel_importer, json_importer
- `src/models.py` - Student, Group, StudentGroup modely
- `import_students.py` - hlavní import skript
- `analyze_flox_data.py` - základní analýza
- `detailed_analysis.py` - detailní analýza struktury

### Výstupní soubory
- `data/processed/students.json` - 2905 studentů
- `data/processed/groups.json` - 149 skupin
- `data/processed/student_groups.json` - 6758 vztahů
- CSV verze všech souborů

### Další kroky
- Vyřešit problém s roky ve skupinách
- Zpracovat list addresses
- Vytvořit SQL databázové schéma
- Implementovat validaci dat
- Přidat podporu pro inkrementální import

---