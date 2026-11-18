@echo off
chcp 65001 > nul
echo ============================================================
echo   RESTAURADOR DE VERSAO ANTERIOR - TCP Custo Manutencao
echo ============================================================
echo.
echo Restaurando arquivos a partir de backup_v1...
copy /Y backup_v1\generate_dashboard_data.py generate_dashboard_data.py
copy /Y backup_v1\dashboard_data.js dashboard_data.js
copy /Y backup_v1\index.html index.html
copy /Y backup_v1\app.js app.js
copy /Y backup_v1\styles.css styles.css
echo.
echo Pronto! Os arquivos foram restaurados com sucesso para a versao v1.
echo Se desejar restaurar no Git, execute: git checkout backup-versao-anterior
echo.
pause

