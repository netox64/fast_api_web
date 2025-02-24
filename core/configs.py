from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import ClassVar


class Settings(BaseSettings):
    # URL de conexão com PostgreSQL usando asyncpg
    DB_URL: str = "postgresql+asyncpg://root:root@localhost:5432/fast_api"

    # Base para os modelos do SQLAlchemy
    DBBaseModel: ClassVar = declarative_base()

    # Método para criar a fábrica de sessões assíncronas
    @property
    def async_session_factory(self):
        engine = create_async_engine(self.DB_URL, echo=True)
        return sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    class Config:
        case_sensitive = True


# Instância única das configurações
settings = Settings()
