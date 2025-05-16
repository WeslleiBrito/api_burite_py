from datetime import date
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from app.business.tools.calcular_faturamento_mes_corrente import calcular_faturamento_mes_corrente
from app.business.tools.calculo_faturamento_ultimos_12_meses import faturamento as faturamento_12_meses
from app.db.session import SessionLocal
from app.models.pagar_rateio import PagarRateio


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


faixas_anexo_1 = [
    {
        "limite_superior": 180000.0,
        "aliquota_nominal": 0.04,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.6875, "CSLL": 0.0, "ICMS": 0.3125, "IRPJ": 0.0, "Cofins": 0.0, "PIS": 0.0},
    },
    {
        "limite_superior": 360000.0,
        "aliquota_nominal": 0.0547,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.5027, "CSLL": 0.0, "ICMS": 0.3399, "IRPJ": 0.0, "Cofins": 0.1572, "PIS": 0.0},
    },
    {
        "limite_superior": 540000.0,
        "aliquota_nominal": 0.0684,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.4023, "CSLL": 0.0453, "ICMS": 0.3406, "IRPJ": 0.0395, "Cofins": 0.1389, "PIS": 0.0336},
    },
    {
        "limite_superior": 720000.0,
        "aliquota_nominal": 0.0754,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3965, "CSLL": 0.0464, "ICMS": 0.3395, "IRPJ": 0.0464, "Cofins": 0.1379, "PIS": 0.0331},
    },
    {
        "limite_superior": 900000.0,
        "aliquota_nominal": 0.076,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3974, "CSLL": 0.0461, "ICMS": 0.3395, "IRPJ": 0.0461, "Cofins": 0.1382, "PIS": 0.0329},
    },
    {
        "limite_superior": 1080000.0,
        "aliquota_nominal": 0.0828,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3966, "CSLL": 0.0459, "ICMS": 0.3401, "IRPJ": 0.0459, "Cofins": 0.1389, "PIS": 0.0326},
    },
    {
        "limite_superior": 1260000.0,
        "aliquota_nominal": 0.0836,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3946, "CSLL": 0.0467, "ICMS": 0.3397, "IRPJ": 0.0467, "Cofins": 0.1388, "PIS": 0.0335},
    },
    {
        "limite_superior": 1440000.0,
        "aliquota_nominal": 0.0845,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3964, "CSLL": 0.0462, "ICMS": 0.3396, "IRPJ": 0.0462, "Cofins": 0.1385, "PIS": 0.0331},
    },
    {
        "limite_superior": 1620000.0,
        "aliquota_nominal": 0.0903,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3958, "CSLL": 0.0465, "ICMS": 0.3402, "IRPJ": 0.0465, "Cofins": 0.1385, "PIS": 0.0332},
    },
    {
        "limite_superior": 1800000.0,
        "aliquota_nominal": 0.0912,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3947, "CSLL": 0.0471, "ICMS": 0.3399, "IRPJ": 0.0471, "Cofins": 0.1382, "PIS": 0.0329},
    },
    {
        "limite_superior": 1980000.0,
        "aliquota_nominal": 0.0995,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.395, "CSLL": 0.0462, "ICMS": 0.3392, "IRPJ": 0.0462, "Cofins": 0.1387, "PIS": 0.0332},
    },
    {
        "limite_superior": 2160000.0,
        "aliquota_nominal": 0.1004,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3972, "CSLL": 0.0459, "ICMS": 0.3397, "IRPJ": 0.0459, "Cofins": 0.1384, "PIS": 0.0329},
    },
    {
        "limite_superior": 2340000.0,
        "aliquota_nominal": 0.1013,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3960, "CSLL": 0.0464, "ICMS": 0.3405, "IRPJ": 0.0464, "Cofins": 0.1382, "PIS": 0.0326},
    },
    {
        "limite_superior": 2520000.0,
        "aliquota_nominal": 0.1023,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3960, "CSLL": 0.0459, "ICMS": 0.3402, "IRPJ": 0.0459, "Cofins": 0.1389, "PIS": 0.0332},
    },
    {
        "limite_superior": 2700000.0,
        "aliquota_nominal": 0.1032,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3953, "CSLL": 0.0465, "ICMS": 0.3402, "IRPJ": 0.0465, "Cofins": 0.1385, "PIS": 0.0329},
    },
    {
        "limite_superior": 2880000.0,
        "aliquota_nominal": 0.1123,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3953, "CSLL": 0.0463, "ICMS": 0.3402, "IRPJ": 0.0463, "Cofins": 0.1389, "PIS": 0.0329},
    },
    {
        "limite_superior": 3060000.0,
        "aliquota_nominal": 0.1132,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3966, "CSLL": 0.0459, "ICMS": 0.3402, "IRPJ": 0.0459, "Cofins": 0.1387, "PIS": 0.0327},
    },
    {
        "limite_superior": 3240000.0,
        "aliquota_nominal": 0.1142,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3955, "CSLL": 0.0464, "ICMS": 0.3400, "IRPJ": 0.0464, "Cofins": 0.1382, "PIS": 0.0332},
    },
    {
        "limite_superior": 3420000.0,
        "aliquota_nominal": 0.1151,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3960, "CSLL": 0.0460, "ICMS": 0.3393, "IRPJ": 0.0460, "Cofins": 0.1390, "PIS": 0.0330},
    },
    {
        "limite_superior": 3600000.0,
        "aliquota_nominal": 0.1161,
        "desconto": 0.0,
        "partilhas": {"CPP": 0.3960, "CSLL": 0.0465, "ICMS": 0.3401, "IRPJ": 0.0465, "Cofins": 0.1377, "PIS": 0.0327},
    },
]


