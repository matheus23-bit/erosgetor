@echo off
chcp 65001 > nul
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║      ErosGest AI v2 — Build de Produção                 ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
python --version > nul 2>&1
if errorlevel 1 (echo [ERRO] Python nao encontrado & pause & exit /b 1)
echo [1/4] Instalando dependencias...
pip install pyinstaller pillow pyttsx3 SpeechRecognition --quiet
echo [2/4] Gerando icone...
python create_icon.py
echo [3/4] Compilando EXE...
pyinstaller --onefile --windowed --name "ErosGest AI" --icon="icon.ico" --add-data "icon.ico;." --add-data "database;database" --add-data "modules;modules" --add-data "workers;workers" --hidden-import "database.db" --hidden-import "modules.ai_assistant" --hidden-import "workers.price_worker" --hidden-import "pyttsx3" --hidden-import "speech_recognition" --hidden-import "tkinter" --hidden-import "tkinter.ttk" --hidden-import "sqlite3" --hidden-import "hashlib" --collect-submodules "database" --collect-submodules "modules" --collect-submodules "workers" --noconfirm --clean main.py
if errorlevel 1 (echo [ERRO] Build falhou! & pause & exit /b 1)
echo [4/4] Pronto!
echo LOGIN PADRAO: admin / admin123
pause
