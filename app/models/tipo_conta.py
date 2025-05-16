from sqlalchemy import Column, Integer, String
from app.db.base import Base
from sqlalchemy.orm import relationship


class TipoConta(Base):
    __tablename__ = "tipoconta"

    tipocont_cod = Column(Integer, primary_key=True, index=True)
    conta_fixa = Column(String, index=True)

    pagar_rateios = relationship("PagarRateio", back_populates="tipo_conta_rel")
