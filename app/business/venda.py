from typing import List
from app.models import Produto, ResumeSubgroupo, Funcionario
from app.models.venda_item import VendaItem
from app.models.venda import Venda as vendaModel
from app.db.session import SessionLocal
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, func
from datetime import date
from app.tipos.retorno_venda import RetornoVenda
from app.tipos.retorno_venda_item import RetornoVendaItem
from app.tipos.retorno_venda_vendedor import RetornoVendaVendedor
from app.tipos.retorno_faturamento import RetornoFaturamento


# noinspection PyTypedDict
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

    def venda_por_vendedor_periodo(self, data_inicio: date | None = None, data_fim: date | None = None) -> List[RetornoVendaVendedor]:

        data_i: date | None = data_inicio
        data_f: date | None = data_fim

        if not data_i and not data_f:
            data_i = date.today()
            data_f = date.today()
        elif not data_i and data_f:
            data_i = date(1970, 1, 1)
        elif data_i and not data_f:
            data_f = date.today()

        db = SessionLocal()

        vi = VendaItem
        p = Produto
        rs = ResumeSubgroupo
        v = vendaModel
        f = Funcionario

        query = (
            self.db.query(
                f.fun_cod.label("cod_vendedor"),
                f.fun_nome.label("vendedor_descricao"),
                func.sum(vi.desconto).label("desconto"),
                func.sum((vi.qtd - vi.qtd_devolvida) * vi.vrcusto_composicao).label("custo"),
                func.sum((vi.total / vi.qtd) * (vi.qtd - vi.qtd_devolvida)).label("faturamento"),
            )
            .join(p, vi.produto == p.prod_cod)
            .join(rs, rs.cod_subgroup == p.prod_subgrupo)
            .join(v, vi.venda == v.vend_cod)
            .join(f, v.vendedor == f.fun_cod)
            .filter(vi.dtvenda.between(data_i, data_f))
            .group_by(f.fun_cod, f.fun_nome)
        )

        resultados = query.all()

        retorno: List[RetornoVendaVendedor] = []

        for row in resultados:
            item: RetornoVendaVendedor = {
                "cod_vendedor": row.cod_vendedor,
                "vendedor_descricao": row.vendedor_descricao,
                "desconto": float(row.desconto or 0),
                "custo": float(row.custo or 0),
                "faturamento": float(row.faturamento or 0),
                "data_venda": (data_i, data_f)
            }
            retorno.append(item)

        return retorno

    def venda_por_venda_periodo(self, data_inicio: date | None = None, data_fim: date | None = None) -> List[RetornoVenda]:

        data_i: date | None = data_inicio
        data_f: date | None = data_fim

        if not data_i and not data_f:
            data_i = date.today()
            data_f = date.today()
        elif not data_i and data_f:
            data_i = date(1970, 1, 1)
        elif data_i and not data_f:
            data_f = date.today()


        vi = VendaItem
        p = Produto
        rs = ResumeSubgroupo
        v = vendaModel
        f = Funcionario

        query = (
            self.db.query(
                v.vend_cod.label("venda"),
                f.fun_cod.label("cod_vendedor"),
                f.fun_nome.label("vendedor_descricao"),
                func.sum((vi.desconto / vi.qtd) * (vi.qtd - vi.qtd_devolvida)).label("desconto"),
                func.sum((vi.qtd - vi.qtd_devolvida) * vi.vrcusto_composicao).label("custo"),
                func.sum((vi.total / vi.qtd) * (vi.qtd - vi.qtd_devolvida)).label("faturamento"),
            )
            .join(p, vi.produto == p.prod_cod)
            .join(rs, rs.cod_subgroup == p.prod_subgrupo)
            .join(v, vi.venda == v.vend_cod)
            .join(f, v.vendedor == f.fun_cod)
            .filter(vi.dtvenda.between(data_i, data_f))
            .group_by(v.vend_cod, f.fun_nome)
        )

        resultados = query.all()

        retorno: List[RetornoVenda] = []

        for row in resultados:
            item: RetornoVenda = {
                "venda": row.venda,
                "cod_vendedor": row.cod_vendedor,
                "vendedor_descricao": row.vendedor_descricao,
                "desconto": float(row.desconto or 0),
                "custo": float(row.custo or 0),
                "faturamento": float(row.faturamento or 0),
                "data_venda": (data_i, data_f)
            }
            retorno.append(item)

        return retorno

    def faturamento_por_periodo(self, data_inicio: date | None = None, data_fim: date | None = None) -> RetornoFaturamento:
        data_i: date | None = data_inicio
        data_f: date | None = data_fim

        if not data_i and not data_f:
            data_i = date.today()
            data_f = date.today()
        elif not data_i and data_f:
            data_i = date(1970, 1, 1)
        elif data_i and not data_f:
            data_f = date.today()

        vi = VendaItem

        query = (
            self.db.query(
                func.sum((vi.desconto / vi.qtd) * (vi.qtd - vi.qtd_devolvida)).label("desconto"),
                func.sum((vi.qtd - vi.qtd_devolvida) * vi.vrcusto_composicao).label("custo"),
                func.sum((vi.total / vi.qtd) * (vi.qtd - vi.qtd_devolvida)).label("faturamento"),
            )
            .filter(vi.dtvenda.between(data_i, data_f))
        )

        resultados = query.all()

        retorno: RetornoFaturamento = {
            "faturamento": resultados[0].faturamento,
            "custo": resultados[0].custo,
            "desconto": resultados[0].desconto,
            "data": (data_i, data_f)
        }

        return retorno


if __name__ == "__main__":
    relatorio = Venda()
    r = relatorio.faturamento_por_periodo()
    print(r)




