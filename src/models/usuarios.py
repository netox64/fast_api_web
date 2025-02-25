from sqlalchemy import ARRAY, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from core.configs import settings

class UsuariosModel(settings.DBBaseModel):
    __tablename__ = "tb_usuarios"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(100))
    email: str = Column(String(100))
    password: str = Column(String(100))
    imagem: str = Column(String(100))
    roles: list[str] = Column(ARRAY(String))
    linkedin_id = Column(Integer, ForeignKey("tb_linkedins.id"), unique=True)
    
    linkedin = relationship("LinkedinModel", back_populates="usuario", uselist=False)
    
    def get_roles(self):
        return self.roles.split(",") if self.roles else []

    def set_roles(self, roles: list[str]):
        self.roles = ",".join(roles)
        
    class Config:
        orm_mode = True
    
