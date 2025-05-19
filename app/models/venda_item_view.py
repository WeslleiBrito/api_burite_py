from sqlalchemy import Column, Integer, String, Float, Date, select
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class VendaItemAnalitico(Base):
    __tablename__ = 'venda_item_analitico'  # Nome da view que você pode criar no banco

    codigo = Column(Integer, primary_key=True)
    venda = Column(Integer)
    fun_cod = Column(Integer)
    vendedor = Column(String)
    quantidade = Column(Float)
    descricao = Column(String)
    custo = Column(Float)
    faturamento = Column(Float)
    data_venda = Column(Date)

    def __repr__(self):
        return f"<VendaItemAnalitico(venda={self.venda}, descricao='{self.descricao}', quantidade={self.quantidade})>"
