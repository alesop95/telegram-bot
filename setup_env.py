#!/usr/bin/env python3
"""
Script per configurare l'ambiente di sviluppo del bot Telegram
Versione pulita senza emoji per massima compatibilità
"""
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(command, description):
    """Esegue un comando e gestisce gli errori"""
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[SUCCESS] {description} completato")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Errore in {description}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return None

def create_project_structure():
    """Crea la struttura completa del progetto e sposta i file esistenti"""
    print("[INFO] Creazione struttura progetto e spostamento file...")
    
    # Definisce la struttura delle cartelle
    directories = [
        "src/bot",
        "src/database", 
        "src/handlers",
        "src/utils",
        "src/config",
        "tests/unit",
        "tests/integration",
        "docs",
        "scripts",
        "logs",
        "data",
        "docker"
    ]
    
    # Crea tutte le cartelle
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Crea __init__.py per i package Python
        if directory.startswith("src/"):
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.write_text("")
    
    # Mappa dei file da spostare: {file_attuale: nuova_posizione}
    file_moves = {
        # File bot principali
        "main.py": "src/bot/main.py",
        "main_cloud.py": "src/bot/main_cloud.py",
        
        # Configurazione
        "config.py": "src/config/settings.py",
        
        # Database
        "database.py": "src/database/sqlite_manager.py",
        "database_postgres.py": "src/database/postgres_manager.py",
        
        # Handlers
        "bot_handlers.py": "src/handlers/commands.py",
        
        # Utilities
        "utils.py": "src/utils/formatters.py",
        "health_server.py": "src/utils/health_server.py",
        
        # Test
        "tests/test_database.py": "tests/unit/test_database.py",
        
        # Docker
        "Dockerfile": "docker/Dockerfile",
        "docker-compose.yml": "docker/docker-compose.yml",
        
        # Scripts
        "deploy.sh": "scripts/deploy.sh",
        "run_bot.bat": "scripts/run_bot.bat",
        
        # Documentazione
        "DEPLOYMENT.md": "docs/DEPLOYMENT.md",
        "ARCHITECTURE.md": "docs/ARCHITECTURE.md",
        "RECAP_COMPLETO.md": "docs/RECAP_COMPLETO.md",
    }
    
    # Sposta i file esistenti
    moved_files = []
    for old_path, new_path in file_moves.items():
        old_file = Path(old_path)
        new_file = Path(new_path)
        
        if old_file.exists():
            try:
                # Assicurati che la directory di destinazione esista
                new_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Sposta il file
                shutil.move(str(old_file), str(new_file))
                moved_files.append(f"  {old_path} -> {new_path}")
                
            except Exception as e:
                print(f"[WARNING] Errore spostando {old_path}: {e}")
    
    if moved_files:
        print("[INFO] File spostati:")
        for move in moved_files:
            print(move)
    
    print("[SUCCESS] Struttura progetto creata e file organizzati")

def update_imports_in_moved_files():
    """Aggiorna gli import nei file spostati per riflettere la nuova struttura"""
    print("[INFO] Aggiornamento import nei file spostati...")
    
    # Mappa degli import da aggiornare: {vecchio_import: nuovo_import}
    import_updates = {
        # Import principali
        "from config import": "from src.config.settings import",
        "from database import": "from src.database.sqlite_manager import",
        "from database_postgres import": "from src.database.postgres_manager import", 
        "from bot_handlers import": "from src.handlers.commands import",
        "from utils import": "from src.utils.formatters import",
        "from health_server import": "from src.utils.health_server import",
        
        # Import specifici
        "import config": "from src.config import settings as config",
        "import database": "from src.database import sqlite_manager as database",
        "import utils": "from src.utils import formatters as utils",
    }
    
    # File da aggiornare con i loro nuovi percorsi
    files_to_update = [
        "src/bot/main.py",
        "src/bot/main_cloud.py", 
        "src/handlers/commands.py",
        "src/utils/health_server.py",
        "tests/unit/test_database.py"
    ]
    
    updated_files = []
    for file_path in files_to_update:
        file_obj = Path(file_path)
        if file_obj.exists():
            try:
                # Leggi il contenuto del file
                content = file_obj.read_text(encoding='utf-8')
                original_content = content
                
                # Applica gli aggiornamenti degli import
                for old_import, new_import in import_updates.items():
                    if old_import in content:
                        content = content.replace(old_import, new_import)
                
                # Scrivi il file aggiornato solo se è cambiato
                if content != original_content:
                    file_obj.write_text(content, encoding='utf-8')
                    updated_files.append(file_path)
                    
            except Exception as e:
                print(f"[WARNING] Errore aggiornando {file_path}: {e}")
    
    if updated_files:
        print("[INFO] Import aggiornati in:")
        for file_path in updated_files:
            print(f"  {file_path}")
    
    print("[SUCCESS] Import aggiornati")

