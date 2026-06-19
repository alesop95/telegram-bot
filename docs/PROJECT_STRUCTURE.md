# Struttura Progetto Bot Telegram

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
