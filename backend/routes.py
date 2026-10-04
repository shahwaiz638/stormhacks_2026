import json
import logging
import math
from urllib.parse import urlsplit
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from google.genai import errors as genai_errors
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile
from starlette.formparsers import MultiPartException, MultiPartParser

import database
from models import MatchesResponse, Report, ReportInput, ReportRecord, ReportResponse, ReportType
from services import (
    MAX_IMAGES, MAX_IMAGE_BYTES, build_matching_text, decode_base64_image,
    extract_item_attributes, generate_embedding, image_data_url,
    rerank_and_evaluate_matches, validate_image,
)

router = APIRouter()
logger = logging.getLogger(__name__)
MAX_BODY_BYTES = 27 * 1024 * 1024


def database_call(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except Exception as exc:
        logger.warning("Database operation failed (%s)", type(exc).__name__)
        raise HTTPException(503, "Database operation failed; please try again") from None


def gemini_call(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except genai_errors.APIError as exc:
        logger.warning("Gemini API failed (status %s)", exc.code)
        if exc.code == 429 or exc.code >= 500:
            raise HTTPException(503, "Gemini is temporarily unavailable; please try again") from None
        raise HTTPException(502, "Gemini processing failed; please try again") from None
    except Exception as exc:
        logger.warning("Gemini operation failed (%s)", type(exc).__name__)
        raise HTTPException(502, "Gemini processing failed; please try again") from None


async def parse_report(request: Request, require_type=False):
    """Accept existing React multipart forms or JSON, with a bounded body."""
    chunks, size = [], 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > MAX_BODY_BYTES:
            raise HTTPException(400, "Request too large; images are limited to 5 MiB each")
        chunks.append(chunk)
    body = b"".join(chunks)
    content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
    images = []
    if content_type == "application/json":
        try:
            data = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            raise HTTPException(400, "Malformed JSON") from None
        if not isinstance(data, dict):
            raise HTTPException(422, "Request must be a JSON object")
    elif content_type == "multipart/form-data":
        async def body_stream():
            yield body
        try:
            form = await MultiPartParser(
                request.headers, body_stream(), max_files=MAX_IMAGES, max_fields=20,
                max_part_size=7_000_000,
            ).parse()
        except MultiPartException:
            raise HTTPException(400, "Invalid multipart form or too many photos (maximum 5)") from None
        data = {}
        try:
            for key, value in form.multi_items():
                if isinstance(value, UploadFile):
                    if key not in ("photo", "photos", "image"):
                        raise HTTPException(400, "Use photo or photos for image uploads")
                    image_bytes = await value.read(MAX_IMAGE_BYTES + 1)
                    if image_bytes:
                        images.append((image_bytes, value.content_type))
                else:
                    data[key] = value
        finally:
            await form.close()
    else:
        raise HTTPException(415, "Send application/json or multipart/form-data")
    for key in ("image_base64", "image", "image_url"):
        if isinstance(data.get(key), str) and len(data[key]) > 7_000_000:
            raise HTTPException(400, "Image exceeds the 5 MiB limit")
    try:
        report = (Report if require_type else ReportInput).model_validate(data)
    except ValidationError as exc:
        # Avoid echoing Base64 images or private identifying details in errors.
        errors = [{"loc": ["body", *e["loc"]], "msg": e["msg"], "type": e["type"]}
                  for e in exc.errors()]
        raise RequestValidationError(errors) from None
    return report, images


def prepare_images(report, uploads):
    images = []
    try:
        for data, mime in uploads:
            images.append(validate_image(data, mime))
        value = report.image_base64
        url = report.image_url
        if url and url.startswith("data:"):
            if value:
                raise ValueError("Provide only one Base64 image value")
            value, url = url, None
        if value:
            if images or url:
                raise ValueError("Use uploads, Base64, or an image URL, not a combination")
            images.append(decode_base64_image(value, report.image_mime_type))
        if url:
            parsed = urlsplit(url)
            if (len(url) > 2048 or parsed.scheme not in ("https", "http")
                    or not parsed.hostname or parsed.username or parsed.password):
                raise ValueError("image_url must be an HTTP(S) URL without credentials")
            if images:
                raise ValueError("Use uploads or an image URL, not both")
        if len(images) > MAX_IMAGES:
            raise ValueError("At most 5 photos are allowed")
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None
    # Store a display-sized data URL in the existing TEXT column, not full files.
    stored_url = image_data_url(*images[0]) if images else url
    return images, stored_url


def find_matches(lost_report, embedding):
    candidates = database_call(database.search_similar_reports, "FOUND", embedding, limit=5)
    if not candidates:
        return [], []
    # Images/vectors stay outside the Gemini reranking prompt.
    excluded = {"image_url", "description_vector"}
    lost_details = {k: v for k, v in lost_report.items() if k not in excluded}
    candidate_details = [{k: v for k, v in row.items() if k not in excluded} for row in candidates]
    warnings = []
    try:
        evaluations = gemini_call(rerank_and_evaluate_matches, lost_details, candidate_details)
        by_id = {evaluation["candidate_id"]: evaluation for evaluation in evaluations}
    except HTTPException:
        by_id = {}
        warnings.append("AI explanations unavailable; matches are ranked by vector similarity")
    matches = []
    for candidate in candidates:
        score = float(candidate["vector_score"])
        if not math.isfinite(score):
            continue
        evaluation = by_id.get(candidate["id"])
        match = dict(candidate)
        match.update(
            candidate_id=candidate["id"], vector_score=score,
            match_percentage=round(max(0.0, min(1.0, score)) * 100),
            ai_match_percentage=evaluation["match_percentage"] if evaluation else None,
            matching_reasons=evaluation["matching_reasons"] if evaluation else [],
            summary_explanation=evaluation["summary_explanation"] if evaluation else
                "Candidate retrieved by text vector similarity; AI explanation unavailable.",
        )
        matches.append(match)
    # Keep ranking tied to measured cosine similarity; AI estimates are separate.
    matches.sort(key=lambda match: match["vector_score"], reverse=True)
    return matches, warnings


def process_report(report, uploads, report_type):
    images, stored_url = prepare_images(report, uploads)
    title = report.title or report.description[:80]
    record = {
        "id": str(uuid4()), "report_type": report_type, "title": title,
        "description": report.description, "location_name": report.location_name,
        "event_timestamp": report.event_timestamp, "image_url": stored_url,
    }
    context = json.dumps({k: record[k] for k in ("title", "description", "location_name")})
    attributes = gemini_call(
        extract_item_attributes, context,
        image_bytes=images[0][0] if images else None,
        mime_type=images[0][1] if images else "image/jpeg",
        additional_images=images[1:],
    )
    text = build_matching_text(record, attributes)
    embedding = gemini_call(generate_embedding, text,
        task_type="RETRIEVAL_QUERY" if report_type == "LOST" else "RETRIEVAL_DOCUMENT")
    database_call(database.save_report, record, attributes, embedding)
    warnings = []
    if report.private_detail:
        warnings.append("Private identifying detail was not stored; the table has no private-detail column")
    if len(images) > 1:
        warnings.append("All photos were analyzed; only the first photo is stored for display")
    if stored_url and not images:
        warnings.append("image_url was stored as metadata; remote images are not fetched or analyzed")
    matches = []
    if report_type == "LOST":
        try:
            matches, match_warnings = find_matches({**record, **attributes}, embedding)
            warnings.extend(match_warnings)
        except HTTPException:
            # The insert already committed: don't encourage a duplicate submission.
            warnings.append("Report saved, but matching failed; retry GET /reports/{report_id}/matches")
    return {"success": True, "report_id": record["id"], "report_type": report_type,
            "attributes": attributes, "matches": matches, "warnings": warnings}


# Describe both accepted formats in /docs while retaining the existing form aliases.
REPORT_BODY = {"requestBody": {"required": True, "content": {
    "application/json": {"schema": ReportInput.model_json_schema()},
    "multipart/form-data": {"schema": {
        "type": "object", "required": ["description"], "properties": {
            "title": {"type": "string"}, "itemName": {"type": "string"},
            "description": {"type": "string"}, "location_name": {"type": "string"},
            "lastSeenLocation": {"type": "string"}, "foundLocation": {"type": "string"},
            "event_timestamp": {"type": "string", "format": "date-time"},
            "lastSeenAt": {"type": "string"}, "foundAt": {"type": "string"},
            "timeZone": {"type": "string", "default": "UTC"},
            "photo": {"type": "string", "format": "binary"},
            "photos": {"type": "array", "items": {"type": "string", "format": "binary"}},
        }
    }},
}}}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/reports/found", response_model=ReportResponse, status_code=201, openapi_extra=REPORT_BODY)
async def create_found_report(request: Request):
    report, images = await parse_report(request)
    return await run_in_threadpool(process_report, report, images, "FOUND")


@router.post("/reports/lost", response_model=ReportResponse, status_code=201, openapi_extra=REPORT_BODY)
async def create_lost_report(request: Request):
    report, images = await parse_report(request)
    return await run_in_threadpool(process_report, report, images, "LOST")


@router.post("/reports", response_model=ReportResponse, status_code=201,
    openapi_extra={"requestBody": {"required": True, "content": {
        "application/json": {"schema": Report.model_json_schema()}}}})
async def create_report(request: Request):
    """Compatibility endpoint: accepts report_type plus the same fields."""
    report, images = await parse_report(request, require_type=True)
    return await run_in_threadpool(process_report, report, images, report.report_type)


@router.get("/reports", response_model=list[ReportRecord])
def list_reports(report_type: ReportType | None = Query(default=None, alias="type"),
                 limit: int = Query(default=50, ge=1, le=100),
                 offset: int = Query(default=0, ge=0)):
    return database_call(database.get_reports, report_type, limit, offset)


@router.get("/reports/{report_id}", response_model=ReportRecord)
def read_report(report_id: UUID):
    report = database_call(database.get_report, str(report_id))
    if report is None:
        raise HTTPException(404, "Report not found")
    return report


@router.get("/reports/{report_id}/matches", response_model=MatchesResponse)
def report_matches(report_id: UUID):
    report = database_call(database.get_report, str(report_id), include_vector=True)
    if report is None:
        raise HTTPException(404, "Report not found")
    if report["report_type"] != "LOST":
        raise HTTPException(400, "Only LOST reports can search for FOUND matches")
    matches, warnings = find_matches(report, report["description_vector"])
    return {"report_id": str(report_id), "matches": matches, "warnings": warnings}
