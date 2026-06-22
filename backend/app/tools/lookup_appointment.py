from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, model_validator

from app.domain.booking import AppointmentStore
from app.store import get_store

router = APIRouter()


class LookupRequest(BaseModel):
    confirmation_code: Optional[str] = None
    citizen_name: Optional[str] = None
    date: Optional[str] = None

    @model_validator(mode="after")
    def require_code_or_name(self):
        if not self.confirmation_code and not self.citizen_name:
            raise ValueError("Fornire confirmation_code oppure citizen_name")
        return self


@router.post("/lookup_appointment")
def lookup_appointment(req: LookupRequest, store: AppointmentStore = Depends(get_store)) -> dict:
    if req.confirmation_code:
        return store.lookup_by_code(req.confirmation_code)
    return store.lookup_by_name(req.citizen_name, date=req.date)
