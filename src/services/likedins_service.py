from src.models.linkedin import LinkedinModel
from src.models.usuarios import UsuariosModel
from src.repositories.linkedins_repository import LinkedinsRepository
from typing import List, Optional
from fastapi import HTTPException

from src.services.usuarios_service import UsuariosService
from src.utils.dtos.connect import ConnectIn, ConnectOut
from src.utils.dtos.linkedin import LinkedinIn

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import random 

class LinkedinsService:
    def __init__(self,usuarios_service:UsuariosService, linkedins_repository: LinkedinsRepository):
        self.usuarios_service = usuarios_service
        self.linkedins_repository = linkedins_repository

    async def get_all_linkedins(self) -> List[LinkedinModel]:
        return await self.linkedins_repository.get_all()
    
    async def get_usuarios_by_id(self, id: int) -> Optional[LinkedinModel]:
        pessoa = await self.linkedins_repository.get_by_id(id)
        if not pessoa:
            raise HTTPException(status_code=404, detail="Linkedin não encontrada")
        return pessoa

    async def cadastrar_linkedin(self, linkedin_dto: LinkedinIn) -> LinkedinModel:
        if linkedin_dto.mrl_favorita is None:
            linkedin_dto.mrl_favorita = "Valor padrão"
        if linkedin_dto.q_mrl_favorita is None:
            linkedin_dto.q_mrl_favorita = 0
        if linkedin_dto.mrf_favorito is None:
            linkedin_dto.mrf_favorito = "Valor padrão"
        if linkedin_dto.q_mrf_favorito is None:
            linkedin_dto.q_mrf_favorito = 0
        if linkedin_dto.q_perfis_analisados is None:
            linkedin_dto.q_perfis_analisados = 0
        usuario: UsuariosModel = await self.usuarios_service.get_usuarios_by_id(linkedin_dto.usuario_id)
        linkedin_data = linkedin_dto.model_dump()
        linkedin_data.pop('usuario_id', None)
        linkedin: LinkedinModel = LinkedinModel(**linkedin_data)
        linkedin.usuario = usuario 
        
        return await self.linkedins_repository.create(linkedin)
    
    async def delete_linkedin(self, id: int) -> bool:
        return await self.linkedins_repository.delete(id)
    
    async def get_linkedin_by_email(self, email: str) -> Optional[LinkedinModel]:
        pessoa = await self.linkedins_repository.get_by_email(email)
        if not pessoa:
            raise HTTPException(status_code=404, detail="Linkedin não encontrada")
        return pessoa
    
    async def get_connections(self, connect_obj: ConnectIn) -> ConnectOut:
        usuario = await self.usuarios_service.get_usuarios_by_id(connect_obj.usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="usuario não encontrada")
        
        linkedin = await  self.linkedins_repository.get_by_id(usuario.linkedin_id)
        if not linkedin:
            raise HTTPException(status_code=404, detail="Linkedin não encontrada")
        
        EMAIL:str = linkedin.email
        PASSWORD:str = linkedin.password

        service = Service(ChromeDriverManager().install())
        chrome_options = Options()
        if not connect_obj.mode_view:  # Verifica se o modo de visualização está desativado
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=service, options=chrome_options)

        MAX_CONEXOES:int = 50
        conexoes_realizadas:int = 0
        try:
            driver.get("https://www.linkedin.com/login")
            time.sleep(3)

            driver.find_element(By.ID, "username").send_keys(EMAIL)
            driver.find_element(By.ID, "password").send_keys(PASSWORD)
            driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
            time.sleep(5)

            driver.get("https://www.linkedin.com/mynetwork")
            time.sleep(5)

            while conexoes_realizadas < MAX_CONEXOES:
                botoes_conectar = driver.find_elements(By.XPATH, "//button[.//span[contains(text(),'Conectar')]]")
                for botao in botoes_conectar:
                    if conexoes_realizadas >= MAX_CONEXOES:
                        break 

                    try:
                        botao.click()
                        conexoes_realizadas += 1
                        print(f"✅ {conexoes_realizadas} conexões) realizada(s)!")
                        time.sleep(random.uniform(3, 6))

                    except Exception as e:
                        print("⚠️ Erro ao clicar no botão:", e)

                if conexoes_realizadas < MAX_CONEXOES:
                    print("🔄 Atualizando a página para buscar mais conexões...")
                    driver.refresh()
                    time.sleep(5) 
            print("🎉 Meta de conexões atingida!")
        finally:
            driver.quit()  # Fecha o navegador
        
        return ConnectOut(total_connections=conexoes_realizadas, message_connections="Meta de conexões atingida!")