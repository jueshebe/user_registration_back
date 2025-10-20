"""App global utils."""
from typing import Optional


def normalize(string_data: Optional[str]) -> str:
    """Remove all problematic characters."""
    if not isinstance(string_data, str):
        return ""

    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("ñ", "n"),
        (".", ""),
        ("'", ""),
    )
    lower_case = string_data.lower()
    for char1, char2 in replacements:
        lower_case = lower_case.replace(char1, char2)
    return lower_case
