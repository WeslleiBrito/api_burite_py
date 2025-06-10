import subprocess
import socket
from datetime import datetime
from threading import Thread
import sys
from pystray import Icon, MenuItem, Menu
from PIL import Image, UnidentifiedImageError
from plyer import notification

# Configurações
PORTA = 8000
ICON_PATH = "icone-servidor.png"  # Caminho do ícone

# Variável global para o processo
processo = None


def obter_informacoes_sistema():
    """Obtém informações do sistema de forma segura"""
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        hora = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        return hostname, ip, hora
    except Exception as e:
        print(f"Erro ao obter informações do sistema: {e}")
        return "Desconhecido", "127.0.0.1", datetime.now().strftime("%H:%M:%S %d/%m/%Y")


def mostrar_notificacao(hostname, ip, hora):
    """Mostra notificação de inicialização"""
    try:
        notification.notify(
            title="FastAPI Servidor Iniciado",
            message=f"{ip}:{PORTA} em {hostname}\nIniciado às {hora}",
            timeout=6
        )
    except Exception as e:
        print(f"Erro ao mostrar notificação: {e}")


def iniciar_servidor():
    """Inicia o servidor FastAPI sem abrir janelas"""
    global processo

    # Configuração para ocultar janela no Windows
    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    try:
        processo = subprocess.Popen(
            [
                "./venv/Scripts/python.exe",
                "-m", "uvicorn",
                "app.main:app",
                "--reload",
                "--port", str(PORTA)
            ],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        processo.wait()
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        sys.exit(1)


def encerrar(icon, item):
    """Encerra o servidor e remove o ícone da bandeja"""
    global processo
    try:
        if processo:
            processo.terminate()
            processo.wait()
    except Exception as e:
        print(f"Erro ao encerrar servidor: {e}")
    finally:
        icon.stop()
    return True


def iniciar_bandeja():
    """Inicia o ícone na bandeja do sistema"""
    try:
        # Tenta carregar a imagem do ícone
        try:
            imagem = Image.open(ICON_PATH)
        except UnidentifiedImageError:
            # Cria uma imagem alternativa se o ícone não for encontrado
            imagem = Image.new('RGB', (64, 64), color='red')

        menu = Menu(MenuItem("Encerrar servidor", encerrar))
        icone = Icon("Servidor FastAPI", imagem, "Servidor FastAPI", menu)
        icone.run()
    except Exception as e:
        print(f"Erro ao iniciar ícone da bandeja: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Obtém informações do sistema
    hostname, ip, hora = obter_informacoes_sistema()

    # Mostra notificação
    mostrar_notificacao(hostname, ip, hora)

    # Inicia servidor em thread separada
    Thread(target=iniciar_servidor, daemon=True).start()

    # Inicia ícone na bandeja (thread principal)
    iniciar_bandeja()