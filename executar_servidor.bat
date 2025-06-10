@echo off
title Iniciar Servidor FastAPI

echo Verificando ambiente...
if not exist ".\venv\Scripts\python.exe" (
    echo [ERRO] Ambiente virtual não encontrado em .\venv\
    echo Crie um com: python -m venv venv
    pause
    exit /b 1
)

if not exist "start_server_with_tray.pyw" (
    echo [ERRO] Arquivo start_server_with_tray.pyw não encontrado!
    pause
    exit /b 1
)

echo Iniciando servidor FastAPI na porta 8000...
echo - IP: %COMPUTERNAME%
echo - URL: http://localhost:8000
echo - URL na rede: http://%COMPUTERNAME%:8000
echo.
echo Use o ícone na bandeja do sistema para encerrar.

.\venv\Scripts\python.exe start_server_with_tray.pyw

echo Servidor encerrado.
pause