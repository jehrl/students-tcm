"""Detailed analysis of the Excel structure and data patterns."""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
import re
from typing import Dict, List, Set, Tuple

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')


def analyze_excel_in_detail():
    """Perform deep analysis of the Excel file structure."""
    
    print("=" * 80)
    print("DETAILNÍ ANALÝZA STRUKTURY DAT - FLOX_PERSONS.XLSX")
    print("=" * 80)
    
    # Load Excel file
    xl_file = pd.ExcelFile('Flox_persons.xlsx', engine='openpyxl')
    
    print("\n1. STRUKTURA EXCEL SOUBORU:")
    print("-" * 40)
    print(f"Počet listů: {len(xl_file.sheet_names)}")
    print(f"Názvy listů: {', '.join(xl_file.sheet_names)}")
    
    # Analyze each sheet
    all_sheets = {}
    for sheet_name in xl_file.sheet_names:
        df = pd.read_excel(xl_file, sheet_name=sheet_name)
        all_sheets[sheet_name] = df
        print(f"\nList '{sheet_name}':")
        print(f"  - Počet řádků: {len(df)}")
        print(f"  - Počet sloupců: {len(df.columns)}")
        print(f"  - Sloupce: {', '.join(df.columns[:10])}")
        if len(df.columns) > 10:
            print(f"    ... a {len(df.columns) - 10} dalších sloupců")
    
    # Focus on persons sheet
    df_persons = all_sheets['persons']
    
    print("\n2. ANALÝZA SLOUPCŮ V LISTU 'PERSONS':")
    print("-" * 40)
    
    for col in df_persons.columns:
        non_null = df_persons[col].notna().sum()
        null_count = df_persons[col].isna().sum()
        unique_count = df_persons[col].nunique()
        dtype = df_persons[col].dtype
        
        print(f"\n{col}:")
        print(f"  - Typ: {dtype}")
        print(f"  - Vyplněno: {non_null}/{len(df_persons)} ({non_null/len(df_persons)*100:.1f}%)")
        print(f"  - Prázdných: {null_count}")
        print(f"  - Unikátních hodnot: {unique_count}")
        
        # Show sample values for important columns
        if col in ['groups', 'internal_note'] and non_null > 0:
            sample_values = df_persons[col].dropna().head(3)
            print(f"  - Ukázka hodnot:")
            for i, val in enumerate(sample_values, 1):
                print(f"    {i}. {str(val)[:100]}...")
    
    # Analyze addresses sheet
    if 'addresses' in all_sheets:
        df_addresses = all_sheets['addresses']
        print("\n3. ANALÝZA LISTU 'ADDRESSES':")
        print("-" * 40)
        print(f"Počet adres: {len(df_addresses)}")
        print(f"Sloupce: {', '.join(df_addresses.columns)}")
    
    # Detailed groups analysis
    print("\n4. DETAILNÍ ANALÝZA SKUPIN (GROUPS):")
    print("-" * 40)
    
    # Extract all individual groups
    all_groups = []
    group_patterns = defaultdict(list)
    
    for groups_str in df_persons['groups'].dropna():
        groups_list = [g.strip() for g in str(groups_str).split(',') if g.strip()]
        all_groups.extend(groups_list)
        
        for group in groups_list:
            # Categorize groups by patterns
            if 'LEKTOŘI' in group or 'LEKTOR' in group:
                group_patterns['LEKTOŘI'].append(group)
            elif 'STUDIUM' in group:
                group_patterns['STUDIUM'].append(group)
            elif 'SEMINÁŘ' in group:
                group_patterns['SEMINÁŘ'].append(group)
            elif re.search(r'G\d+', group):  # G1, G2, etc.
                group_patterns['GENERACE'].append(group)
            elif 'TCM' in group or 'TČM' in group:
                group_patterns['TCM_KURZY'].append(group)
            elif 'AKU' in group:
                group_patterns['AKUPUNKTURA'].append(group)
            elif 'FYTO' in group or 'FYTOTERAPIE' in group:
                group_patterns['FYTOTERAPIE'].append(group)
            elif 'TUINA' in group:
                group_patterns['TUINA'].append(group)
            elif 'QIGONG' in group:
                group_patterns['QIGONG'].append(group)
            elif 'ČLEN' in group or 'ČLENOVÉ' in group:
                group_patterns['ČLENSTVÍ'].append(group)
            elif 'ADMIN' in group:
                group_patterns['ADMIN'].append(group)
            else:
                group_patterns['OSTATNÍ'].append(group)
    
    # Count occurrences
    group_counts = Counter(all_groups)
    
    print(f"Celkový počet unikátních skupin: {len(group_counts)}")
    print(f"Celkový počet přiřazení ke skupinám: {sum(group_counts.values())}")
    
    print("\nKategorie skupin:")
    for category, groups in group_patterns.items():
        unique_groups = set(groups)
        print(f"\n{category}: {len(unique_groups)} unikátních skupin")
        # Show top 3 most common
        category_counts = Counter(groups)
        for group, count in category_counts.most_common(3):
            print(f"  - {group}: {count}x")
    
    # Analyze year patterns in groups
    print("\n5. ANALÝZA ČASOVÝCH ÚDAJŮ VE SKUPINÁCH:")
    print("-" * 40)
    
    years_found = defaultdict(list)
    year_pattern = re.compile(r'(\d{4})')
    
    for group in group_counts.keys():
        years = year_pattern.findall(group)
        for year in years:
            years_found[year].append(group)
    
    sorted_years = sorted(years_found.keys())
    print(f"Nalezené roky: {', '.join(sorted_years)}")
    print(f"Rozsah: {sorted_years[0]} - {sorted_years[-1]}" if sorted_years else "Žádné roky nenalezeny")
    
    # Analyze student distribution
    print("\n6. DISTRIBUCE STUDENTŮ:")
    print("-" * 40)
    
    groups_per_student = []
    for groups_str in df_persons['groups'].dropna():
        groups_list = [g.strip() for g in str(groups_str).split(',') if g.strip()]
        groups_per_student.append(len(groups_list))
    
    if groups_per_student:
        print(f"Průměrný počet skupin na studenta: {np.mean(groups_per_student):.2f}")
        print(f"Medián počtu skupin na studenta: {np.median(groups_per_student):.0f}")
        print(f"Maximum skupin u jednoho studenta: {max(groups_per_student)}")
        print(f"Minimum skupin u studenta (který má skupiny): {min(groups_per_student)}")
    
    # Analyze email patterns
    print("\n7. ANALÝZA EMAILOVÝCH ADRES:")
    print("-" * 40)
    
    email_domains = defaultdict(int)
    invalid_emails = []
    
    for email in df_persons['email'].dropna():
        email_str = str(email).strip().lower()
        if '@' in email_str:
            domain = email_str.split('@')[1]
            email_domains[domain] += 1
        else:
            invalid_emails.append(email_str)
    
    print(f"Celkem emailů: {df_persons['email'].notna().sum()}")
    print(f"Unikátních domén: {len(email_domains)}")
    print(f"Neplatných emailů: {len(invalid_emails)}")
    
    print("\nTop 10 emailových domén:")
    for domain, count in sorted(email_domains.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {domain}: {count}x")
    
    # Address analysis
    print("\n8. ANALÝZA ADRES:")
    print("-" * 40)
    
    # Count filled address fields
    address_fields = ['address_street', 'address_city', 'address_zip', 'address_country']
    for field in address_fields:
        filled = df_persons[field].notna().sum()
        print(f"{field}: {filled}/{len(df_persons)} ({filled/len(df_persons)*100:.1f}%)")
    
    # Analyze countries
    if 'address_country' in df_persons.columns:
        countries = df_persons['address_country'].value_counts().head(5)
        print("\nTop 5 zemí:")
        for country, count in countries.items():
            print(f"  - {country}: {count}x")
    
    # Data quality issues
    print("\n9. POTENCIÁLNÍ PROBLÉMY S DATY:")
    print("-" * 40)
    
    # Check for duplicates
    duplicate_emails = df_persons[df_persons['email'].duplicated(keep=False) & df_persons['email'].notna()]
    if not duplicate_emails.empty:
        print(f"⚠️  Duplicitní emaily: {len(duplicate_emails)} záznamů")
        print(f"   Unikátních duplicitních emailů: {duplicate_emails['email'].nunique()}")
    
    # Check for missing critical data
    missing_name = df_persons[(df_persons['name'].isna()) | (df_persons['surname'].isna())]
    if not missing_name.empty:
        print(f"⚠️  Záznamy bez jména nebo příjmení: {len(missing_name)}")
    
    # Check for inconsistent data
    both_address_fields = df_persons[(df_persons['address'].notna()) & 
                                     (df_persons['address_street'].notna())]
    if not both_address_fields.empty:
        print(f"⚠️  Záznamy s duplicitními adresními poli: {len(both_address_fields)}")
    
    print("\n10. DOPORUČENÍ PRO DATABÁZOVÝ MODEL:")
    print("-" * 40)
    print("""
    Na základě analýzy doporučuji následující strukturu:
    
    1. TABULKA: students (hlavní tabulka studentů)
       - user_id (PK)
       - email (UNIQUE, NOT NULL)
       - name, surname, title
       - active (boolean)
       - newsletter (boolean)
       - internal_note (TEXT)
       - created_at, updated_at
    
    2. TABULKA: addresses (adresy - 1:1 nebo 1:N se studenty)
       - address_id (PK)
       - user_id (FK -> students)
       - street, descriptive_number, orientation_number
       - city, zip, state, country
       - phone
       - is_primary (boolean)
    
    3. TABULKA: groups (kurzy/skupiny)
       - group_id (PK)
       - name (UNIQUE)
       - category (ENUM: STUDIUM, SEMINÁŘ, LEKTOŘI, ...)
       - year_from, year_to (extrahované z názvu)
       - is_active (boolean)
       - description
    
    4. TABULKA: student_groups (vazební tabulka M:N)
       - student_id (FK -> students)
       - group_id (FK -> groups)
       - enrolled_at
       - completed_at
       - status (ENUM: active, completed, dropped)
       - PRIMARY KEY (student_id, group_id)
    
    5. TABULKA: group_categories (číselník kategorií)
       - category_id (PK)
       - name
       - description
    """)
    
    return df_persons, all_sheets


if __name__ == "__main__":
    df_persons, all_sheets = analyze_excel_in_detail()