import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.endpoints import router
from app.database import Base, engine
from app.services.scheduler import task_scheduler

# Configure logging - MUST be before importing scheduler
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Suppress APScheduler logging before scheduler starts
logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger("apscheduler.executors").setLevel(logging.ERROR)
logging.getLogger("apscheduler.executors.default").setLevel(logging.ERROR)
logging.getLogger("apscheduler.scheduler").setLevel(logging.ERROR)

# Get the app directory
BASE_DIR = Path(__file__).resolve().parent


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
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Setup templates
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# -------------------
# CORS configuration
# -------------------
# Comma-separated list, e.g.:
# ALLOWED_ORIGINS="http://localhost:3000,https://myfrontend.com"
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*").strip()
if _raw_origins == "*" or _raw_origins == "":
    allowed_origins = ["*"]
else:
    allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# If you specify concrete origins, we can safely
# allow credentials (cookies/Authorization headers).
allow_credentials = "*" not in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],  # or list specific headers if you prefer
    # Optional: expose headers you need the browser to read
    expose_headers=["Content-Disposition"],
    max_age=600,  # cache preflight for 10 minutes
)

# Include API routers
app.include_router(router, prefix="/api/v1")


# Frontend route - this should be AFTER API routes
@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    """Serve the frontend application"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api-info")
def api_info():
    """API information endpoint"""
    return {
        "name": "SEO Description Generator API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "frontend": "/",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
