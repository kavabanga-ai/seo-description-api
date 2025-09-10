from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Request schemas
class GenerateDescriptionRequest(BaseModel):
    product_id: str
    keywords: Optional[List[str]] = None
    basic_info: Optional[str] = None


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
    features: Optional[str] = None
    generated_at: Optional[datetime] = None
