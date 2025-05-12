from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.business.services.venda_item_service import listar_vendas_por_mes
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
                    description="Identificador do produto a ser consultado"),
                    db: Session = Depends(get_db)):
    return listar_vendas_por_mes(produto_id, db)


@router.get("/teste", response_model=List[VendaItemResumo])
def rota_teste(db: Session = Depends(get_db)):
    return listar_vendas_por_mes(produto_id=22731, db=db)


