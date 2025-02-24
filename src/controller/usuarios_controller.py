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

# Definido Esquema de segurança Bearer Token para Swagger, manter nas requisições
bearer_scheme = HTTPBearer()
router = APIRouter()

#TODO: Instanciação das dependencias para injeção ->

# Dependência para injetar a sessão do banco
async def get_db_session() -> AsyncSession:  # type: ignore
    async with settings.async_session_factory() as db_session:
        yield db_session

# Dependência para o serviço
def get_usuarios_service(db: AsyncSession = Depends(get_db_session)) -> UsuariosService:
    usuarios_repo = UsuariosRepository(db)
    return UsuariosService(usuarios_repo)

# Dependência para o serviço de autenticação
def get_auth_service(usuarios_service: UsuariosService = Depends(get_usuarios_service)) -> AuthService:
    return AuthService(usuarios_service)

#TODO #1 Dependência para pegar o token manualmente
# async def get_token_from_header(request: Request):
#     authorization: str = request.headers.get("Authorization")
#     if not authorization:
#         raise HTTPException(status_code=401, detail="Authorization header missing")
# 
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Invalid authorization code")
# 
#     token = authorization[7:]  # Remove o "Bearer " e fica com o token
#     return token

#TODO #1 extrai da mesma forma o token
async def get_token_from_header(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    return credentials.credentials

#TODO #2 Middleware ou Dependência para pegar o token e verificar usando AuthService
def get_current_user(token: str = Depends(get_token_from_header), auth_service: AuthService = Depends(get_auth_service)):
    user = auth_service.verify_token(token)
    return user

#TODO #3 Middleware ou Dependência
def role_required(roles: list):
    def dependency(current_user: dict = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])  # Obtém a lista de roles
        if not any(role in user_roles for role in roles):
            raise HTTPException(status_code=403, detail="Acesso negado")
        return current_user
    return dependency

#TODO:Endpoint ---------------------------------------------------------------------------------------------------------
# rota padrão swagger
@router.get("/users/me")
async def read_users_me(token: str = Depends(bearer_scheme)):
    return {"token": token}

# Endpoint para autenticação (gerar token)
@router.post("/auth/login", response_model=Token,tags=["Auth"])
async def login_for_access_token(usuario: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    token_acess: str = await auth_service.authenticar(usuario)
    return Token(jwt = token_acess)


# Endpoint para criar uma pessoa
@router.post("/usuarios", response_model=None, tags=["Usuário"])
async def create_usuario(usuario:UserCreate, usuarios_service: UsuariosService = Depends(get_usuarios_service)):
    usuario = await usuarios_service.create_usuarios(usuario)
    return usuario


# Endpoint para obter todos os usuarios
@router.get("/usuarios", response_model=None, tags=["Usuário"])
async def get_usuarios(usuarios_service: UsuariosService = Depends(get_usuarios_service), jwt: dict = Depends(get_current_user)):
    if "id" in jwt:
        usuarios = await usuarios_service.get_all_usuarios()
        return usuarios
    else:
        raise HTTPException(status_code=403, detail="Acesso negado: Roles insuficientes")


# Endpoint para obter um usuario pelo ID
@router.get("/usuarios/{usuario_id}", response_model=None, tags=["Usuário"])
async def get_usuario(usuario_id: int, usuarios_service: UsuariosService = Depends(get_usuarios_service), jwt_with_role: dict = Depends(role_required(["USUARIO", "ADMIN"]))):
    if "roles" in jwt_with_role:
        usuario = await usuarios_service.get_usuarios_by_id(usuario_id)
        return usuario
    else:
        raise HTTPException(status_code=403, detail="Acesso negado: Roles insuficientes")

