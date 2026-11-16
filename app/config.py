"""Configuração via variáveis de ambiente (sem hardcode de produção)."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Lê .env e o ambiente do processo. Trocar o banco é só mudar DATABASE_URL."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = Field(default="development", alias="ENV")
    secret_key: str = Field(
        default="troque-esta-chave-em-producao-use-valor-longo-e-aleatorio",
        alias="SECRET_KEY",
    )
    database_url: str = Field(default="sqlite:///./data/app.db", alias="DATABASE_URL")
    access_token_minutes: int = Field(default=15, alias="ACCESS_TOKEN_MINUTES")
    refresh_token_days: int = Field(default=7, alias="REFRESH_TOKEN_DAYS")
    allowed_origins: str = Field(default="", alias="ALLOWED_ORIGINS")
    seed_on_start: bool = Field(default=True, alias="SEED_ON_START")

    # Valor padrão proibido em produção
    _DEFAULT_SECRET: str = "troque-esta-chave-em-producao-use-valor-longo-e-aleatorio"

    @field_validator("env")
    @classmethod
    def normalizar_env(cls, value: str) -> str:
        return value.strip().lower()

    @property
    def is_production(self) -> bool:
        return self.env in {"production", "prod"}

    @property
    def cors_origins(self) -> list[str]:
        if not self.allowed_origins.strip():
            return []
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    def validate_for_boot(self) -> None:
        """Falha cedo se a chave secreta padrão for usada em produção."""
        if self.is_production and self.secret_key == self._DEFAULT_SECRET:
            raise RuntimeError(
                "SECRET_KEY está com o valor padrão. "
                "Defina uma chave longa e aleatória antes de subir em produção."
            )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_for_boot()
    return settings
