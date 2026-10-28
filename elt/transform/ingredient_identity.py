from __future__ import annotations

import re
import unicodedata


def ingredient_key(value: str) -> str:
    folded = value.casefold().replace("œ", "oe").replace("æ", "ae")
    normalized = unicodedata.normalize("NFKD", folded)
    without_marks = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", "-", without_marks).strip("-")


def ingredient_keys(*names: str) -> list[str]:
    return sorted({key for key in map(ingredient_key, names) if key})
