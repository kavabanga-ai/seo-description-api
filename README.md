# SEO Description Generator API

A simple FastAPI application that generates SEO-optimized product descriptions using AI (Dify).

## Features

- ✅ RESTful API for product description generation
- ✅ PostgreSQL database for storing requests and results
- ✅ Asynchronous task processing with built-in scheduler
- ✅ Simple API key authentication
- ✅ Handles 100,000+ queries efficiently
- ✅ Status tracking for generation requests
- ✅ Automatic retry logic for failed requests

## Installation

1. Clone the repository
```bash
git clone git@gitlab.evoclick.ru:luis/seo-description-api.git
cd seo-description-api
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Set up PostgreSQL database
```bash
# Create database
createdb seo_descriptions

# Run migrations
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Running the Application

### Development
```bash
python run.py
```

### Production
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
```

## API Endpoints

### Generate Description
```bash
POST /v1/generate
X-API-Key: your-api-key

{
  "items": [
    {
      "product_id": "PROD-12345",
      "keywords": ["organic", "eco-friendly"],
      "basic_info": "Product details..."
    }
  ]
}
```

### Check Status
```bash
GET /v1/status/{product_id}
X-API-Key: your-api-key
```

### Get Description
```bash
GET /v1/description/{product_id}
X-API-Key: your-api-key
```

## Configuration

Key environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `API_KEY`: API authentication key
- `DIFY_API_URL`: Dify AI service URL
- `DIFY_API_KEY`: Dify API key
- `SCHEDULER_INTERVAL_SECONDS`: Task processing interval
- `BATCH_SIZE`: Number of products to process per batch

## Architecture

1. **API Layer**: FastAPI handles incoming requests
2. **Database**: PostgreSQL stores product requests and results
3. **Scheduler**: APScheduler processes pending tasks
4. **AI Service**: Dify API generates descriptions
5. **Task Processing**: Asynchronous processing with status updates

## Performance

- Handles 100,000+ queries through efficient batch processing
- Configurable batch size and processing intervals
- Asynchronous processing prevents blocking
- Database indexing on product_id for fast lookups

## Monitoring

Check application health:
```bash
GET /health
```

View logs for monitoring task processing and errors.
