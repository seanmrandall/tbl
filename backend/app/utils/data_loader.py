import pandas as pd
import os
import pickle
from typing import Dict, Any, Optional
import tempfile
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self):
        self.cache_dir = tempfile.gettempdir()
        self.current_dataset_key = None
        self.current_dataset = None
        
    def upload_dataset(self, file, delimiter: str = 'comma') -> Dict[str, Any]:
        """Upload and validate CSV dataset"""
        try:
            # Validate file size (1GB limit)
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > 1024 * 1024 * 1024:  # 1GB
                raise ValueError("File size exceeds 1GB limit")
            
            # Validate filename
            filename = secure_filename(file.filename)
            if not filename.lower().endswith(('.csv', '.txt')):
                raise ValueError("Only CSV and TXT files are supported")
            
            # Map delimiter string to actual delimiter
            delimiter_map = {
                'comma': ',',
                'tab': '\t'
            }
            actual_delimiter = delimiter_map.get(delimiter, ',')
            
            # Read CSV
            df = pd.read_csv(file, sep=actual_delimiter)
            
            # Validate header
            if df.empty:
                raise ValueError("CSV file is empty")
            
            # Clean column names (trim whitespace)
            df.columns = df.columns.str.strip()
            
            # Validate data types (numeric and string only)
            for col in df.columns:
                if df[col].dtype not in ['object', 'int64', 'float64']:
                    # Convert to string if not numeric
                    df[col] = df[col].astype(str)
            
            # Generate dataset key
            dataset_key = f"dataset_{len(df)}_{hash(filename)}"
            
            # Cache dataset
            self._cache_dataset(dataset_key, df)
            
            # Set as current dataset
            self.current_dataset_key = dataset_key
            self.current_dataset = df
            
            return {
                "dataset_key": dataset_key,
                "row_count": len(df),
                "column_count": len(df.columns)
            }
            
        except Exception as e:
            logger.error(f"Error uploading dataset: {str(e)}")
            raise
    
    def get_schema(self, dataset_key: str) -> Dict[str, Any]:
        """Get dataset schema"""
        df = self._load_dataset(dataset_key)
        
        columns = []
        for col in df.columns:
            col_type = "string" if df[col].dtype == 'object' else "numeric"
            columns.append({
                "name": col,
                "type": col_type,
                "unique_values": df[col].nunique()
            })
        
        return {
            "columns": columns,
            "row_count": len(df),
            "dataset_key": dataset_key
        }
    
    def get_dataset(self, dataset_key: str) -> pd.DataFrame:
        """Get dataset by key"""
        return self._load_dataset(dataset_key)
    
    def load_demo_injuries_dataset(self) -> Dict[str, Any]:
        """Load the synthetic injuries demo dataset from the project directory."""
        try:
            demo_path = os.path.join(os.path.dirname(__file__), '../../data/synthetic_injuries_100k.txt')
            demo_path = os.path.abspath(demo_path)
            if not os.path.exists(demo_path):
                raise FileNotFoundError(f"Demo dataset not found at {demo_path}")
            df = pd.read_csv(demo_path, sep='\t', header=0)
            dataset_key = "synthetic_injuries_demo"
            self._cache_dataset(dataset_key, df)
            self.current_dataset_key = dataset_key
            self.current_dataset = df
            return {
                "dataset_key": dataset_key,
                "row_count": len(df),
                "column_count": len(df.columns),
                "description": "Synthetic injuries demo dataset (100k rows)"
            }
        except Exception as e:
            logger.error(f"Error loading demo injuries dataset: {str(e)}")
            raise
    
    def _cache_dataset(self, dataset_key: str, df: pd.DataFrame):
        """Cache dataset to pickle file"""
        cache_path = os.path.join(self.cache_dir, f"{dataset_key}.pkl")
        with open(cache_path, 'wb') as f:
            pickle.dump(df, f)
    
    def _load_dataset(self, dataset_key: str) -> pd.DataFrame:
        """Load dataset from pickle cache"""
        cache_path = os.path.join(self.cache_dir, f"{dataset_key}.pkl")
        
        if not os.path.exists(cache_path):
            raise ValueError(f"Dataset {dataset_key} not found")
        
        with open(cache_path, 'rb') as f:
            return pickle.load(f)
    
    def clear_cache(self):
        """Clear all cached datasets"""
        for file in os.listdir(self.cache_dir):
            if file.endswith('.pkl'):
                os.remove(os.path.join(self.cache_dir, file))
        self.current_dataset = None
        self.current_dataset_key = None

# Global instance
data_loader = DataLoader() 