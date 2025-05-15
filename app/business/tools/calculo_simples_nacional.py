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
            db.query(func.sum(PagarRateio.valor_rateio))
            .filter(
                PagarRateio.tipo_conta == 88,
                extract("year", PagarRateio.data_vencimento) == ano,
                extract("month", PagarRateio.data_vencimento) == mes,
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
            pis=resultado["Pis"],
            cpp=resultado["CPP"],
            icms=resultado["ICMS"],
            total_guia=resultado["total_guia"],
        )


if __name__ == "__main__":
    guia = GuiaSimplesNacionalAnexo1().calcular()
    print(guia.model_dump())
