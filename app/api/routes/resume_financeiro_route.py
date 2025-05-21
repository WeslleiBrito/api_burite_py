from fastapi import APIRouter, Query
from typing import Optional
from datetime import date

from app.services.resumo_financeiro_service import ResumoFinanceiroService

router_resumo = APIRouter()

resumo_financeiro = ResumoFinanceiroService()

@router_resumo.get("/")
def resumo(
    data_inicial: Optional[date] = Query(None, title="Data Inicial", description="Data de início do período (yyyy-mm-dd)"),
    data_final: Optional[date] = Query(None, title="Data Final", description="Data de fim do período (yyyy-mm-dd)")
):
    return resumo_financeiro.resumo(data_inicial, data_final)