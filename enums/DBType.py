from enum import Enum


class DBType(str, Enum):
    SQLITE = "sqlite"
    POSTGRES = "postgres"
