@echo off
chcp 65001 > nul
echo Restaurando Versao 2 - Intermediaria (Code e QTY)...
copy /Y versoes\v2_code_qty\app.js app.js
copy /Y versoes\v2_code_qty\dashboard_data.js dashboard_data.js
copy /Y versoes\v2_code_qty\generate_dashboard_data.py generate_dashboard_data.py
copy /Y versoes\v2_code_qty\index.html index.html
copy /Y versoes\v2_code_qty\styles.css styles.css
echo Pronto! Versao 2 (Code e QTY) restaurada.
pause
