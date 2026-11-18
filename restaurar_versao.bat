@echo off
chcp 65001 > nul
cls
echo ============================================================
echo       GERENCIADOR DE VERSÕES - TCP Custo Manutenção
echo ============================================================
echo.
echo Selecione qual versão você deseja restaurar para o projeto:
echo.
echo   [1] Versão 1 - Original (Base histórica inicial sem Code/QTY)
echo   [2] Versão 2 - Intermediária (Primeira carga com Code/QTY)
echo   [3] Versão 3 - Atual Completa (Base completa, Lupa e Famílias)
echo   [S] Sair sem alterar
echo.
set /p op="Digite a opção desejada [1, 2, 3 ou S]: "

if /i "%op%"=="1" goto rest_v1
if /i "%op%"=="2" goto rest_v2
if /i "%op%"=="3" goto rest_v3
if /i "%op%"=="S" goto fim
goto fim

:rest_v1
echo.
echo Restaurando Versão 1 (Original)...
copy /Y versoes\v1_original\app.js app.js
copy /Y versoes\v1_original\dashboard_data.js dashboard_data.js
copy /Y versoes\v1_original\generate_dashboard_data.py generate_dashboard_data.py
copy /Y versoes\v1_original\index.html index.html
copy /Y versoes\v1_original\styles.css styles.css
echo.
echo [OK] Versão 1 restaurada com sucesso!
goto fim

:rest_v2
echo.
echo Restaurando Versão 2 (Intermediária Code/QTY)...
copy /Y versoes\v2_code_qty\app.js app.js
copy /Y versoes\v2_code_qty\dashboard_data.js dashboard_data.js
copy /Y versoes\v2_code_qty\generate_dashboard_data.py generate_dashboard_data.py
copy /Y versoes\v2_code_qty\index.html index.html
copy /Y versoes\v2_code_qty\styles.css styles.css
echo.
echo [OK] Versão 2 restaurada com sucesso!
goto fim

:rest_v3
echo.
echo Restaurando Versão 3 (Atual com Lupa e Famílias)...
copy /Y versoes\v3_atual\app.js app.js
copy /Y versoes\v3_atual\dashboard_data.js dashboard_data.js
copy /Y versoes\v3_atual\generate_dashboard_data.py generate_dashboard_data.py
copy /Y versoes\v3_atual\index.html index.html
copy /Y versoes\v3_atual\styles.css styles.css
echo.
echo [OK] Versão 3 restaurada com sucesso!
goto fim

:fim
echo.
pause
