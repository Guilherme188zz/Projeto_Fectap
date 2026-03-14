@echo off
title Sistema Gnuvet
cd /d "%~dp0"
echo Iniciando o Sistema Gnuvet...
echo.
echo Aguarde, o navegador abrira automaticamente.
echo Para encerrar o sistema, feche esta janela.
echo.
python -m streamlit run app.py
pause
