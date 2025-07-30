from typing import List, Tuple
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



class Nodo:
    def __init__(self, valor: RetornoVendaItem):
        self.valor: RetornoVendaItem = valor
        self.proximo: Nodo | None = None

class ListaRetornoVendaItem:
    def __init__(self):
        self.head: Nodo | None = None
        self.tamanho: int = 0

    def add(self, valor: RetornoVendaItem):
        novo = Nodo(valor)
        if not self.head:
            self.head = novo
        else:
            atual = self.head
            while atual.proximo:
                atual = atual.proximo

            atual.proximo = novo
        self.tamanho += 1

    def __iter__(self):
        atual = self.head
        while atual:
            yield atual.valor  # ou: yield atual, se quiser o Nodo inteiro
            atual = atual.proximo

    def __len__(self):
        return self.tamanho

    def __getitem__(self, indice: int):
        if indice < 0 or indice >= self.tamanho:
            raise IndexError("Índice fora do alcance")

        atual = self.head
        for _ in range(indice):
            atual = atual.proximo

        return atual.valor

    def to_list(self) -> list:
        resultado = [None] * self.tamanho
        atual = self.head
        i = 0
        while atual:
            resultado[i] = atual.valor
            atual = atual.proximo
            i += 1
        return resultado


# noinspection PyTypedDict,PyShadowingNames
class Venda:
    def __init__(self):
        self._db = SessionLocal()
        self._total_values: RetornoTotalValues = TotalValues().total_values()

    def venda_item_periodo(self, inicio: date, fim: date) -> list[RetornoVendaItem]:

        percentual_vr = float(self._total_values["porcentagem_despesa_variavel"])
        percentual_comissao = float(self._total_values["comissao"])

        resultados: List[Tuple[VendaItem, vendaDb, Produto, Funcionario]] = (
            self._db.query(VendaItem, vendaDb, Produto, Funcionario)
            .join(vendaDb, VendaItem.venda == vendaDb.vend_cod)
            .join(Produto, VendaItem.produto == Produto.prod_cod)
            .outerjoin(vendaDb.vendedor_rel)  # ou .outerjoin(Funcionario, vendaDb.vendedor == Funcionario.fun_cod)
            .filter(vendaDb.data.between(inicio, fim))
            .all()
        )

        total_itens = len(resultados)
        lista_retorno = [None] * total_itens  # Pré-alocação eficiente
        i = 0

        for venda_item, venda, produto, funcionario in resultados:

            qtd = venda_item.qtd - venda_item.qtd_devolvida if venda_item.qtd_devolvida > 0  else venda_item.qtd
            custo = venda_item.vrcusto_composicao * qtd
            faturamento = (venda_item.total / venda_item.qtd) * qtd
            despesa_fixa = venda_item.fixed_unit_expense * qtd
            despesa_variavel = faturamento * percentual_vr
            desconto =  (venda_item.desconto / venda_item.qtd) * qtd if venda_item.desconto > 0 else 0
            comissao = faturamento * percentual_comissao
            total_custos = custo + despesa_fixa + despesa_variavel + comissao

            if total_custos >= faturamento:
                total_custos = total_custos - comissao
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
                    despesa_variavel=round(despesa_variavel,2),
                    comissao=round(comissao, 3),
                    lucro=round(lucro, 3),
                    lucro_percentual=round(lucro_p, 3),
                )

            i = i + 1

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
        venda_items: List[RetornoVendaItem] = self.venda_item_periodo(data_i, data_f)

        vendas_dict = {}

        for item in venda_items:
            cod = item["venda"]
            if cod not in vendas_dict:
                vendas_dict[cod] = {
                    "venda": cod,
                    "cod_vendedor": item["cod_vendedor"],
                    "vendedor_descricao": item["nome_vendedor"],
                    "desconto": 0.0,
                    "custo": 0.0,
                    "faturamento": 0.0,
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
    r = relatorio.venda_por_venda_periodo(data_fim=date.today())

    for item in r:
        print(item)



