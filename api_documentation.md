# SEO Description Generator API Documentation

## Overview

The SEO Description Generator API creates optimized product descriptions in Russian based on product features. The API uses AI to generate engaging, SEO-friendly content automatically.

**Base URL:** `http://your-api-domain.com`

**Authentication:** All endpoints require an API key in the header.

---

## Authentication

All API requests must include your API key in the `X-API-Key` header:

```
X-API-Key: your_api_key_here
```

---

## Endpoints

### 1. Generate Description

Generate SEO-optimized descriptions for one or more products.

**Endpoint:** `POST /generate`

**Headers:**
```
Content-Type: application/json
X-API-Key: your_api_key_here
```

**Request Body:**

```json
{
  "items": [
    {
      "product_id": "840",
      "features": [
        {
          "label": "Размер матрицы",
          "value": "1/2.7"
        },
        {
          "label": "Скорость при макс.разр. кадр/сек",
          "value": "30.0"
        },
        {
          "label": "Ик-подсветка",
          "value": "Да"
        }
      ],
      "basic_info": "VCI-121-01 BOLID Camera"
    }
  ]
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `items` | Array | Yes | Array of products to process |
| `items[].product_id` | String | Yes | Unique product identifier |
| `items[].features` | Array | No | Product features (simple format) |
| `items[].features[].label` | String | Yes | Feature name/label |
| `items[].features[].value` | String | Yes | Feature value |
| `items[].basic_info` | String | No | Additional product information |

**Response:**

```json
{
  "summary": {
    "requested": 1,
    "enqueued": 1,
    "conflicted": 0,
    "failed": 0,
    "duplicates_in_request": 0
  },
  "items": [
    {
      "index": 0,
      "product_id": "840",
      "status": "enqueued",
      "http_status": 200,
      "queue_id": "queue-abc123def4",
      "created_at": "2025-11-14T12:00:00Z"
    }
  ]
}
```

**Response Fields:**

| Field | Description |
|-------|-------------|
| `summary.requested` | Total number of products in request |
| `summary.enqueued` | Number of products successfully queued |
| `summary.conflicted` | Number of products already processing |
| `summary.failed` | Number of products that failed |
| `summary.duplicates_in_request` | Number of duplicate products in request |
| `items[].status` | Status: `enqueued` or error |
| `items[].http_status` | HTTP status code (200 = success, 409 = conflict) |
| `items[].queue_id` | Unique queue identifier |

**Status Codes:**

- `200` - Success
- `401` - Invalid API key
- `409` - Product already being processed

---

### 2. Check Status

Check the generation status of a product.

**Endpoint:** `GET /status/{product_id}`

**Headers:**
```
X-API-Key: your_api_key_here
```

**Response:**

```json
{
  "product_id": "840",
  "status": "completed",
  "progress": 100,
  "message": "Description generated successfully",
  "completed_at": "2025-11-14T12:05:00Z"
}
```

**Status Values:**

| Status | Progress | Description |
|--------|----------|-------------|
| `pending` | 0% | Waiting in queue |
| `processing` | 50% | Generating description (may take a few minutes) |
| `completed` | 100% | Description ready |
| `failed` | 0% | Generation failed |
| `not_found` | 0% | Product not found |

---

### 3. Get Description

Retrieve the generated description for a product.

**Endpoint:** `GET /description/{product_id}`

**Headers:**
```
X-API-Key: your_api_key_here
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `only` | String | No | Filter output: `description`, `specifications`, or `features` |

**Response:**

```json
{
  "product_id": "840",
  "description": "Профессиональная IP-камера VCI-121-01 от BOLID с разрешением FullHD...",
  "specifications": "• Размер матрицы: 1/2.7\n• Скорость при макс.разр.: 30.0 кадр/сек\n• ИК-подсветка: Да",
  "features": "• Размер матрицы: 1/2.7\n• Скорость при макс.разр.: 30.0 кадр/сек\n• ИК-подсветка: Да",
  "generated_at": "2025-11-14T12:05:00Z"
}
```

**With Filter (`?only=description`):**

```json
{
  "product_id": "840",
  "description": "Профессиональная IP-камера VCI-121-01 от BOLID с разрешением FullHD...",
  "generated_at": "2025-11-14T12:05:00Z"
}
```

**Status Codes:**

- `200` - Success
- `404` - Product not found or description not ready
- `401` - Invalid API key

---

## Alternative Feature Format (Complex)

The API also accepts the complex feature format for compatibility:

```json
{
  "items": [
    {
      "product_id": "840",
      "features": [
        {
          "featureId": 1,
          "label": "Размер матрицы",
          "values": [
            {
              "id": "1",
              "value": "1/2.7"
            }
          ]
        }
      ]
    }
  ]
}
```

The API automatically converts this to the simple format internally.

---

## Complete Example Workflow

### Step 1: Submit Product for Generation

```bash
curl -X POST https://your-api-domain.com/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "items": [
      {
        "product_id": "840",
        "features": [
          {"label": "Размер матрицы", "value": "1/2.7"},
          {"label": "Скорость", "value": "30.0 кадр/сек"},
          {"label": "ИК-подсветка", "value": "Да"}
        ],
        "basic_info": "VCI-121-01"
      }
    ]
  }'
```

**Response:**
```json
{
  "summary": {"requested": 1, "enqueued": 1, "conflicted": 0, "failed": 0},
  "items": [
    {
      "index": 0,
      "product_id": "840",
      "status": "enqueued",
      "http_status": 200,
      "queue_id": "queue-abc123"
    }
  ]
}
```

### Step 2: Check Status (Wait 1-3 minutes)

```bash
curl -X GET https://your-api-domain.com/status/840 \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "product_id": "840",
  "status": "processing",
  "progress": 50,
  "message": "Generating description (this may take a few minutes)"
}
```

### Step 3: Get Description (When status = completed)

```bash
curl -X GET https://your-api-domain.com/description/840 \
  -H "X-API-Key: your_api_key"
```

**Response:**
```json
{
  "product_id": "840",
  "description": "Профессиональная IP-камера VCI-121-01...",
  "specifications": "• Размер матрицы: 1/2.7\n• Скорость: 30.0 кадр/сек",
  "generated_at": "2025-11-14T12:05:00Z"
}
```

---

## Error Handling

### Common Errors

**401 Unauthorized**
```json
{
  "detail": "Invalid API key"
}
```

**404 Not Found**
```json
{
  "detail": "Product not found"
}
```

**409 Conflict**
```json
{
  "index": 0,
  "product_id": "840",
  "http_status": 409,
  "error": "ALREADY_PROCESSING",
  "message": "Product 840 is already being processed. Please wait for completion."
}
```

---

## Rate Limits & Best Practices

1. **Batch Requests:** Send multiple products in one request (up to 100 recommended)
2. **Polling:** Wait at least 30 seconds between status checks
3. **Generation Time:** Expect 1-3 minutes per product
4. **Retry Logic:** If status is `processing`, continue checking periodically

---

## Support

For issues or questions, please contact your API provider or check the project repository.

---

**Last Updated:** November 14, 2025
**API Version:** 1.0