def setup_virtual_environment():
    """Configura l'ambiente virtuale Python"""
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("[INFO] Ambiente virtuale già esistente")
        return True
    
    # Crea ambiente virtuale
    python_cmd = "python" if platform.system() == "Windows" else "python3"
    if not run_command(f"{python_cmd} -m venv .venv", "Creazione ambiente virtuale"):
        return False
    
    # Determina il comando di attivazione
    if platform.system() == "Windows":
        activate_cmd = ".venv\\Scripts\\activate"
        pip_cmd = ".venv\\Scripts\\pip"
    else:
        activate_cmd = "source .venv/bin/activate"
        pip_cmd = ".venv/bin/pip"
    
    # Aggiorna pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Aggiornamento pip"):
        return False
    
    # Installa dipendenze
    if Path("requirements.txt").exists():
        if not run_command(f"{pip_cmd} install -r requirements.txt", "Installazione dipendenze"):
            return False
    
    # Installa dipendenze di sviluppo
    dev_packages = [
        "pytest",
        "pytest-asyncio", 
        "pytest-cov",
        "black",
        "flake8",
        "mypy",
        "pre-commit"
    ]
    
    for package in dev_packages:
        run_command(f"{pip_cmd} install {package}", f"Installazione {package}")
    
    print("[SUCCESS] Ambiente virtuale configurato")
    print(f"[INFO] Per attivare: {activate_cmd}")
    
    return True

def create_activation_scripts():
    """Crea script per attivare facilmente l'ambiente"""
    
    # Script Windows
    windows_script = """@echo off
echo Attivazione ambiente virtuale Python...
call .venv\\Scripts\\activate.bat
echo Ambiente attivato!
echo Per disattivare: deactivate
cmd /k
"""
    
    try:
        with open("activate_env.bat", "w", encoding="utf-8") as f:
            f.write(windows_script)
    except UnicodeEncodeError:
        with open("activate_env.bat", "w", encoding="cp1252") as f:
            f.write(windows_script)
    
    # Script Unix/Linux/Mac
    unix_script = """#!/bin/bash
echo "Attivazione ambiente virtuale Python..."
source .venv/bin/activate
echo "Ambiente attivato!"
echo "Per disattivare: deactivate"
exec "$SHELL"
"""
    
    with open("activate_env.sh", "w", encoding="utf-8") as f:
        f.write(unix_script)
    
    # Rendi eseguibile su Unix
    if platform.system() != "Windows":
        os.chmod("activate_env.sh", 0o755)
    
    print("[SUCCESS] Script di attivazione creati")

def update_gitignore():
    """Aggiorna .gitignore per l'ambiente virtuale"""
    gitignore_additions = """
# Virtual Environment
.venv/
venv/
env/
ENV/

# Development tools
.mypy_cache/
.pytest_cache/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
desktop.ini
"""
    
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        current_content = gitignore_path.read_text()
        if ".venv/" not in current_content:
            with open(".gitignore", "a") as f:
                f.write(gitignore_additions)
            print("[SUCCESS] .gitignore aggiornato")
    else:
        gitignore_path.write_text(gitignore_additions)
        print("[SUCCESS] .gitignore creato")

