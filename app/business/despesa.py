from sqlalchemy import func, and_
from datetime import date
from app.business.tools.consultar_despesa import ConsultaDespesa
from app.business.tools.calculo_simples_nacional import GuiaSimplesNacionalAnexo1
import calendar
from app.business.tools.gerar_data import gerar_data
from app.models.pagar_rateio import PagarRateio
from app.models.tipo_conta import TipoConta
from app.db.session import SessionLocal



class Despesas:
    def __init__(self, data_inicio: date | None = None, data_fim: date | None = None):

        self._data_i, self._data_f = gerar_data(data_inicio, data_fim).values()
        self._primeiro_dia = self._data_i.replace(day=1)
        self._ultimo_dia = self._data_f.replace(day=calendar.monthrange(self._data_f.year, self._data_f.month)[1])
        self._db = SessionLocal()
        self.despesas_fixas = 0.0
        self.despesas_variaveis = 0.0
        self._calcular()

    def _calcular(self):
        resultados = (
            self._db.query(
                func.sum(PagarRateio.rateio_vlrrateio),
                TipoConta.conta_fixa
            )
            .join(TipoConta, PagarRateio.rateio_tipoconta == TipoConta.tipocont_cod)
            .filter(
                and_(
                    PagarRateio.rateio_dtvencimento >= self._primeiro_dia,
                    PagarRateio.rateio_dtvencimento <= self._ultimo_dia,
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


        verifica_imposto_simples = ConsultaDespesa(data_base=self._ultimo_dia, codigo_despesa=88).despesa_existe()

        if not verifica_imposto_simples:
            i = GuiaSimplesNacionalAnexo1(data_base=self._primeiro_dia).calcular().total_guia
            self.despesas_variaveis += i


if __name__ == "__main__":
    despesa = Despesas(date(2025, 1, 12), date(2025, 4, 10))

    print(despesa.despesas_variaveis, despesa.despesas_fixas)