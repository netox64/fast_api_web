from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.configs import settings
from src.services.usuarios_service import UsuariosService
from src.services.authentication_service import AuthService
from src.repositories.usuarios_repository import UsuariosRepository
from src.utils.dtos.user import UserCreate
from src.utils.dtos.user_login import LoginRequest
from src.utils.dtos.token import Token
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer()
router = APIRouter()

async def get_db_session() -> AsyncSession:  # type: ignore
    async with settings.async_session_factory() as db_session:
        yield db_session

def get_usuarios_service(db: AsyncSession = Depends(get_db_session)) -> UsuariosService:
    usuarios_repo = UsuariosRepository(db)
    return UsuariosService(usuarios_repo)

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
@router.get("/users/me")
async def read_users_me(token: str = Depends(bearer_scheme)):
    return {"token": token}

@router.post("/auth/login", response_model=Token,tags=["Auth"])
async def login_for_access_token(usuario: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    token_acess: str = await auth_service.authenticar(usuario)
    return Token(jwt = token_acess)

@router.post("/usuarios", response_model=None, tags=["Usuário"])
async def create_usuario(usuario:UserCreate, usuarios_service: UsuariosService = Depends(get_usuarios_service)):
    usuario = await usuarios_service.create_usuarios(usuario)
    return usuario

@router.get("/usuarios", response_model=None, tags=["Usuário"])
async def get_usuarios(usuarios_service: UsuariosService = Depends(get_usuarios_service), jwt: dict = Depends(get_current_user)):
    if "id" in jwt:
        usuarios = await usuarios_service.get_all_usuarios()
        return usuarios
    else:
        raise HTTPException(status_code=403, detail="Acesso negado: Roles insuficientes")

@router.get("/usuarios/{usuario_id}", response_model=None, tags=["Usuário"])
async def get_usuario(usuario_id: int, usuarios_service: UsuariosService = Depends(get_usuarios_service), jwt_with_role: dict = Depends(role_required(["USUARIO", "ADMIN"]))):
    if "roles" in jwt_with_role:
        usuario = await usuarios_service.get_usuarios_by_id(usuario_id)
        return usuario
    else:
        raise HTTPException(status_code=403, detail="Acesso negado: Roles insuficientes")

