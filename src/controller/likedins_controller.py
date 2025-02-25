from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.configs import settings
from src.repositories.linkedins_repository import LinkedinsRepository
from src.services.likedins_service import LinkedinsService
from src.services.usuarios_service import UsuariosService
from src.services.authentication_service import AuthService
from src.repositories.usuarios_repository import UsuariosRepository
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.utils.dtos.connect import ConnectOut, ConnectIn
from src.utils.dtos.linkedin import LinkedinIn, LinkedinOut

bearer_scheme = HTTPBearer()
router = APIRouter()

async def get_db_session() -> AsyncSession:  # type: ignore
    async with settings.async_session_factory() as db_session:
        yield db_session

def get_usuarios_service(db: AsyncSession = Depends(get_db_session)) -> UsuariosService:
    usuarios_repo = UsuariosRepository(db)
    return UsuariosService(usuarios_repo)

def get_linkedins_service(usuarios_service:UsuariosService = Depends(get_usuarios_service),db: AsyncSession = Depends(get_db_session)) -> LinkedinsService:
    linkedins_repo = LinkedinsRepository(db)
    return LinkedinsService(usuarios_service,linkedins_repo)

def get_auth_service(usuarios_service: UsuariosService = Depends(get_usuarios_service)) -> AuthService:
    return AuthService(usuarios_service)

async def get_token_from_header(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    return credentials.credentials

def get_current_user(token: str = Depends(get_token_from_header), auth_service: AuthService = Depends(get_auth_service)):
    user = auth_service.verify_token(token)
    return user

def role_required(roles: list):
    def dependency(current_user: dict = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])  # Obtém a lista de roles
        if not any(role in user_roles for role in roles):
            raise HTTPException(status_code=403, detail="Acesso negado")
        return current_user
    return dependency


#Routes
@router.post("/linkedins", response_model=LinkedinOut, tags=["Linkedin"])
async def cadastrar_linkedin(linkedin:LinkedinIn, linkedins_service: LinkedinsService = Depends(get_linkedins_service),jwt_with_role: dict = Depends(role_required(["USUARIO", "ADMIN"]))):
    if "roles" in jwt_with_role:
        linkedin = await linkedins_service.cadastrar_linkedin(linkedin)
        return linkedin
    else:
        raise HTTPException(status_code=403, detail="Acesso negado: Roles insuficientes")

@router.get("/linkedins/usuarios/{email}", response_model=LinkedinOut, tags=["Linkedin"])
async def get_linkedin_usuario_by_id(email: str, linkedins_service: LinkedinsService = Depends(get_linkedins_service), jwt_with_role: dict = Depends(role_required(["USUARIO", "ADMIN"]))):
    if "roles" in jwt_with_role:
        linkedin = await linkedins_service.get_linkedin_by_email(email)
        return linkedin
    else:
        raise HTTPException(status_code=403, detail="Acesso negado: Roles insuficientes")

@router.post("/automatize/connections", response_model=ConnectOut, tags=["Linkedin"])
async def create_new_conection_linkedin(connect_obj:ConnectIn, linkedins_service: LinkedinsService = Depends(get_linkedins_service),jwt_with_role: dict = Depends(role_required(["USUARIO", "ADMIN"]))):
    if "roles" in jwt_with_role:
        data:ConnectOut = await linkedins_service.get_connections(connect_obj)
        return data
    else:
        raise HTTPException(status_code=403, detail="Acesso negado: Roles insuficientes")

