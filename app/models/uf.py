from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Uf(Base):
    __tablename__ = "uf"

    uf_cod: Mapped[int] = mapped_column(primary_key=True, index=True)
    uf_descricao: Mapped[str] = mapped_column()
    uf_sigla: Mapped[str] = mapped_column()
