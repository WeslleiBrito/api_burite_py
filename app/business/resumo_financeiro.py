import calendar

from app.business.despesa import Despesas
from app.business.tools.gerar_data import gerar_data
from app.business.venda import Venda
from datetime import date

from app.tipos.retorno_resumo_financeiro import RetornoResumoFinanceiro


class ResumoFinanceiro:
    def __init__(self):
        super().__init__()

    @staticmethod
    def resumo(data_inicio: date | None = None, data_fim: date | None = None) -> RetornoResumoFinanceiro:
        data_i, data_f = gerar_data(data_inicio, data_fim).values()

        primeiro_dia = data_i
        ultimo_dia = data_f

        if data_inicio == None:
            primeiro_dia = data_i.replace(day=1)

        if data_fim == None:
            ultimo_dia = data_f.replace(day=calendar.monthrange(data_f.year, data_f.month)[1])

        fat = Venda()
        faturamento = fat.faturamento_por_periodo(data_inicio=primeiro_dia, data_fim=ultimo_dia)
        despesa = Despesas(data_inicio=primeiro_dia, data_fim=ultimo_dia)

        lucro = round(faturamento["faturamento"] - (faturamento["custo"] + despesa.despesas_fixas + despesa.despesas_fixas), 2)

        return {
            "faturamento": round(faturamento["faturamento"], 2),
            "custo": round(faturamento["custo"], 2),
            "desconto": round(faturamento["desconto"], 2),
            "despesa_fixa": round(despesa.despesas_fixas, 2),
            "despesa_variavel": round(despesa.despesas_variaveis, 2),
            "lucro_rs": round(lucro, 2),
            "lucro_percentual": round(lucro / faturamento["faturamento"], 2),
            "periodo": faturamento["data"]
        }


if __name__ == "__main__":
    resumo_financeiro = ResumoFinanceiro()
    print(resumo_financeiro.resumo(date(2025, 5, 6)))