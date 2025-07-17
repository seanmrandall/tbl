from lark import Lark, Transformer, v_args
from typing import Dict, Any, List, Optional
import pandas as pd

# Lark grammar for Stata-style tab commands
GRAMMAR = r"""
start: tab_command

tab_command: "tab" variable [variable] ["if" condition]

variable: CNAME

condition: or_expr

or_expr: and_expr ("|" and_expr)*
and_expr: comparison ("&" comparison)*

comparison: COMP

COMP: /[a-zA-Z_][a-zA-Z0-9_]*\s*(==|!=|<=|>=|<|>)\s*("[^"]*"|-?\d+(?:\.\d+)?)/
CNAME: /[a-zA-Z_][a-zA-Z0-9_]*/

%import common.WS
%ignore WS
"""

class TabCommandTransformer(Transformer):
    def __init__(self):
        super().__init__()
    
    def start(self, args):
        return args[0]
    
    def tab_command(self, args):
        # Debug: print the args to see what we're getting
        print(f"DEBUG: tab_command args: {args}")
        print(f"DEBUG: args types: {[type(arg) for arg in args]}")
        
        # The args array contains the parsed elements after "tab"
        # So args[0] = first variable, args[1] = second variable (if exists), args[2] = condition (if exists)
        var1 = args[0] if len(args) > 0 else None
        var2 = args[1] if len(args) > 1 and isinstance(args[1], str) else None
        condition = args[2] if len(args) > 2 and isinstance(args[2], dict) else None
        
        # If we have a condition at position 1, then there's no second variable
        if len(args) > 1 and isinstance(args[1], dict):
            condition = args[1]
            var2 = None
        
        print(f"DEBUG: parsed var1={var1}, var2={var2}, condition={condition}")
        
        return {
            "command": "tab",
            "variable1": var1,
            "variable2": var2,
            "condition": condition
        }
    
    def variable(self, args):
        return str(args[0])
    
    def condition(self, args):
        return args[0]
    
    def or_expr(self, args):
        if len(args) == 1:
            return args[0]
        else:
            return {"operator": "|", "left": args[0], "right": args[1]}
    
    def and_expr(self, args):
        if len(args) == 1:
            return args[0]
        else:
            return {"operator": "&", "left": args[0], "right": args[1]}
    
    def comparison(self, args):
        # args[0] is a string like 'atsi==1' or 'region=="Urban"'
        import re
        print(f"DEBUG: comparison args: {args}")
        if not args or not args[0]:
            raise ValueError(f"Empty comparison args: {args}")
        comp_str = str(args[0])
        m = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*(==|!=|<=|>=|<|>)\s*(\"[^\"]*\"|-?\d+(?:\.\d+)?)', comp_str)
        if not m:
            print(f"DEBUG: Failed to match comparison regex for: {comp_str}")
            raise ValueError(f"Invalid comparison: {comp_str}")
        var, op, val = m.groups()
        # Remove quotes from string values
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        else:
            try:
                val = float(val) if '.' in val else int(val)
            except Exception:
                pass
        return {
            "variable": var,
            "operator": op,
            "value": val
        }
    
    def operator(self, args):
        if len(args) > 0:
            return str(args[0])
        else:
            return ""
    
    def value(self, args):
        val = str(args[0])
        # Remove quotes from strings
        if val.startswith('"') and val.endswith('"'):
            return val[1:-1]
        # Convert to number if possible
        try:
            return float(val) if '.' in val else int(val)
        except ValueError:
            return val

class StataParser:
    def __init__(self):
        self.parser = Lark(GRAMMAR, parser='lalr', transformer=TabCommandTransformer())
    
    def parse(self, command: str) -> Dict[str, Any]:
        """Parse a Stata-style tab command"""
        try:
            # Clean the command
            command = command.strip()
            
            # Parse the command
            result = self.parser.parse(command)
            
            return result
            
        except Exception as e:
            raise ValueError(f"Invalid command syntax: {str(e)}")
    
    def validate_variables(self, parsed_command: Dict[str, Any], available_columns: List[str]) -> None:
        """Validate that variables exist in the dataset"""
        variables = []
        
        if parsed_command.get("variable1"):
            variables.append(parsed_command["variable1"])
        if parsed_command.get("variable2"):
            variables.append(parsed_command["variable2"])
        
        # Check condition variables
        if parsed_command.get("condition"):
            variables.extend(self._extract_variables_from_condition(parsed_command["condition"]))
        
        # Validate all variables exist
        for var in variables:
            if var not in available_columns:
                raise ValueError(f"Variable '{var}' not found in dataset")
    
    def _extract_variables_from_condition(self, condition: Dict[str, Any]) -> List[str]:
        """Extract all variables from a condition tree"""
        variables = []
        
        if isinstance(condition, dict):
            if "variable" in condition:
                variables.append(condition["variable"])
            elif "operator" in condition:
                variables.extend(self._extract_variables_from_condition(condition["left"]))
                variables.extend(self._extract_variables_from_condition(condition["right"]))
        
        return list(set(variables))  # Remove duplicates

# Global parser instance
stata_parser = StataParser() 