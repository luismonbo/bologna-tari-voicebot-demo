import logging
import os
import re

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AppointmentModel, SessionLocal

logger = logging.getLogger(__name__)

UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)

router = APIRouter()


async def get_db():
    async with SessionLocal() as session:
        yield session


@router.get("/appointments")
async def get_appointments(db: AsyncSession = Depends(get_db)):
    """Fetch all booked appointments."""
    query = select(AppointmentModel).order_by(AppointmentModel.date, AppointmentModel.time)
    result = await db.execute(query)
    appointments = result.scalars().all()

    return {
        "appointments": [
            {
                "office": a.office,
                "date": a.date,
                "time": a.time,
                "citizen_name": a.citizen_name,
                "contact": a.contact,
                "reason": a.reason,
            }
            for a in appointments
        ]
    }


@router.get("/calls/recent")
async def get_recent_calls(limit: int = Query(default=10, ge=1, le=10)):
    """Fetch recent calls from Vapi API."""
    vapi_key = os.environ.get("VAPI_PRIVATE_API_KEY")
    if not vapi_key:
        raise HTTPException(status_code=500, detail="Vapi API key not configured")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://api.vapi.ai/call",
                headers={"Authorization": f"Bearer {vapi_key}"},
                params={"limit": limit},
            )
            response.raise_for_status()

            calls_data = response.json()
            # Vapi returns an array directly, not wrapped in a "calls" key
            calls = calls_data if isinstance(calls_data, list) else []

            return {
                "calls": [
                    {
                        "id": call.get("id"),
                        "timestamp": call.get("createdAt"),
                        "duration": extract_duration(call),
                        "citizen_name": call.get("customer")
                        if isinstance(call.get("customer"), str) and call.get("customer")
                        else None,
                        "result": determine_call_result(call),
                    }
                    for call in calls
                ]
            }
    except httpx.HTTPStatusError as e:
        logger.error("Vapi API error %s: %s", e.response.status_code, e.response.text)
        raise HTTPException(status_code=502, detail="Errore nel recupero delle chiamate")
    except Exception as e:
        logger.error("Error fetching calls: %s", str(e))
        raise HTTPException(status_code=502, detail="Errore nel recupero delle chiamate")


@router.get("/call/{call_id}/transcript")
async def get_call_transcript(call_id: str):
    """Fetch transcript for a specific call from Vapi API."""
    if not UUID_PATTERN.match(call_id):
        raise HTTPException(status_code=422, detail="Formato call_id non valido")

    vapi_key = os.environ.get("VAPI_PRIVATE_API_KEY")
    if not vapi_key:
        raise HTTPException(status_code=500, detail="Vapi API key not configured")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.vapi.ai/call/{call_id}",
                headers={"Authorization": f"Bearer {vapi_key}"},
            )
            response.raise_for_status()

            call_data = response.json()
            messages = call_data.get("messages", [])

            transcript = []
            for msg in messages:
                role = msg.get("role", "")
                # Only include user and bot conversation messages
                if role not in ("user", "bot"):
                    continue

                # Map Vapi roles to frontend roles
                if role == "user":
                    mapped_role = "citizen"
                elif role == "bot":
                    mapped_role = "assistant"
                else:
                    continue

                # Vapi messages use "message" field, not "content"
                text = msg.get("message", "")
                if text:
                    transcript.append({"role": mapped_role, "text": text})

            return {
                "transcript": transcript,
                "metadata": {
                    "duration": extract_duration(call_data),
                    "timestamp": call_data.get("createdAt"),
                    "citizen_name": call_data.get("customer", {}).get("name"),
                },
            }
    except httpx.HTTPError as e:
        logger.error("Failed to fetch transcript from Vapi: %s", str(e))
        raise HTTPException(status_code=502, detail="Errore nel recupero della trascrizione")


def extract_duration(call: dict) -> int:
    """Extract duration in seconds from Vapi call data.

    Vapi stores duration in the costs array under the 'minutes' key.
    We convert minutes to seconds for consistent formatting.
    """
    costs = call.get("costs", [])
    if costs and isinstance(costs, list) and len(costs) > 0:
        minutes = costs[0].get("minutes", 0)
        # Convert minutes to seconds
        return int(minutes * 60)
    return 0


def determine_call_result(call: dict) -> str:
    """Determine call result based on Vapi call data.

    Mark calls with actual conversation messages as 'info'.
    Vapi uses "bot"/"user" roles in messages, plus system/tool messages.
    """
    messages = call.get("messages", [])

    # Filter for actual conversation messages (user/bot), not system or tool calls
    conversation_messages = [
        m for m in messages if m.get("role") in ("user", "bot") and m.get("message")
    ]

    # If there are conversation messages, it was a meaningful call
    if conversation_messages:
        return "info"

    # Otherwise it's an error/abandoned call
    return "error"
