from pydantic import BaseModel

class AnnualTaxBillingResumo(BaseModel):
    substituido: float
    nao_substituido: float
