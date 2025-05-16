from pydantic import BaseModel
from datetime import date

class VendaItemResumo(BaseModel):
    mes: str
    total_quantidade: float
    total_vendido: float
    custo_total: float

class IVenda(BaseModel):
    venda: int
    data_venda: date
    cod_vendedor: int
    nome_vendedor: str
    cod_cliente: int
    nome_cliente: str
    cod_produto: int
    nome_produto: str
    quantidade: float
    custo: float
    despesa_fixa: float
    despesa_variavel: float
    desconto: float
    faturamento: float
    cod_subgrupo: int
    nome_subgrupo: str