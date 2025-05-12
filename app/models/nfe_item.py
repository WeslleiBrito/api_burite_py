from sqlalchemy import Column, Integer, Float, ForeignKey
from app.db.base import Base

class NfeItem(Base):
    __tablename__ = "nfe_item"

    id = Column(Integer, primary_key=True, index=True)
    cNfe = Column(Integer, ForeignKey("nfe.ide_codigo"))
    CST = Column(Integer)
    qCOM = Column(Float)
    qtdcancelamento = Column(Float)
    vProd = Column(Float)
    vDesc = Column(Float)
