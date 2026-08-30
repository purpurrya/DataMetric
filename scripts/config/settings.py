from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8123
    clickhouse_db: str = "datametric"
    clickhouse_user: str = "default"
    clickhouse_password: str = "clickhouse_password"

    redis_host: str = "localhost"
    redis_port: int = 6379

    data_dir: str = "data/raw"


settings = Settings()
