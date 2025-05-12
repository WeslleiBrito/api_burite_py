from sqlalchemy import Column, Integer, Float, ForeignKey
from app.db.base import Base

class NfceItem(Base):
    __tablename__ = "nfce_item"

    id = Column(Integer, primary_key=True, index=True)
    cNfe = Column(Integer, ForeignKey("nfce.ide_codigo"))
    CST = Column(Integer)
    qCOM = Column(Float)
    qtdcancelamento = Column(Float)
    vProd = Column(Float)
    vDesc = Column(Float)
