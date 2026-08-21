# DataMetric

Пет-проект для практики. 
Генерирует синтетические события интернет-магазина, загружает их в ClickHouse и отдаёт аналитику через FastAPI.

## Технологии
- Python
- FastAPI
- ClickHouse
- Pandas / NumPy
- Docker Compose
- uv

## Развёртывание

### Клонирование репозитория
```bash
git clone https://github.com/purpurrya/DataMetric.git
cd DataMetric
```

### Установка зависимостей
```bash
uv sync
```

### Настройка окружения
```bash
cp .env.example .env
```

### Запуск ClickHouse и приложения
```bash
docker compose up -d
```

### Генерация синтетических данных
```bash
uv run python -m scripts.event_generator
```

### Загрузка данных в ClickHouse
```bash
uv run python -m scripts.ch_loader
```

API будет доступно по адресу:
```
http://localhost:8000/docs
```

## API

### Health
- `GET /health` — проверка доступности ClickHouse

### Статистика
- `GET /stat/funnel` — конверсия по воронке view → cart → checkout → purchase
- `GET /stat/revenue-by-city` — доход по городам
- `GET /stat/daily` — сессии и доход по дням
- `GET /stat/summary` — средний чек, cart abandonment rate, purchase fail rate, длительность сессий

## Структура проекта
- `main.py` — FastAPI-приложение
- `schemas.py` — Pydantic-модели ответов
- `scripts/event_generator.py` — генерация синтетических событий
- `scripts/ch_loader.py` — загрузка csv в ClickHouse
- `scripts/aggregation.py` — расчёт метрик на pandas
- `scripts/sql_aggregation.py` — те же метрики на SQL
- `sql/` — миграции ClickHouse
