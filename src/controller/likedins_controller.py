from fastapi import APIRouter, Depends
from src.controller.container_ioc import get_linkedins_service, role_required
from src.services.likedins_service import LinkedinsService
from src.utils.dtos.linkedin import LinkedinIn, LinkedinOut
from src.utils.dtos.connect import ConnectOut, ConnectIn, DataOut
from fastapi import HTTPException

class LinkedinsController:
    def __init__(self):
        self.router = APIRouter()

        @self.router.post("/linkedins", response_model=LinkedinOut, tags=["Linkedin"])
        async def cadastrar_linkedin(linkedin: LinkedinIn, linkedins_service: LinkedinsService = Depends(get_linkedins_service), jwt_with_role: dict = Depends(role_required(["USUARIO", "ADMIN"]))):
            if "roles" in jwt_with_role:
                linkedin = await linkedins_service.cadastrar_linkedin(linkedin)
                return linkedin
            else:
                raise HTTPException(status_code=403, detail="Acesso negado: Roles insuficientes")
            
        @self.router.get("/linkedins/usuarios/{email}", response_model=LinkedinOut, tags=["Linkedin"])
        async def get_linkedin_usuario_by_id(email: str, linkedins_service: LinkedinsService = Depends(get_linkedins_service), jwt_with_role: dict = Depends(role_required(["USUARIO", "ADMIN"]))):
            if "roles" in jwt_with_role:
                linkedin = await linkedins_service.get_linkedin_by_email(email)
                return linkedin
            else:
                raise HTTPException(status_code=403, detail="Acesso negado: Roles insuficientes")

        @self.router.post("/automatize/connections", response_model=ConnectOut, tags=["Linkedin"])
        async def create_new_conection_linkedin(connect_obj: ConnectIn, linkedins_service: LinkedinsService = Depends(get_linkedins_service), jwt_with_role: dict = Depends(role_required(["USUARIO", "ADMIN"])) ):
            if "roles" in jwt_with_role:
                data: ConnectOut = await linkedins_service.get_connections(connect_obj)
                return data
            else:
                raise HTTPException(status_code=403, detail="Acesso negado: Roles insuficientes")

        @self.router.post("/automatize/analytic", response_model=DataOut, tags=["Linkedin"])
        async def create_new_conection_linkedin(connect_obj: ConnectIn,linkedins_service: LinkedinsService = Depends(get_linkedins_service), jwt_with_role: dict = Depends(role_required(["USUARIO", "ADMIN"]))):
            if "roles" in jwt_with_role:
                data: DataOut = await linkedins_service.get_data_rede(connect_obj)
                return data
            else:
                raise HTTPException(status_code=403, detail="Acesso negado: Roles insuficientes")
        
