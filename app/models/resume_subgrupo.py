from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import relationship
from app.db.base import Base

class ResumeSubgroupo(Base):
    __tablename__ = "resume_subgroups"

    cod_subgroup = Column(Integer, primary_key=True)
    fixed_unit_expense = Column(Float)

    produtos = relationship("Produto", back_populates="subgrupo_rel")
