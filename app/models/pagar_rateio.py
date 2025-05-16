from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from app.db.base import Base
from sqlalchemy.orm import relationship


class PagarRateio(Base):
    __tablename__ = "pagar_rateio"

    rateio_cod = Column(Integer, primary_key=True, index=True)
    rateio_tipoconta = Column(Integer, ForeignKey("tipoconta.tipocont_cod"), index=True)
    rateio_vlrrateio = Column(Float)
    rateio_dtvencimento = Column(Date)

    tipo_conta_rel = relationship("TipoConta", back_populates="pagar_rateios")

