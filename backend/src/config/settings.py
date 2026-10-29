from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator, SecretStr
from typing import Literal
from urllib.parse import urlsplit
import re


class Settings(BaseSettings):
    app_name: str = "CampusLink Backend"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api"

    database_url: str = "sqlite:///./data/campuslink.db"

    jwt_secret_key: str = "replace-with-a-random-secret-at-least-32-bytes-long"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    auto_create_tables: bool = True
    seed_demo_data: bool = True
    upload_dir: str = "./data/uploads"
    upload_storage: Literal['local', 'supabase'] = 'local'
    supabase_url: str | None = None
    supabase_storage_key: SecretStr | None = None
    supabase_storage_bucket: str = 'campuslink-images'
    frontend_dist: str | None = None

    @model_validator(mode='after')
    def validate_production_settings(self):
        if self.upload_storage == 'supabase':
            parts = urlsplit(self.supabase_url or '')
            if (parts.scheme != 'https' or not re.fullmatch(r'[a-z0-9-]+\.supabase\.co', parts.netloc)
                    or parts.path not in ('', '/') or parts.query or parts.fragment):
                raise ValueError('Supabase storage requires an official HTTPS project URL')
            if not self.supabase_storage_key or not self.supabase_storage_key.get_secret_value().strip():
                raise ValueError('Supabase storage requires a server-only storage key')
            key = self.supabase_storage_key.get_secret_value()
            if not key.startswith(('sb_secret_', 'eyJ')):
                raise ValueError('Use a server-only secret key or legacy service_role key, not a publishable key')
            if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,62}', self.supabase_storage_bucket):
                raise ValueError('Invalid Supabase bucket name')
        if self.app_env.lower() == 'production':
            if not self.database_url.startswith('postgresql'):
                raise ValueError('Production mode requires PostgreSQL')
            if len(self.jwt_secret_key) < 32 or self.jwt_secret_key.startswith(('replace-', 'change-')):
                raise ValueError('Production mode requires a private random JWT secret of at least 32 characters')
            if self.debug or self.seed_demo_data or self.auto_create_tables:
                raise ValueError('Production mode requires debug, demo seeding and automatic table creation to be disabled')
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CAMPUSLINK_",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

