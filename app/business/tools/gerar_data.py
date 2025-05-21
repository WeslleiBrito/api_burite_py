from datetime import date
from app.tipos.retorno_data import RetornoDatas


def gerar_data(data_inicio: date | None = None, data_fim: date | None = None) -> RetornoDatas:
    data_i: date | None = data_inicio
    data_f: date | None = data_fim

    if not data_i and not data_f:
        data_i = date.today()
        data_f = date.today()
    elif not data_i and data_f:
        data_i = date(1970, 1, 1)
    elif data_i and not data_f:
        data_f = date.today()

    return {
        "data_inicio": data_i,
        "data_fim": data_f
    }