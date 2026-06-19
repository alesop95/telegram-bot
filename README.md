# Bot Telegram Personalizzato

Un bot Telegram avanzato che permette di creare messaggi personalizzati, gestire temi chat e condividere contenuti multimediali senza bisogno di Telegram Premium.

## Funzionalità

### Messaggi Personalizzati
- **Testo formattato**: grassetto, corsivo, codice, collegamenti
- **Bottoni interattivi**: azioni rapide e menu di navigazione
- **Template riutilizzabili**: Salvare e riutilizzare messaggi frequenti
- **Messaggi programmati**: Invio automatico a orari specifici

### Personalizzazione Temi
- **5 temi disponibili**: Default, Dark, Colorful, Professional, Gaming
- **Impostazioni personalizzate**: Notifiche, lingua, fuso orario
- **Esperienza personalizzata**: Ogni utente ha le sue preferenze

### Contenuti Multimediali
- **Foto**: Con didascalie personalizzate e formattazione
- **Video**: Supporto completo con informazioni dettagliate
- **Audio**: File musicali e messaggi vocali
- **Documenti**: Tutti i tipi di file (PDF, Word, Excel, etc.)
- **Sticker**: Gestione completa degli sticker

### Statistiche e Gestione
- **Statistiche personali**: Template creati, utilizzi, attività
- **Statistiche admin**: Utenti totali, comandi più usati
- **Database SQLite**: Salvataggio sicuro di tutti i dati
- **Logging completo**: Monitoraggio di tutte le attività

## Installazione

### 1. Prerequisiti
- Python 3.8 o superiore
- Account Telegram
- Bot Token da @BotFather

### 2. Configurazione

1. **Clonare o scaricare il progetto**
   ```bash
   git clone <repository-url>
   cd telegram_bot
   ```

2. **Installare le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurare il bot**
   ```bash
   # Copiare il file di configurazione
   cp .env.example .env
   
   # Modificare il file .env con i tuoi dati
   nano .env
   ```

4. **Ottienere il Bot Token**
   - Aprire Telegram e cercare @BotFather
   - Inviare `/newbot` e seguire le istruzioni
   - Copiare il token ricevuto nel file `.env`

5. **Ottienere il proprio User ID**
   - Cercare @userinfobot su Telegram
   - Inviare `/start` per ottenere l'ID
   - Inserire l'ID nel file `.env` come ADMIN_USER_ID

### 3. Avvio del Bot

```bash
python main.py
```

Il bot si avvierà e sarà pronto per ricevere messaggi!

## Comandi Disponibili

### Comandi Base
- `/start` - Avvia il bot e mostra il menu principale
- `/help` - Mostra tutti i comandi disponibili
- `/settings` - Gestisci le tue impostazioni personali

### Messaggi Personalizzati
- `/custom` - Crea messaggi personalizzati
- `/templates` - Gestisci i tuoi template
- `/schedule` - Programma messaggi (in sviluppo)

### Multimedia e Temi
- `/multimedia` - Gestione contenuti multimediali
- `/theme` - Cambia il tema della chat
- `/photo` - Invia foto con didascalia personalizzata

### Statistiche
- `/stats` - Le tue statistiche personali
- `/profile` - Il tuo profilo utente

## Come Usare

### 1. Primo Avvio
1. Invia `/start` al bot
2. Scegli le tue preferenze dal menu
3. Esplora le funzionalità disponibili

### 2. Creare Messaggi Personalizzati
1. Usare `/custom` o cliccare "Messaggi Personalizzati"
2. Scegliere il tipo di messaggio:
   - **Formattato**: Con grassetto, corsivo, etc.
   - **Con Bottoni**: Bottoni interattivi
   - **Da Template**: Usa un template salvato

### 3. Gestire Template
1. Usare `/templates` per vedere i tuoi template
2. Creare nuovi template con contenuti riutilizzabili
3. Usare i template per velocizzare l'invio di messaggi

### 4. Personalizzare l'Esperienza
1. Usare `/theme` per cambiare tema
2. Andare in `/settings` per personalizzare:
   - Notifiche
   - Lingua
   - Fuso orario

