from app.business.venda import Venda as VendaBusiness


class VendaService(VendaBusiness):
    def __init__(self):
        super().__init__()
