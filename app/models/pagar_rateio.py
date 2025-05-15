from sqlalchemy import Column, Integer, Float, Date
from app.db.base import Base


class PagarRateio(Base):
    __tablename__ = "pagar_rateio"

    rateio_cod = Column("rateio_cod", Integer, primary_key=True, index=True)
    tipo_conta = Column("rateio_tipoconta", Integer, index=True)
    valor_rateio = Column("rateio_vlrrateio", Float)
    data_vencimento = Column("rateio_dtvencimento", Date)
