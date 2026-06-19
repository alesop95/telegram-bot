@echo off
echo ========================================
echo    Bot Telegram Personalizzato
echo ========================================
echo.

REM Controlla se Python è installato
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non è installato o non è nel PATH
    echo Scarica Python da: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Controlla se il file .env esiste
if not exist ".env" (
    echo ATTENZIONE: File .env non trovato!
    echo.
    echo 1. Copia .env.example in .env
    echo 2. Modifica .env con i tuoi dati
    echo 3. Ottieni il token da @BotFather su Telegram
    echo.
    pause
    exit /b 1
)

REM Installa le dipendenze se necessario
if not exist "venv\" (
    echo Creazione ambiente virtuale...
    python -m venv venv
)

echo Attivazione ambiente virtuale...
call venv\Scripts\activate.bat

echo Installazione dipendenze...
pip install -r requirements.txt

echo.
echo Avvio del bot...
echo Premi Ctrl+C per fermare il bot
echo.

python main.py

pause
