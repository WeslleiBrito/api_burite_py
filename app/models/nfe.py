from sqlalchemy import Column, Integer, Date
from sqlalchemy.orm import relationship
from app.db.base import Base


class Nfe(Base):
    __tablename__ = "nfe"
    ide_codigo: Column[int] = Column(Integer, primary_key=True, index=True)
    ide_dhemi = Column(Date)
    mov_estoque = Column(Integer)

    # Adicione o relationship
    itens = relationship("NfeItem", back_populates="nfe")