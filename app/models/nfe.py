from sqlalchemy import Column, Integer, Date
from app.db.base import Base

class Nfe(Base):
    __tablename__ = "nfe"

    ide_codigo = Column(Integer, primary_key=True, index=True)
    ide_dhemi = Column(Date)
