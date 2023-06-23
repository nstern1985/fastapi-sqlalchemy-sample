import os
from typing import Optional
from pydantic import BaseSettings
from enums.DBType import DBType


class Settings(BaseSettings):
    ROLE_NAME: str = "employees-api-manager"
    ENV: str = "dev"

    DB_DRIVER: str = DBType.SQLITE
    DB_PORT: Optional[int] = None
    DB_HOST: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USERNAME: Optional[str] = None
    DB_PASSWORD: Optional[str] = None

    # region local app settings
    APP_HOST: str = "localhost"
    APP_PORT: int = 5000
    # endregion

    SWAGGER_API_KEY: str = "1234567"

    class Config:
        case_sensitive = True


settings = Settings(_env_file=os.path.join(f"{os.path.dirname(os.path.abspath(__file__))}", ".env"))
