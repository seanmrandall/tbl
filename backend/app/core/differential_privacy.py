import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
import math

logger = logging.getLogger(__name__)

class DifferentialPrivacyEngine:
    def __init__(self, base_epsilon: float = 1.0):  # Normal epsilon level
        """
        Initialize differential privacy engine
        
        Args:
            base_epsilon: Base epsilon value for privacy budget (lower = more noise)
        """
        self.base_epsilon = base_epsilon
        self.sensitivity = 1.0  # For frequency tables, sensitivity is 1
    
    def apply_differential_privacy(self, df: pd.DataFrame, subset_size: int, total_size: int) -> pd.DataFrame:
        """
        Apply differential privacy to a frequency table using Laplace noise
        
        Args:
            df: Input frequency table DataFrame
            subset_size: Size of the filtered subset
            total_size: Total size of the original dataset
        
        Returns:
            DataFrame with noise added to all counts
        """
        # Calculate dynamic epsilon based on subset size
        epsilon = self._calculate_dynamic_epsilon(subset_size, total_size)
        logger.info(f"Applying differential privacy with epsilon={epsilon:.4f} (subset_size={subset_size}, total_size={total_size})")
        
        # Calculate noise scale
        noise_scale = self.sensitivity / epsilon
        
        # Apply noise to all numeric values
        result = df.copy()
        
        for col in result.columns:
            if col in ['index', 'variable']:  # Skip non-numeric columns
                continue
                
            # Convert to numeric, handling any non-numeric values
            numeric_col = pd.to_numeric(result[col], errors='coerce')
            
            # Generate Laplace noise for each cell
            noise = np.random.laplace(0, noise_scale, len(numeric_col))
            
            # Add noise to the counts
            noisy_counts = numeric_col + noise
            
            # Ensure counts are non-negative
            noisy_counts = np.maximum(noisy_counts, 0)
            
            # Round to integers for frequency counts
            noisy_counts = np.round(noisy_counts).astype(int)
            
            result[col] = noisy_counts
        
        return result
    
    def _calculate_dynamic_epsilon(self, subset_size: int, total_size: int) -> float:
        """
        Calculate dynamic epsilon based on subset size
        
        Args:
            subset_size: Size of the filtered subset
            total_size: Total size of the original dataset
        
        Returns:
            Adjusted epsilon value
        """
        # Calculate the proportion of data being analyzed
        proportion = subset_size / total_size if total_size > 0 else 1.0
        
        # For smaller subsets, use smaller epsilon (more noise)
        # For larger subsets, use larger epsilon (less noise)
        # Use a logarithmic scaling to balance privacy and utility
        
        if proportion <= 0.1:  # Very small subset (< 10% of data)
            adjusted_epsilon = self.base_epsilon * 0.3
        elif proportion <= 0.3:  # Small subset (10-30% of data)
            adjusted_epsilon = self.base_epsilon * 0.5
        elif proportion <= 0.7:  # Medium subset (30-70% of data)
            adjusted_epsilon = self.base_epsilon * 0.8
        else:  # Large subset (> 70% of data)
            adjusted_epsilon = self.base_epsilon
        
        # Ensure epsilon is within reasonable bounds
        adjusted_epsilon = max(0.1, min(adjusted_epsilon, 2.0))
        
        logger.info(f"Dynamic epsilon calculation: proportion={proportion:.3f}, base_epsilon={self.base_epsilon}, adjusted_epsilon={adjusted_epsilon:.4f}")
        
        return adjusted_epsilon
    
    def create_frequency_table(self, df: pd.DataFrame, var1: str, var2: str = None, subset_size: int = None) -> pd.DataFrame:
        """
        Create a frequency table with differential privacy applied
        
        Args:
            df: Input DataFrame
            var1: First variable for cross-tabulation
            var2: Second variable for cross-tabulation (optional)
            subset_size: Size of the filtered subset (if None, uses full dataset size)
        
        Returns:
            DataFrame with frequency counts and differential privacy applied
        """
        total_size = len(df)
        if subset_size is None:
            subset_size = total_size
        
        if var2 is None:
            # One-way frequency table
            freq_table = df[var1].value_counts().to_frame('freq')
            freq_table = freq_table.reset_index()
            freq_table.columns = [var1, 'freq']
            
            # Apply differential privacy
            freq_df = freq_table.set_index(var1)['freq'].to_frame()
            private_df = self.apply_differential_privacy(freq_df, subset_size, total_size)
            
            # Convert back to long format
            result = private_df.reset_index()
            result.columns = [var1, 'freq']
            
        else:
            # Two-way cross-tabulation
            crosstab = pd.crosstab(df[var1], df[var2], margins=True, margins_name='Total')
            
            # Apply differential privacy
            private_df = self.apply_differential_privacy(crosstab, subset_size, total_size)
            
            # Convert to long format for API response
            result = private_df.reset_index()
            result = result.melt(id_vars=[var1], var_name=var2, value_name='freq')
            
            # Filter out margin rows/columns for cleaner output
            result = result[
                (result[var1] != 'Total') & 
                (result[var2] != 'Total')
            ].reset_index(drop=True)
        
        return result

# Global differential privacy engine instance
differential_privacy_engine = DifferentialPrivacyEngine() 