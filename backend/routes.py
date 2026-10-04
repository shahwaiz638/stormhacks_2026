from fastapi import APIRouter
from models import Report

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/reports")
def create_report(report: Report):
    return {
        "message": "Report received",
        "report": report
    }