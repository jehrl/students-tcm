"""JSON file importer implementation."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from loguru import logger

from .base_importer import BaseImporter


class JSONImporter(BaseImporter):
    """Importer for JSON files with nested structure support."""
    
    def __init__(self,
                 source: Union[str, Path],
                 encoding: str = 'utf-8',
                 validate: bool = True,
                 orient: str = 'records'):
        """
        Initialize JSON importer.
        
        Args:
            source: Path to JSON file
            encoding: File encoding
            validate: Whether to validate data
            orient: JSON orientation ('records', 'index', 'columns', 'values', 'table')
        """
        super().__init__(source, encoding, validate)
        self.orient = orient
    
    def load(self, **kwargs) -> pd.DataFrame:
        """
        Load data from JSON file.
        
        Kwargs:
            normalize: Whether to normalize nested JSON
            record_path: Path to records in nested JSON
            meta: Fields to include from meta information
            max_level: Maximum level to normalize
            
        Returns:
            Loaded DataFrame
        """
        try:
            normalize = kwargs.pop('normalize', False)
            
            logger.info(f"Loading JSON file: {self.source}")
            
            if normalize:
                # Handle nested JSON structures
                with open(self.source, 'r', encoding=self.encoding) as file:
                    data = json.load(file)
                
                # Use json_normalize for nested structures
                record_path = kwargs.pop('record_path', None)
                meta = kwargs.pop('meta', None)
                max_level = kwargs.pop('max_level', None)
                
                df = pd.json_normalize(
                    data,
                    record_path=record_path,
                    meta=meta,
                    max_level=max_level
                )
            else:
                # Simple JSON reading
                read_params = {
                    'path_or_buf': self.source,
                    'orient': self.orient,
                    'encoding': self.encoding
                }
                read_params.update(kwargs)
                df = pd.read_json(**read_params)
            
            logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except FileNotFoundError:
            logger.error(f"File not found: {self.source}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading JSON: {e}")
            raise
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate JSON data.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if validation passes
        """
        validation_errors = []
        
        # Basic validation
        if df.empty:
            validation_errors.append("DataFrame is empty")
        
        # Check for nested objects that weren't properly normalized
        object_columns = df.select_dtypes(include=['object']).columns
        for col in object_columns:
            # Check if column contains dict or list objects
            sample = df[col].dropna().head()
            if not sample.empty:
                first_val = sample.iloc[0]
                if isinstance(first_val, (dict, list)):
                    logger.warning(f"Column '{col}' contains nested structures")
        
        if validation_errors:
            for error in validation_errors:
                logger.error(f"Validation error: {error}")
            return False
        
        logger.success("JSON validation passed")
        return True
    
    def analyze_structure(self) -> Dict[str, Any]:
        """
        Analyze the structure of the JSON file.
        
        Returns:
            Dictionary describing the JSON structure
        """
        try:
            with open(self.source, 'r', encoding=self.encoding) as file:
                data = json.load(file)
            
            def get_structure(obj, max_depth=3, current_depth=0):
                """Recursively analyze JSON structure."""
                if current_depth >= max_depth:
                    return "..."
                
                if isinstance(obj, dict):
                    return {
                        key: get_structure(value, max_depth, current_depth + 1)
                        for key, value in list(obj.items())[:5]  # Limit keys
                    }
                elif isinstance(obj, list):
                    if obj:
                        return [get_structure(obj[0], max_depth, current_depth + 1)]
                    return []
                else:
                    return type(obj).__name__
            
            structure = {
                'type': type(data).__name__,
                'structure': get_structure(data),
                'size_bytes': self.source.stat().st_size if self.source.exists() else 0
            }
            
            # Count records if it's a list
            if isinstance(data, list):
                structure['record_count'] = len(data)
            
            return structure
            
        except Exception as e:
            logger.error(f"Error analyzing JSON structure: {e}")
            return {}
    
    def flatten_nested_json(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Flatten specific nested columns in a DataFrame.
        
        Args:
            df: DataFrame with nested columns
            columns: List of column names to flatten
            
        Returns:
            DataFrame with flattened columns
        """
        result = df.copy()
        
        for col in columns:
            if col not in result.columns:
                logger.warning(f"Column '{col}' not found in DataFrame")
                continue
            
            # Check if column contains dictionaries
            sample = result[col].dropna().head(1)
            if not sample.empty and isinstance(sample.iloc[0], dict):
                # Normalize the column
                normalized = pd.json_normalize(result[col].dropna())
                # Add prefix to avoid column name conflicts
                normalized.columns = [f"{col}_{subcol}" for subcol in normalized.columns]
                # Merge back with original DataFrame
                result = pd.concat([result.drop(columns=[col]), normalized], axis=1)
                logger.info(f"Flattened column '{col}' into {len(normalized.columns)} columns")
        
        return result