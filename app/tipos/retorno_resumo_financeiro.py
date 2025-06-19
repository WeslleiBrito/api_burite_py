from typing import TypedDict, Dict
from datetime import date


# noinspection PyTypedDict,PyShadowingNames
class RetornoResumoFinanceiro(TypedDict):
    faturamento: float
    custo: float
    desconto: float
    despesa_fixa: float
    despesa_variavel: float
    comissao: float
    lucro_rs: float
    lucro_percentual: float
    periodo: Dict[str, date]
