from pathlib import Path

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"

# Load .env before Settings reads values (absolute path, not CWD-dependent)
_env_loaded = load_dotenv(ENV_FILE, override=False)


class Settings(BaseSettings):
    nvidia_api_key: str = ""
    nim_model: str = "meta/llama-3.3-70b-instruct"
    nim_embed_model: str = "nvidia/nv-embedqa-e5-v5"
    demo_mode: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    knowledge_dir: str = "knowledge"
    memory_db_path: str = "data/memory"
    retrieval_threshold: float = 0.35

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("demo_mode", mode="before")
    @classmethod
    def parse_demo_mode(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)

    @field_validator("nvidia_api_key", mode="before")
    @classmethod
    def strip_api_key(cls, value: object) -> str:
        if value is None:
            return ""
        text = str(value).strip()
        if text.lower() in {"", "your_nvidia_api_key_here", "none", "null"}:
            return ""
        return text

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def use_nvidia(self) -> bool:
        return bool(self.nvidia_api_key) and not self.demo_mode

    @property
    def env_file_path(self) -> Path:
        return ENV_FILE

    @property
    def env_file_loaded(self) -> bool:
        return _env_loaded and ENV_FILE.exists()

    @property
    def masked_api_key(self) -> str:
        if not self.nvidia_api_key:
            return "NOT SET"
        key = self.nvidia_api_key
        if len(key) <= 8:
            return "***"
        return f"{key[:4]}...{key[-4:]}"


settings = Settings()