def create_project_tree():
    """Crea un file con l'albero del progetto"""
    tree_content = """
telegram_bot/
├── src/                          # Codice sorgente principale
│   ├── bot/                      # Core del bot
│   │   ├── __init__.py
│   │   ├── main.py               # Entry point locale (SQLite)
│   │   └── main_cloud.py         # Entry point cloud (PostgreSQL)
│   ├── config/                   # Configurazioni
│   │   ├── __init__.py
│   │   └── settings.py           # Impostazioni centrali
│   ├── database/                 # Gestione database
│   │   ├── __init__.py
│   │   ├── sqlite_manager.py     # SQLite per sviluppo locale
│   │   └── postgres_manager.py   # PostgreSQL per produzione
│   ├── handlers/                 # Handler comandi Telegram
│   │   ├── __init__.py
│   │   ├── commands.py           # Comandi base
│   │   ├── callbacks.py          # Callback queries
│   │   └── media.py              # Gestione multimedia
│   └── utils/                    # Utilità e helper
│       ├── __init__.py
│       ├── formatters.py         # Formattazione messaggi
│       ├── validators.py         # Validazione input
│       └── security.py           # Funzioni sicurezza
├── tests/                        # Test automatici
│   ├── unit/                     # Test unitari
│   │   ├── test_database.py
│   │   ├── test_handlers.py
│   │   └── test_utils.py
│   ├── integration/              # Test integrazione
│   │   ├── test_bot_flow.py
│   │   └── test_database_flow.py
│   └── conftest.py               # Configurazione pytest
├── docker/                       # File Docker
│   ├── Dockerfile                # Immagine produzione
│   ├── Dockerfile.dev            # Immagine sviluppo
│   └── docker-compose.yml        # Orchestrazione servizi
├── docs/                         # Documentazione
│   ├── API.md                    # Documentazione API
│   ├── DEPLOYMENT.md             # Guida deployment
│   └── DEVELOPMENT.md            # Guida sviluppo
├── scripts/                      # Script utilità
│   ├── deploy.sh                 # Script deployment
│   ├── backup_db.sh              # Backup database
│   └── health_check.py           # Controllo salute
├── .github/                      # GitHub Actions
│   └── workflows/
│       ├── deploy.yml            # CI/CD pipeline
│       ├── test.yml              # Test automatici
│       └── security.yml          # Security scan
├── logs/                         # File di log
├── data/                         # Dati persistenti
├── .venv/                        # Ambiente virtuale Python
├── requirements.txt              # Dipendenze Python
├── requirements-dev.txt          # Dipendenze sviluppo
├── .env.example                  # Template variabili ambiente
├── .gitignore                    # File da ignorare Git
├── README.md                     # Documentazione principale
├── setup_env.py                  # Setup ambiente sviluppo
├── activate_env.bat              # Attiva env (Windows)
├── activate_env.sh               # Attiva env (Unix/Linux)
├── railway.json                  # Config Railway
├── render.yaml                   # Config Render
└── pyproject.toml                # Config Python moderna
"""
    
    with open("PROJECT_STRUCTURE.md", "w", encoding="utf-8") as f:
        f.write(f"# Struttura Progetto Bot Telegram\n{tree_content}")
    
    print("[SUCCESS] Albero progetto creato in PROJECT_STRUCTURE.md")

def clean_old_files():
    """Rimuove file temporanei e di backup"""
    print("[INFO] Pulizia file temporanei...")
    
    files_to_clean = [
        "activate_env.bat",
        "activate_env.sh", 
        "PROJECT_STRUCTURE.md"
    ]
    
    for file_name in files_to_clean:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"[INFO] Rimosso: {file_name}")
            except Exception as e:
                print(f"[WARNING] Errore rimuovendo {file_name}: {e}")
    
    print("[SUCCESS] Pulizia completata")

def main():
    """Funzione principale"""
    print("Setup Ambiente di Sviluppo Bot Telegram")
    print("=" * 50)
    
    # Verifica Python
    try:
        python_version = sys.version_info
        if python_version < (3, 8):
            print("[ERROR] Python 3.8+ richiesto")
            return False
        print(f"[SUCCESS] Python {python_version.major}.{python_version.minor} rilevato")
    except Exception as e:
        print(f"[ERROR] Errore verifica Python: {e}")
        return False
    
    # Setup completo
    steps = [
        clean_old_files,
        create_project_structure,
        update_imports_in_moved_files,
        setup_virtual_environment,
        create_activation_scripts,
        update_gitignore,
        create_project_tree
    ]
    
    for step in steps:
        try:
            step()
        except Exception as e:
            print(f"[ERROR] Errore in {step.__name__}: {e}")
            return False
    
    print("\n[SUCCESS] Setup completato con successo!")
    print("\n[INFO] Prossimi passi:")
    print("1. Attiva l'ambiente: activate_env.bat (Windows) o ./activate_env.sh (Unix)")
    print("2. Copia .env.example in .env e configura i tuoi token")
    print("3. Esegui i test: pytest")
    print("4. Avvia il bot: python src/bot/main.py")
    
    return True

if __name__ == "__main__":
    main()
