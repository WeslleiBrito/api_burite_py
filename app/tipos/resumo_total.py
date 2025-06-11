
from typing import TypedDict

class RetornoResumoTotal(TypedDict):
    faturamento: float
    custo: float
    comissao: float
    despesa_fixa: float
    despesa_variavel: float
    lucro_rs: float
    lucro_percentual: float