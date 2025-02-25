from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from core.configs import settings

class LinkedinModel(settings.DBBaseModel):
    __tablename__ ="tb_linkedins"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    email: str = Column(String(100))
    password: str = Column(String(100))
    # linguagem favorita da sua rede
    mrl_favorita: str = Column(String(100))
    # quantidade de pessoas da sua rede essa linguagem
    q_mrl_favorita: int = Column(Integer)
    # Framework favorito da sua rede
    mrf_favorito: str = Column(String(100))
    # quantidade de pessoas da sua rede que usam esse framework
    q_mrf_favorito: int = Column(Integer)
    
    q_perfis_analisados: int = Column(Integer)
    
    usuario = relationship("UsuariosModel", back_populates="linkedin", uselist=False)
    
    class Config:
        orm_mode = True