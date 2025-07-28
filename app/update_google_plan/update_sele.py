import gspread
from oauth2client.service_account import ServiceAccountCredentials
from app.business.venda import Venda  # métodos que já existem
import os
from dotenv import load_dotenv
from datetime import date, datetime


load_dotenv()

# Configurações
CREDENCIAIS = fr"{os.getenv('CREDENCIAIS')}" # JSON da conta de serviço do Google
SHEET_NAME = os.getenv('SHEET_SALES')

# Autenticação Google
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENCIAIS, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Buscar dados direto do banco
venda = Venda()
vendas = venda.venda_por_venda_periodo(data_inicio=date.today(), data_fim=date.today())  # Ex: retorna lista de dicionários

def serializar(val):
    if isinstance(val, (date, datetime)):
        return val.isoformat()  # '2025-07-28'
    return val

# Atualizar planilha com as vendas
sheet.clear()
if vendas and isinstance(vendas[0], dict):
    headers = list(vendas[0].keys())
    valores = [headers] + [[serializar(v) for v in item.values()] for item in vendas]
    sheet.update(values=valores, range_name="A1")
else:
    print("Nenhum dado encontrado para vendas.")

print("Planilha atualizada com sucesso!")
