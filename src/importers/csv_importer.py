"""CSV file importer implementation."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from loguru import logger

from .base_importer import BaseImporter


class CSVImporter(BaseImporter):
    """Importer for CSV files with advanced options."""
    
    def __init__(self,
                 source: Union[str, Path],
                 encoding: str = 'utf-8',
                 validate: bool = True,
                 delimiter: str = ',',
                 quotechar: str = '"'):
        """
        Initialize CSV importer.
        
        Args:
            source: Path to CSV file
            encoding: File encoding
            validate: Whether to validate data
            delimiter: Field delimiter
            quotechar: Quote character
        """
        super().__init__(source, encoding, validate)
        self.delimiter = delimiter
        self.quotechar = quotechar
    
    def load(self, **kwargs) -> pd.DataFrame:
        """
        Load data from CSV file.
        
        Kwargs:
            nrows: Number of rows to read
            usecols: List of columns to use
            dtype: Dictionary of column types
            parse_dates: List of columns to parse as dates
            na_values: Additional strings to recognize as NA
            skip_rows: Number of rows to skip
            
        Returns:
            Loaded DataFrame
        """
        try:
            # Merge default parameters with kwargs
            read_params = {
                'filepath_or_buffer': self.source,
                'encoding': self.encoding,
                'delimiter': self.delimiter,
                'quotechar': self.quotechar,
                'engine': 'python',  # More flexible but slower
                'on_bad_lines': 'warn'
            }
            read_params.update(kwargs)
            
            logger.info(f"Loading CSV file: {self.source}")
            df = pd.read_csv(**read_params)
            
            # Log basic statistics
            logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
            logger.info(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            
            return df
            
        except FileNotFoundError:
            logger.error(f"File not found: {self.source}")
            raise
        except pd.errors.EmptyDataError:
            logger.error(f"Empty CSV file: {self.source}")
            raise
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate CSV data.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if validation passes
        """
        validation_errors = []
        
        # Check for empty DataFrame
        if df.empty:
            validation_errors.append("DataFrame is empty")
        
        # Check for duplicate columns
        if df.columns.duplicated().any():
            duplicates = df.columns[df.columns.duplicated()].tolist()
            validation_errors.append(f"Duplicate columns found: {duplicates}")
        
        # Check for completely null columns
        null_columns = df.columns[df.isnull().all()].tolist()
        if null_columns:
            validation_errors.append(f"Completely null columns: {null_columns}")
        
        # Log validation results
        if validation_errors:
            for error in validation_errors:
                logger.error(f"Validation error: {error}")
            return False
        
        logger.success("CSV validation passed")
        return True
    
    def detect_delimiter(self, sample_size: int = 10000) -> str:
        """
        Auto-detect the delimiter used in the CSV file.
        
        Args:
            sample_size: Number of bytes to read for detection
            
        Returns:
            Detected delimiter
        """
        import csv
        
        with open(self.source, 'r', encoding=self.encoding) as file:
            sample = file.read(sample_size)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
        logger.info(f"Detected delimiter: '{delimiter}'")
        return delimiter
    
    def get_column_stats(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for each column.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with column statistics
        """
        stats = {}
        
        for col in df.columns:
            col_stats = {
                'dtype': str(df[col].dtype),
                'null_count': df[col].isnull().sum(),
                'null_percentage': (df[col].isnull().sum() / len(df)) * 100,
                'unique_values': df[col].nunique(),
                'memory_usage': df[col].memory_usage(deep=True)
            }
            
            # Add numeric statistics if applicable
            if pd.api.types.is_numeric_dtype(df[col]):
                col_stats.update({
                    'mean': df[col].mean(),
                    'std': df[col].std(),
                    'min': df[col].min(),
                    'max': df[col].max()
                })
            
            stats[col] = col_stats
        
        return stats