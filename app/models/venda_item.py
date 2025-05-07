from sqlalchemy import Column, Integer, Float, Date, String
from app.db.base import Base

class VendaItem(Base):
    __tablename__ = "venda_item"

    id = Column(Integer, primary_key=True, index=True)
    produto = Column(Integer, index=True)
    qtd = Column(Float)
    qtd_devolvida = Column(Float)
    total = Column(Float)
    vrcusto_composicao = Column(Float)
    dtvenda = Column(Date)
