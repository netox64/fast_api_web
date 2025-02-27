from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.linkedins_repository import LinkedinsRepository
from src.repositories.usuarios_repository import UsuariosRepository
from src.services.authentication_service import AuthService
from src.services.likedins_service import LinkedinsService
from src.services.usuarios_service import UsuariosService
from core.configs import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException

bearer_scheme = HTTPBearer()

async def get_db_session() -> AsyncSession:
    """Obtém uma sessão de banco de dados"""
    async with settings.async_session_factory() as db_session:
        yield db_session

def get_usuarios_service(db: AsyncSession = Depends(get_db_session)) -> UsuariosService:
    """Obtém o serviço de usuários"""
    usuarios_repo = UsuariosRepository(db)
    return UsuariosService(usuarios_repo)

def get_linkedins_service( usuarios_service: UsuariosService = Depends(get_usuarios_service),
                              db: AsyncSession = Depends(get_db_session)) -> LinkedinsService:
    """Obtém o serviço de LinkedIns"""
    linkedins_repo = LinkedinsRepository(db)
    return LinkedinsService(usuarios_service, linkedins_repo)

def get_auth_service( usuarios_service: UsuariosService = Depends(get_usuarios_service)) -> AuthService:
    """Obtém o serviço de autenticação"""
    return AuthService(usuarios_service)

async def get_token_from_header( credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """Obtém o token de autenticação"""
    return credentials.credentials

def get_current_user( token: str = Depends(get_token_from_header),auth_service: AuthService = Depends(get_auth_service)):
    """Obtém o usuário a partir do token"""
    user = auth_service.verify_token(token)
    return user

def role_required(roles: list):
    """Verifica se o usuário tem a role necessária"""

    def dependency(current_user: dict = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])
        if not any(role in user_roles for role in roles):
            raise HTTPException(status_code=403, detail="Acesso negado")
        return current_user

    return dependency