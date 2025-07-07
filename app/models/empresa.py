from app.db.base import Base
from sqlalchemy import Column, Integer, Date, String


class Empresa(Base):
    __tablename__ = "empresa"

    emp_cod: int = Column(Integer, primary_key=True, index=True)
    emp_fantasia: str = Column(String())
    emp_cnpj: str = Column(String())
    emp_ie: str = Column(String())
    emp_tel: str = Column(String())
    emp_cep: str = Column(String())
    emp_endereco: str = Column(String())
    emp_numero: str = Column(String())
    emp_bairro: str = Column(String())
