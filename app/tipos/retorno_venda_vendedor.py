from typing import TypedDict, Tuple
from datetime import date

class RetornoVendaVendedor(TypedDict):
    cod_vendedor: int | None
    vendedor_descricao: str
    desconto: float
    custo: float
    faturamento: float
    despesa_fixa: float
    despesa_variavel: float
    comissao: float
    lucro: float
    lucro_percentual: float
    quantidade_vendas: int
    data_venda: date | Tuple[date]