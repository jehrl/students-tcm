"""Compare contacts from kontakty.csv with existing database."""

import pandas as pd
import json
from pathlib import Path
import sys

def analyze_contacts():
    """Analyze and compare contacts from CSV with existing database."""
    
    print("=" * 80)
    print("ANALÝZA KONTAKTŮ - POROVNÁNÍ S DATABÁZÍ")
    print("=" * 80)
    
    # Load kontakty.csv
    print("\n1. NAČÍTÁM KONTAKTY.CSV...")
    try:
        # Try different encodings
        encodings = ['utf-8', 'cp1250', 'iso-8859-2', 'windows-1250']
        df_contacts = None
        
        for encoding in encodings:
            try:
                df_contacts = pd.read_csv('kontakty.csv', encoding=encoding)
                print(f"   ✓ Soubor načten s kódováním: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if df_contacts is None:
            print("   ✗ Nepodařilo se načíst soubor s žádným kódováním")
            return
            
    except Exception as e:
        print(f"   ✗ Chyba při načítání: {e}")
        return
    
    print(f"   - Počet záznamů: {len(df_contacts)}")
    print(f"   - Počet sloupců: {len(df_contacts.columns)}")
    print(f"   - Sloupce: {', '.join(df_contacts.columns[:10])}")
    if len(df_contacts.columns) > 10:
        print(f"     ... a {len(df_contacts.columns) - 10} dalších")
    
    # Show first few rows
    print("\n   Ukázka dat:")
    print(df_contacts.head(3).to_string())
    
    # Find email column
    email_columns = [col for col in df_contacts.columns if 'email' in col.lower() or 'e-mail' in col.lower()]
    if not email_columns:
        # Try to find column with @ symbol
        for col in df_contacts.columns:
            sample = df_contacts[col].dropna().astype(str).head(10)
            if sample.str.contains('@').any():
                email_columns.append(col)
                break
    
    if not email_columns:
        print("\n   ⚠️ Nenalezen sloupec s emaily!")
        print("   Dostupné sloupce:", df_contacts.columns.tolist())
        return
    
    email_col = email_columns[0]
    print(f"\n   Email sloupec: {email_col}")
    
    # Extract emails from kontakty.csv
    contacts_emails = set()
    for email in df_contacts[email_col].dropna():
        email_str = str(email).strip().lower()
        if '@' in email_str:
            contacts_emails.add(email_str)
    
    print(f"\n2. STATISTIKY KONTAKTY.CSV:")
    print(f"   - Celkem záznamů: {len(df_contacts)}")
    print(f"   - Záznamů s emaily: {len(contacts_emails)}")
    print(f"   - Unikátních emailů: {len(contacts_emails)}")
    
    # Load existing database
    print("\n3. NAČÍTÁM EXISTUJÍCÍ DATABÁZI...")
    students_file = Path('data/processed/students.json')
    
    if not students_file.exists():
        print("   ✗ Soubor students.json neexistuje!")
        return
    
    with open(students_file, 'r', encoding='utf-8') as f:
        students = json.load(f)
    
    # Extract emails from database
    db_emails = set()
    for student in students:
        if student.get('email'):
            email = student['email'].strip().lower()
            db_emails.add(email)
    
    print(f"   - Studentů v databázi: {len(students)}")
    print(f"   - Emailů v databázi: {len(db_emails)}")
    
    # Compare
    print("\n4. POROVNÁNÍ:")
    print("=" * 40)
    
    # Emails in kontakty but not in database
    missing_in_db = contacts_emails - db_emails
    
    # Emails in database but not in kontakty
    missing_in_contacts = db_emails - contacts_emails
    
    # Common emails
    common_emails = contacts_emails & db_emails
    
    print(f"   📊 Emaily v obou souborech: {len(common_emails)}")
    print(f"   ⚠️  Emaily v kontakty.csv, ale NE v databázi: {len(missing_in_db)}")
    print(f"   ℹ️  Emaily v databázi, ale NE v kontakty.csv: {len(missing_in_contacts)}")
    
    # Create detailed report for missing contacts
    if missing_in_db:
        print("\n5. KONTAKTY CHYBĚJÍCÍ V DATABÁZI:")
        print("-" * 40)
        
        # Get full info for missing contacts
        missing_contacts = []
        for idx, row in df_contacts.iterrows():
            if row[email_col] and str(row[email_col]).strip().lower() in missing_in_db:
                contact_info = {
                    'email': str(row[email_col]).strip(),
                    'row_number': idx + 2,  # +2 for header and 0-index
                }
                
                # Add other relevant columns
                for col in df_contacts.columns:
                    if col != email_col and pd.notna(row[col]):
                        contact_info[col] = str(row[col])
                
                missing_contacts.append(contact_info)
        
        # Sort by email
        missing_contacts.sort(key=lambda x: x['email'])
        
        # Show first 20
        print(f"\n   Prvních {min(20, len(missing_contacts))} chybějících kontaktů:")
        for i, contact in enumerate(missing_contacts[:20], 1):
            print(f"\n   {i}. Email: {contact['email']} (řádek {contact['row_number']})")
            # Show other available info
            for key, value in contact.items():
                if key not in ['email', 'row_number']:
                    print(f"      {key}: {value[:50]}...")
        
        if len(missing_contacts) > 20:
            print(f"\n   ... a {len(missing_contacts) - 20} dalších")
        
        # Save missing contacts to file
        output_file = Path('data/processed/missing_contacts.json')
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(missing_contacts, f, ensure_ascii=False, indent=2)
        
        print(f"\n   ✓ Seznam chybějících kontaktů uložen do: {output_file}")
        
        # Also save as CSV for easier review
        csv_output = Path('data/processed/missing_contacts.csv')
        pd.DataFrame(missing_contacts).to_csv(csv_output, index=False, encoding='utf-8')
        print(f"   ✓ CSV verze uložena do: {csv_output}")
    
    # Summary
    print("\n6. SOUHRN:")
    print("=" * 40)
    if missing_in_db:
        print(f"⚠️  NAŠEL JSEM {len(missing_in_db)} NOVÝCH KONTAKTŮ, KTERÉ NEJSOU V DATABÁZI!")
        print("   Tyto kontakty by měly být importovány do systému.")
    else:
        print("✅ Všechny kontakty z kontakty.csv jsou již v databázi.")
    
    return missing_contacts if missing_in_db else []


if __name__ == "__main__":
    missing = analyze_contacts()