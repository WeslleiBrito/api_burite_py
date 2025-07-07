from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.db.base import Base
from app.models.cidade import Cidade

class Empresa(Base):
    __tablename__ = "empresa"

    emp_cod: Mapped[int] = mapped_column(primary_key=True, index=True)
    emp_fantasia: Mapped[str] = mapped_column()
    emp_cnpj: Mapped[str] = mapped_column()
    emp_ie: Mapped[str] = mapped_column()
    emp_logo: Mapped[str] = mapped_column()
    emp_tel: Mapped[str] = mapped_column()
    emp_email: Mapped[str] = mapped_column()
    emp_cep: Mapped[str] = mapped_column()
    emp_endereco: Mapped[str] = mapped_column()
    emp_numero: Mapped[str] = mapped_column()
    emp_bairro: Mapped[str] = mapped_column()
    emp_cidade: Mapped[int] = mapped_column(ForeignKey("cidade.cid_cod"))

    cidade: Mapped["Cidade"] = relationship("Cidade")
