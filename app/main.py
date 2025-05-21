from fastapi import FastAPI
from app.api.routes import resume_financeiro_route
from app.api.routes import venda_route

app = FastAPI()
app.include_router(venda_route.router_venda, prefix="/vendas", tags=["vendas"])
app.include_router(resume_financeiro_route.router_resumo, prefix="/resumo-financeiro", tags=["resumo-financeiro"])
