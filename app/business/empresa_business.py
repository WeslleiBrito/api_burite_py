import base64
import os.path
from fastapi import HTTPException
from typing import Tuple, Optional

from app.db.session import SessionLocal
from app.models.empresa import Empresa
from app.schemas import RetornoEmpresa, LogoBase64
from app.tipos.erro import ErroPadrao


def _convert_imagem64(path: str) -> Tuple[Optional[LogoBase64], Optional[ErroPadrao]]:
    path_formatado = fr"{path}"

    if not os.path.isfile(path_formatado):
        # Retorna erro com código e descrição padronizada
        return None, {
            "status_code": 1001,
            "description": "Caminho da imagem não localizado"
        }

    try:
        with open(path_formatado, "rb") as imagem:
            base64_logo = base64.b64encode(imagem.read()).decode("utf-8")

        return {
            "tipo": "image/png",
            "logo_base64": base64_logo
        }, None

    except Exception as e:
        return None, {
            "status_code": 1002,
            "description": f"Erro ao ler a imagem: {str(e)}"
        }


class EmpresaBusiness:

    @staticmethod
    def empresa() -> RetornoEmpresa:
        with SessionLocal() as db:
            resultado: Empresa = db.query(Empresa).first()

            logo, erro = _convert_imagem64(resultado.emp_logo)

            if erro:
                raise HTTPException(status_code=erro["status_code"], detail=erro["description"])

            return {
                "nome": resultado.emp_fantasia,
                "cnpj": resultado.emp_cnpj,
                "inscricaoEstadual": resultado.emp_ie,
                "logo": logo,
                "telefone": resultado.emp_tel,
                "email": resultado.emp_email,
                "endereco": {
                    "rua": resultado.emp_endereco,
                    "numero": resultado.emp_numero,
                    "bairro": resultado.emp_bairro,
                    "cidade": resultado.cidade.cid_nome,
                    "siglaEstado": resultado.cidade.uf.uf_sigla,
                    "estado": resultado.cidade.uf.uf_descricao,
                    "cep": resultado.emp_cep
                }
            }

if __name__ == "__main__":
    dados: RetornoEmpresa = EmpresaBusiness.empresa()
    print(dados)



