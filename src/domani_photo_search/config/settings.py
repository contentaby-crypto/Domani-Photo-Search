from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "domani-photo-search"
    app_env: str = "dev"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    csv_source_path: str = "/mnt/data/База данных фото Domani - New (4).csv"
    processed_data_dir: str = "./data/processed"
    photos_jsonl_path: str = "./data/processed/photos.jsonl"
    dictionaries_dir: str = "./data/processed/dictionaries"
    history_db_path: str = "./data/processed/query_history.sqlite3"

    bot_token: str = ""
    telegram_secret_token: str = ""
    telegram_api_base: str = "https://api.telegram.org"
    search_api_base_url: str = "http://localhost:8000"

    openai_api_key: str = ""
    openai_model: str = "gpt-5"
    openai_timeout_sec: int = 30
    enable_llm_ranking: bool = False

    admin_api_token: str = "change-me"

    @property
    def processed_dir(self) -> Path:
        return Path(self.processed_data_dir)

    @property
    def photos_index_path(self) -> Path:
        return Path(self.photos_jsonl_path)

    @property
    def dictionaries_path(self) -> Path:
        return Path(self.dictionaries_dir)

    @property
    def history_db(self) -> Path:
        return Path(self.history_db_path)


settings = Settings()
