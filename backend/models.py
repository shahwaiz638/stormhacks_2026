from pydantic import BaseModel
from typing import Optional


class Report(BaseModel):
    report_type: str
    title: str
    description: str
    location: str
    date: str
    image_url: Optional[str] = None