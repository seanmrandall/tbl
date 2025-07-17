import pandas as pd
import numpy as np
from typing import List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class SuppressionEngine:
    def __init__(self):
        self.suppression_value = "<5"
    
    def apply_suppression(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply suppression rules to a frequency table
        
        Rules:
        1. Primary: Any count < 5 becomes "<5"
        2. Complementary: If exactly one cell in a row/column is suppressed, 
           also suppress the second-smallest cell in that row/column
        """
        # Convert to numeric for calculations
        numeric_df = df.copy()
        
        # Apply primary suppression (<5 rule)
        numeric_df = self._apply_primary_suppression(numeric_df)
        
        # Apply complementary suppression
        numeric_df = self._apply_complementary_suppression(numeric_df)
        
        # Convert back to string format, formatting numbers as integers
        result_df = numeric_df.copy()
        for col in result_df.columns:
            result_df[col] = result_df[col].apply(lambda x: 
                int(x) if pd.notna(x) and x != self.suppression_value else x
            )
        result_df = result_df.astype(str)
        result_df = result_df.replace('nan', self.suppression_value)
        
        return result_df
    
    def _apply_primary_suppression(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply primary suppression: counts < 5 become NaN"""
        result = df.copy()
        
        # Convert to numeric, coercing errors to NaN
        # Handle DataFrame by applying to_numeric to each column
        for col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce')
        
        # Apply <5 rule
        mask = (result < 5) & (result > 0)
        result[mask] = np.nan
        
        return result
    
    def _apply_complementary_suppression(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply complementary suppression rule"""
        result = df.copy()
        
        # Check rows for complementary suppression
        for idx in range(len(result)):
            row = result.iloc[idx]
            suppressed_cells = row.isna().sum()
            
            if suppressed_cells == 1:
                # Find the second-smallest non-suppressed cell
                non_suppressed = row.dropna()
                if len(non_suppressed) > 1:
                    second_smallest_idx = non_suppressed.nsmallest(2).index[-1]
                    result.iloc[idx, result.columns.get_loc(second_smallest_idx)] = np.nan
        
        # Check columns for complementary suppression
        for col in result.columns:
            col_data = result[col]
            suppressed_cells = col_data.isna().sum()
            
            if suppressed_cells == 1:
                # Find the second-smallest non-suppressed cell
                non_suppressed = col_data.dropna()
                if len(non_suppressed) > 1:
                    second_smallest_idx = non_suppressed.nsmallest(2).index[-1]
                    result.loc[second_smallest_idx, col] = np.nan
        
        return result
    
    def create_frequency_table(self, df: pd.DataFrame, var1: str, var2: str = None) -> pd.DataFrame:
        """
        Create a frequency table with suppression applied
        
        Args:
            df: Input DataFrame
            var1: First variable for cross-tabulation
            var2: Second variable for cross-tabulation (optional)
        
        Returns:
            DataFrame with frequency counts and suppression applied
        """
        if var2 is None:
            # One-way frequency table
            freq_table = df[var1].value_counts().to_frame('freq')
            freq_table = freq_table.reset_index()
            freq_table.columns = [var1, 'freq']
            
            # Apply suppression
            freq_df = freq_table.set_index(var1)['freq'].to_frame()
            suppressed_df = self.apply_suppression(freq_df)
            
            # Convert back to long format
            result = suppressed_df.reset_index()
            result.columns = [var1, 'freq']
            
        else:
            # Two-way cross-tabulation
            crosstab = pd.crosstab(df[var1], df[var2], margins=True, margins_name='Total')
            
            # Apply suppression
            suppressed_df = self.apply_suppression(crosstab)
            
            # Convert to long format for API response
            result = suppressed_df.reset_index()
            result = result.melt(id_vars=[var1], var_name=var2, value_name='freq')
            
            # Filter out margin rows/columns for cleaner output
            result = result[
                (result[var1] != 'Total') & 
                (result[var2] != 'Total')
            ].reset_index(drop=True)
        
        return result

# Global suppression engine instance
suppression_engine = SuppressionEngine() 