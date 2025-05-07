from fastapi import FastAPI
from app.api.routes import vendas

app = FastAPI()
app.include_router(vendas.router, prefix="/vendas", tags=["vendas"])
