from typing import Dict

from app.business.tools.calcular_faturamento_mes_corrente import calcular_faturamento_mes_corrente
from app.business.tools.calculo_faturamento_ultimos_12_meses import faturamento
from app.db.session import SessionLocal
from pydantic import BaseModel

class SimplesNacionalGuia(BaseModel):
    faturamento_12_meses: float
    faturamento_mes_substituido: float
    faturamento_mes_nao_substituido: float
    aliquota_efetiva: float
    irpj: float
    csll: float
    cofins: float
    pis: float
    cpp: float
    icms: float
    total_guia: float



# Tabela de percentuais de repartição da alíquota efetiva para o Anexo I (Simples Nacional)
faixas_anexo_1 = [
    {
        "limite_superior": 180000.00,
        "aliquota_nominal": 0.04,
        "desconto": 0.0,
        "partilhas": {
            "IRPJ": 0.055,
            "CSLL": 0.035,
            "Cofins": 0.1274,
            "Pis": 0.0276,
            "CPP": 0.415,
            "ICMS": 0.34,
        },
    },
    {
        "limite_superior": 360000.00,
        "aliquota_nominal": 0.073,
        "desconto": 5940.00,
        "partilhas": {
            "IRPJ": 0.055,
            "CSLL": 0.035,
            "Cofins": 0.1274,
            "Pis": 0.0276,
            "CPP": 0.415,
            "ICMS": 0.34,
        },
    },
    {
        "limite_superior": 720000.00,
        "aliquota_nominal": 0.095,
        "desconto": 13860.00,
        "partilhas": {
            "IRPJ": 0.055,
            "CSLL": 0.035,
            "Cofins": 0.1274,
            "Pis": 0.0276,
            "CPP": 0.42,
            "ICMS": 0.335,
        },
    },
    {
        "limite_superior": 1800000.00,
        "aliquota_nominal": 0.107,
        "desconto": 22500.00,
        "partilhas": {
            "IRPJ": 0.055,
            "CSLL": 0.035,
            "Cofins": 0.1274,
            "Pis": 0.0276,
            "CPP": 0.42,
            "ICMS": 0.335,
        },
    },
    {
        "limite_superior": 3600000.00,
        "aliquota_nominal": 0.143,
        "desconto": 87300.00,
        "partilhas": {
            "IRPJ": 0.055,
            "CSLL": 0.035,
            "Cofins": 0.1274,
            "Pis": 0.0276,
            "CPP": 0.42,
            "ICMS": 0.335,
        },
    },
    {
        "limite_superior": 4800000.00,
        "aliquota_nominal": 0.19,
        "desconto": 378000.00,
        "partilhas": {
            "IRPJ": 0.135,
            "CSLL": 0.10,
            "Cofins": 0.2827,
            "Pis": 0.0613,
            "CPP": 0.421,
            "ICMS": 0.0,
        },
    },
]

def calcular_guia_simples_nacional_anexo_1(
    faturamento_12_meses: float,
    faturamento_mes_substituido: float,
    faturamento_mes_nao_substituido: float,
) -> SimplesNacionalGuia:
    """Calcula os tributos do Simples Nacional Anexo I para o mês corrente."""

    total_faturamento_mes = faturamento_mes_substituido + faturamento_mes_nao_substituido

    faixa = next(
        (f for f in faixas_anexo_1 if faturamento_12_meses <= f["limite_superior"]),
        faixas_anexo_1[-1],
    )

    aliquota_efetiva = (
        (faturamento_12_meses * faixa["aliquota_nominal"]) - faixa["desconto"]
    ) / faturamento_12_meses

    resultado = {}
    for imposto, percentual in faixa["partilhas"].items():
        base = (
            faturamento_mes_nao_substituido
            if imposto == "ICMS"
            else total_faturamento_mes
        )
        resultado[imposto] = round(base * aliquota_efetiva * percentual, 2)

    resultado["total_guia"] = round(sum(resultado.values()), 2)
    resultado["aliquota_efetiva"] = round(aliquota_efetiva * 100, 4)

    return SimplesNacionalGuia(
        faturamento_12_meses=faturamento_12_meses,
        faturamento_mes_substituido=faturamento_mes_substituido,
        faturamento_mes_nao_substituido=faturamento_mes_nao_substituido,
        aliquota_efetiva=resultado["aliquota_efetiva"],
        irpj=resultado["IRPJ"],
        csll=resultado["CSLL"],
        cofins=resultado["Cofins"],
        pis=resultado["Pis"],
        cpp=resultado["CPP"],
        icms=resultado["ICMS"],
        total_guia=resultado["total_guia"]
    )


def guia() -> SimplesNacionalGuia:
    db_local = SessionLocal()
    try:
        faturamento_12_meses = faturamento()
        faturamento_mes_corrente = calcular_faturamento_mes_corrente(db=db_local)

        guia = calcular_guia_simples_nacional_anexo_1(
            faturamento_12_meses=faturamento_12_meses.nao_substituido + faturamento_12_meses.substituido,
            faturamento_mes_substituido=faturamento_mes_corrente["substituido"],
            faturamento_mes_nao_substituido=faturamento_mes_corrente["nao_substituido"]
        )

        return guia
    finally:
        db_local.close()

if __name__ == "__main__":
    print(guia())
