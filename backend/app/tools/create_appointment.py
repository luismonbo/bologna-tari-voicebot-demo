from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.domain.booking import AppointmentStore
from app.domain.dates import parse_iso_date, parse_iso_time, validate_future_date
from app.domain.validators import (
    normalize_italian_phone,
    sanitize_citizen_name,
    validate_citizen_name,
    validate_italian_phone,
)
from app.store import get_store

router = APIRouter()


class CreateRequest(BaseModel):
    office: str
    date: str
    time: str
    citizen_name: str
    contact: str
    reason: Optional[str] = None


@router.post("/create_appointment")
async def create_appointment(
    req: CreateRequest, store: AppointmentStore = Depends(get_store)
) -> dict:
    # Validate dates and times
    try:
        d = parse_iso_date(req.date)
        validate_future_date(d)
        parse_iso_time(req.time)
    except ValueError as e:
        return {"status": "validation_error", "message": str(e), "field": "date_or_time"}

    # Validate and sanitize citizen name
    valid_name, name_error = validate_citizen_name(req.citizen_name)
    if not valid_name:
        return {"status": "validation_error", "message": name_error, "field": "citizen_name"}
    sanitized_name = sanitize_citizen_name(req.citizen_name)

    # Validate and normalize contact phone number
    valid_phone, phone_error = validate_italian_phone(req.contact)
    if not valid_phone:
        return {"status": "validation_error", "message": phone_error, "field": "contact"}
    normalized_phone = normalize_italian_phone(req.contact)

    return await store.book(
        office=req.office.lower(),
        date=req.date,
        time=req.time,
        citizen_name=sanitized_name,
        contact=normalized_phone,
        reason=req.reason,
    )
