from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_vendas():
    return {"mensagem": "Rota de vendas funcionando!"}
