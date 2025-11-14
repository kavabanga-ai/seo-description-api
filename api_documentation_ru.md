# Документация API генератора SEO-описаний

## Обзор

API генератора SEO-описаний создает оптимизированные описания товаров на русском языке на основе характеристик продукта. API использует искусственный интеллект для автоматической генерации привлекательного SEO-контента.

**Базовый URL:** `http://your-api-domain.com`

**Аутентификация:** Все эндпоинты требуют API-ключ в заголовке.

---

## Аутентификация

Все запросы к API должны включать ваш API-ключ в заголовке `X-API-Key`:

```
X-API-Key: ваш_api_ключ
```

---

## Эндпоинты

### 1. Генерация описания

Генерация SEO-оптимизированных описаний для одного или нескольких товаров.

**Эндпоинт:** `POST /generate`

**Заголовки:**
```
Content-Type: application/json
X-API-Key: ваш_api_ключ
```

**Тело запроса:**

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

**Параметры:**

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `items` | Массив | Да | Массив товаров для обработки |
| `items[].product_id` | Строка | Да | Уникальный идентификатор товара |
| `items[].features` | Массив | Нет | Характеристики товара (простой формат) |
| `items[].features[].label` | Строка | Да | Название характеристики |
| `items[].features[].value` | Строка | Да | Значение характеристики |
| `items[].basic_info` | Строка | Нет | Дополнительная информация о товаре |

**Ответ:**

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

**Поля ответа:**

| Поле | Описание |
|------|----------|
| `summary.requested` | Общее количество товаров в запросе |
| `summary.enqueued` | Количество товаров успешно поставленных в очередь |
| `summary.conflicted` | Количество товаров, которые уже обрабатываются |
| `summary.failed` | Количество товаров с ошибкой |
| `summary.duplicates_in_request` | Количество дубликатов в запросе |
| `items[].status` | Статус: `enqueued` (в очереди) или ошибка |
| `items[].http_status` | HTTP код статуса (200 = успех, 409 = конфликт) |
| `items[].queue_id` | Уникальный идентификатор очереди |

**Коды статуса:**

- `200` - Успех
- `401` - Неверный API-ключ
- `409` - Товар уже обрабатывается

---

### 2. Проверка статуса

Проверка статуса генерации описания товара.

**Эндпоинт:** `GET /status/{product_id}`

**Заголовки:**
```
X-API-Key: ваш_api_ключ
```

**Ответ:**

```json
{
  "product_id": "840",
  "status": "completed",
  "progress": 100,
  "message": "Description generated successfully",
  "completed_at": "2025-11-14T12:05:00Z"
}
```

**Значения статуса:**

| Статус | Прогресс | Описание |
|--------|----------|----------|
| `pending` | 0% | Ожидание в очереди |
| `processing` | 50% | Генерация описания (может занять несколько минут) |
| `completed` | 100% | Описание готово |
| `failed` | 0% | Ошибка генерации |
| `not_found` | 0% | Товар не найден |

---

### 3. Получение описания

Получение сгенерированного описания товара.

**Эндпоинт:** `GET /description/{product_id}`

**Заголовки:**
```
X-API-Key: ваш_api_ключ
```

**Параметры запроса:**

| Параметр | Тип | Обязательно | Описание |
|----------|-----|-------------|----------|
| `only` | Строка | Нет | Фильтр вывода: `description`, `specifications` или `features` |

**Ответ:**

```json
{
  "product_id": "840",
  "description": "Профессиональная IP-камера VCI-121-01 от BOLID с разрешением FullHD...",
  "specifications": "• Размер матрицы: 1/2.7\n• Скорость при макс.разр.: 30.0 кадр/сек\n• ИК-подсветка: Да",
  "features": "• Размер матрицы: 1/2.7\n• Скорость при макс.разр.: 30.0 кадр/сек\n• ИК-подсветка: Да",
  "generated_at": "2025-11-14T12:05:00Z"
}
```

**С фильтром (`?only=description`):**

```json
{
  "product_id": "840",
  "description": "Профессиональная IP-камера VCI-121-01 от BOLID с разрешением FullHD...",
  "generated_at": "2025-11-14T12:05:00Z"
}
```

**Коды статуса:**

- `200` - Успех
- `404` - Товар не найден или описание не готово
- `401` - Неверный API-ключ

---

## Альтернативный формат характеристик (сложный)

API также принимает сложный формат характеристик для совместимости:

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

API автоматически конвертирует этот формат в простой формат внутри системы.

---

## Полный пример рабочего процесса

