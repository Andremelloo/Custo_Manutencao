@echo off
chcp 65001 > nul
echo Restaurando Versao 3 - Atual (Base Completa com Filtro de Familia e Lupa)...
copy /Y versoes\v3_atual\app.js app.js
copy /Y versoes\v3_atual\dashboard_data.js dashboard_data.js
copy /Y versoes\v3_atual\generate_dashboard_data.py generate_dashboard_data.py
copy /Y versoes\v3_atual\index.html index.html
copy /Y versoes\v3_atual\styles.css styles.css
echo Pronto! Versao 3 (Atual) restaurada.
pause

