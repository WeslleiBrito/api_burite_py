from fastapi import APIRouter, Path
from app.schemas.venda_item import VendaItemResumo
from typing import List
from app.services.venda_service import VendaService

router = APIRouter()

venda_service = VendaService()

@router.get("/produto/{id}", response_model=List[VendaItemResumo])
def resumo_vendas(produto_id: int = Path(..., alias="id",gt=0,title="ID do Produto",
                    description="Identificador do produto a ser consultado")):

    return venda_service.venda_produto_id_anual_mes_por_mes(produto_id)



