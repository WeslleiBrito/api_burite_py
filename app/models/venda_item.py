from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship, backref
from app.db.base import Base


class VendaItem(Base):
    __tablename__ = "venda_item"

    item_cod = Column(Integer, primary_key=True, index=True)
    venda = Column(Integer, ForeignKey("venda.vend_cod"))
    produto = Column(Integer, ForeignKey("produto.prod_cod"))
    qtd = Column(Float)
    qtd_devolvida = Column(Float)
    vrcusto_composicao = Column(Float)
    total = Column(Float)
    dtvenda = Column(Date)
    desconto = Column(Float)

    venda_rel = relationship("Venda", back_populates="itens")
    produto_rel = relationship("Produto", back_populates="itens")

    vendedor_rel = relationship(
        "Funcionario",
        secondary="venda",
        primaryjoin="VendaItem.venda == Venda.vend_cod",
        secondaryjoin="Venda.vendedor == Funcionario.fun_cod",
        viewonly=True,
        backref=backref("itens_vendidos", viewonly=True)
    )

    @property
    def fixed_unit_expense(self) -> float | None:
        if self.produto_rel and self.produto_rel.subgrupo_rel:
            return self.produto_rel.subgrupo_rel.fixed_unit_expense
        return None  # ou return 0.0, se quiser evitar None