from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from app.api.endpoints import router
from app.database import Base, engine
from app.services.scheduler import task_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    task_scheduler.start()
    logging.info("Application started")
    yield
    # Shutdown
    task_scheduler.stop()
    logging.info("Application stopped")


app = FastAPI(
    title="SEO Description Generator API",
    description="API for generating SEO-optimized product descriptions using AI",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(router, prefix="/v1")


@app.get("/")
def read_root():
    return {
        "name": "SEO Description Generator API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
