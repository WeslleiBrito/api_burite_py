from fastapi import APIRouter, Path, Query
from app.schemas.venda_item import VendaItemResumo
from typing import List, Optional
from app.services.venda_service import VendaService
from datetime import date


router_venda = APIRouter()

venda_service = VendaService()


@router_venda.get("/venda-vendedor")
def venda_vendedor(
    data_inicial: Optional[date] = Query(None, title="Data Inicial", description="Data de início do período (yyyy-mm-dd)"),
    data_final: Optional[date] = Query(None, title="Data Final", description="Data de fim do período (yyyy-mm-dd)")
):
    return venda_service.venda_por_vendedor_periodo(data_inicial, data_final)

@router_venda.get("/vendas")
def venda(
    data_inicial: Optional[date] = Query(None, title="Data Inicial", description="Data de início do período (yyyy-mm-dd)"),
    data_final: Optional[date] = Query(None, title="Data Final", description="Data de fim do período (yyyy-mm-dd)")
):
    return venda_service.venda_por_venda_periodo(data_inicial, data_final)

@router_venda.get("/venda-item")
def venda_item(
    data_inicial: Optional[date] = Query(None, title="Data Inicial", description="Data de início do período (yyyy-mm-dd)"),
    data_final: Optional[date] = Query(None, title="Data Final", description="Data de fim do período (yyyy-mm-dd)")
):
    return venda_service.venda_item_periodo(data_inicial, data_final)

@router_venda.get("/faturamento")
def venda_item(
    data_inicial: Optional[date] = Query(None, title="Data Inicial", description="Data de início do período (yyyy-mm-dd)"),
    data_final: Optional[date] = Query(None, title="Data Final", description="Data de fim do período (yyyy-mm-dd)")
):
    return venda_service.faturamento_por_periodo(data_inicial, data_final)

@router_venda.get("/produto/{id}", response_model=List[VendaItemResumo])
def resumo_vendas(produto_id: int = Path(..., alias="id",gt=0,title="ID do Produto",
                    description="Identificador do produto a ser consultado")):

    return venda_service.venda_produto_id_anual_mes_por_mes(produto_id)


@router_venda.get("/resumo-total-venda")
def venda_item(
    data_inicial: Optional[date] = Query(None, title="Data Inicial", description="Data de início do período (yyyy-mm-dd)"),
    data_final: Optional[date] = Query(None, title="Data Final", description="Data de fim do período (yyyy-mm-dd)")
):
    return venda_service.resumo_total_periodo(data_inicial, data_final)
