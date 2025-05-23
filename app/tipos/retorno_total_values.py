from typing import TypedDict, Dict
from datetime import date


# noinspection PyTypedDict,PyShadowingNames
class RetornoTotalValues(TypedDict):
    id: str
    faturamento: float  # invoicing
    custo: float  # cost
    desconto: float  # discount
    despesa_fixa: float  # fixed_expenses
    despesa_variavel: float  # variable_expenses
    porcentagem_despesa_variavel: float
    lucro_rs: float  # general_monetary_profit
    lucro_percentual: float  # general_percentage_profit
    comissao: float  # commission
    numero_meses: int  # number_of_months
    periodo: Dict[str, date]  # baseado em created_at e updated_at
