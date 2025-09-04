"""Script to analyze and import Flox_persons.xlsx data."""

import sys
import pandas as pd
from pathlib import Path
from src.importers import ExcelImporter
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")

def analyze_excel_structure():
    """Analyze the structure of Flox_persons.xlsx."""
    
    file_path = Path("Flox_persons.xlsx")
    
    # Initialize importer
    importer = ExcelImporter(file_path)
    
    # Get sheets information
    sheets_info = importer.get_sheets_info()
    print("\n=== EXCEL FILE STRUCTURE ===")
    print(f"Number of sheets: {sheets_info.get('sheet_count', 0)}")
    print(f"Sheet names: {sheets_info.get('sheet_names', [])}")
    
    # Load the first sheet (or all sheets if multiple)
    print("\n=== LOADING DATA ===")
    df = importer.import_data()
    
    print(f"\nData shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"\nColumn names:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")
    
    print("\n=== DATA TYPES ===")
    print(df.dtypes)
    
    print("\n=== FIRST 5 ROWS ===")
    print(df.head())
    
    # Analyze groups column specifically
    if 'groups' in df.columns:
        print("\n=== GROUPS ANALYSIS ===")
        print(f"Sample group values:")
        # Show unique values if not too many
        unique_groups = df['groups'].dropna().head(10)
        for i, group in enumerate(unique_groups, 1):
            print(f"  {i}. {group}")
        
        # Count non-null groups
        groups_count = df['groups'].notna().sum()
        print(f"\nStudents with groups: {groups_count}/{len(df)}")
    
    # Check for null values
    print("\n=== NULL VALUES ===")
    null_counts = df.isnull().sum()
    print(null_counts[null_counts > 0])
    
    return df


if __name__ == "__main__":
    df = analyze_excel_structure()