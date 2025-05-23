from app.db.session import SessionLocal
from app.models.total_values import TotalValues as MTotalValues
from app.tipos.retorno_total_values import RetornoTotalValues


class TotalValues:
    def __init__(self):
        self._db = SessionLocal()

    def total_values(self) -> RetornoTotalValues:

        resultado = self._db.query(MTotalValues).first()

        retorno: RetornoTotalValues = {
            "id": resultado.id,
            "faturamento": resultado.invoicing,
            "custo": resultado.cost,
            "desconto": resultado.discount,
            "despesa_fixa": resultado.fixed_expenses,
            "despesa_variavel": resultado.variable_expenses,
            "porcentagem_despesa_variavel": resultado.variable_expense_percentage,
            "lucro_rs": resultado.general_monetary_profit,
            "lucro_percentual": resultado.general_percentage_profit,
            "numero_meses": resultado.number_of_months,
            "comissao": resultado.commission,
            "periodo": {
                "data_criacao": resultado.created_at,
                "data_atualizacao": resultado.updated_at
            }
        }

        return retorno
