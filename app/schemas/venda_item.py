from pydantic import BaseModel

class VendaItemResumo(BaseModel):
    mes: str
    total_quantidade: float
    total_vendido: float
    custo_total: float
