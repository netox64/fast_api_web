from pydantic import BaseModel, EmailStr
from typing import Optional

# Modelo de entrada (o que o cliente envia)
class LinkedinIn(BaseModel):
    email: EmailStr
    password:str
    mrl_favorita: Optional[str] = None
    q_mrl_favorita: Optional[int] = None
    mrf_favorito: Optional[str] = None
    q_mrf_favorito: Optional[int] = None
    q_perfis_analisados: Optional[int] = None
    usuario_id:int


# Modelo de saída (o que a API envia de volta)
class LinkedinOut(BaseModel):
    id: int 
    email: str 
    password: str 
    mrl_favorita: str 
    q_mrl_favorita: int 
    mrf_favorito: str 
    q_mrf_favorito: int 
    q_perfis_analisados: int 
