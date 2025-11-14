import json

from sqlalchemy.orm import Session

from app.models import Product, StatusEnum
from app.schemas import GenerateDescriptionRequest


def get_product(db: Session, product_id: str):
    return db.query(Product).filter(Product.product_id == product_id).first()


def create_product(db: Session, request: GenerateDescriptionRequest):
    # Convert features to JSON string - handle both Feature objects and dicts
    features_list = []
    if request.features:
        for feature in request.features:
            if isinstance(feature, dict):
                features_list.append(feature)
            else:
                # Convert Feature object to dict
                features_list.append({"label": feature.label, "value": feature.value})

    features_json = json.dumps(features_list)

    db_product = Product(
        product_id=request.product_id,
        status=StatusEnum.pending,
        features=features_json,
        basic_info=request.basic_info,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product_status(
    db: Session,
    product_id: str,
    status: StatusEnum,
    description: str = None,
    specifications: str = None,
    error_message: str = None,
):
    product = get_product(db, product_id)
    if product:
        product.status = status
        if description is not None:
            product.description = description
        if specifications is not None:
            product.specifications = specifications
        if error_message is not None:
            product.error_message = error_message
        db.commit()
        db.refresh(product)
    return product


def delete_product(db: Session, product_id: str):
    product = get_product(db, product_id)
    if product:
        db.delete(product)
        db.commit()
        return True
    return False


def get_pending_products(db: Session, limit: int = 10):
    return (
        db.query(Product)
        .filter(Product.status == StatusEnum.pending)
        .limit(limit)
        .all()
    )
