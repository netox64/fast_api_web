from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from src.models.usuarios import UsuariosModel


class UsuariosRepository:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_all(self) -> List[UsuariosModel]:
        result = await self.db_session.execute(select(UsuariosModel))
        return result.scalars().all()

    async def get_by_email(self, email: str) -> Optional[UsuariosModel]:
        result = await self.db_session.execute(select(UsuariosModel).filter(UsuariosModel.email == email))
        return result.scalars().first()  # Retorna o usuário ou None
    
    async def get_by_id(self, pessoa_id: int) -> Optional[UsuariosModel]:
        result = await self.db_session.execute(
            select(UsuariosModel).filter(UsuariosModel.id == pessoa_id)
        )
        return result.scalars().first()  # Retorna a primeira pessoa ou None

    async def create(self, usuario:UsuariosModel ) -> UsuariosModel:
        self.db_session.add(usuario)
        await self.db_session.commit()
        await self.db_session.refresh(usuario)  # Atualiza o objeto com os dados do banco
        return usuario

    async def update(self, pessoa_id: int, username: str, funcao: str, imagem: str) -> Optional[UsuariosModel]:
        pessoa = await self.get_by_id(pessoa_id)
        if pessoa:
            pessoa.username = username
            pessoa.funcao = funcao
            pessoa.imagem = imagem
            await self.db_session.commit()
            await self.db_session.refresh(pessoa)
            return pessoa
        return None

    async def delete(self, pessoa_id: int) -> bool:
        pessoa = await self.get_by_id(pessoa_id)
        if pessoa:
            await self.db_session.delete(pessoa)
            await self.db_session.commit()
            return True
        return False
