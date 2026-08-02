.PHONY: helhelp install dev test lint format clean docker-build docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install      Install dependencies"
	@echo "  make dev          Run development server"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linter"
	@echo "  make format       Format code"
	@echo "  make clean        Clean cache files"
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-up    Start Docker containers"
	@echo "  make docker-down  Stop Docker containers"

install:
	uv sync

dev:
	uv run fastapi dev main.py

test:
	uv run pytest

lint:
	uv run flake8

format:
	uv run black .

clean:
	uv run find . -type f -name '*.pyc' -delete
	uv run find . -type d -name '__pycache__' -delete

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down