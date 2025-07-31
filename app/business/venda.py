from typing import List, Tuple

from app.business.tools.calculo_faturamento_ultimos_12_meses import faturamento
from app.business.tools.gerar_data import gerar_data
from app.business.valores_totais import TotalValues
from app.models import Produto, Funcionario
from app.models.venda_item import VendaItem
from app.db.session import SessionLocal
from sqlalchemy import func
from datetime import date
import datetime
from app.schemas import VendaItemResumo
from app.tipos.resumo_total import RetornoResumoTotal
from app.tipos.retorno_total_values import RetornoTotalValues
from app.tipos.retorno_venda import RetornoVenda
from app.tipos.retorno_venda_item import RetornoVendaItem
from app.tipos.retorno_venda_vendedor import RetornoVendaVendedor
from app.tipos.retorno_faturamento import RetornoFaturamento
from app.models.venda import Venda as vendaDb
from typing import Dict
from contextlib import contextmanager

class Nodo:
    def __init__(self, valor: RetornoVendaItem):
        self.valor: RetornoVendaItem = valor
        self.proximo: Nodo | None = None

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# noinspection PyTypedDict,PyShadowingNames
class Venda:
    def __init__(self):
        self._db = SessionLocal()
        self._total_values: RetornoTotalValues = TotalValues().total_values()

    def venda_item_periodo(self, inicio: date, fim: date) -> list[RetornoVendaItem]:
        percentual_vr = float(self._total_values["porcentagem_despesa_variavel"])
        percentual_comissao = float(self._total_values["comissao"])

        with get_db_session() as db:
            resultados: List[Tuple[VendaItem, vendaDb, Produto, Funcionario]] = (
                db.query(VendaItem, vendaDb, Produto, Funcionario)
                .join(vendaDb, VendaItem.venda == vendaDb.vend_cod)
                .join(Produto, VendaItem.produto == Produto.prod_cod)
                .outerjoin(vendaDb.vendedor_rel)
                .filter(vendaDb.data.between(inicio, fim))
                .all()
            )

            total_itens = len(resultados)
            lista_retorno = [None] * total_itens

            for i, (venda_item, venda, produto, funcionario) in enumerate(resultados):
                qtd = venda_item.qtd - venda_item.qtd_devolvida if venda_item.qtd_devolvida > 0 else venda_item.qtd
                custo = venda_item.vrcusto_composicao * qtd
                faturamento = (venda_item.total / venda_item.qtd) * qtd
                despesa_fixa = venda_item.fixed_unit_expense * qtd
                despesa_variavel = faturamento * percentual_vr
                desconto = (venda_item.desconto / venda_item.qtd) * qtd if venda_item.desconto > 0 else 0
                comissao = faturamento * percentual_comissao
                total_custos = custo + despesa_fixa + despesa_variavel + comissao

                if total_custos >= faturamento:
                    total_custos -= comissao
                    comissao = 0

                lucro = faturamento - total_custos
                lucro_p = lucro / faturamento if faturamento != 0 else 0

                lista_retorno[i] = RetornoVendaItem(
                    item_cod=venda_item.item_cod,
                    venda=venda.vend_cod,
                    cod_produto=produto.prod_cod,
                    descricao=produto.prod_descricao,
                    qtd=qtd,
                    qtd_devolvida=venda_item.qtd_devolvida,
                    custo=round(custo, 2),
                    desconto=round(desconto, 2),
                    total=round(faturamento, 2),
                    data_venda=venda.data,
                    cod_vendedor=funcionario.fun_cod if funcionario.fun_cod else None,
                    nome_vendedor=funcionario.fun_nome if funcionario.fun_nome else "",
                    despesa_fixa=round(despesa_fixa, 3),
                    despesa_variavel=round(despesa_variavel, 2),
                    comissao=round(comissao, 3),
                    lucro=round(lucro, 3),
                    lucro_percentual=round(lucro_p, 3),
                )

        return lista_retorno

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
        vendedor_dict: Dict[str, RetornoVendaVendedor] = {}
        venda_inserida = set()

        for item in venda_item:
            cod = item["cod_vendedor"]
            if cod not in vendedor_dict:
                vendedor_dict[cod] = {
                    "cod_vendedor": cod,
                    "vendedor_descricao": item["nome_vendedor"],
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
                }

            vendedor = vendedor_dict[cod]
            vendedor["custo"] += item["custo"]
            vendedor["faturamento"] += item["total"]
            vendedor["desconto"] += item["desconto"]
            vendedor["despesa_fixa"] += item["despesa_fixa"]
            vendedor["despesa_variavel"] += item["despesa_variavel"]
            vendedor["comissao"] += item["comissao"]
            vendedor["lucro"] += item["lucro"]
            vendedor["quantidade_vendas"] += 1 if item["venda"] not in venda_inserida else 0
            venda_inserida.add(item["venda"])


        for key in vendedor_dict.keys():
            vendedor_dict[key]["custo"] = round(vendedor_dict[key]["custo"], 2)
            vendedor_dict[key]["faturamento"] = round(vendedor_dict[key]["faturamento"], 2)
            vendedor_dict[key]["desconto"] = round(vendedor_dict[key]["desconto"], 2)
            vendedor_dict[key]["despesa_fixa"] = round(vendedor_dict[key]["despesa_fixa"], 2)
            vendedor_dict[key]["despesa_variavel"] = round(vendedor_dict[key]["despesa_variavel"], 2)
            vendedor_dict[key]["comissao"] = round(vendedor_dict[key]["comissao"], 3)
            vendedor_dict[key]["lucro"] = round(vendedor_dict[key]["lucro"], 2)
            lucro = vendedor_dict[key]["lucro"]
            faturamento = vendedor_dict[key]["faturamento"]
            if lucro != 0:
                vendedor_dict[key]["lucro_percentual"] = round(lucro / faturamento, 3)


        return list(vendedor_dict.values())

    def venda_por_venda_periodo(self, data_inicio: date | None = None, data_fim: date | None = None) -> List[RetornoVenda]:

        data_i, data_f = gerar_data(data_inicio, data_fim).values()
        venda_items: List[RetornoVendaItem] = self.venda_item_periodo(data_i, data_f)

        vendas_dict = {}

        for item in venda_items:
            cod = item["venda"]
            if cod not in vendas_dict:
                vendas_dict[cod] = {
                    "venda": cod,
                    "cod_vendedor": item["cod_vendedor"],
                    "vendedor_descricao": item["nome_vendedor"],
                    "faturamento": 0.0,
                    "custo": 0.0,
                    "desconto": 0.0,
                    "despesa_fixa": 0.0,
                    "despesa_variavel": 0.0,
                    "comissao": 0.0,
                    "lucro": 0.0,
                    "lucro_percentual": 0.0,
                    "data_venda": item["data_venda"]
                }

            venda = vendas_dict[cod]
            venda["desconto"] += item["desconto"]
            venda["custo"] += item["custo"]
            venda["faturamento"] += item["total"]
            venda["despesa_fixa"] += item["despesa_fixa"]
            venda["despesa_variavel"] += item["despesa_variavel"]
            venda["comissao"] += item["comissao"]
            venda["lucro"] += item["lucro"]

        # Calcula o percentual no final
        for venda in vendas_dict.values():
            faturamento = venda["faturamento"]
            lucro = venda["lucro"]
            venda["lucro_percentual"] = round(lucro / faturamento, 3) if faturamento else 0.0

        return list(vendas_dict.values())


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
    r = relatorio.venda_item_periodo(inicio=date(1970,1,1), fim=date.today())

    print(r)



