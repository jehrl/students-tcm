"""Excel file importer implementation."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from loguru import logger

from .base_importer import BaseImporter


class ExcelImporter(BaseImporter):
    """Importer for Excel files (.xlsx, .xls)."""
    
    def __init__(self,
                 source: Union[str, Path],
                 encoding: str = 'utf-8',
                 validate: bool = True,
                 sheet_name: Optional[Union[str, int, List]] = 0):
        """
        Initialize Excel importer.
        
        Args:
            source: Path to Excel file
            encoding: File encoding (not typically used for Excel)
            validate: Whether to validate data
            sheet_name: Sheet name or index to read
        """
        super().__init__(source, encoding, validate)
        self.sheet_name = sheet_name
        self._sheets_info: Dict[str, Any] = {}
    
    def load(self, **kwargs) -> pd.DataFrame:
        """
        Load data from Excel file.
        
        Kwargs:
            header: Row number to use as column names
            usecols: Columns to parse
            nrows: Number of rows to parse
            skiprows: Rows to skip at the beginning
            dtype: Data type for columns
            
        Returns:
            Loaded DataFrame
        """
        try:
            # Get sheet information first
            self._sheets_info = self.get_sheets_info()
            
            # Merge parameters
            read_params = {
                'io': self.source,
                'sheet_name': self.sheet_name,
                'engine': 'openpyxl'  # Modern Excel files
            }
            read_params.update(kwargs)
            
            logger.info(f"Loading Excel file: {self.source}")
            
            # Handle multiple sheets
            if isinstance(self.sheet_name, list) or self.sheet_name is None:
                dfs = pd.read_excel(**read_params)
                # Combine multiple sheets if needed
                if isinstance(dfs, dict):
                    logger.info(f"Loaded {len(dfs)} sheets")
                    # Return first sheet by default, or combine as needed
                    sheet_name = list(dfs.keys())[0]
                    df = dfs[sheet_name]
                    logger.info(f"Using sheet: {sheet_name}")
                else:
                    df = dfs
            else:
                df = pd.read_excel(**read_params)
                logger.info(f"Loaded sheet: {self.sheet_name}")
            
            logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except FileNotFoundError:
            logger.error(f"File not found: {self.source}")
            raise
        except ValueError as e:
            logger.error(f"Error reading Excel file: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate Excel data.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if validation passes
        """
        validation_errors = []
        
        # Basic validation
        if df.empty:
            validation_errors.append("DataFrame is empty")
        
        # Check for duplicate columns
        if df.columns.duplicated().any():
            duplicates = df.columns[df.columns.duplicated()].tolist()
            validation_errors.append(f"Duplicate columns: {duplicates}")
        
        # Check for unnamed columns (common in Excel)
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            logger.warning(f"Found {len(unnamed_cols)} unnamed columns")
        
        # Check for completely null rows (often at the end of Excel files)
        null_rows = df[df.isnull().all(axis=1)]
        if not null_rows.empty:
            logger.warning(f"Found {len(null_rows)} completely empty rows")
        
        if validation_errors:
            for error in validation_errors:
                logger.error(f"Validation error: {error}")
            return False
        
        logger.success("Excel validation passed")
        return True
    
    def get_sheets_info(self) -> Dict[str, Any]:
        """
        Get information about all sheets in the Excel file.
        
        Returns:
            Dictionary with sheet information
        """
        try:
            xl_file = pd.ExcelFile(self.source, engine='openpyxl')
            sheets_info = {
                'sheet_names': xl_file.sheet_names,
                'sheet_count': len(xl_file.sheet_names)
            }
            
            # Get row count for each sheet (requires reading)
            sheet_details = {}
            for sheet in xl_file.sheet_names:
                try:
                    df = pd.read_excel(xl_file, sheet_name=sheet, nrows=0)
                    sheet_details[sheet] = {
                        'columns': list(df.columns),
                        'column_count': len(df.columns)
                    }
                except Exception as e:
                    logger.warning(f"Could not read sheet '{sheet}': {e}")
            
            sheets_info['sheet_details'] = sheet_details
            return sheets_info
            
        except Exception as e:
            logger.error(f"Error getting sheets info: {e}")
            return {}
    
    def load_all_sheets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all sheets from the Excel file.
        
        Returns:
            Dictionary mapping sheet names to DataFrames
        """
        try:
            logger.info(f"Loading all sheets from {self.source}")
            dfs = pd.read_excel(self.source, sheet_name=None, engine='openpyxl')
            
            for sheet_name, df in dfs.items():
                logger.info(f"Sheet '{sheet_name}': {df.shape[0]} rows, {df.shape[1]} columns")
            
            return dfs
            
        except Exception as e:
            logger.error(f"Error loading all sheets: {e}")
            raise
    
    def clean_excel_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean common Excel data issues.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        # Remove completely empty rows and columns
        df = df.dropna(how='all', axis=0)
        df = df.dropna(how='all', axis=1)
        
        # Remove unnamed columns
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            # Check if they're actually empty
            empty_unnamed = [col for col in unnamed_cols if df[col].isna().all()]
            if empty_unnamed:
                df = df.drop(columns=empty_unnamed)
                logger.info(f"Removed {len(empty_unnamed)} empty unnamed columns")
        
        # Strip whitespace from string columns
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        
        return df