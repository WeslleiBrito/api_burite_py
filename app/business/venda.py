from typing import List
from app.business.tools.gerar_data import gerar_data
from app.business.valores_totais import TotalValues
from app.models import Produto
from app.models.venda_item import VendaItem
from app.db.session import SessionLocal
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, func
from datetime import date
import datetime
from app.schemas.venda_item import VendaItemResumo
from app.tipos.resumo_total import RetornoResumoTotal
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

        with SessionLocal() as db:

            resultados: List[VendaItem] = (
                db.query(VendaItem)
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
                lucro_p: float = round(lucro / total if lucro !=0 else 0, 3)

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

    def resumo_total_periodo(self, data_inicio: date | None = None, data_fim: date | None = None) -> RetornoResumoTotal:

        venda_item = self.venda_item_periodo(data_inicio, data_fim)

        totais = {
            "faturamento": 0.00,
            "custo": 0.00,
            "despesa_variavel": 0.00,
            "comissao": 0.00,
            "despesa_fixa": 0.00,
            "lucro": 0.00,
            "lucro_percentual": 0.00
        }

        for item in venda_item:
            totais["faturamento"] += item["total"]
            totais["custo"] += item["custo"]
            totais["comissao"] += item["comissao"]
            totais["despesa_variavel"] += item["despesa_variavel"]
            totais["despesa_fixa"] += item["despesa_fixa"]
            totais["lucro"] += item["lucro"]

        totais["faturamento"] = round(totais["faturamento"], 2)
        totais["custo"] = round(totais["custo"], 2)
        totais["comissao"] = round(totais["comissao"], 2)
        totais["despesa_variavel"] = round(totais["despesa_variavel"], 2)
        totais["despesa_fixa"] = round(totais["despesa_fixa"], 2)
        totais["lucro"] = round(totais["lucro"], 2)
        totais["lucro_percentual"] = round((totais["lucro"] / totais["faturamento"]) if (totais["faturamento"] != 0 and totais["lucro"] != 0) else 0, 2)

        return totais

    def venda_por_vendedor_periodo(self, data_inicio: date | None = None, data_fim: date | None = None) -> List[RetornoVendaVendedor]:

        data_i, data_f = gerar_data(data_inicio, data_fim).values()


        venda_item: List[RetornoVendaItem] = self.venda_item_periodo(data_i, data_f)

        codigos_vendedores = set()
        dados_vendedores: List[RetornoVendaVendedor] = []

        for vendedor in venda_item:
            cod = vendedor["cod_vendedor"]
            if cod not in codigos_vendedores:
                codigos_vendedores.add(cod)
                dados_vendedores.append({
                    "cod_vendedor": cod,
                    "vendedor_descricao": vendedor["nome_vendedor"],
                    "desconto": 0.00,
                    "custo": 0.00,
                    "faturamento": 0.00,
                    "despesa_fixa": 0.00,
                    "despesa_variavel": 0.00,
                    "comissao": 0.00,
                    "lucro": 0.00,
                    "lucro_percentual": 0.00,
                    "quantidade_vendas": 0,
                    "data_venda": (
                        venda_item[0]["data_venda"],
                        venda_item[-1]["data_venda"]
                    )
                })

        venda_inserida = set()

        for item in venda_item:

            for index, vendedor in enumerate(dados_vendedores):

                if item["cod_vendedor"] == vendedor["cod_vendedor"]:
                    dados_vendedores[index]["desconto"] += item["desconto"]
                    dados_vendedores[index]["custo"] += item["custo"]
                    dados_vendedores[index]["faturamento"] += item["total"]
                    dados_vendedores[index]["despesa_fixa"] += item["despesa_fixa"]
                    dados_vendedores[index]["despesa_variavel"] += item["despesa_variavel"]
                    dados_vendedores[index]["comissao"] += item["comissao"]
                    dados_vendedores[index]["lucro"] += item["lucro"]
                    dados_vendedores[index]["quantidade_vendas"] += 1 if item["venda"] not in venda_inserida else 0
                    dados_vendedores[index]["desconto"] += item["desconto"]
                    venda_inserida.add(item["venda"])



        for index, ven in enumerate(dados_vendedores):

            dados_vendedores[index]["desconto"] = round(dados_vendedores[index]["desconto"], 2)
            dados_vendedores[index]["custo"] = round(dados_vendedores[index]["custo"], 2)
            dados_vendedores[index]["faturamento"] = round(dados_vendedores[index]["faturamento"], 2)
            dados_vendedores[index]["despesa_fixa"] = round(dados_vendedores[index]["despesa_fixa"], 2)
            dados_vendedores[index]["despesa_variavel"] = round(dados_vendedores[index]["despesa_variavel"], 2)
            dados_vendedores[index]["comissao"] = round(dados_vendedores[index]["comissao"], 3)
            dados_vendedores[index]["lucro"] = round(dados_vendedores[index]["lucro"], 2)
            dados_vendedores[index]["desconto"] = round(dados_vendedores[index]["desconto"], 2)

            dados_vendedores[index]["lucro_percentual"] = round(
                dados_vendedores[index]["lucro"] / dados_vendedores[index]["faturamento"], 3
            ) if dados_vendedores[index]["lucro"] != 0 else 0.00

        return dados_vendedores

    def venda_por_venda_periodo(self, data_inicio: date | None = None, data_fim: date | None = None) -> List[RetornoVenda]:

        data_i, data_f = gerar_data(data_inicio, data_fim).values()

        venda_item: List[RetornoVendaItem] = self.venda_item_periodo(data_i, data_f)

        codigos_vendas = set()
        dados_vendas: List[RetornoVenda] = []

        for venda in venda_item:
            cod = venda["venda"]
            if cod not in codigos_vendas:
                codigos_vendas.add(cod)
                dados_vendas.append({
                    "venda": cod,
                    "cod_vendedor": venda["cod_vendedor"],
                    "vendedor_descricao": venda["nome_vendedor"],
                    "desconto": 0.00,
                    "custo": 0.00,
                    "faturamento": 0.00,
                    "despesa_fixa": 0.00,
                    "despesa_variavel": 0.00,
                    "comissao": 0.00,
                    "lucro": 0.00,
                    "lucro_percentual": 0.00,
                    "data_venda": venda["data_venda"]
                })

        for item in venda_item:

            for index, nota in enumerate(dados_vendas):

                if item["venda"] == nota["venda"]:
                    dados_vendas[index]["desconto"] += item["desconto"]
                    dados_vendas[index]["custo"] += item["custo"]
                    dados_vendas[index]["faturamento"] += item["total"]
                    dados_vendas[index]["despesa_fixa"] += item["despesa_fixa"]
                    dados_vendas[index]["despesa_variavel"] += item["despesa_variavel"]
                    dados_vendas[index]["comissao"] += item["comissao"]
                    dados_vendas[index]["lucro"] += item["lucro"]
                    dados_vendas[index]["desconto"] += item["desconto"]


        for index, ven in enumerate(dados_vendas):

            dados_vendas[index]["desconto"] = round(dados_vendas[index]["desconto"], 2)
            dados_vendas[index]["custo"] = round(dados_vendas[index]["custo"], 2)
            dados_vendas[index]["faturamento"] = round(dados_vendas[index]["faturamento"], 2)
            dados_vendas[index]["despesa_fixa"] = round(dados_vendas[index]["despesa_fixa"], 2)
            dados_vendas[index]["despesa_variavel"] = round(dados_vendas[index]["despesa_variavel"], 2)
            dados_vendas[index]["comissao"] = round(dados_vendas[index]["comissao"], 3)
            dados_vendas[index]["lucro"] = round(dados_vendas[index]["lucro"], 2)
            dados_vendas[index]["desconto"] = round(dados_vendas[index]["desconto"], 2)

            dados_vendas[index]["lucro_percentual"] = round(
                dados_vendas[index]["lucro"] / dados_vendas[index]["faturamento"], 3
            ) if dados_vendas[index]["lucro"] != 0 else 0.00

        return dados_vendas


    @staticmethod
    def faturamento_por_periodo(data_inicio: date | None = None, data_fim: date | None = None) -> RetornoFaturamento:

        data_i, data_f = gerar_data(data_inicio, data_fim).values()

        vi = VendaItem

        with SessionLocal() as db:
            query = (
                db.query(
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

    @staticmethod
    def venda_produto_id_anual_mes_por_mes(produto_id: int) -> List[VendaItemResumo]:
        hoje = datetime.date.today()
        doze_meses_atras = hoje - datetime.timedelta(days=365)

        with SessionLocal() as db:
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
                    mes=res.mes,
                    total_quantidade=res.total_quantidade,
                    total_vendido=res.total_vendido,
                    custo_total=res.custo_total
                )
                for res in resultados
            ]


if __name__ == "__main__":
    relatorio = Venda()
    r = relatorio.venda_por_venda_periodo()

    for v in r:
        print(v)




