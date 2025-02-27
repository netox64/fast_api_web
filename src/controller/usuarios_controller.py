from fastapi import APIRouter, Depends
from fastapi import HTTPException
from src.controller.container_ioc import get_usuarios_service, get_current_user, role_required, get_token_from_header, \
    get_auth_service
from src.services.authentication_service import AuthService
from src.services.usuarios_service import UsuariosService
from src.utils.dtos.user import UserCreate
from src.utils.dtos.user_login import LoginRequest
from src.utils.dtos.token import Token

class UsuariosController:
    def __init__(self):
        self.router = APIRouter()

        @self.router.get("/users/me")
        async def read_users_me(token: str = Depends(get_token_from_header)):
            return {"token": token}

        @self.router.post("/auth/login", response_model=Token, tags=["Auth"])
        async def login_for_access_token(usuario: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
            token_acess: str = await auth_service.authenticar(usuario)
            return Token(jwt=token_acess)

        @self.router.post("/usuarios", response_model=None, tags=["Usuário"])
        async def create_usuario(usuario: UserCreate, usuarios_service: UsuariosService = Depends(get_usuarios_service)):
            usuario = await usuarios_service.create_usuarios(usuario)
            return usuario

        @self.router.get("/usuarios", response_model=None, tags=["Usuário"])
        async def get_usuarios(usuarios_service: UsuariosService = Depends(get_usuarios_service), jwt: dict = Depends(get_current_user)):
            if "id" in jwt:
                usuarios = await usuarios_service.get_all_usuarios()
                return usuarios
            else:
                raise HTTPException(status_code=403, detail="Acesso negado: Roles insuficientes")

        @self.router.get("/usuarios/{usuario_id}", response_model=None, tags=["Usuário"])
        async def get_usuario(usuario_id: int, usuarios_service: UsuariosService = Depends(get_usuarios_service), jwt_with_role: dict = Depends(role_required(["USUARIO", "ADMIN"]))):
            if "roles" in jwt_with_role:
                usuario = await usuarios_service.get_usuarios_by_id(usuario_id)
                return usuario
            else:
                raise HTTPException(status_code=403, detail="Acesso negado: Roles insuficientes")
