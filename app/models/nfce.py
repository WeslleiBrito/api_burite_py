from sqlalchemy import Column, Integer, Date
from app.db.base import Base

class Nfce(Base):
    __tablename__ = "nfce"

    ide_codigo = Column(Integer, primary_key=True, index=True)
    ide_dhemi = Column(Date)
    mov_estoque = Column(Integer)
