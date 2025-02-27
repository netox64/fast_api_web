import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from src.models.usuarios import UsuariosModel
from src.services.usuarios_service import UsuariosService
from src.utils.dtos.user_login import LoginRequest
from fastapi import status
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from decouple import Config
from pathlib import Path


class AuthService:
    config = Config(str(Path(__file__).resolve().parent.parent.parent / ".env"))

    SECRET_KEY = config("SECRET_KEY", default="segredodojwt")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def __init__(self, usuarios_service: UsuariosService):
        self.usuarios_service = usuarios_service
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    # authenticar usuario com jwt
    async def authenticar(self, usuario: LoginRequest):
        usuario_db: UsuariosModel = await self.usuarios_service.get_usuario_by_email(usuario.email)
        if not usuario_db or not self.pwd_context.verify(usuario.password, usuario_db.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha incorretos", headers={"WWW-Authenticate": "Bearer"})

        access_token = self.create_access_token(data = {"id": usuario_db.id, "username": usuario_db.username, "email": usuario_db.email, "imagem": usuario_db.imagem, "roles": usuario_db.roles})
        return access_token
    
    # Função para criar o token JWT
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    # Função para verificar o token JWT
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if not isinstance(payload, dict) or "id" not in payload or "roles" not in payload:
                raise HTTPException(status_code=401, detail="Token inválido")
            return payload
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expirado")
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token inválido")

    # Função para obter o usuário com base no token
    def get_current_user(self, token: str):
        return self.verify_token(token)
