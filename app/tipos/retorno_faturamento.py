from typing import TypedDict, Tuple
from datetime import date


class RetornoFaturamento(TypedDict):
    faturamento: str
    custo: str
    desconto: str
    data: Tuple[date]