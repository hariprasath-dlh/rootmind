"""
helpers.py - Reusable Helper Functions

Houses lightweight, non-business specific logic, timezone conversion,
or common text formatting functions.
"""

from typing import Any, Dict


def clean_dict_keys(dirty_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cleans dict keys by trimming white space and standardizing naming formats.
    
    Args:
        dirty_dict (Dict[str, Any]): Dictionary to standardize.

    Returns:
        Dict[str, Any]: Standardized copy of dictionary.
    """
    return {k.strip().lower(): v for k, v in dirty_dict.items()}
