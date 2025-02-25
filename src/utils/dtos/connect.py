from pydantic import BaseModel

# Modelo de entrada (o que o cliente envia)
class ConnectIn(BaseModel):
    mode_view:bool
    usuario_id:int


# Modelo de saída (o que a API envia de volta)
class ConnectOut(BaseModel):
    total_connections: int 
    message_connections:str
