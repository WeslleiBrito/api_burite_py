from typing import List
from app.business.tools.gerar_data import gerar_data
from app.business.valores_totais import TotalValues
from app.models import Produto, ResumeSubgroupo, Funcionario
from app.models.venda_item import VendaItem
from app.models.venda import Venda as vendaModel
from app.db.session import SessionLocal
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, func, distinct
from datetime import date
import datetime
from app.schemas.venda_item import VendaItemResumo
from app.tipos.retorno_total_values import RetornoTotalValues
from app.tipos.retorno_venda import RetornoVenda
from app.tipos.retorno_venda_item import RetornoVendaItem
from app.tipos.retorno_venda_vendedor import RetornoVendaVendedor
from app.tipos.retorno_faturamento import RetornoFaturamento


# noinspection PyTypedDict,PyShadowingNames
class Venda:
    def __init__(self):
        self._db = SessionLocal()
        self._total_values: RetornoTotalValues = TotalValues().total_values()


    def venda_item_periodo(self, data_inicio: date | None = None, data_fim: date | None = None) -> List[RetornoVendaItem]:

        data_i, data_f = gerar_data(data_inicio, data_fim).values()

        resultados: List[VendaItem] = (
            self._db.query(VendaItem)
            .options(
                joinedload(VendaItem.produto_rel).joinedload(Produto.subgrupo_rel)
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

            despesa_fixa: float = round(nova_quantidade * venda_item.fixed_unit_expense, 3)
            despesa_variavel: float = round(total * float(self._total_values["porcentagem_despesa_variavel"]), 3)
            comissao: float = round(total * float(self._total_values["comissao"]), 3)

            if (comissao + despesa_variavel  + custo + despesa_fixa) > total:
                comissao = 0.0

            lucro: float = round(total - (custo + despesa_fixa + despesa_variavel + comissao), 3)
            lucro_p: float = round(lucro / total, 3)

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
                "nome_vendedor": nome_vendedor,
                "despesa_fixa": despesa_fixa,
                "despesa_variavel": despesa_variavel,
                "comissao": comissao,
                "lucro": lucro,
                "lucro_percentual": lucro_p
            }

            retorno.append(item_retorno)

        return retorno

    def venda_por_vendedor_periodo(self, data_inicio: date | None = None, data_fim: date | None = None) -> List[RetornoVendaVendedor]:

        data_i, data_f = gerar_data(data_inicio, data_fim).values()

        vi = VendaItem
        p = Produto
        rs = ResumeSubgroupo
        v = vendaModel
        f = Funcionario

        query = (
            self._db.query(
                f.fun_cod.label("cod_vendedor"),
                f.fun_nome.label("vendedor_descricao"),
                func.sum(vi.desconto).label("desconto"),
                func.count(distinct(v.vend_cod)).label("quantidade_vendas"),
                func.sum((vi.qtd - vi.qtd_devolvida) * vi.vrcusto_composicao).label("custo"),
                func.sum((vi.total / vi.qtd) * (vi.qtd - vi.qtd_devolvida)).label("faturamento"),
                func.sum((vi.qtd - vi.qtd_devolvida) * rs.fixed_unit_expense).label("despesa_fixa")
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
            comissao = row.faturamento * float(self._total_values["comissao"])
            despesa_variavel = row.faturamento * float(self._total_values["porcentagem_despesa_variavel"])

            if (comissao + row.custo + despesa_variavel + row.despesa_fixa) > row.faturamento:
                comissao = 0.0

            lucro = row.faturamento - (comissao + row.custo + despesa_variavel + row.despesa_fixa)
            lucro_p = round(lucro / row.faturamento, 3)

            item: RetornoVendaVendedor = {
                "cod_vendedor": row.cod_vendedor,
                "vendedor_descricao": row.vendedor_descricao,
                "desconto": float(row.desconto or 0),
                "custo": float(row.custo or 0),
                "faturamento": float(row.faturamento or 0),
                "despesa_fixa": row.despesa_fixa,
                "despesa_variavel": round(despesa_variavel, 3),
                "comissao": round(comissao, 3),
                "lucro": round(lucro, 3),
                "lucro_percentual": round(lucro_p, 3),
                "quantidade_vendas": row.quantidade_vendas,
                "data_venda": (data_i, data_f)
            }
            retorno.append(item)

        return retorno

    def venda_por_venda_periodo(self, data_inicio: date | None = None, data_fim: date | None = None) -> List[RetornoVenda]:

        data_i, data_f = gerar_data(data_inicio, data_fim).values()


        vi = VendaItem
        p = Produto
        rs = ResumeSubgroupo
        v = vendaModel
        f = Funcionario

        query = (
            self._db.query(
                v.vend_cod.label("venda"),
                f.fun_cod.label("cod_vendedor"),
                f.fun_nome.label("vendedor_descricao"),
                func.sum((vi.desconto / vi.qtd) * (vi.qtd - vi.qtd_devolvida)).label("desconto"),
                func.sum((vi.qtd - vi.qtd_devolvida) * vi.vrcusto_composicao).label("custo"),
                func.sum((vi.total / vi.qtd) * (vi.qtd - vi.qtd_devolvida)).label("faturamento"),
                func.sum((vi.qtd - vi.qtd_devolvida) * rs.fixed_unit_expense).label("despesa_fixa")
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

            comissao = row.faturamento * float(self._total_values["comissao"])
            despesa_variavel = row.faturamento * float(self._total_values["porcentagem_despesa_variavel"])

            if (comissao + row.custo + despesa_variavel + row.despesa_fixa) > row.faturamento:
                comissao = 0.0

            lucro = row.faturamento - (comissao + row.custo + despesa_variavel + row.despesa_fixa)
            lucro_p = round(lucro / row.faturamento, 3)

            item: RetornoVenda = {
                "venda": row.venda,
                "cod_vendedor": row.cod_vendedor,
                "vendedor_descricao": row.vendedor_descricao,
                "desconto": float(row.desconto or 0),
                "custo": float(row.custo or 0),
                "faturamento": float(row.faturamento or 0),
                "despesa_fixa": row.despesa_fixa,
                "despesa_variavel": round(despesa_variavel, 3),
                "comissao": round(comissao, 3),
                "lucro": round(lucro, 3),
                "lucro_percentual": round(lucro_p, 3),
                "data_venda": (data_i, data_f)
            }
            retorno.append(item)

        return retorno

    def faturamento_por_periodo(self, data_inicio: date | None = None, data_fim: date | None = None) -> RetornoFaturamento:

        data_i, data_f = gerar_data(data_inicio, data_fim).values()

        vi = VendaItem

        query = (
            self._db.query(
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

    def venda_produto_id_anual_mes_por_mes(self, produto_id: int) -> List[VendaItemResumo]:
        hoje = datetime.date.today()
        doze_meses_atras = hoje - datetime.timedelta(days=365)

        resultados = (
            self._db.query(
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
                mes=res.mes,
                total_quantidade=res.total_quantidade,
                total_vendido=res.total_vendido,
                custo_total=res.custo_total
            )
            for res in resultados
        ]


if __name__ == "__main__":
    relatorio = Venda()
    r = relatorio.venda_item_periodo()

    for v in r:
        print(v)




