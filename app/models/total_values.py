from datetime import datetime, UTC

from sqlalchemy import BigInteger, Numeric, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class TotalValues(Base):
    __tablename__ = "total_values"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    invoicing: Mapped[float] = mapped_column(Numeric(12, 2))
    cost: Mapped[float] = mapped_column(Numeric(12, 2))
    fixed_expenses: Mapped[float] = mapped_column(Numeric(12, 2))
    variable_expenses: Mapped[float] = mapped_column(Numeric(12, 2))
    discount: Mapped[float] = mapped_column(Numeric(12, 2))
    general_monetary_profit: Mapped[float] = mapped_column(Numeric(12, 2))
    number_of_months: Mapped[int] = mapped_column(Integer)
    general_percentage_profit: Mapped[float] = mapped_column(Numeric(5, 2))
    commission: Mapped[float] = mapped_column(Numeric(12, 2))
    variable_expense_percentage: Mapped[float] = mapped_column(Numeric(12, 3))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))