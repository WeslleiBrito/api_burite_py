from typing import TypedDict, Optional
from datetime import date


class RetornoVendaItem(TypedDict):
    item_cod: int
    venda: Optional[int]
    cod_produto: int
    descricao: str
    qtd: float
    qtd_devolvida: float
    custo: float
    desconto: float
    total: float
    data_venda: date
    cod_vendedor: int | None
    nome_vendedor: str
    despesa_fixa: float
    despesa_variavel: float
    comissao: float
    lucro: float
    lucro_percentual: float