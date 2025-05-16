from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.venda_item import VendaItem
from app.schemas.venda_item import VendaItemResumo, IVenda
from typing import List
from app.db.session import SessionLocal
import datetime



class Venda:
    def __init__(self):
        self.db: Session = SessionLocal()

    def venda_produto_id_anual_mes_por_mes(self, produto_id: int) -> List[VendaItemResumo]:
        hoje = datetime.date.today()
        doze_meses_atras = hoje - datetime.timedelta(days=365)

        resultados = (
            self.db.query(
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
    venda = Venda()

    for item in venda.venda_produto_id_anual_mes_por_mes(20694):
        print(item)
