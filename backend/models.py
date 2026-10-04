from pydantic import BaseModel
from typing import Any, Literal, Optional


class Report(BaseModel):
    report_type: Literal["lost", "found"]
    title: str
    description: str
    location: str
    date: str
    image_url: Optional[str] = None


class ReportResponse(BaseModel):
    message: str
    report: Report
    attributes: dict[str, Any]
    embedding: list[float]
    saved: bool
    image_analyzed: bool = False
