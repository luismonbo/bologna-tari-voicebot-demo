from fastapi import APIRouter
from pydantic import BaseModel

from app import rag

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("/query_services")
def query_services(req: QueryRequest) -> dict:
    return rag.query(req.question)
