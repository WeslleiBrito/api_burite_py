from sqlalchemy import Column, String, Float
from app.db.base import Base

class TotalValues(Base):
    __tablename__ = "total_values"

    id = Column(String(36), primary_key=True)
    variable_expense_percentage = Column(Float)
