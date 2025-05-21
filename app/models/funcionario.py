from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Funcionario(Base):
    __tablename__ = "funcionario"

    fun_cod = Column(Integer, primary_key=True)
    fun_nome = Column(String(255))

    vendas = relationship("Venda", back_populates="vendedor_rel")
