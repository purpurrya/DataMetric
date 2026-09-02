# DataMetric

Пет-проект для практики. 
На основе Retail Rocket ecommerce dataset (kaggle.com/datasets/retailrocket/ecommerce-dataset) загружает данные в ClickHouse и отдаёт аналитику через FastAPI.
Первая версия, где вместо работы с реальным датасетом осуществлялась работа с генерируемыми синтетическими данными хранится в ветке `synth-ver` репозитория.

## Технологии
- Python
- FastAPI
- ClickHouse
- Redis
- Pandas
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
uv sync --all-groups
```

### Настройка окружения
```bash
cp .env.example .env
```

### Запуск ClickHouse и приложения
```bash
docker compose up -d
```

### Скачивание датасета
Используется [Retail Rocket ecommerce dataset](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset).
```bash
make download-data
```

### Загрузка данных в ClickHouse
```bash
make load
```

API будет доступно по адресу:
```
http://localhost:8000/docs
```

### Дашборд (Streamlit)

В Docker Compose дашборд поднимается вместе с остальными сервисами и доступен на `http://localhost:8501`.

Чтобы запустить дашборд без Docker (например, для разработки):
```bash
# 1. Поднять только ClickHouse и Redis в Docker
docker compose up -d clickhouse redis

# 2. Запустить API локально (host=localhost уже настроен в .env)
make dev

# 3. В отдельном терминале запустить дашборд
make dashboard
# или напрямую:
uv run --group dashboard streamlit run dashboard/app.py
```
Дашборд откроется на `http://localhost:8501` и обращается к API по адресу из переменной окружения `API_URL` (по умолчанию `http://localhost:8000`).

### Тесты
```bash
make test
```

## API

### Health
- `GET /health` — проверка доступности ClickHouse

### Статистика
- `GET /stat/funnel` — конверсия по воронке view → cart (addtocart) → purchase (transaction)
- `GET /stat/purchases-by-category` — количество покупок по категориям товара
- `GET /stat/daily` — сессии и транзакции по дням
- `GET /stat/summary` — среднее число товаров в транзакции, cart abandonment rate, view-to-cart rate, статистика длительности и размера сессий

## Структура проекта
- `main.py` — FastAPI-приложение
- `schemas.py` — Pydantic-модели ответов
- `dashboard/app.py` — Streamlit-дашборд, читает данные из API
- `scripts/ch_loader.py` — загрузка датасета (events, item_properties, category_tree) в ClickHouse
- `scripts/aggregation.py` — расчёт метрик на pandas
- `scripts/sql_aggregation.py` — те же метрики на SQL
- `scripts/config/` — настройки (`settings.py`) и логирование (`logging.py`)
- `sql/` — миграции ClickHouse
- `tests/` — тесты
- `Dockerfile` — образ API
- `Dockerfile.dashboard` — образ дашборда
