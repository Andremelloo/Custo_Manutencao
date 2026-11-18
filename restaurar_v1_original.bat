@echo off
chcp 65001 > nul
echo Restaurando Versao 1 - Original (Historica)...
copy /Y versoes\v1_original\app.js app.js
copy /Y versoes\v1_original\dashboard_data.js dashboard_data.js
copy /Y versoes\v1_original\generate_dashboard_data.py generate_dashboard_data.py
copy /Y versoes\v1_original\index.html index.html
copy /Y versoes\v1_original\styles.css styles.css
echo Pronto! Versao 1 (Original) restaurada.
pause
