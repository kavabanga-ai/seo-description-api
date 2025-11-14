from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, field_validator


# Simple Feature structure
class Feature(BaseModel):
    label: str
    value: str


# Request schemas
class GenerateDescriptionRequest(BaseModel):
    product_id: str
    features: Optional[Union[List[Feature], List[Dict[str, Any]]]] = None
    basic_info: Optional[str] = None

    @field_validator("features", mode="before")
    @classmethod
    def parse_features(cls, v):
        """Parse features - supports both simple and complex formats"""
        if not v:
            return []

        simplified = []
        for item in v:
            if isinstance(item, dict):
                # Handle complex format from client
                if "label" in item and "values" in item:
                    label = item["label"]
                    values = item.get("values", [])
                    if values and len(values) > 0:
                        value = values[0].get("value", "")
                        if label and value:
                            simplified.append({"label": label, "value": value})
                # Handle simple format
                elif "label" in item and "value" in item:
                    simplified.append({"label": item["label"], "value": item["value"]})
            elif hasattr(item, "label") and hasattr(item, "value"):
                simplified.append({"label": item.label, "value": item.value})

        return simplified


class GenerateDescriptionBatchRequest(BaseModel):
    items: List[GenerateDescriptionRequest]


# Response schemas
class GenerateDescriptionItem(BaseModel):
    index: int
    product_id: str
    status: Optional[str] = None
    http_status: int
    queue_id: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None
    created_at: Optional[datetime] = None


class GenerateDescriptionSummary(BaseModel):
    requested: int
    enqueued: int
    conflicted: int
    failed: int
    duplicates_in_request: int


class GenerateDescriptionResponse(BaseModel):
    summary: GenerateDescriptionSummary
    items: List[GenerateDescriptionItem]


class StatusResponse(BaseModel):
    product_id: str
    status: str
    progress: int
    message: Optional[str] = None
    completed_at: Optional[datetime] = None


class DescriptionResponse(BaseModel):
    product_id: str
    description: Optional[str] = None
    features: Optional[str] = None  # Kept for backwards compatibility
    specifications: Optional[str] = None  # New field for specifications
    generated_at: Optional[datetime] = None
