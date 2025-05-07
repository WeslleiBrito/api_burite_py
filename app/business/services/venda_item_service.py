from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.venda_item import VendaItem
from app.schemas.venda_item import VendaItemResumo
from typing import List
import datetime

def listar_vendas_por_mes(produto_id: int, db: Session) -> List[VendaItemResumo]:

    hoje = datetime.date.today()
    doze_meses_atras = hoje - datetime.timedelta(days=365)

    resultados = (
        db.query(
            func.date_format(VendaItem.dtvenda, "%Y-%m").label("mes"),
            func.sum(VendaItem.qtd - VendaItem.qtd_devolvida).label("total_quantidade"),
            func.sum(
                (VendaItem.total / VendaItem.qtd) * (VendaItem.qtd - VendaItem.qtd_devolvida)
            ).label("total_vendido"),
            func.sum(
                VendaItem.vrcusto_composicao * (VendaItem.qtd - VendaItem.qtd_devolvida)
            ).label("custo_total"),
        )
        .filter(
            VendaItem.produto == produto_id,
            VendaItem.dtvenda >= doze_meses_atras
        )
        .group_by(func.date_format(VendaItem.dtvenda, "%Y-%m"))
        .order_by(func.date_format(VendaItem.dtvenda, "%Y-%m"))
        .all()
    )

    return [
        VendaItemResumo(
            mes=r.mes,
            total_quantidade=r.total_quantidade,
            total_vendido=r.total_vendido,
            custo_total=r.custo_total
        )
        for r in resultados
    ]


if __name__ == "__main__":
    from app.db.session import SessionLocal

    db_local = SessionLocal()
    try:
        resultado = listar_vendas_por_mes(produto_id=22731, db=db_local)
        for item in resultado:
            print(item)
    finally:
        db_local.close()
