import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.crud import create_product, delete_product, get_product
from app.database import get_db
from app.models import StatusEnum
from app.schemas import (
    DescriptionResponse,
    GenerateDescriptionBatchRequest,
    GenerateDescriptionItem,
    GenerateDescriptionResponse,
    GenerateDescriptionSummary,
    StatusResponse,
)

router = APIRouter()


def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@router.post("/generate", response_model=GenerateDescriptionResponse)
def generate_description(
    request: GenerateDescriptionBatchRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Generate SEO descriptions for products"""

    # Handle single item as list
    items = request.items if hasattr(request, "items") else [request]

    summary = GenerateDescriptionSummary(
        requested=len(items),
        enqueued=0,
        conflicted=0,
        failed=0,
        duplicates_in_request=0,
    )

    response_items = []
    seen_products = set()

    for index, item in enumerate(items):
        # Check for duplicates in request
        if item.product_id in seen_products:
            summary.duplicates_in_request += 1
            continue
        seen_products.add(item.product_id)

        # Check if product exists
        existing_product = get_product(db, item.product_id)

        if existing_product:
            if existing_product.status == StatusEnum.pending:
                # Product is already being processed
                summary.conflicted += 1
                response_items.append(
                    GenerateDescriptionItem(
                        index=index,
                        product_id=item.product_id,
                        http_status=409,
                        error="ALREADY_PROCESSING",
                        message=f"Product {item.product_id} is already being processed."
                        f" Please wait for completion.",
                    )
                )
            else:
                # Delete existing and create new
                delete_product(db, item.product_id)
                new_product = create_product(db, item)
                summary.enqueued += 1
                response_items.append(
                    GenerateDescriptionItem(
                        index=index,
                        product_id=item.product_id,
                        status="enqueued",
                        http_status=200,
                        queue_id=f"queue-{uuid.uuid4().hex[:10]}",
                        created_at=new_product.created_at,
                    )
                )
        else:
            # Create new product
            new_product = create_product(db, item)
            summary.enqueued += 1
            response_items.append(
                GenerateDescriptionItem(
                    index=index,
                    product_id=item.product_id,
                    status="enqueued",
                    http_status=200,
                    queue_id=f"queue-{uuid.uuid4().hex[:10]}",
                    created_at=new_product.created_at,
                )
            )

    # Return 202 if all items were enqueued, otherwise 200

    return GenerateDescriptionResponse(summary=summary, items=response_items)


@router.get("/status/{product_id}", response_model=StatusResponse)
def check_status(
    product_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Check generation status for a product"""

    product = get_product(db, product_id)

    if not product:
        return StatusResponse(
            product_id=product_id,
            status="Notfound",
            progress=0,
            message="Product not found",
        )

    # Calculate progress based on status
    progress_map = {
        StatusEnum.pending: 0,
        StatusEnum.processing: 50,
        StatusEnum.completed: 100,
        StatusEnum.failed: 0,
    }

    message_map = {
        StatusEnum.pending: "Waiting in queue",
        StatusEnum.processing: "Generating description",
        StatusEnum.completed: "Description generated successfully",
        StatusEnum.failed: product.error_message or "Generation failed",
    }

    return StatusResponse(
        product_id=product_id,
        status=product.status.value,
        progress=progress_map[product.status],
        message=message_map[product.status],
        completed_at=(
            product.updated_at if product.status == StatusEnum.completed else None
        ),
    )


@router.get("/description/{product_id}", response_model=DescriptionResponse)
def get_description(
    product_id: str,
    only: Optional[str] = Query(None, regex="^(features|description)$"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Get generated description for a product"""

    product = get_product(db, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.status != StatusEnum.completed:
        raise HTTPException(
            status_code=404,
            detail=f"Description not ready. Current status: {product.status.value}",
        )

    # Parse description and features
    description = product.description or ""
    features = ""

    if "Features:" in description:
        parts = description.split("Features:")
        description = parts[0].strip()
        features = parts[1].strip() if len(parts) > 1 else ""

    # Filter based on 'only' parameter
    if only == "description":
        return DescriptionResponse(
            product_id=product_id,
            description=description,
            generated_at=product.updated_at,
        )
    elif only == "features":
        return DescriptionResponse(
            product_id=product_id, features=features, generated_at=product.updated_at
        )
    else:
        return DescriptionResponse(
            product_id=product_id,
            description=description,
            features=features,
            generated_at=product.updated_at,
        )
