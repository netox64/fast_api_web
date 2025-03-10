from fastapi import FastAPI
from src.controller import usuarios_controller, likedins_controller
from fastapi.middleware.cors import CORSMiddleware

from src.controller.likedins_controller import LinkedinsController
from src.controller.usuarios_controller import UsuariosController

# Criando a instância do FastAPI
app = FastAPI(
    title="Minha API", description="API de exemplo usando FastAPI", version="1.0.0",
    contact={"name": "Neto Rapariga","email": "clodoaldo.brtp4@gmail.com"},
    license_info={"name": "MIT","url": "https://opensource.org/licenses/MIT"},
    swagger_ui_parameters={"persistAuthorization": True},
)

#configure cors
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Instanciar os controladores e adicionar suas rotas
linkedins = LinkedinsController()
usuarios = UsuariosController()

# Criando endpoint
app.include_router(linkedins.router,prefix="")
app.include_router(usuarios.router,prefix="")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
