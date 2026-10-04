from datetime import datetime, timezone
from typing import Annotated, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator

ReportType = Literal["LOST", "FOUND"]
ShortText = Annotated[str, Field(max_length=200)]


class ReportInput(BaseModel):
    """JSON names plus aliases used by the existing React multipart forms."""
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    title: str | None = Field(default=None, min_length=1, max_length=255,
                              validation_alias=AliasChoices("title", "itemName"))
    description: str = Field(min_length=1, max_length=5000)
    location_name: str = Field(min_length=1, max_length=100,
        validation_alias=AliasChoices("location_name", "location", "lastSeenLocation", "foundLocation"))
    event_timestamp: datetime = Field(
        validation_alias=AliasChoices("event_timestamp", "date", "lastSeenAt", "foundAt"))
    time_zone: str = Field(default="UTC", max_length=100,
                           validation_alias=AliasChoices("time_zone", "timeZone"))
    image_base64: str | None = Field(default=None, max_length=7_000_000,
        validation_alias=AliasChoices("image_base64", "image"))
    images: list[Annotated[str, Field(max_length=7_000_000)]] = Field(default_factory=list, max_length=5)
    image_mime_type: str | None = Field(default=None, max_length=100)
    image_url: str | None = Field(default=None, max_length=7_000_000)
    # The real table has no private-detail column. Never persist or publish this.
    private_detail: str | None = Field(default=None, max_length=1000, exclude=True,
        validation_alias=AliasChoices("private_detail", "privateDetail"))

    @model_validator(mode="after")
    def normalize_timestamp(self):
        try:
            zone = ZoneInfo(self.time_zone)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("time_zone must be a valid IANA timezone") from None
        value = self.event_timestamp
        try:
            if value.tzinfo is None:
                value = value.replace(tzinfo=zone)
                # Reject nonexistent local times during the spring DST transition.
                if value.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None) != self.event_timestamp:
                    raise ValueError("event_timestamp is not a valid local time")
            value = value.astimezone(timezone.utc)
        except OverflowError:
            raise ValueError("event_timestamp is outside the supported range") from None
        if value.year < 1000:
            raise ValueError("event_timestamp must be in year 1000 or later")
        self.event_timestamp = value
        return self


class Report(ReportInput):
    report_type: ReportType

    @field_validator("report_type", mode="before")
    @classmethod
    def normalize_type(cls, value):
        return value.upper() if isinstance(value, str) else value


class ItemAttributes(BaseModel):
    category: str | None = Field(default=None, max_length=50)
    primary_color: str | None = Field(default=None, max_length=50)
    brand: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    distinctive_features: list[ShortText] = Field(default_factory=list, max_length=20)
    keywords: list[ShortText] = Field(default_factory=list, max_length=10)


class MatchEvaluation(BaseModel):
    candidate_id: str = Field(min_length=1, max_length=36)
    match_percentage: int = Field(ge=0, le=100)
    is_probable_match: bool
    is_same_item_type: bool
    matching_reasons: list[ShortText] = Field(max_length=10)
    summary_explanation: str = Field(max_length=1000)


class ReportRecord(ItemAttributes):
    id: str
    report_type: ReportType
    title: str
    description: str | None
    image_url: str | None
    location_name: str | None
    event_timestamp: datetime | None
    created_at: datetime | None


class MatchResult(ReportRecord):
    candidate_id: str
    vector_score: float
    # Derived from cosine similarity, not a calibrated probability.
    match_percentage: int = Field(ge=0, le=100,
        description="Clamped cosine similarity times 100; not a probability")
    matching_reasons: list[str]
    summary_explanation: str
    ai_match_percentage: int | None = Field(default=None, ge=0, le=100,
        description="Gemini's subjective estimate; not a calibrated probability")


class ReportResponse(BaseModel):
    success: bool = True
    report_id: str | None = None
    saved: bool = False
    report_type: ReportType
    attributes: ItemAttributes
    matches: list[MatchResult] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class MatchesResponse(BaseModel):
    report_id: str
    matches: list[MatchResult]
    warnings: list[str] = Field(default_factory=list)
