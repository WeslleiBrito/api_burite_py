from typing import TypedDict, Tuple
from datetime import date

class RetornoVenda(TypedDict):
    venda: int
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
    data_venda: date | Tuple[date]

