from pydantic import BaseModel, EmailStr


# Modelo de entrada (o que o cliente envia)
class UserCreate(BaseModel):
    username: str 
    email: EmailStr
    password:str
    imagem: str


# Modelo de saída (o que a API envia de volta)
class UserOut(BaseModel):
    id: int
    name: str
    password: str
