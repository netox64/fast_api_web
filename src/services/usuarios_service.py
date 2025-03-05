from src.repositories.usuarios_repository import UsuariosRepository
from src.models.usuarios import UsuariosModel
from typing import List, Optional
from fastapi import HTTPException
from passlib.context import CryptContext
from src.utils.dtos.user import UserCreate


class UsuariosService:
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, usuarios_repository: UsuariosRepository):
        self.usuarios_repository = usuarios_repository

    async def get_all_usuarios(self) -> List[UsuariosModel]:
        return await self.usuarios_repository.get_all()

    async def get_usuarios_by_id(self, id: int) -> Optional[UsuariosModel]:
        pessoa = await self.usuarios_repository.get_by_id(id)
        if not pessoa:
            raise HTTPException(status_code=404, detail="Pessoa não encontrada")
        return pessoa

    async def create_usuarios(self, usuario_dto:UserCreate) -> UsuariosModel:
        usuario_com_email = await self.usuarios_repository.get_by_email(str(usuario_dto.email))
        if usuario_com_email:
            raise HTTPException(status_code=409, detail="Ja existe um usuario com esse email no sistema")
        hashed_password:str = self.pwd_context.hash(usuario_dto.password)
        usuario_data = usuario_dto.model_dump()
        usuario_data['password'] = hashed_password 
        usuario_data['roles'] = ['USUARIO']  # Adicionar role padrão se não fornecido
            
        usuario: UsuariosModel = UsuariosModel(**usuario_data)
        return await self.usuarios_repository.create(usuario)

    async def update_usuarios(self, id: int, nome: str, funcao: str, imagem: str) -> Optional[UsuariosModel]:
        pessoa = await self.usuarios_repository.update(id, nome, funcao, imagem)
        if not pessoa:
            raise HTTPException(status_code=404, detail="Pessoa não encontrada")
        return pessoa

    async def delete_usuarios(self, id: int) -> bool:
        return await self.usuarios_repository.delete(id)
    
    async def get_usuario_by_email(self, email: str) -> Optional[UsuariosModel]:
        pessoa = await self.usuarios_repository.get_by_email(email)
        if not pessoa:
            raise HTTPException(status_code=404, detail="Pessoa não encontrada")
        return pessoa