### Шаг 1: Отправка товара на генерацию

```bash
curl -X POST https://your-api-domain.com/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ваш_api_ключ" \
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

**Ответ:**
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

### Шаг 2: Проверка статуса (Подождите 1-3 минуты)

```bash
curl -X GET https://your-api-domain.com/status/840 \
  -H "X-API-Key: ваш_api_ключ"
```

**Ответ:**
```json
{
  "product_id": "840",
  "status": "processing",
  "progress": 50,
  "message": "Generating description (this may take a few minutes)"
}
```

### Шаг 3: Получение описания (Когда status = completed)

```bash
curl -X GET https://your-api-domain.com/description/840 \
  -H "X-API-Key: ваш_api_ключ"
```

**Ответ:**
```json
{
  "product_id": "840",
  "description": "Профессиональная IP-камера VCI-121-01...",
  "specifications": "• Размер матрицы: 1/2.7\n• Скорость: 30.0 кадр/сек",
  "generated_at": "2025-11-14T12:05:00Z"
}
```

---

## Обработка ошибок

### Распространенные ошибки

**401 Unauthorized (Не авторизован)**
```json
{
  "detail": "Invalid API key"
}
```

**404 Not Found (Не найдено)**
```json
{
  "detail": "Product not found"
}
```

**409 Conflict (Конфликт)**
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

## Ограничения и рекомендации

1. **Пакетные запросы:** Отправляйте несколько товаров в одном запросе (рекомендуется до 100)
2. **Опрос статуса:** Ждите минимум 30 секунд между проверками статуса
3. **Время генерации:** Ожидайте 1-3 минуты на товар
4. **Логика повтора:** Если статус `processing`, продолжайте периодически проверять

---

## Примеры интеграции

### Python

```python
import requests
import time

API_URL = "https://your-api-domain.com"
API_KEY = "ваш_api_ключ"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Шаг 1: Отправка на генерацию
payload = {
    "items": [{
        "product_id": "840",
        "features": [
            {"label": "Размер матрицы", "value": "1/2.7"},
            {"label": "Скорость", "value": "30.0 кадр/сек"}
        ]
    }]
}

response = requests.post(f"{API_URL}/generate", json=payload, headers=headers)
print(f"Статус отправки: {response.json()}")

# Шаг 2: Ожидание и проверка статуса
product_id = "840"
while True:
    time.sleep(30)  # Ждем 30 секунд
    status_response = requests.get(f"{API_URL}/status/{product_id}", headers=headers)
    status_data = status_response.json()

    print(f"Статус: {status_data['status']} ({status_data['progress']}%)")

    if status_data['status'] == 'completed':
        break
    elif status_data['status'] == 'failed':
        print(f"Ошибка: {status_data['message']}")
        break

# Шаг 3: Получение описания
desc_response = requests.get(f"{API_URL}/description/{product_id}", headers=headers)
description = desc_response.json()
print(f"Описание: {description['description']}")
```

### PHP

```php
<?php

$apiUrl = "https://your-api-domain.com";
$apiKey = "ваш_api_ключ";

$headers = [
    'Content-Type: application/json',
    'X-API-Key: ' . $apiKey
];

// Шаг 1: Отправка на генерацию
$payload = [
    'items' => [[
        'product_id' => '840',
        'features' => [
            ['label' => 'Размер матрицы', 'value' => '1/2.7'],
            ['label' => 'Скорость', 'value' => '30.0 кадр/сек']
        ]
    ]]
];

$ch = curl_init($apiUrl . '/generate');
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
echo "Статус отправки: " . $response . "\n";

// Шаг 2: Проверка статуса
$productId = '840';
do {
    sleep(30);

    $ch = curl_init($apiUrl . '/status/' . $productId);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    $statusResponse = json_decode(curl_exec($ch), true);
    echo "Статус: " . $statusResponse['status'] . " (" . $statusResponse['progress'] . "%)\n";

} while ($statusResponse['status'] == 'processing' || $statusResponse['status'] == 'pending');

// Шаг 3: Получение описания
if ($statusResponse['status'] == 'completed') {
    $ch = curl_init($apiUrl . '/description/' . $productId);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    $description = json_decode(curl_exec($ch), true);
    echo "Описание: " . $description['description'] . "\n";
}

curl_close($ch);
?>
```

---

## Поддержка

По вопросам и проблемам обращайтесь к поставщику API или проверьте репозиторий проекта.

---

**Последнее обновление:** 14 ноября 2025
**Версия API:** 1.0
