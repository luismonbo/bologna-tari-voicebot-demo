import re
from datetime import date


def parse_iso_date(value: str) -> date:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"Data deve essere YYYY-MM-DD, ricevuto: {value!r}")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"Data non valida: {value!r}")


def validate_future_date(d: date) -> date:
    if d < date.today():
        raise ValueError(f"La data {d} è nel passato")
    return d


def parse_iso_time(value: str) -> str:
    if not re.fullmatch(r"\d{2}:\d{2}", value):
        raise ValueError(f"Orario deve essere HH:MM, ricevuto: {value!r}")
    hour, minute = int(value[:2]), int(value[3:])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Orario non valido: {value!r}")
    return value
