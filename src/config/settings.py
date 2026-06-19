"""
Configurazione del bot Telegram
"""
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()

class Config:
    """Classe di configurazione per il bot"""
    
    # Token del bot Telegram (ottenuto da @BotFather)
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # ID dell'amministratore del bot
    ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', 0))
    
    # Percorso del database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'bot_database.db')
    
    # Configurazione webhook (per produzione)
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    PORT = int(os.getenv('PORT', 8443))
    
    # Messaggi predefiniti
    WELCOME_MESSAGE = """
🤖 *Benvenuto nel tuo Bot Personalizzato!*

Questo bot ti permette di:
• 📝 Inviare messaggi personalizzati
• 🎨 Personalizzare temi delle chat
• 📸 Condividere contenuti multimediali
• ⚙️ Gestire impostazioni avanzate

Usa /help per vedere tutti i comandi disponibili!
    """
    
    HELP_MESSAGE = """
🔧 *Comandi Disponibili:*

*Messaggi:*
/custom - Crea un messaggio personalizzato
/templates - Gestisci template di messaggi
/schedule - Programma un messaggio

*Multimedia:*
/photo - Invia una foto con didascalia
/video - Invia un video
/audio - Invia un file audio

*Personalizzazione:*
/theme - Cambia tema della chat
/settings - Impostazioni personali
/profile - Il tuo profilo

*Amministrazione:*
/stats - Statistiche del bot
/users - Lista utenti (solo admin)
/broadcast - Messaggio a tutti (solo admin)

*Aiuto:*
/help - Mostra questo messaggio
/about - Informazioni sul bot
    """
