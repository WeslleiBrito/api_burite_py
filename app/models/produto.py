from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Produto(Base):
    __tablename__ = "produto"

    prod_cod = Column(Integer, primary_key=True)
    prod_descricao = Column(String(255))
    prod_subgrupo = Column(Integer, ForeignKey("resume_subgroups.cod_subgroup"))

    subgrupo_rel = relationship("ResumeSubgroupo", back_populates="produtos")
    itens = relationship("VendaItem", back_populates="produto_rel")
