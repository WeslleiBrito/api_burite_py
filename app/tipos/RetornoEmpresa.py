from typing import TypedDict

class _Endereco(TypedDict):
    rua: str
    numero: str
    bairro: str
    cidade: str
    cep: str
    siglaEstado: str

class RetornoEmpresa(TypedDict):
    nome: str
    logo: str
    cnpj: str
    inscricaoEstadual: str
    endereco: _Endereco
    telefone: str
    email: str


