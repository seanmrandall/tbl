import pandas as pd
from typing import Dict, Any, List
import logging
from app.core.parser import stata_parser
from app.core.suppression import suppression_engine
from app.core.differential_privacy import differential_privacy_engine

logger = logging.getLogger(__name__)

class QueryEngine:
    def __init__(self):
        self.parser = stata_parser
        self.suppression_engine = suppression_engine
        self.differential_privacy_engine = differential_privacy_engine
    
    def execute_query(self, df: pd.DataFrame, command: str, privacy_mode: str = "suppression") -> Dict[str, Any]:
        """
        Execute a Stata-style tab command with privacy protection
        
        Args:
            df: Input DataFrame
            command: Stata-style command (e.g., "tab sex age if region == 'Rural'")
            privacy_mode: Privacy protection mode ("suppression" or "differential_privacy")
        
        Returns:
            Dictionary with query results and metadata
        """
        try:
            logger.info(f"Executing query: {command}")
            logger.info(f"Dataset columns: {df.columns.tolist()}")
            
            # Parse the command
            parsed = self.parser.parse(command)
            logger.info(f"Parsed command: {parsed}")
            
            # Validate variables exist in dataset
            self.parser.validate_variables(parsed, df.columns.tolist())
            
            # Apply filtering if condition exists
            filtered_df = df.copy()
            if parsed.get("condition"):
                logger.info(f"Applying filter: {parsed['condition']}")
                filtered_df = self._apply_filter(filtered_df, parsed["condition"])
                logger.info(f"Filtered dataset size: {len(filtered_df)}")
            
            # Check if filtered dataset is empty
            if filtered_df.empty:
                return {
                    "columns": [],
                    "data": [],
                    "message": "No data matches the specified conditions"
                }
            
            # Create frequency table
            var1 = parsed["variable1"]
            var2 = parsed.get("variable2")
            logger.info(f"Creating frequency table for variables: {var1}, {var2}")
            
            # Validate variables
            if var1 is None:
                raise ValueError("First variable is None - parser error")
            if var1 not in filtered_df.columns:
                raise ValueError(f"Variable '{var1}' not found in dataset. Available columns: {filtered_df.columns.tolist()}")
            if var2 is not None and var2 not in filtered_df.columns:
                raise ValueError(f"Variable '{var2}' not found in dataset. Available columns: {filtered_df.columns.tolist()}")
            
            # Choose privacy engine based on mode
            print(f"DEBUG QUERY ENGINE: Using privacy mode: {privacy_mode}")
            print(f"DEBUG QUERY ENGINE: Privacy mode type: {type(privacy_mode)}")
            print(f"DEBUG QUERY ENGINE: Privacy mode comparison: {privacy_mode == 'differential_privacy'}")
            logger.info(f"Using privacy mode: {privacy_mode}")
            logger.info(f"Privacy mode type: {type(privacy_mode)}")
            logger.info(f"Privacy mode comparison: {privacy_mode == 'differential_privacy'}")
            
            if privacy_mode == "differential_privacy":
                print("DEBUG QUERY ENGINE: Creating frequency table with differential privacy")
                logger.info("Creating frequency table with differential privacy")
                freq_table = self.differential_privacy_engine.create_frequency_table(
                    filtered_df, var1, var2, subset_size=len(filtered_df)
                )
                print(f"DEBUG QUERY ENGINE: Differential privacy result shape: {freq_table.shape}")
                print(f"DEBUG QUERY ENGINE: Differential privacy result columns: {freq_table.columns.tolist()}")
                print(f"DEBUG QUERY ENGINE: Differential privacy result values:")
                print(freq_table.to_string())
                logger.info(f"Differential privacy result: {freq_table.head()}")
            else:  # Default to suppression
                print("DEBUG QUERY ENGINE: Creating frequency table with suppression")
                logger.info("Creating frequency table with suppression")
                freq_table = self.suppression_engine.create_frequency_table(
                    filtered_df, var1, var2
                )
                print(f"DEBUG QUERY ENGINE: Suppression result shape: {freq_table.shape}")
                print(f"DEBUG QUERY ENGINE: Suppression result columns: {freq_table.columns.tolist()}")
                print(f"DEBUG QUERY ENGINE: Suppression result values:")
                print(freq_table.to_string())
                logger.info(f"Suppression result: {freq_table.head()}")
            
            # Convert to API response format
            columns = freq_table.columns.tolist()
            data = freq_table.values.tolist()
            logger.info(f"Query completed successfully. Result: {len(data)} rows")
            
            return {
                "columns": columns,
                "data": data,
                "row_count": len(filtered_df),
                "command": command
            }
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception args: {e.args}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Provide more specific error message
            if str(e) == "None" or str(e) == "":
                raise ValueError("Query execution failed: Invalid command or dataset not found")
            else:
                raise ValueError(f"Query execution failed: {str(e)}")
    
    def _apply_filter(self, df: pd.DataFrame, condition: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply filter condition to DataFrame
        
        Args:
            df: Input DataFrame
            condition: Parsed condition tree
        
        Returns:
            Filtered DataFrame
        """
        if isinstance(condition, dict):
            # Check if this is a binary operator (AND/OR)
            if "operator" in condition and condition["operator"] in ["&", "|"]:
                # Binary operator (& or |)
                left_mask = self._apply_filter_mask(df, condition["left"])
                right_mask = self._apply_filter_mask(df, condition["right"])
                
                if condition["operator"] == "&":
                    return df[left_mask & right_mask]
                elif condition["operator"] == "|":
                    return df[left_mask | right_mask]
                else:
                    raise ValueError(f"Unsupported operator: {condition['operator']}")
            
            # Check if this is a comparison operation
            elif "variable" in condition and "operator" in condition and "value" in condition:
                # Comparison operation
                var = condition["variable"]
                op = condition["operator"]
                val = condition["value"]
                
                if op == "==":
                    return df[df[var] == val]
                elif op == "!=":
                    return df[df[var] != val]
                elif op == "<":
                    return df[df[var] < val]
                elif op == ">":
                    return df[df[var] > val]
                elif op == "<=":
                    return df[df[var] <= val]
                elif op == ">=":
                    return df[df[var] >= val]
                else:
                    raise ValueError(f"Unsupported comparison operator: {op}")
            else:
                raise ValueError(f"Invalid condition format: {condition}")
        
        return df
    
    def _apply_filter_mask(self, df: pd.DataFrame, condition: Dict[str, Any]) -> pd.Series:
        """
        Apply filter condition and return boolean mask
        
        Args:
            df: Input DataFrame
            condition: Parsed condition tree
        
        Returns:
            Boolean mask
        """
        if isinstance(condition, dict):
            # Check if this is a binary operator (AND/OR)
            if "operator" in condition and condition["operator"] in ["&", "|"]:
                # Binary operator (& or |)
                left_mask = self._apply_filter_mask(df, condition["left"])
                right_mask = self._apply_filter_mask(df, condition["right"])
                
                if condition["operator"] == "&":
                    return left_mask & right_mask
                elif condition["operator"] == "|":
                    return left_mask | right_mask
                else:
                    raise ValueError(f"Unsupported operator: {condition['operator']}")
            
            # Check if this is a comparison operation
            elif "variable" in condition and "operator" in condition and "value" in condition:
                # Comparison operation
                var = condition["variable"]
                op = condition["operator"]
                val = condition["value"]
                
                if op == "==":
                    return df[var] == val
                elif op == "!=":
                    return df[var] != val
                elif op == "<":
                    return df[var] < val
                elif op == ">":
                    return df[var] > val
                elif op == "<=":
                    return df[var] <= val
                elif op == ">=":
                    return df[var] >= val
                else:
                    raise ValueError(f"Unsupported comparison operator: {op}")
            else:
                raise ValueError(f"Invalid condition format: {condition}")
        
        return pd.Series([True] * len(df), index=df.index)

# Global query engine instance
query_engine = QueryEngine() 