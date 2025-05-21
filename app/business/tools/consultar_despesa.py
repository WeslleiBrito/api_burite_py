from app.db.session import SessionLocal
from typing import Optional
from sqlalchemy import extract, func
from app.models.pagar_rateio import PagarRateio
from datetime import date


class ConsultaDespesa:
    def __init__(self, data_base: Optional[date] = None, codigo_despesa: int = 88):
        self.db = SessionLocal()
        self.data_base = data_base or date.today()
        self.codigo = codigo_despesa

    def _consultar_guia_real(self) -> Optional[float]:

        ano = self.data_base.year
        mes = self.data_base.month

        resultado = (
            self.db.query(func.sum(PagarRateio.rateio_vlrrateio))
            .filter(
                PagarRateio.rateio_tipoconta == self.codigo,
                extract("year", PagarRateio.rateio_dtvencimento) == ano,
                extract("month", PagarRateio.rateio_dtvencimento) == mes,
            )
            .scalar()
        )
        return resultado if resultado else None

    def get_despesa(self) -> Optional[float]:
        return self._consultar_guia_real()

    def despesa_existe(self) -> bool:
        return True if self._consultar_guia_real() else False