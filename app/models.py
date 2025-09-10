import enum

from sqlalchemy import Column, DateTime, Enum, String, Text
from sqlalchemy.sql import func

from app.database import Base


class StatusEnum(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True, index=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.pending, nullable=False)
    description = Column(Text, nullable=True)
    specifications = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)  # Store as JSON string
    basic_info = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )
