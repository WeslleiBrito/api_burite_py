from typing import TypedDict, Tuple
from datetime import date

class RetornoVendaVendedor(TypedDict):
    cod_vendedor: int | None
    vendedor_descricao: str
    desconto: float
    custo: float
    faturamento: float
    data_venda: date | Tuple[date]