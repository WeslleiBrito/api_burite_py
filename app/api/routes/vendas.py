from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.business.services.venda_item_service import Venda
from app.schemas.venda_item import VendaItemResumo
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/produto/{id}", response_model=List[VendaItemResumo])
def resumo_vendas(produto_id: int = Path(..., alias="id",gt=0,title="ID do Produto",
                    description="Identificador do produto a ser consultado")):
    venda = Venda()
    return venda.venda_produto_id_anual_mes_por_mes(produto_id)



