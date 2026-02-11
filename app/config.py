# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "GPU as a Service"
    PROJECT_VERSION: str = "0.1.0"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # DB
    DB_USER: str = os.getenv("DB_USER", "gpu_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "gpu_password")
    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "gpu_service")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # JWT
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "change_this_in_production_super_secret_key",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()
