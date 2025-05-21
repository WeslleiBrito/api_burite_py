from typing import TypedDict, Tuple
from datetime import date


class RetornoFaturamento(TypedDict):
    faturamento: float
    custo: float
    desconto: float
    data: Tuple[date]