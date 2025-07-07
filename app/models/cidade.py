from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.db.base import Base
from app.models.uf import Uf

class Cidade(Base):
    __tablename__ = "cidade"

    cid_cod: Mapped[int] = mapped_column(primary_key=True)
    cid_nome: Mapped[str] = mapped_column()
    cid_estado: Mapped[int] = mapped_column(ForeignKey("uf.uf_cod"))

    uf: Mapped["Uf"] = relationship("Uf")
