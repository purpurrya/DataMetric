# DataMetric

Пет-проект для практики. 
На основе Retail Rocket ecommerce dataset (kaggle.com/datasets/retailrocket/ecommerce-dataset) загружает данные в ClickHouse и отдаёт аналитику через FastAPI.
Первая версия, где вместо работы с реальным датасетом осуществлялась работа с генерируемыми синтетическими данными хранится в ветке synth-ver репозитория.

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

### Скачивание датасета
Используется [Retail Rocket ecommerce dataset](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset).
Нужен настроенный Kaggle API токен.
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
- `scripts/ch_loader.py` — загрузка датасета (events, item_properties, category_tree) в ClickHouse
- `scripts/aggregation.py` — расчёт метрик на pandas
- `scripts/sql_aggregation.py` — те же метрики на SQL
- `sql/` — миграции ClickHouse

Версия проекта на синтетически сгенерированных данных (до перехода на Retail
Rocket) сохранена в ветке `synth-ver`.
