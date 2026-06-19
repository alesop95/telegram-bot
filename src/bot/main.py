"""
Bot Telegram Personalizzato
Creato per gestire messaggi personalizzati, temi chat e contenuti multimediali
"""
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from src.config.settings import Config
from src.database.sqlite_manager import DatabaseManager
from src.handlers.commands import BotHandlers

# Configurazione logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramBot:
    """Classe principale del bot Telegram"""
    
    def __init__(self):
        self.config = Config()
        self.db_manager = DatabaseManager(self.config.DATABASE_PATH)
        self.handlers = BotHandlers(self.db_manager)
        self.application = None
    
    def setup_handlers(self):
        """Configura tutti gli handler del bot"""
        if not self.application:
            logger.error("Application non inizializzata")
            return
        
        # Handler per comandi
        self.application.add_handler(CommandHandler("start", self.handlers.start_command))
        self.application.add_handler(CommandHandler("help", self.handlers.help_command))
        self.application.add_handler(CommandHandler("custom", self.handlers.custom_message_command))
        self.application.add_handler(CommandHandler("theme", self.handlers.theme_command))
        self.application.add_handler(CommandHandler("multimedia", self.handlers.multimedia_command))
        self.application.add_handler(CommandHandler("templates", self.handlers.templates_command))
        self.application.add_handler(CommandHandler("settings", self.handlers.settings_command))
        self.application.add_handler(CommandHandler("stats", self.handlers.stats_command))
        
        # Handler per callback dei bottoni
        self.application.add_handler(CallbackQueryHandler(self.handlers.button_callback))
        
        # Handler per messaggi di testo
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handlers.handle_text_message
        ))
        
        # Handler per contenuti multimediali
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.application.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        self.application.add_handler(MessageHandler(filters.AUDIO, self.handle_audio))
        self.application.add_handler(MessageHandler(filters.DOCUMENT, self.handle_document))
        self.application.add_handler(MessageHandler(filters.STICKER, self.handle_sticker))
        
        # Handler per errori
        self.application.add_error_handler(self.error_handler)
        
        logger.info("Tutti gli handler configurati correttamente")
    
    async def handle_photo(self, update: Update, context):
        """Handler per le foto ricevute"""
        user_id = update.effective_user.id
        photo = update.message.photo[-1]  # Prende la foto con qualità più alta
        caption = update.message.caption or ""
        
        self.db_manager.log_command_usage(user_id, 'photo_received')
        
        await update.message.reply_text(
            f"📸 *Foto ricevuta!*\n\n"
            f"📏 Dimensioni: {photo.width}x{photo.height}\n"
            f"💾 Dimensione: {photo.file_size} bytes\n"
            f"📝 Didascalia: {caption if caption else 'Nessuna didascalia'}\n\n"
            f"✅ Foto processata con successo!",
            parse_mode='Markdown'
        )
    
    async def handle_video(self, update: Update, context):
        """Handler per i video ricevuti"""
        user_id = update.effective_user.id
        video = update.message.video
        caption = update.message.caption or ""
        
        self.db_manager.log_command_usage(user_id, 'video_received')
        
        duration_min = video.duration // 60
        duration_sec = video.duration % 60
        
        await update.message.reply_text(
            f"🎥 *Video ricevuto!*\n\n"
            f"⏱️ Durata: {duration_min}:{duration_sec:02d}\n"
            f"📏 Dimensioni: {video.width}x{video.height}\n"
            f"💾 Dimensione: {video.file_size} bytes\n"
            f"📝 Didascalia: {caption if caption else 'Nessuna didascalia'}\n\n"
            f"✅ Video processato con successo!",
            parse_mode='Markdown'
        )
    
    async def handle_audio(self, update: Update, context):
        """Handler per i file audio ricevuti"""
        user_id = update.effective_user.id
        audio = update.message.audio or update.message.voice
        
        self.db_manager.log_command_usage(user_id, 'audio_received')
        
        if update.message.audio:
            # File audio normale
            duration_min = audio.duration // 60
            duration_sec = audio.duration % 60
            title = audio.title or "Sconosciuto"
            performer = audio.performer or "Sconosciuto"
            
            await update.message.reply_text(
                f"🎵 *File Audio ricevuto!*\n\n"
                f"🎼 Titolo: {title}\n"
                f"🎤 Artista: {performer}\n"
                f"⏱️ Durata: {duration_min}:{duration_sec:02d}\n"
                f"💾 Dimensione: {audio.file_size} bytes\n\n"
                f"✅ Audio processato con successo!",
                parse_mode='Markdown'
            )
        else:
            # Messaggio vocale
            duration_min = audio.duration // 60
            duration_sec = audio.duration % 60
            
            await update.message.reply_text(
                f"🎙️ *Messaggio Vocale ricevuto!*\n\n"
                f"⏱️ Durata: {duration_min}:{duration_sec:02d}\n"
                f"💾 Dimensione: {audio.file_size} bytes\n\n"
                f"✅ Messaggio vocale processato con successo!",
                parse_mode='Markdown'
            )
    
    async def handle_document(self, update: Update, context):
        """Handler per i documenti ricevuti"""
        user_id = update.effective_user.id
        document = update.message.document
        
        self.db_manager.log_command_usage(user_id, 'document_received')
        
        file_size_mb = document.file_size / (1024 * 1024)
        
        await update.message.reply_text(
            f"📄 *Documento ricevuto!*\n\n"
            f"📁 Nome: {document.file_name}\n"
            f"📋 Tipo MIME: {document.mime_type}\n"
            f"💾 Dimensione: {file_size_mb:.2f} MB\n\n"
            f"✅ Documento processato con successo!",
            parse_mode='Markdown'
        )
    
    async def handle_sticker(self, update: Update, context):
        """Handler per gli sticker ricevuti"""
        user_id = update.effective_user.id
        sticker = update.message.sticker
        
        self.db_manager.log_command_usage(user_id, 'sticker_received')
        
        await update.message.reply_text(
            f"🎭 *Sticker ricevuto!*\n\n"
            f"😊 Emoji: {sticker.emoji or 'Nessuna emoji'}\n"
            f"📦 Set: {sticker.set_name or 'Set sconosciuto'}\n"
            f"📏 Dimensioni: {sticker.width}x{sticker.height}\n\n"
            f"✅ Sticker processato con successo!",
            parse_mode='Markdown'
        )
    
    async def error_handler(self, update: Update, context):
        """Handler per gli errori"""
        logger.error(f"Errore durante l'aggiornamento {update}: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Si è verificato un errore. Il team di sviluppo è stato notificato.\n"
                "Riprova più tardi o contatta il supporto se il problema persiste."
            )
    
    async def start_bot(self):
        """Avvia il bot"""
        if not self.config.TELEGRAM_BOT_TOKEN:
            logger.error("Token del bot non configurato! Controlla il file .env")
            return
        
        # Crea l'applicazione
        self.application = Application.builder().token(self.config.TELEGRAM_BOT_TOKEN).build()
        
        # Configura gli handler
        self.setup_handlers()
        
        logger.info("🤖 Bot Telegram avviato correttamente!")
        logger.info(f"📊 Database: {self.config.DATABASE_PATH}")
        logger.info(f"👤 Admin ID: {self.config.ADMIN_USER_ID}")
        
        # Avvia il bot
        await self.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    
    def run(self):
        """Metodo per avviare il bot in modo sincrono"""
        try:
            asyncio.run(self.start_bot())
        except KeyboardInterrupt:
            logger.info("🛑 Bot fermato dall'utente")
        except Exception as e:
            logger.error(f"❌ Errore critico: {e}")

def main():
    """Funzione principale"""
    print("🚀 Avvio Bot Telegram Personalizzato...")
    print("=" * 50)
    
    # Controlla se il token è configurato
    config = Config()
    if not config.TELEGRAM_BOT_TOKEN:
        print("❌ ERRORE: Token del bot non configurato!")
        print("1. Copia il file .env.example in .env")
        print("2. Ottieni il token da @BotFather su Telegram")
        print("3. Inserisci il token nel file .env")
        print("4. Inserisci il tuo user ID nel file .env")
        return
    
    # Avvia il bot
    bot = TelegramBot()
    bot.run()

if __name__ == "__main__":
    main()
