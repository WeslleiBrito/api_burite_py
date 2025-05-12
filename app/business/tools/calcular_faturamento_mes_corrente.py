from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from app.models.nfce_item import NfceItem
from app.models.nfce import Nfce
import datetime

def calcular_faturamento_mes_corrente(db: Session):
    hoje = datetime.date.today()
    ano_corrente = hoje.year
    mes_corrente = hoje.month

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
            extract("year", Nfce.ide_dhemi) == ano_corrente,
            extract("month", Nfce.ide_dhemi) == mes_corrente
        )
        .one()
    )

    return {
        "substituido": resultado.substituido or 0,
        "nao_substituido": resultado.nao_substituido or 0
    }



if __name__ == "__main__":
    from app.db.session import SessionLocal

    db_local = SessionLocal()
    try:
        resultado = calcular_faturamento_mes_corrente(db=db_local)
        print("Faturamento mês corrente:")
        print("Substituído:", resultado["substituido"])
        print("Não Substituído:", resultado["nao_substituido"])
    finally:
        db_local.close()
