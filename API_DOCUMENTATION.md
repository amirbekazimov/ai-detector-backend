# AI Detector API - Документация

## Обзор

AI Detector API - это система для отслеживания и классификации посетителей веб-сайтов, с особым акцентом на обнаружение AI-ботов.

## Основные возможности

✅ **Регистрация и аутентификация пользователей**
✅ **Управление сайтами** (добавление/удаление)
✅ **JavaScript сниппет** для отслеживания
✅ **Обнаружение AI-ботов** по User-Agent
✅ **Сохранение событий** в базу данных
✅ **Дашборд статистики** с графиками и таблицами
✅ **Система логирования** ошибок и событий

## API Endpoints

### Аутентификация

#### POST `/api/v1/auth/register`
Регистрация нового пользователя
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

#### POST `/api/v1/auth/login`
Вход в систему
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Управление сайтами

#### POST `/api/v1/sites`
Создание нового сайта
```json
{
  "domain": "example.com"
}
```

#### GET `/api/v1/sites`
Получение списка сайтов пользователя

#### GET `/api/v1/sites/{site_id}/snippet`
Получение JavaScript сниппета для сайта

#### DELETE `/api/v1/sites/{site_id}`
Удаление сайта

### Отслеживание

#### GET `/api/v1/tracking/{site_id}.js`
JavaScript сниппет для отслеживания

#### POST `/api/v1/tracking/events`
Прием событий отслеживания
```json
{
  "site_id": "site_126c9b771139",
  "event_type": "page_view",
  "url": "https://example.com/page",
  "user_agent": "Mozilla/5.0...",
  "timestamp": "2025-09-24T18:00:00.000Z"
}
```

#### POST `/api/v1/tracking/events/batch`
Прием batch событий

### Дашборд

#### GET `/api/v1/dashboard/sites`
Получение сайтов пользователя со статистикой

#### GET `/api/v1/dashboard/stats/{site_id}`
Статистика сайта за период
- `days` (query): количество дней (1-30, по умолчанию 7)

#### GET `/api/v1/dashboard/visits/{site_id}`
Список последних визитов
- `days` (query): количество дней (1-30, по умолчанию 7)
- `limit` (query): количество записей (1-100, по умолчанию 50)
- `offset` (query): смещение для пагинации

#### GET `/api/v1/dashboard/daily-stats/{site_id}`
Ежедневная статистика
- `days` (query): количество дней (1-30, по умолчанию 7)

## Обнаружение AI-ботов

Система автоматически классифицирует посетителей на основе User-Agent:

### Поддерживаемые AI-боты:
- **GPTBot** - OpenAI ChatGPT
- **PerplexityBot** - Perplexity AI
- **Google-Extended** - Google Gemini
- **Claude-Web** - Anthropic Claude
- **BingBot** - Microsoft Bing AI
- **facebookexternalhit** - Meta AI
- **Другие AI-боты** - расширяемый список

### Пример ответа с классификацией:
```json
{
  "status": "success",
  "message": "Event received and saved",
  "event_id": 123,
  "is_ai_bot": true,
  "bot_name": "GPTBot"
}
```

## Структура данных

### Событие отслеживания:
```json
{
  "id": 123,
  "site_id": "site_126c9b771139",
  "event_type": "page_view",
  "url": "https://example.com/page",
  "path": "/page",
  "title": "Page Title",
  "referrer": "https://google.com",
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.1",
  "screen_resolution": "1920x1080",
  "viewport_size": "1200x800",
  "language": "en-US",
  "timezone": "America/New_York",
  "is_ai_bot": "GPTBot",
  "bot_name": "GPTBot",
  "timestamp": "2025-09-24T18:00:00+00:00",
  "created_at": "2025-09-24T18:00:00+00:00"
}
```

## Логирование

Система ведет логи в папке `logs/`:

- **`app_YYYYMMDD.log`** - общие логи приложения
- **`tracking_YYYYMMDD.log`** - события отслеживания
- **`errors_YYYYMMDD.log`** - ошибки системы

### Пример лога события:
```
2025-09-24 18:20:08 - app.tracking - INFO - Tracking event: event_type=page_view | site_id=site_126c9b771139 | ip=127.0.0.1 | user_agent=PerplexityBot/1.0... | is_ai_bot=True | bot_name=PerplexityBot
```

## JavaScript Сниппет

Для интеграции на сайт используйте полученный сниппет:

```html
<!-- AI Detector Script -->
<script>
(function() {
    var script = document.createElement('script');
    script.src = 'http://localhost:8000/api/v1/tracking/site_126c9b771139.js';
    script.async = true;
    document.head.appendChild(script);
})();
</script>
<!-- End AI Detector Script -->
```

## CORS

API поддерживает CORS для следующих доменов:
- `http://localhost:3000`
- `http://localhost:8080`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:8080`
- `http://127.0.0.1:5500`

## Аутентификация

Все защищенные endpoints требуют Bearer токен в заголовке:
```
Authorization: Bearer <your_token>
```

## Статус коды

- `200` - Успешный запрос
- `400` - Неверные данные
- `401` - Не авторизован
- `404` - Ресурс не найден
- `500` - Внутренняя ошибка сервера
