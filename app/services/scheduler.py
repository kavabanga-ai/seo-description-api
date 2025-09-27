import asyncio
import json
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.crud import get_pending_products, update_product_status
from app.database import SessionLocal
from app.models import StatusEnum
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_processing = False
        self.max_retries = 3  # Maximum number of retries
        self.retry_delay = 10  # Delay between retries in seconds

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

                    # Retry logic for API calls
                    retries = 0
                    success = False

                    while retries < self.max_retries and not success:
                        # Generate description using AI
                        result = await ai_service.generate_description(
                            product.product_id, keywords, product.basic_info
                        )

                        if result["success"]:
                            # Combine description and specifications
                            full_description = result["description"]

                            # Store specifications separately if present
                            specifications = result.get("specifications", "")

                            update_product_status(
                                db,
                                product.product_id,
                                StatusEnum.completed,
                                description=full_description,
                                specifications=specifications,  # This requires DB update
                            )
                            logger.info(
                                f"Successfully generated "
                                f"description for {product.product_id}"
                            )
                            success = True
                        elif result.get("retry", False):
                            # This was a timeout, retry
                            retries += 1
                            if retries < self.max_retries:
                                logger.info(
                                    f"Retrying {product.product_id} "
                                    f"(attempt {retries + 1}/{self.max_retries})"
                                )
                                await asyncio.sleep(self.retry_delay)
                            else:
                                # Max retries reached, still treat as processing
                                # Don't mark as failed yet
                                logger.warning(
                                    f"Max retries reached for {product.product_id}, "
                                    f"keeping in processing state"
                                )
                                # Keep the status as processing so it can be retried later
                                # Don't update to failed unless Dify explicitly returns an error
                        else:
                            # Actual error from Dify, mark as failed
                            update_product_status(
                                db,
                                product.product_id,
                                StatusEnum.failed,
                                error_message=result.get("error", "Unknown error"),
                            )
                            logger.error(
                                f"Failed to generate description for {product.product_id}: "
                                f"{result.get('error')}"
                            )
                            success = True  # Exit retry loop

                except Exception as e:
                    logger.error(
                        f"Unexpected error processing product {product.product_id}: {str(e)}"
                    )
                    # Only mark as failed for unexpected errors
                    update_product_status(
                        db, product.product_id, StatusEnum.failed, error_message=str(e)
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
            "interval",
            seconds=settings.SCHEDULER_INTERVAL_SECONDS,
            id="process_pending_tasks",
            replace_existing=True,
        )
        self.scheduler.start()
        logger.info(
            f"Scheduler started with "
            f"interval: {settings.SCHEDULER_INTERVAL_SECONDS} seconds"
        )

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")


task_scheduler = TaskScheduler()
