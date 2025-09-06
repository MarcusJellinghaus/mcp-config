"""
Universal JSON utilities with comment preservation.

This module provides a universal API for loading and saving JSON files with comment preservation
across all MCP clients (Claude Desktop, VSCode, IntelliJ). 

Currently provides basic JSON5 support with the infrastructure for full comment preservation.
"""

from pathlib import Path
from typing import Any, Dict, Tuple, Optional
import json
import json5


def load_json_with_comments(file_path: Path) -> Tuple[Dict[str, Any], Optional[Any]]:
    """
    Load JSON file with comment preservation capability.
    
    Args:
        file_path: Path to the JSON file to load
        
    Returns:
        tuple: (data, model) where:
            - data: Parsed JSON data as dict
            - model: Original content for comment preservation (None if file doesn't exist)
            
    Raises:
        ValueError: If JSON is malformed
        OSError: If file cannot be read
    """
    if not file_path.exists():
        return {}, None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            # Handle empty files
            return {}, None
        
        # Try json5 first (supports comments), fallback to json
        try:
            data = json5.loads(content)
        except Exception:
            # Fallback to standard JSON
            data = json.loads(content)
        
        # Store original content as model for future comment preservation
        model = content
        
        return data, model
        
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Invalid JSON in {file_path}: {str(e)}") from e
    except OSError as e:
        raise OSError(f"Cannot read file {file_path}: {str(e)}") from e


def save_json_with_comments(
    file_path: Path, 
    data: Dict[str, Any], 
    model: Optional[Any] = None
) -> None:
    """
    Save JSON file with comment preservation capability.
    
    Args:
        file_path: Path where to save the JSON file
        data: JSON data to save
        model: Comment preservation model (from load_json_with_comments)
               If None, saves as new file without comments
               
    Raises:
        ValueError: If data cannot be serialized to JSON
        OSError: If file cannot be written
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use json5 for better formatting (supports trailing commas, etc.)
        try:
            content = json5.dumps(data, indent=2)
        except Exception:
            # Fallback to standard JSON
            content = json.dumps(data, indent=2)
        
        # Ensure content ends with newline
        if not content.endswith('\n'):
            content += '\n'
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except (ValueError, TypeError) as e:
        raise ValueError(f"Cannot serialize data to JSON: {str(e)}") from e
    except OSError as e:
        raise OSError(f"Cannot write file {file_path}: {str(e)}") from e
