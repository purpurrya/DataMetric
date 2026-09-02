.PHONY: help install dev dashboard test lint format clean docker-build docker-up docker-down download-data load

help:
	@echo "Available commands:"
	@echo "  make install       Install dependencies"
	@echo "  make dev           Run development server (API)"
	@echo "  make dashboard     Run Streamlit dashboard locally"
	@echo "  make test          Run tests"
	@echo "  make lint          Run linter"
	@echo "  make format        Format code"
	@echo "  make clean         Clean cache files"
	@echo "  make docker-build  Build Docker images"
	@echo "  make docker-up     Start Docker containers (API, dashboard, ClickHouse, Redis)"
	@echo "  make docker-down   Stop Docker containers"
	@echo "  make download-data Download dataset"
	@echo "  make load          Load dataset to ClickHouse"

install:
	uv sync --all-groups

dev:
	uv run fastapi dev main.py

dashboard:
	uv run --group dashboard streamlit run dashboard/app.py

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	uv run find . -type f -name '*.pyc' -delete
	uv run find . -type d -name '__pycache__' -delete

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

download-data:
	kaggle datasets download -d retailrocket/ecommerce-dataset -p data/raw --unzip

load:
	uv run python -m scripts.ch_loader