class GuiaSimplesNacionalAnexo1:
    def __init__(self, data_base: Optional[date] = None):
        self.data_base = data_base or date.today()
        self.faturamento_12_meses = 0.0
        self.faturamento_mes_substituido = 0.0
        self.faturamento_mes_nao_substituido = 0.0

        db = SessionLocal()
        try:
            resumo_12_meses = faturamento_12_meses(data_b=self.data_base)
            resumo_mes = calcular_faturamento_mes_corrente(db=db, data_base=self.data_base)

            self.faturamento_12_meses = resumo_12_meses.substituido + resumo_12_meses.nao_substituido
            self.faturamento_mes_substituido = resumo_mes.substituido
            self.faturamento_mes_nao_substituido = resumo_mes.nao_substituido

            self.valor_real_guia = self._consultar_guia_real(db=db)
        finally:
            db.close()

    def _consultar_guia_real(self, db: Session) -> Optional[float]:
        ano = self.data_base.year
        mes = self.data_base.month

        resultado = (
            db.query(func.sum(PagarRateio.rateio_vlrrateio))
            .filter(
                PagarRateio.rateio_tipoconta == 88,
                extract("year", PagarRateio.rateio_dtvencimento) == ano,
                extract("month", PagarRateio.rateio_dtvencimento) == mes,
            )
            .scalar()
        )
        return resultado if resultado else None

    def calcular(self) -> SimplesNacionalGuia:
        total_mes = self.faturamento_mes_substituido + self.faturamento_mes_nao_substituido

        faixa = next(
            (f for f in faixas_anexo_1 if self.faturamento_12_meses <= f["limite_superior"]),
            faixas_anexo_1[-1],
        )

        aliquota_efetiva = (
            (self.faturamento_12_meses * faixa["aliquota_nominal"]) - faixa["desconto"]
        ) / self.faturamento_12_meses

        # Usa valor real da contabilidade se existir
        if self.valor_real_guia:
            resultado = {
                imposto: round(self.valor_real_guia * percentual, 2)
                for imposto, percentual in faixa["partilhas"].items()
            }
            resultado["total_guia"] = round(self.valor_real_guia, 2)
            resultado["aliquota_efetiva"] = round(
                self.valor_real_guia / total_mes * 100 if total_mes else 0, 4
            )
        else:
            resultado = {}
            for imposto, percentual in faixa["partilhas"].items():
                base = (
                    self.faturamento_mes_nao_substituido
                    if imposto == "ICMS"
                    else total_mes
                )
                resultado[imposto] = round(base * aliquota_efetiva * percentual, 2)

            resultado["total_guia"] = round(sum(resultado.values()), 2)
            resultado["aliquota_efetiva"] = round(aliquota_efetiva * 100, 4)

        return SimplesNacionalGuia(
            faturamento_12_meses=self.faturamento_12_meses,
            faturamento_mes_substituido=self.faturamento_mes_substituido,
            faturamento_mes_nao_substituido=self.faturamento_mes_nao_substituido,
            aliquota_efetiva=resultado["aliquota_efetiva"],
            irpj=resultado["IRPJ"],
            csll=resultado["CSLL"],
            cofins=resultado["Cofins"],
            pis=resultado["PIS"],
            cpp=resultado["CPP"],
            icms=resultado["ICMS"],
            total_guia=resultado["total_guia"],
        )


if __name__ == "__main__":
    guia = GuiaSimplesNacionalAnexo1().calcular()
    print(guia.model_dump())
