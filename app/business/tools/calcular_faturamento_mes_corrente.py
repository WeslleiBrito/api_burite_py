from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract, and_
from app.db.session import SessionLocal
from app.models.nfce_item import NfceItem
from app.models.nfce import Nfce
from app.models.nfe_item import NfeItem
from app.models.nfe import Nfe
from app.schemas.faturamento_ultimos_doze_meses import AnnualTaxBillingResumo
from typing import Optional
import datetime

def calcular_faturamento_mes_corrente(db: Session, data_base: Optional[datetime.date] = None) -> AnnualTaxBillingResumo:
    data_base = data_base or datetime.date.today()
    ano = data_base.year
    mes = data_base.month

    valor_calculado_nfce = (
            (NfceItem.vProd - NfceItem.vDesc)
    )

    resultado_nfce = (
        db.query(
            func.sum(
                case(
                    (and_(NfceItem.CST == 500, Nfce.mov_estoque > 0), valor_calculado_nfce),
                    else_=0
                )
            ).label("substituido"),
            func.sum(
                case(
                    (and_(NfceItem.CST != 500, Nfce.mov_estoque > 0), valor_calculado_nfce),
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

    valor_calculado_nfe = (
            (NfeItem.vProd - NfeItem.vDesc)
    )

    resultado_nfe = (
        db.query(
            func.sum(
                case(
                    (and_(NfeItem.CST == 500, Nfe.mov_estoque > 0), valor_calculado_nfe),
                    else_=0
                )
            ).label("substituido"),
            func.sum(
                case(
                    (and_(NfeItem.CST != 500, Nfe.mov_estoque > 0), valor_calculado_nfe),
                    else_=0
                )
            ).label("nao_substituido")
        )
        .join(Nfe, NfeItem.cNfe == Nfe.ide_codigo)
        .filter(
            extract("year", Nfe.ide_dhemi) == ano,
            extract("month", Nfe.ide_dhemi) == mes
        )
        .one()
    )

    return AnnualTaxBillingResumo(
        substituido=resultado_nfce.substituido + resultado_nfe.substituido or 0,
        nao_substituido=resultado_nfce.nao_substituido + resultado_nfe.nao_substituido or 0
    )


if __name__ == "__main__":
    db = SessionLocal()
    try:
        # Data de referência: 17/05/2025 -> considera todo o mês de maio/2025
        resultado = calcular_faturamento_mes_corrente(db, datetime.date(2025, 4, 1))
    finally:
        db.close()
