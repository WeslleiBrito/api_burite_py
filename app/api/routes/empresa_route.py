from fastapi import APIRouter

from app.services.empresa_service import EmpresaService
from app.schemas import RetornoEmpresa

router_empresa = APIRouter()

empresa = EmpresaService()

@router_empresa.get("", response_model=RetornoEmpresa)
def dados_empresa():

    return empresa.empresa()