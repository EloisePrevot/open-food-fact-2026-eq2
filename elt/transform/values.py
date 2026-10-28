from __future__ import annotations

import json
import math
import re
from typing import Any

NUTRI_SCORE_GRADES = ("a", "b", "c", "d", "e")


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def optional_text(value: Any) -> str | None:
    return text(value) or None


def to_float(value: Any) -> float | None:
    try:
        number = float(text(value).replace(",", "."))
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def to_int(value: Any) -> int | None:
    number = to_float(value)
    return int(number) if number is not None and number.is_integer() else None


def to_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return {"true": True, "1": True, "yes": True, "false": False, "0": False, "no": False}.get(
        text(value).casefold()
    )


def grade(value: Any) -> str | None:
    candidate = text(value).casefold()
    return candidate if candidate in NUTRI_SCORE_GRADES else None


def split_tags(value: Any) -> list[str]:
    return [tag.strip() for tag in text(value).split(",") if tag.strip()]


def strip_language(tag: str) -> str:
    return re.sub(r"^[a-z]{2}:", "", tag)


def json_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if not isinstance(value, str) or not value.strip():
        return []
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        return [value]
    return decoded if isinstance(decoded, list) else [decoded]


def text_list(value: Any) -> list[str]:
    return [text(item) for item in json_list(value) if text(item)]


def french_or_english(record: dict[str, Any], field: str) -> str:
    return text(record.get(f"{field}F")) or text(record.get(field))


def join_words(*parts: str) -> str:
    return " ".join(part for part in parts if part)
