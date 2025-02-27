from src.models.linkedin import LinkedinModel
from src.models.usuarios import UsuariosModel
from src.repositories.linkedins_repository import LinkedinsRepository
from typing import List, Optional,Dict
from fastapi import HTTPException
from collections import Counter
import time
import re
import random 

from src.services.usuarios_service import UsuariosService
from src.utils.dtos.connect import ConnectIn, ConnectOut, DataOut
from src.utils.dtos.linkedin import LinkedinIn

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


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
        if not connect_obj.mode_view:
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
                        time.sleep(random.uniform(3, 6))

                    except Exception as e:
                        print("Erro ao clicar no botão:", e)

                if conexoes_realizadas < MAX_CONEXOES:
                    driver.refresh()
                    time.sleep(5) 
        finally:
            driver.quit()  # Fecha o navegador
        
        return ConnectOut(total_connections=conexoes_realizadas, message_connections="Meta de conexões atingida!")

    async def get_data_rede(self, connect_obj: ConnectIn) -> DataOut:
        usuario = await self.usuarios_service.get_usuarios_by_id(connect_obj.usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="usuario não encontrada")

        linkedin = await  self.linkedins_repository.get_by_id(usuario.linkedin_id)
        if not linkedin:
            raise HTTPException(status_code=404, detail="Linkedin não encontrada")

        EMAIL: str = linkedin.email
        PASSWORD: str = linkedin.password

        service = Service(ChromeDriverManager().install())
        chrome_options = Options()
        if not connect_obj.mode_view:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=service, options=chrome_options)

        MAX_CONEXOES: int = 0
        cards_visitados: int = 0
        lista_de_dicionarios: List[Dict[str, str]] = []
        
        try:
            driver.get("https://www.linkedin.com/login")
            time.sleep(3)

            driver.find_element(By.ID, "username").send_keys(EMAIL)
            driver.find_element(By.ID, "password").send_keys(PASSWORD)
            driver.find_element(By.ID, "password").send_keys(Keys.RETURN)
            time.sleep(5)

            driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
            time.sleep(5)

            try:
                conexoes_text = driver.find_element(By.CSS_SELECTOR, "h1.t-18.t-black.t-normal").text
                quant_conect_text: str = re.sub(r"[^\d.]", "", conexoes_text)
                quant_conect_text = re.sub(r"[^\d]", "", quant_conect_text)
                MAX_CONEXOES = int(quant_conect_text)

            except Exception as e:
                print("Erro ao capturar o número de conexões:", e)

            while cards_visitados < MAX_CONEXOES:

                try:
                    connection_cards = driver.find_elements(By.CLASS_NAME, "mn-connection-card__details")
                    for card in connection_cards:
                        nome = card.find_element(By.CLASS_NAME, "mn-connection-card__name").text
                        cargo = card.find_element(By.CLASS_NAME, "mn-connection-card__occupation").text
                        lista_de_dicionarios.append({"nome": nome, "stack": cargo})

                        cards_visitados += 1
                        if cards_visitados >= MAX_CONEXOES:
                            break 

                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(5)

                    try:
                        exibir_mais_btn = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[span[text()='Exibir mais resultados']]")))
                        exibir_mais_btn.click()
                        time.sleep(5)
                    except Exception as e:
                        print("Botão 'Exibir mais resultados' não encontrado ou erro:", e)

                except Exception as e:
                    print("Erro ao iterar sobre as conexões:", e)
                    break

                if cards_visitados >= MAX_CONEXOES:
                    break

        finally:
            driver.quit()

        stack_counter = Counter()
        for pessoa in lista_de_dicionarios:
            stacks = pessoa["stack"].split(" | ")
            stack_counter.update(stacks)
        stack_mais_comum, frequencia_apr = stack_counter.most_common(1)[0]
        return DataOut(total_connections=MAX_CONEXOES,total_analisados=cards_visitados,perfil_mais_encontrado=stack_mais_comum,frequencia=frequencia_apr,message_porcentagem=f' essa stack corresponde a {round(float((frequencia_apr*100)/cards_visitados),2)} % da sua rede')