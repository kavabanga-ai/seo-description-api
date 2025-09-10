import asyncio
import json
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import get_pending_products, update_product_status
from app.models import StatusEnum
from app.services.ai_service import ai_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_processing = False

    async def process_pending_tasks(self):
        """Process pending product descriptions"""
        if self.is_processing:
            return

        self.is_processing = True
        db = SessionLocal()

        try:
            # Get batch of pending products
            pending_products = get_pending_products(db, settings.BATCH_SIZE)

            if not pending_products:
                return

            logger.info(f"Processing {len(pending_products)} pending products")

            # Process each product
            for product in pending_products:
                try:
                    # Update status to processing
                    update_product_status(db, product.product_id, StatusEnum.processing)

                    # Parse keywords from JSON
                    keywords = json.loads(product.keywords) if product.keywords else []

                    # Generate description using AI
                    result = await ai_service.generate_description(
                        product.product_id,
                        keywords,
                        product.basic_info
                    )

                    if result["success"]:
                        # Combine description and features
                        full_description = result["description"]
                        if result.get("features"):
                            full_description += f"\n\nFeatures:\n{result['features']}"

                        update_product_status(
                            db,
                            product.product_id,
                            StatusEnum.completed,
                            description=full_description
                        )
                        logger.info(f"Successfully generated description for {product.product_id}")
                    else:
                        update_product_status(
                            db,
                            product.product_id,
                            StatusEnum.failed,
                            error_message=result.get("error", "Unknown error")
                        )
                        logger.error(f"Failed to generate description for {product.product_id}")

                except Exception as e:
                    logger.error(f"Error processing product {product.product_id}: {str(e)}")
                    update_product_status(
                        db,
                        product.product_id,
                        StatusEnum.failed,
                        error_message=str(e)
                    )

                # Small delay between requests to avoid overwhelming the AI service
                await asyncio.sleep(0.5)

        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
        finally:
            db.close()
            self.is_processing = False

    def start(self):
        """Start the scheduler"""
        self.scheduler.add_job(
            self.process_pending_tasks,
            'interval',
            seconds=settings.SCHEDULER_INTERVAL_SECONDS,
            id='process_pending_tasks',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info(f"Scheduler started with interval: {settings.SCHEDULER_INTERVAL_SECONDS} seconds")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")


task_scheduler = TaskScheduler()
