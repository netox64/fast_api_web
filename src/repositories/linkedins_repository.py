from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy.future import select
from src.models.linkedin import LinkedinModel


class LinkedinsRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_all(self) -> List[LinkedinModel]:
        result = await self.db_session.execute(select(LinkedinModel))
        return result.scalars().all()

    async def get_by_email(self, email: str) -> Optional[LinkedinModel]:
        result = await self.db_session.execute(select(LinkedinModel).filter(LinkedinModel.email == email))
        return result.scalars().first()

    async def get_by_id(self, linkedin_id: int) -> Optional[LinkedinModel]:
        result = await self.db_session.execute(
            select(LinkedinModel).filter(LinkedinModel.id == linkedin_id)
        )
        return result.scalars().first()  # Retorna a primeira pessoa ou None

    async def create(self, linkedin: LinkedinModel) -> LinkedinModel:
        self.db_session.add(linkedin)
        await self.db_session.commit()
        await self.db_session.refresh(linkedin)  # Atualiza o objeto com os dados do banco
        return linkedin

    async def delete(self, linkedin_id: int) -> bool:
        pessoa = await self.get_by_id(linkedin_id)
        if pessoa:
            await self.db_session.delete(pessoa)
            await self.db_session.commit()
            return True
        return False