import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.nfce import Nfce
from app.models.nfce_item import NfceItem
from app.models.nfe import Nfe
from app.models.nfe_item import NfeItem
from app.schemas.faturamento_ultimos_doze_meses import AnnualTaxBillingResumo
from app.db.session import SessionLocal



def faturamento_ultimos_doze_meses_nfce(db: Session) -> AnnualTaxBillingResumo:
    hoje = datetime.date.today()
    inicio = (hoje.replace(day=1) - datetime.timedelta(days=365)).replace(day=1)
    fim = (hoje.replace(day=1) - datetime.timedelta(days=1))

    base_quantidade = NfceItem.qCOM - NfceItem.qtdcancelamento
    valor_unitario = NfceItem.vProd / NfceItem.qCOM
    desconto_unitario = NfceItem.vDesc / NfceItem.qCOM

    valor_calc = (base_quantidade * valor_unitario) - (base_quantidade * desconto_unitario)

    resultado = (
        db.query(
            func.sum(
                case((NfceItem.CST == 500, valor_calc), else_=0)
            ).label("substituido"),
            func.sum(
                case((NfceItem.CST != 500, valor_calc), else_=0)
            ).label("nao_substituido"),
        )
        .join(Nfce, NfceItem.cNfe == Nfce.ide_codigo)
        .filter(Nfce.ide_dhemi.between(inicio, fim))
        .one()
    )

    return AnnualTaxBillingResumo(
        substituido=resultado.substituido or 0,
        nao_substituido=resultado.nao_substituido or 0
    )

def faturamento_ultimos_doze_meses_nfe(db: Session) -> AnnualTaxBillingResumo:
    hoje = datetime.date.today()
    inicio = (hoje.replace(day=1) - datetime.timedelta(days=365)).replace(day=1)
    fim = (hoje.replace(day=1) - datetime.timedelta(days=1))

    base_quantidade = NfeItem.qCOM - NfeItem.qtdcancelamento
    valor_unitario = NfeItem.vProd / NfeItem.qCOM
    desconto_unitario = NfeItem.vDesc / NfeItem.qCOM

    valor_calc = (base_quantidade * valor_unitario) - (base_quantidade * desconto_unitario)

    resultado = (
        db.query(
            func.sum(
                case((NfeItem.CST == 500, valor_calc), else_=0)
            ).label("substituido"),
            func.sum(
                case((NfeItem.CST != 500, valor_calc), else_=0)
            ).label("nao_substituido"),
        )
        .join(Nfe, NfeItem.cNfe == Nfe.ide_codigo)
        .filter(Nfe.ide_dhemi.between(inicio, fim))
        .one()
    )

    return AnnualTaxBillingResumo(
        substituido=resultado.substituido or 0,
        nao_substituido=resultado.nao_substituido or 0
    )


def faturamento() -> AnnualTaxBillingResumo:
    db_local = SessionLocal()

    try:
        nfce = faturamento_ultimos_doze_meses_nfce(db=db_local)
        nfe = faturamento_ultimos_doze_meses_nfe(db=db_local)

        return AnnualTaxBillingResumo(
            substituido=nfce.substituido + nfe.substituido or 0,
            nao_substituido=nfce.nao_substituido + nfe.nao_substituido or 0
        )
    finally:
        db_local.close()



# Teste isolado
if __name__ == "__main__":
    print(faturamento())
