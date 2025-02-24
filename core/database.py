from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from core.configs import settings

# Criando o motor assíncrono de conexão com o banco de dados
engine: AsyncEngine = create_async_engine(settings.DB_URL, echo=False)

# Criando um factory de sessões assíncronas
async_session_factory = sessionmaker(bind=engine,autocommit=False,autoflush=False,expire_on_commit=False,class_=AsyncSession)


# Dependência para injetar sessão no FastAPI
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


# Criando tabelas no banco de dados
async def create_tables() -> None:
    import src.models.__all__models  # Importa todos os modelos antes de criar as tabelas

    print("Criando tabelas no banco de dados...")

    async with engine.begin() as conn:
        await conn.run_sync(settings.DBBaseModel.metadata.drop_all)
        await conn.run_sync(settings.DBBaseModel.metadata.create_all)

    print("Tabelas criadas com sucesso!")
