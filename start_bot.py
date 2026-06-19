#!/usr/bin/env python3
"""
Script di avvio semplificato per il bot Telegram
Gestisce automaticamente l'ambiente virtuale e i percorsi
"""
import os
import sys
import subprocess
from pathlib import Path

def check_virtual_environment():
    """Controlla se l'ambiente virtuale è attivo"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def activate_virtual_environment():
    """Attiva l'ambiente virtuale se non è già attivo"""
    if check_virtual_environment():
        print("[INFO] Ambiente virtuale già attivo")
        return True
    
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("[ERROR] Ambiente virtuale non trovato!")
        print("[INFO] Esegui prima: python setup_env.py")
        return False
    
    # Determina il percorso dell'attivazione
    if os.name == 'nt':  # Windows
        activate_script = venv_path / "Scripts" / "activate.bat"
        python_exe = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/Mac
        activate_script = venv_path / "bin" / "activate"
        python_exe = venv_path / "bin" / "python"
    
    if not python_exe.exists():
        print("[ERROR] Python non trovato nell'ambiente virtuale")
        return False
    
    print("[INFO] Ambiente virtuale trovato")
    return str(python_exe)

def check_project_structure():
    """Controlla se la struttura del progetto è corretta"""
    required_paths = [
        "src/bot",
        "src/config", 
        "src/database",
        "src/handlers"
    ]
    
    missing_paths = []
    for path in required_paths:
        if not Path(path).exists():
            missing_paths.append(path)
    
    if missing_paths:
        print("[ERROR] Struttura progetto incompleta!")
        print("[INFO] Cartelle mancanti:")
        for path in missing_paths:
            print(f"  - {path}")
        print("[INFO] Esegui: python setup_env.py")
        return False
    
    return True

def check_configuration():
    """Controlla se la configurazione è presente"""
    env_file = Path(".env")
    if not env_file.exists():
        print("[WARNING] File .env non trovato!")
        print("[INFO] Crea il file .env copiando da .env.example")
        print("[INFO] Inserisci TELEGRAM_BOT_TOKEN e ADMIN_USER_ID")
        return False
    
    # Verifica che le variabili essenziali siano presenti
    try:
        with open(".env", "r") as f:
            content = f.read()
            if "TELEGRAM_BOT_TOKEN=" not in content or "ADMIN_USER_ID=" not in content:
                print("[WARNING] Configurazione .env incompleta!")
                print("[INFO] Assicurati di aver configurato TELEGRAM_BOT_TOKEN e ADMIN_USER_ID")
                return False
    except Exception as e:
        print(f"[ERROR] Errore leggendo .env: {e}")
        return False
    
    print("[SUCCESS] Configurazione trovata")
    return True

def start_bot(mode="local"):
    """Avvia il bot nel modo specificato"""
    print(f"[INFO] Avvio bot in modalità {mode}...")
    
    # Determina quale file avviare
    if mode == "local":
        bot_file = "src/bot/main.py"
        print("[INFO] Modalità locale (SQLite)")
    elif mode == "cloud":
        bot_file = "src/bot/main_cloud.py"
        print("[INFO] Modalità cloud (PostgreSQL)")
    else:
        print("[ERROR] Modalità non riconosciuta. Usa 'local' o 'cloud'")
        return False
    
    # Controlla che il file esista
    if not Path(bot_file).exists():
        print(f"[ERROR] File {bot_file} non trovato!")
        return False
    
    # Ottieni il Python dell'ambiente virtuale
    python_exe = activate_virtual_environment()
    if not python_exe or python_exe is True:
        python_exe = sys.executable
    
    # Aggiungi src al PYTHONPATH
    env = os.environ.copy()
    current_pythonpath = env.get('PYTHONPATH', '')
    src_path = str(Path.cwd() / "src")
    
    if current_pythonpath:
        env['PYTHONPATH'] = f"{src_path}{os.pathsep}{current_pythonpath}"
    else:
        env['PYTHONPATH'] = src_path
    
    try:
        # Avvia il bot
        subprocess.run([python_exe, bot_file], env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Errore nell'avvio del bot: {e}")
        return False
    except KeyboardInterrupt:
        print("\n[INFO] Bot fermato dall'utente")
        return True
    
    return True

def show_menu():
    """Mostra il menu di selezione"""
    print("\n" + "="*50)
    print("AVVIO BOT TELEGRAM PERSONALIZZATO")
    print("="*50)
    print()
    print("Scegli la modalità di avvio:")
    print("1) Locale (SQLite) - Per sviluppo")
    print("2) Cloud (PostgreSQL) - Per produzione")
    print("3) Setup ambiente")
    print("4) Informazioni progetto")
    print("0) Esci")
    print()

def show_project_info():
    """Mostra informazioni sul progetto"""
    print("\n[INFO] INFORMAZIONI PROGETTO")
    print("-" * 30)
    
    # Controlla struttura
    structure_ok = check_project_structure()
    print(f"Struttura progetto: {'OK' if structure_ok else 'Mancante'}")
    
    # Controlla ambiente virtuale
    venv_exists = Path(".venv").exists()
    venv_active = check_virtual_environment()
    print(f"Ambiente virtuale: {'Esistente' if venv_exists else 'Mancante'} | {'Attivo' if venv_active else 'Non attivo'}")
    
    # Controlla configurazione
    config_ok = Path(".env").exists()
    print(f"Configurazione: {'Presente' if config_ok else 'Mancante'}")
    
    # Controlla file principali
    main_local = Path("src/bot/main.py").exists()
    main_cloud = Path("src/bot/main_cloud.py").exists()
    print(f"Bot locale: {'Presente' if main_local else 'Mancante'}")
    print(f"Bot cloud: {'Presente' if main_cloud else 'Mancante'}")
    
    print("\n[INFO] PROSSIMI PASSI:")
    if not structure_ok or not venv_exists:
        print("1. Esegui: python setup_env.py")
    if not config_ok:
        print("2. Copia .env.example in .env e configuralo")
    if structure_ok and venv_exists and config_ok:
        print("Tutto pronto! Puoi avviare il bot.")

def main():
    """Funzione principale"""
    while True:
        show_menu()
        
        try:
            choice = input("Scelta: ").strip()
        except KeyboardInterrupt:
            print("\n[INFO] Arrivederci!")
            break
        
        if choice == "1":
            # Modalità locale
            if not check_project_structure():
                continue
            if not check_configuration():
                continue
            start_bot("local")
            
        elif choice == "2":
            # Modalità cloud
            if not check_project_structure():
                continue
            if not check_configuration():
                continue
            start_bot("cloud")
            
        elif choice == "3":
            # Setup ambiente
            print("[INFO] Avvio setup ambiente...")
            try:
                subprocess.run([sys.executable, "setup_env.py"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Errore nel setup: {e}")
            except FileNotFoundError:
                print("[ERROR] File setup_env.py non trovato!")
            
        elif choice == "4":
            # Informazioni progetto
            show_project_info()
            
        elif choice == "0":
            print("[INFO] Arrivederci!")
            break
            
        else:
            print("[ERROR] Scelta non valida")
        
        input("\n⏎ Premi INVIO per continuare...")

if __name__ == "__main__":
    main()
