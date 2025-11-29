# Weather Service API ⛅

Асинхронный микросервис для обработки данных о погодных условиях в разных городах.

## Возможности

- **CRUD операции** для записей о погоде
- **Асинхронная архитектура** на базе FastAPI и asyncio
- **Автоматическое обновление** данных о погоде по расписанию
- **Интеграция с OpenWeatherMap API** для получения реальных данных
- **Система логирования** всех действий с интерфейсом просмотра
- **Swagger/ReDoc документация** API
- **Docker контейнеризация** для простого развертывания

## Технологический стек

- **Backend**: Python 3.11, FastAPI, Pydantic v2
- **База данных**: PostgreSQL 15, SQLAlchemy 2.0 (async)
- **Миграции**: Alembic
- **Планировщик**: APScheduler
- **Контейнеризация**: Docker, Docker Compose

## Структура проекта

```
weather_service/
├── app/
│   ├── api/              # API эндпоинты
│   │   ├── weather.py    # CRUD для погоды
│   │   └── logs.py       # Просмотр логов
│   ├── models/           # SQLAlchemy модели
│   │   ├── weather.py    # Модель погоды
│   │   └── log.py        # Модель логов
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес-логика
│   │   ├── weather_service.py
│   │   ├── weather_fetcher.py
│   │   └── log_service.py
│   ├── tasks/            # Периодические задачи
│   │   └── scheduler.py
│   ├── config.py         # Конфигурация
│   ├── database.py       # Настройка БД
│   └── main.py           # Точка входа
├── alembic/              # Миграции БД
├── tests/                # Unit тесты
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Быстрый старт

### Запуск с Docker (рекомендуется)

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd weather_service
```

2. (Опционально) Настройте API ключ OpenWeatherMap:
```bash
cp .env.example .env
# Отредактируйте .env и добавьте WEATHER_API_KEY
```

3. Запустите сервис:
```bash
docker-compose up -d --build
```

4. Сервис доступен по адресу: http://localhost:8000

### Локальный запуск (для разработки)

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Запустите PostgreSQL (можно через Docker):
```bash
docker run -d --name weather_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=weather_db \
  -p 5432:5432 \
  postgres:15-alpine
```

4. Настройте переменные окружения:
```bash
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/weather_db
```

5. Примените миграции:
```bash
alembic upgrade head
```

6. Запустите сервер:
```bash
uvicorn app.main:app --reload
```

## API Документация

После запуска сервиса доступны:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Основные эндпоинты

#### Погода

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/v1/weather/` | Список записей о погоде |
| POST | `/api/v1/weather/` | Создать запись |
| GET | `/api/v1/weather/{id}` | Получить запись по ID |
| PUT | `/api/v1/weather/{id}` | Обновить запись |
| DELETE | `/api/v1/weather/{id}` | Удалить запись |
| GET | `/api/v1/weather/city/{city}` | Получить погоду по городу |
| POST | `/api/v1/weather/fetch/{city}` | Загрузить данные из API |
| GET | `/api/v1/weather/cities` | Список городов |

#### Логи

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/v1/logs/` | Список логов (с фильтрами) |
| GET | `/api/v1/logs/{id}` | Получить лог по ID |
| GET | `/api/v1/logs/summary` | Статистика по действиям |

### Примеры запросов

#### Создание записи о погоде

```bash
curl -X POST "http://localhost:8000/api/v1/weather/" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Moscow",
    "country": "RU",
    "temperature": 15.5,
    "humidity": 60,
    "pressure": 1013
  }'
```

#### Получение погоды для города

```bash
curl "http://localhost:8000/api/v1/weather/city/Moscow"
```

#### Загрузка данных из внешнего API

```bash
curl -X POST "http://localhost:8000/api/v1/weather/fetch/London,UK"
```

#### Получение списка с фильтрами

```bash
curl "http://localhost:8000/api/v1/weather/?page=1&size=10&city=Moscow"
```

#### Просмотр логов

```bash
curl "http://localhost:8000/api/v1/logs/?action=CREATE&status=success"
```

## Запуск тестов

### Через pytest

```bash
# Установите зависимости для тестов
pip install -r requirements.txt

# Запустите все тесты
pytest

# С отчетом покрытия
pytest --cov=app --cov-report=html

# Конкретный тестовый файл
pytest tests/test_weather_api.py -v
```

### Через Docker

```bash
docker-compose run --rm api pytest
```

## Конфигурация

Переменные окружения:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL подключения к БД | `postgresql+asyncpg://...` |
| `WEATHER_API_KEY` | Ключ API OpenWeatherMap | (пусто - mock данные) |
| `WEATHER_UPDATE_INTERVAL_MINUTES` | Интервал обновления | `30` |
| `DEFAULT_CITIES` | Города для мониторинга | `Moscow,London,...` |
| `DEBUG` | Режим отладки | `false` |

### Получение API ключа OpenWeatherMap

1. Зарегистрируйтесь на https://openweathermap.org/
2. Получите бесплатный API ключ
3. Добавьте в `.env` файл:
   ```
   WEATHER_API_KEY=your_api_key_here
   ```

> **Примечание**: Без API ключа сервис работает в режиме mock-данных (генерирует случайные реалистичные данные).

## Модель данных

### Weather (Погода)

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Уникальный ID |
| city | String | Название города |
| country | String | Страна |
| temperature | Float | Температура (°C) |
| feels_like | Float | Ощущается как |
| humidity | Float | Влажность (%) |
| pressure | Float | Давление (hPa) |
| wind_speed | Float | Скорость ветра (м/с) |
| wind_direction | Integer | Направление ветра (°) |
| cloudiness | Integer | Облачность (%) |
| weather_description | String | Описание погоды |
| visibility | Integer | Видимость (м) |
| data_timestamp | DateTime | Время данных |
| created_at | DateTime | Время создания записи |
| updated_at | DateTime | Время обновления |

### ActionLog (Лог действий)

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Уникальный ID |
| action | String | Тип действия (CREATE/UPDATE/DELETE/FETCH) |
| entity | String | Сущность |
| entity_id | Integer | ID сущности |
| details | Text | Детали (JSON) |
| status | String | Статус (success/error) |
| error_message | Text | Сообщение об ошибке |
| ip_address | String | IP адрес клиента |
| user_agent | String | User-Agent |
| created_at | DateTime | Время создания |

## Архитектура

### Асинхронность

- Все операции с БД выполняются асинхронно через SQLAlchemy async
- HTTP клиент (httpx) для запросов к внешним API
- AsyncIOScheduler для периодических задач

### Планировщик задач

Сервис автоматически обновляет данные о погоде:
- Интервал настраивается через `WEATHER_UPDATE_INTERVAL_MINUTES`
- Города для мониторинга в `DEFAULT_CITIES`
- Параллельное получение данных для всех городов

## Остановка сервиса

```bash
docker-compose down

# С удалением данных
docker-compose down -v
```

## Лицензия

MIT

## Автор

Backend Developer Test Task