## Configurazione Avanzata

### File di Configurazione (.env)
```env
# Token del bot (obbligatorio)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# ID amministratore (obbligatorio)
ADMIN_USER_ID=123456789

# Database (opzionale)
DATABASE_PATH=bot_database.db

# Webhook per produzione (opzionale)
WEBHOOK_URL=https://your-domain.com/webhook
PORT=8443
```

### Struttura Database
Il bot utilizza SQLite con le tabelle:
- `users` - Informazioni utenti
- `user_settings` - Impostazioni personalizzate
- `message_templates` - Template salvati
- `scheduled_messages` - Messaggi programmati
- `bot_stats` - Statistiche di utilizzo

## Sviluppo e Personalizzazione

### Struttura del Progetto
```
telegram_bot/
├── 📁 src/                          # Codice sorgente principale
│   ├── 📁 bot/                      # Core del bot
│   │   ├── main.py                  # Entry point locale (SQLite)
│   │   └── main_cloud.py            # Entry point cloud (PostgreSQL)
│   ├── 📁 config/                   # Configurazioni
│   ├── 📁 database/                 # Gestione database
│   ├── 📁 handlers/                 # Handler comandi Telegram
│   └── 📁 utils/                    # Utilità e helper
├── 📁 tests/                        # Test automatici
│   ├── 📁 unit/                     # Test unitari
│   └── 📁 integration/              # Test integrazione
├── 📁 docker/                       # Containerizzazione
├── 📁 docs/                         # Documentazione
├── 📁 .github/workflows/            # CI/CD Pipeline
├── 📁 .venv/                        # Ambiente virtuale Python
├── 📄 requirements.txt              # Dipendenze produzione
├── 📄 requirements-dev.txt          # Dipendenze sviluppo
├── 📄 pyproject.toml                # Configurazione Python moderna
├── 📄 setup_env.py                  # Setup ambiente sviluppo
└── 📄 ARCHITECTURE.md               # Documentazione architettura
```

### Aggiungere Nuove Funzionalità
1. **Nuovo Comando**: Aggiungi l'handler in `bot_handlers.py`
2. **Nuova Tabella**: Modifica `database.py`
3. **Nuova Configurazione**: Aggiungi in `config.py`

### Personalizzare i Messaggi
Modificare i messaggi in `config.py`:
- `WELCOME_MESSAGE` - Messaggio di benvenuto
- `HELP_MESSAGE` - Messaggio di aiuto

## Deploy in Produzione

### Opzione 1: Server Locale
```bash
# Avviare in background
nohup python main.py &

# Oppure usare screen
screen -S telegram_bot
python main.py
# Ctrl+A, D per detach
```

### Opzione 2: Heroku
1. Creare un'app Heroku
2. Configurare le variabili d'ambiente
3. Deployare il codice

### Opzione 3: VPS
1. Configurare un server Linux
2. Installare Python e dipendenze
3. Usare systemd per il servizio automatico

## Sicurezza

- **Token sicuro**: il token del bot non deve essere condiviso
- **Variabili d'ambiente**: usare sempre file `.env` per dati sensibili
- **Backup database**: fare backup regolari del database
- **Logging**: monitorare i log per attività sospette

## Troubleshooting

### Errori Comuni

1. **"Token non configurato"**
   - Controllare che il file `.env` esista
   - Verifica che il token sia corretto

2. **"Bot non risponde"**
   - Controllare la connessione internet
   - Verifica che il bot sia avviato correttamente

3. **"Errore database"**
   - Controllare i permessi del file database
   - Verificare che SQLite sia installato

### Log e Debug
- I log sono salvati in `bot.log`
- Usa `logging.DEBUG` per debug dettagliato
- Controlla sempre i log in caso di errori

## Licenza

Questo progetto è rilasciato sotto licenza MIT. Sentiti libero di modificarlo e distribuirlo.

## Ringraziamenti

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Libreria principale
- [Telegram Bot API](https://core.telegram.org/bots/api) - API ufficiali
- Community Telegram per il supporto e i feedback
