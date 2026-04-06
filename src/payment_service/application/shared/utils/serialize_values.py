from datetime import datetime


def _serialize_value(value: object) -> str | int | float | bool | datetime | None:
    """Serializes value to be JSON-compatible."""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if value is None:
        return None
    return str(value)
