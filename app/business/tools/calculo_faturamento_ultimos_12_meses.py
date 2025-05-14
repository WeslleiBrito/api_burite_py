import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.nfce import Nfce
from app.models.nfce_item import NfceItem
from app.models.nfe import Nfe
from app.models.nfe_item import NfeItem
from app.schemas.faturamento_ultimos_doze_meses import AnnualTaxBillingResumo
from app.db.session import SessionLocal


def calcular_intervalo(data_b: datetime.date) -> tuple[datetime.date, datetime.date]:
    """Calcula o intervalo de 12 meses com base na data fornecida."""
    inicio = (data_b.replace(day=1) - datetime.timedelta(days=365)).replace(day=1)
    fim = (data_b.replace(day=1) - datetime.timedelta(days=1))
    return inicio, fim


def faturamento_ultimos_doze_meses_nfce(db: Session, data_b: Optional[datetime.date] = None) -> AnnualTaxBillingResumo:
    data_b = data_b or datetime.date.today()
    inicio, fim = calcular_intervalo(data_b)

    base_quantidade = NfceItem.qCOM - NfceItem.qtdcancelamento
    valor_unitario = NfceItem.vProd / NfceItem.qCOM
    desconto_unitario = NfceItem.vDesc / NfceItem.qCOM
    valor_calc = (base_quantidade * valor_unitario) - (base_quantidade * desconto_unitario)

    resultado = (
        db.query(
            func.sum(case((500 == NfceItem.CST, valor_calc), else_=0)).label("substituido"),
            func.sum(case((500 != NfceItem.CST, valor_calc), else_=0)).label("nao_substituido"),
        )
        .join(Nfce, NfceItem.cNfe == Nfce.ide_codigo)
        .filter(Nfce.ide_dhemi.between(inicio, fim))
        .one()
    )

    return AnnualTaxBillingResumo(
        substituido=resultado.substituido or 0,
        nao_substituido=resultado.nao_substituido or 0
    )


def faturamento_ultimos_doze_meses_nfe(db: Session, data_b: Optional[datetime.date] = None) -> AnnualTaxBillingResumo:
    data_b = data_b or datetime.date.today()
    inicio, fim = calcular_intervalo(data_b)

    base_quantidade = NfeItem.qCOM - NfeItem.qtdcancelamento
    valor_unitario = NfeItem.vProd / NfeItem.qCOM
    desconto_unitario = NfeItem.vDesc / NfeItem.qCOM
    valor_calc = (base_quantidade * valor_unitario) - (base_quantidade * desconto_unitario)

    resultado = (
        db.query(
            func.sum(case((500 == NfeItem.CST, valor_calc), else_=0)).label("substituido"),
            func.sum(case((500 != NfeItem.CST, valor_calc), else_=0)).label("nao_substituido"),
        )
        .join(Nfe, Nfe.ide_codigo == NfeItem.cNfe)
        .filter(Nfe.ide_dhemi.between(inicio, fim))
        .one()
    )

    return AnnualTaxBillingResumo(
        substituido=resultado.substituido or 0,
        nao_substituido=resultado.nao_substituido or 0
    )


def faturamento(data_b: Optional[datetime.date] = None) -> AnnualTaxBillingResumo:
    db_local = SessionLocal()

    try:
        nfce = faturamento_ultimos_doze_meses_nfce(db=db_local, data_b=data_b)
        nfe = faturamento_ultimos_doze_meses_nfe(db=db_local, data_b=data_b)

        return AnnualTaxBillingResumo(
            substituido=nfce.substituido + nfe.substituido or 0,
            nao_substituido=nfce.nao_substituido + nfe.nao_substituido or 0
        )
    except Exception as erro:
        print("Erro ao calcular faturamento:", erro)
    finally:
        db_local.close()

    return AnnualTaxBillingResumo(nao_substituido=0, substituido=0)


# Teste isolado com data base customizada
if __name__ == "__main__":
    data_base = datetime.date(2024, 12, 1)
    print(faturamento(data_base))
