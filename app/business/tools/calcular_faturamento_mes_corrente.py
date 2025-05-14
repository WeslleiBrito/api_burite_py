from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract

from app.db.session import SessionLocal
from app.models.nfce_item import NfceItem
from app.models.nfce import Nfce
from app.schemas.faturamento_ultimos_doze_meses import AnnualTaxBillingResumo
from typing import Optional
import datetime

def calcular_faturamento_mes_corrente(db: Session, data_base: Optional[datetime.date] = None) -> AnnualTaxBillingResumo:
    data_base = data_base or datetime.date.today()
    ano = data_base.year
    mes = data_base.month

    valor_calculado = (
        ((NfceItem.qCOM - NfceItem.qtdcancelamento) * (NfceItem.vProd / NfceItem.qCOM)) -
        ((NfceItem.vDesc / NfceItem.qCOM) * (NfceItem.qCOM - NfceItem.qtdcancelamento))
    )

    resultado = (
        db.query(
            func.sum(
                case(
                    (NfceItem.CST == 500, valor_calculado),
                    else_=0
                )
            ).label("substituido"),
            func.sum(
                case(
                    (NfceItem.CST != 500, valor_calculado),
                    else_=0
                )
            ).label("nao_substituido")
        )
        .join(Nfce, NfceItem.cNfe == Nfce.ide_codigo)
        .filter(
            extract("year", Nfce.ide_dhemi) == ano,
            extract("month", Nfce.ide_dhemi) == mes
        )
        .one()
    )

    return AnnualTaxBillingResumo(
        substituido=resultado.substituido or 0,
        nao_substituido=resultado.nao_substituido or 0
    )



if __name__ == "__main__":
    db = SessionLocal()
    try:
        # Data de referência: 17/05/2025 -> considera todo o mês de maio/2025
        resultado = calcular_faturamento_mes_corrente(db, datetime.date(2024, 2, 17))
        print(resultado)
    finally:
        db.close()
