import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/seo_descriptions")

    # API Configuration
    API_KEY = os.getenv("API_KEY", "default-api-key")
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))

    # Dify AI Service
    DIFY_API_URL = os.getenv("DIFY_API_URL", "https://luis-agents.kavabanga.team/v1")
    DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")
    DIFY_TIMEOUT = int(os.getenv("DIFY_TIMEOUT", 120))  # Timeout in seconds

    # Scheduler
    SCHEDULER_INTERVAL_SECONDS = int(os.getenv("SCHEDULER_INTERVAL_SECONDS", 5))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))

    # Retry Configuration
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", 10))  # Delay between retries in seconds


settings = Settings()
