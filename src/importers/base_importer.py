"""Base importer class for all data importers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from loguru import logger


class BaseImporter(ABC):
    """Abstract base class for data importers."""
    
    def __init__(self, 
                 source: Union[str, Path],
                 encoding: str = 'utf-8',
                 validate: bool = True):
        """
        Initialize the importer.
        
        Args:
            source: Path to the source file or connection string
            encoding: Character encoding for text files
            validate: Whether to validate data after import
        """
        self.source = Path(source) if isinstance(source, str) else source
        self.encoding = encoding
        self.validate = validate
        self._data: Optional[pd.DataFrame] = None
        self._metadata: Dict[str, Any] = {}
        
        logger.info(f"Initialized {self.__class__.__name__} for {self.source}")
    
    @abstractmethod
    def load(self, **kwargs) -> pd.DataFrame:
        """
        Load data from the source.
        
        Returns:
            DataFrame with loaded data
        """
        pass
    
    @abstractmethod
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate the loaded data.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if validation passes
        """
        pass
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply transformations to the data.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Transformed DataFrame
        """
        logger.info("Applying transformations...")
        
        # Remove leading/trailing whitespace from string columns
        string_columns = df.select_dtypes(include=['object']).columns
        df[string_columns] = df[string_columns].apply(lambda x: x.str.strip())
        
        # Convert column names to lowercase and replace spaces with underscores
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        return df
    
    def import_data(self, **kwargs) -> pd.DataFrame:
        """
        Main method to import and process data.
        
        Returns:
            Processed DataFrame
        """
        logger.info(f"Starting import from {self.source}")
        
        # Load data
        df = self.load(**kwargs)
        self._data = df
        
        # Store metadata
        self._metadata = {
            'source': str(self.source),
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        logger.info(f"Loaded {df.shape[0]} rows and {df.shape[1]} columns")
        
        # Validate if required
        if self.validate:
            if not self.validate_data(df):
                raise ValueError("Data validation failed")
            logger.success("Data validation passed")
        
        # Apply transformations
        df = self.transform(df)
        
        logger.success(f"Import completed successfully")
        return df
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the imported data."""
        return self._metadata
    
    def preview(self, n: int = 5) -> pd.DataFrame:
        """
        Preview the first n rows of data.
        
        Args:
            n: Number of rows to preview
            
        Returns:
            Preview DataFrame
        """
        if self._data is None:
            raise ValueError("No data loaded. Call import_data() first.")
        return self._data.head(n)