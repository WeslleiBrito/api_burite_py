from typing import List, Tuple
from typing_extensions import TypedDict, Dict
from app.models.venda_item import VendaItem
from app.db.session import SessionLocal
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from datetime import date


class RetornoVenda(TypedDict):
    venda: int
    cod_vendedor: int | None
    vendedor_descricao: str
    desconto: float
    custo: float
    faturamento: float
    data_venda: date | Tuple[date]

class RetornoVendaItem(TypedDict):
    item_cod: int
    venda: int
    cod_produto: int
    descricao: str
    qtd: float
    qtd_devolvida: float
    custo: float
    desconto: float
    total: float
    data_venda: date
    cod_vendedor: int | None
    nome_vendedor: str


class Venda:
    def __init__(self):
        self.db = SessionLocal()

    def venda_item_periodo(self, data_inicio: date | None = None, data_fim: date | None = None) -> List[RetornoVendaItem]:

        data_i: date | None = data_inicio
        data_f: date | None = data_fim

        if not data_i and not data_f:
            data_i = date.today()
            data_f = date.today()
        elif not data_i and data_f:
            data_i = date(1970, 1, 1)
        elif data_i and not data_f:
            data_f = date.today()

        resultados: List[VendaItem] = (
            self.db.query(VendaItem)
            .options(
                joinedload(VendaItem.produto_rel),
                joinedload(VendaItem.vendedor_rel)
            )
            .filter(
                and_(
                    VendaItem.dtvenda >= data_i,
                    VendaItem.dtvenda <= data_f
                )
            )
            .all()
        )

        retorno: List[RetornoVendaItem] = []

        for venda_item in resultados:
            qtd = venda_item.qtd
            qtd_devolvida = venda_item.qtd_devolvida
            nova_quantidade = qtd - qtd_devolvida

            custo = round(qtd * venda_item.vrcusto_composicao, 2)
            total = venda_item.total
            desconto = venda_item.desconto

            if qtd_devolvida > 0 and qtd > 0:
                total = (total / qtd) * nova_quantidade
                custo = round(venda_item.vrcusto_composicao * nova_quantidade, 2)
                desconto = round((desconto / qtd) * nova_quantidade)

            vendedor = venda_item.vendedor_rel[0] if venda_item.vendedor_rel else None
            cod_vendedor = vendedor.fun_cod if vendedor else None
            nome_vendedor = vendedor.fun_nome if vendedor else ""

            item_retorno: RetornoVendaItem = {
                "item_cod": venda_item.item_cod,
                "venda": venda_item.venda,
                "cod_produto": venda_item.produto,
                "descricao": venda_item.produto_rel.prod_descricao if venda_item.produto_rel else "",
                "qtd": qtd,
                "qtd_devolvida": qtd_devolvida,
                "custo": custo,
                "desconto": desconto,
                "total": total,
                "data_venda": venda_item.dtvenda,
                "cod_vendedor": cod_vendedor,
                "nome_vendedor": nome_vendedor
            }

            retorno.append(item_retorno)

        return retorno

    def venda_por_periodo(self, data_inicio: date | None = None, data_fim: date | None = None):

        resultado = self.venda_item_periodo(data_inicio, data_fim)

        vendas: Dict[str, RetornoVenda] = {}

        for item in resultado:

            for i in resultado:
                if i["venda"] == item["venda"]:
                    if not str(item["venda"]) in vendas.keys():
                        venda_o: RetornoVenda = {
                            "venda": item["venda"],
                            "desconto": item["desconto"],
                            "cod_vendedor": item["cod_vendedor"],
                            "vendedor_descricao": item["nome_vendedor"],
                            "data_venda": item["data_venda"],
                            "custo": 0.0,
                            "faturamento": 0.0
                        }

                        vendas[str(item["venda"])] = venda_o

                    vendas[str(item["venda"])]["custo"] += i["custo"]
                    vendas[str(item["venda"])]["faturamento"] += i["total"]

        return vendas

    def venda_por_periodo_vendedor(self, data_inicio: date | None = None, data_fim: date | None = None) -> Dict[str, RetornoVenda]:

        data_i: date | None = data_inicio
        data_f: date | None = data_fim

        if not data_i and not data_f:
            data_i = date.today()
            data_f = date.today()
        elif not data_i and data_f:
            data_i = date(1970, 1, 1)
        elif data_i and not data_f:
            data_f = date.today()

        resultado = self.venda_item_periodo(data_i, data_f)

        vendas: Dict[str, RetornoVenda] = {}

        for item in resultado:

            for i in resultado:
                if i["cod_vendedor"] == item["cod_vendedor"]:
                    if not str(item["cod_vendedor"]) in vendas.keys():
                        venda_o: RetornoVenda = {
                            "venda": item["venda"],
                            "desconto": item["desconto"],
                            "cod_vendedor": item["cod_vendedor"],
                            "vendedor_descricao": item["nome_vendedor"],
                            "data_venda": (data_i, data_f),
                            "custo": 0.0,
                            "faturamento": 0.0
                        }

                        vendas[str(item["cod_vendedor"])] = venda_o

                    vendas[str(item["cod_vendedor"])]["custo"] += i["custo"]
                    vendas[str(item["cod_vendedor"])]["faturamento"] += i["total"]

        return vendas

if __name__ == "__main__":
    relatorio = Venda()
    venda = relatorio.venda_por_periodo()
    vendedor = relatorio.venda_por_periodo_vendedor(date(2025, 5, 13), date(2025, 5, 13))

    print(vendedor)



