import base64
import os.path

from app.db.session import SessionLocal
from app.models.empresa import Empresa
from app.tipos.RetornoEmpresa import RetornoEmpresa

def _convert_imagem64(path: str):
    path_formatado = fr"{path}"

    if not os.path.isfile(path_formatado):
        return None, "Caminho não localizado"

    try:
        with open(path_formatado, "rb") as imagem:
            base64_logo = base64.b64encode(imagem.read()).decode("utf-8")
        return {
            "tipo": "image/png",
            "logo_base64": base64_logo
        }, None
    except Exception as e:
        return None, f"Erro ao ler a imagem: {str(e)}"


class EmpresaBusiness:

    def __init__(self):
        pass

    @staticmethod
    def empresa() -> RetornoEmpresa:
        with SessionLocal() as db:

            resultado: Empresa = db.query(Empresa).first()


            return {
                "nome": resultado.emp_fantasia,
                "cnpj": resultado.emp_cnpj,
                "inscricaoEstadual": resultado.emp_ie,
                "logo": _convert_imagem64(resultado.emp_logo),
                "telefone": resultado.emp_tel,
                "email": resultado.emp_email,
                "endereco": {
                    "rua": resultado.emp_endereco,
                    "numero": resultado.emp_numero,
                    "bairro": resultado.emp_bairro,
                    "cidade": resultado.cidade.cid_nome,
                    "siglaEstado": resultado.cidade.uf.uf_sigla,
                    "cep": resultado.emp_cep
                }
            }


if __name__ == "__main__":
    dados: RetornoEmpresa = EmpresaBusiness.empresa()
    print(dados)



