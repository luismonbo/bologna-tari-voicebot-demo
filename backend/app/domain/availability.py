from datetime import date

from app.domain.dates import parse_iso_date, validate_future_date

# Mon–Fri, 09:00–12:30, 30-minute slots
_OFFICE_CONFIG = {
    "tributi": {
        "weekdays": {0, 1, 2, 3, 4},
        "slots": ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30"],
    }
}


def get_available_slots(office: str, d: date) -> list[str]:
    config = _OFFICE_CONFIG.get(office)
    if config is None or d.weekday() not in config["weekdays"]:
        return []
    return list(config["slots"])


def check_availability(office: str, date_str: str, booked_slots: set[str]) -> dict:
    d = parse_iso_date(date_str)
    validate_future_date(d)
    all_slots = get_available_slots(office, d)
    free = [s for s in all_slots if s not in booked_slots]
    return {"date": date_str, "available": len(free) > 0, "slots": free}
