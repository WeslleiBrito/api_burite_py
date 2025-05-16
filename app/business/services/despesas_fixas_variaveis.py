from sqlalchemy import func, and_
from datetime import date
from app.business.tools.consultar_despesa import ConsultaDespesa
from app.business.tools.calculo_simples_nacional import GuiaSimplesNacionalAnexo1
import calendar
from app.models.pagar_rateio import PagarRateio
from app.models.tipo_conta import TipoConta
from app.db.session import SessionLocal



class Despesas:
    def __init__(self, data_base: date):
        self.db = SessionLocal()
        self.data_base = data_base
        self.despesas_fixas = 0.0
        self.despesas_variaveis = 0.0
        self._calcular()

    def _calcular(self):
        # Define o primeiro e último dia do mês da data_base
        primeiro_dia = self.data_base.replace(day=1)
        ultimo_dia = self.data_base.replace(day=calendar.monthrange(self.data_base.year, self.data_base.month)[1])

        # Query ORM para somar valores agrupando por conta_fixa
        resultados = (
            self.db.query(
                func.sum(PagarRateio.rateio_vlrrateio),
                TipoConta.conta_fixa
            )
            .join(TipoConta, PagarRateio.rateio_tipoconta == TipoConta.tipocont_cod)
            .filter(
                and_(
                    PagarRateio.rateio_dtvencimento >= primeiro_dia,
                    PagarRateio.rateio_dtvencimento <= ultimo_dia,
                    ~PagarRateio.rateio_tipoconta.in_([79, 75])  # exclui essas contas
                )
            )
            .group_by(TipoConta.conta_fixa)
            .all()
        )

        for total, conta_fixa in resultados:
            if conta_fixa == 1:
                self.despesas_fixas = total or 0.0
            else:
                self.despesas_variaveis = total or 0.0


        verifica_imposto_simples = ConsultaDespesa(data_base=self.data_base, codigo_despesa=88).despesa_existe()

        if not verifica_imposto_simples:
            i = GuiaSimplesNacionalAnexo1(data_base=self.data_base).calcular().total_guia
            self.despesas_variaveis += i


if __name__ == "__main__":
    despesa = Despesas(date(2025, 5, 16))

    print(despesa.despesas_variaveis, despesa.despesas_fixas)