import json

from fastapi import APIRouter, HTTPException
from google.genai import errors

from models import Report, ReportResponse
from services import extract_item_attributes, generate_embedding
from database import save_report

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/reports", response_model=ReportResponse)
def create_report(report: Report):
    # image_url is metadata for now; this endpoint does not download images.
    context = f"Title: {report.title}\nDescription: {report.description}"
    try:
        attributes = extract_item_attributes(context)
        if not isinstance(attributes, dict):
            raise ValueError("Gemini returned invalid attributes")
        embedding = generate_embedding(
            context + "\nAttributes: " + json.dumps(attributes, sort_keys=True)
        )
    except errors.APIError:
        raise HTTPException(status_code=502, detail="Gemini request failed") from None
    except ValueError:
        raise HTTPException(
            status_code=503,
            detail="Check GOOGLE_API_KEY and Gemini response format",
        ) from None

    try:
        save_report(report.model_dump(), attributes, embedding)
    except NotImplementedError as exc:
        message = str(exc)
        saved = False
    else:
        message = "Report saved"
        saved = True
    return {
        "message": message,
        "report": report,
        "attributes": attributes,
        "embedding": embedding,
        "saved": saved,
        "image_analyzed": False,
    }
