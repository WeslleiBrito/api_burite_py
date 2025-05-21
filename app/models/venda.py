from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Venda(Base):
    __tablename__ = "venda"

    vend_cod = Column(Integer, primary_key=True)  # Integer, como você confirmou
    vendedor = Column(Integer, ForeignKey("funcionario.fun_cod"))
    dtvenda = Column(Date)

    # Relacionamento correto com itens de venda
    itens = relationship("VendaItem", back_populates="venda_rel")

    # Relacionamento com funcionário (vendedor)
    vendedor_rel = relationship("Funcionario", back_populates="vendas")
