import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, func, case, extract, or_
from datetime import datetime

Base = declarative_base()

# Modelo fictício baseado na estrutura presumida
class Nfe(Base):
    __tablename__ = 'nfe'
    ide_codigo = Column(Integer, primary_key=True)
    ide_dhemi = Column(DateTime, nullable=False)

class NfeItem(Base):
    __tablename__ = 'nfe_item'
    id = Column(Integer, primary_key=True)
    cNfe = Column(Integer, ForeignKey('nfe.ide_codigo'))
    CST = Column(Integer)
    cancelado = Column(Integer)
    qCom = Column(Float)
    vProd = Column(Float)
    vDesc = Column(Float)
    qtdcancelamento = Column(Float)

# Função de cálculo
def calcular_totais(session, ano, mes):
    valor_calculado_nfe = (
        ((func.coalesce(NfeItem.qCom, 0) - func.coalesce(NfeItem.qtdcancelamento, 0)) *
         (func.coalesce(NfeItem.vProd, 0) / func.nullif(NfeItem.qCom, 0))) -
        ((func.coalesce(NfeItem.vDesc, 0) / func.nullif(NfeItem.qCom, 0)) *
         (func.coalesce(NfeItem.qCom, 0) - func.coalesce(NfeItem.qtdcancelamento, 0)))
    )

    return (
        session.query(
            func.sum(
                case(
                    (
                        (NfeItem.CST == 500) &
                        ((NfeItem.cancelado == 0) | (NfeItem.cancelado.is_(None))),
                        valor_calculado_nfe
                    ),
                    else_=0
                )
            ).label("substituido"),
            func.sum(
                case(
                    (
                        (NfeItem.CST != 500) &
                        ((NfeItem.cancelado == 0) | (NfeItem.cancelado.is_(None))),
                        valor_calculado_nfe
                    ),
                    else_=0
                )
            ).label("nao_substituido")
        )
        .join(Nfe, NfeItem.cNfe == Nfe.ide_codigo)
        .filter(
            extract("year", Nfe.ide_dhemi) == ano,
            extract("month", Nfe.ide_dhemi) == mes
        )
        .one()
    )


# Teste
def test_calculo_nfe():
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()

    # Data de referência
    data_emissao = datetime(2024, 5, 1)

    # Criação da NFe
    nfe = Nfe(ide_codigo=1, ide_dhemi=data_emissao)
    session.add(nfe)
    session.commit()

    # Itens com CST 500 e não cancelado
    item1 = NfeItem(cNfe=1, CST=500, cancelado=0, qCom=10, vProd=100, vDesc=10, qtdcancelamento=0)  # valor: 90
    # Itens com CST diferente e não cancelado
    item2 = NfeItem(cNfe=1, CST=102, cancelado=0, qCom=5, vProd=50, vDesc=0, qtdcancelamento=0)     # valor: 50
    # Item cancelado (não entra)
    item3 = NfeItem(cNfe=1, CST=500, cancelado=1, qCom=10, vProd=100, vDesc=10, qtdcancelamento=0)  # ignorado

    session.add_all([item1, item2, item3])
    session.commit()

    resultado = calcular_totais(session, 2024, 5)

    assert round(resultado.substituido, 2) == 90.0
    assert round(resultado.nao_substituido, 2) == 50.0
