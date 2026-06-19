"""
Bot Telegram Personalizzato - Versione Cloud
Ottimizzato per deployment su Railway, Render, Heroku
"""
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from src.config.settings import Config
from src.database.postgres_manager import PostgreSQLManager
from src.handlers.commands import BotHandlers
from src.utils.health_server import HealthServer, record_request, record_active_user
import time

# Configurazione logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()  # Solo console per cloud
    ]
)
logger = logging.getLogger(__name__)

class CloudTelegramBot:
    """Classe principale del bot per deployment cloud"""
    
    def __init__(self):
        self.config = Config()
        self.db_manager = None
        self.handlers = None
        self.application = None
        self.health_server = None
        
        # Configurazione cloud
        self.database_url = os.getenv('DATABASE_URL')
        self.port = int(os.getenv('PORT', 8000))
        self.environment = os.getenv('ENVIRONMENT', 'development')
    
    async def init_database(self):
        """Inizializza il database PostgreSQL"""
        if not self.database_url:
            # Fallback per sviluppo locale
            self.database_url = f"postgresql://botuser:secure_password_123@localhost:5432/telegram_bot"
            logger.warning("DATABASE_URL non trovato, uso database locale")
        
        try:
            self.db_manager = PostgreSQLManager(self.database_url)
            await self.db_manager.init_pool()
            self.handlers = BotHandlers(self.db_manager)
            logger.info("Database PostgreSQL inizializzato correttamente")
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione database: {e}")
            raise
    
    def setup_handlers(self):
        """Configura tutti gli handler del bot con metriche"""
        if not self.application or not self.handlers:
            logger.error("Application o handlers non inizializzati")
            return
        
        # Wrapper per aggiungere metriche agli handler
        async def handler_with_metrics(handler_func, command_name):
            async def wrapper(update: Update, context):
                start_time = time.time()
                success = True
                try:
                    record_active_user()
                    await handler_func(update, context)
                except Exception as e:
                    success = False
                    logger.error(f"Errore in {command_name}: {e}")
                    raise
                finally:
                    duration = time.time() - start_time
                    record_request(command_name, success, duration)
            return wrapper
        
        # Handler per comandi con metriche
        commands = [
            ("start", self.handlers.start_command),
            ("help", self.handlers.help_command),
            ("custom", self.handlers.custom_message_command),
            ("theme", self.handlers.theme_command),
            ("multimedia", self.handlers.multimedia_command),
            ("templates", self.handlers.templates_command),
            ("settings", self.handlers.settings_command),
            ("stats", self.handlers.stats_command)
        ]
        
        for cmd_name, handler in commands:
            wrapped_handler = handler_with_metrics(handler, f"/{cmd_name}")
            self.application.add_handler(CommandHandler(cmd_name, wrapped_handler))
        
        # Altri handler
        self.application.add_handler(CallbackQueryHandler(
            handler_with_metrics(self.handlers.button_callback, "callback_query")
        ))
        
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handler_with_metrics(self.handlers.handle_text_message, "text_message")
        ))
        
        # Handler per contenuti multimediali
        media_handlers = [
            (filters.PHOTO, self.handle_photo, "photo"),
            (filters.VIDEO, self.handle_video, "video"),
            (filters.AUDIO, self.handle_audio, "audio"),
            (filters.DOCUMENT, self.handle_document, "document"),
            (filters.STICKER, self.handle_sticker, "sticker")
        ]
        
        for filter_type, handler, name in media_handlers:
            self.application.add_handler(MessageHandler(
                filter_type,
                handler_with_metrics(handler, name)
            ))
        
        # Handler per errori
        self.application.add_error_handler(self.error_handler)
        
        logger.info("Tutti gli handler configurati con metriche")
    
    async def handle_photo(self, update: Update, context):
        """Handler per le foto ricevute"""
        user_id = update.effective_user.id
        photo = update.message.photo[-1]
        caption = update.message.caption or ""
        
        await self.db_manager.log_command_usage(user_id, 'photo_received')
        
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
        
        await self.db_manager.log_command_usage(user_id, 'video_received')
        
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
        
        await self.db_manager.log_command_usage(user_id, 'audio_received')
        
        if update.message.audio:
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
        
        await self.db_manager.log_command_usage(user_id, 'document_received')
        
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
        
        await self.db_manager.log_command_usage(user_id, 'sticker_received')
        
        await update.message.reply_text(
            f"🎭 *Sticker ricevuto!*\n\n"
            f"😊 Emoji: {sticker.emoji or 'Nessuna emoji'}\n"
            f"📦 Set: {sticker.set_name or 'Set sconosciuto'}\n"
            f"📏 Dimensioni: {sticker.width}x{sticker.height}\n\n"
            f"✅ Sticker processato con successo!",
            parse_mode='Markdown'
        )
    
    async def error_handler(self, update: Update, context):
        """Handler per gli errori con logging avanzato"""
        error_msg = f"Errore durante l'aggiornamento {update}: {context.error}"
        logger.error(error_msg)
        
        # Log errore nel database
        if update and update.effective_user and self.db_manager:
            try:
                await self.db_manager.log_command_usage(
                    update.effective_user.id, 
                    "error", 
                    success=False,
                    metadata={"error": str(context.error)}
                )
            except Exception as e:
                logger.error(f"Errore nel logging dell'errore: {e}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Si è verificato un errore. Il team di sviluppo è stato notificato.\n"
                "Riprova più tardi o contatta il supporto se il problema persiste."
            )
    
    async def start_health_server(self):
        """Avvia il server per health checks"""
        try:
            self.health_server = HealthServer(self)
            # Avvia il server in background
            asyncio.create_task(
                self.health_server.start_server(host="0.0.0.0", port=self.port)
            )
            logger.info(f"Health server avviato sulla porta {self.port}")
        except Exception as e:
            logger.error(f"Errore nell'avvio health server: {e}")
    
    async def cleanup_task(self):
        """Task di pulizia periodica"""
        while True:
            try:
                await asyncio.sleep(24 * 3600)  # Ogni 24 ore
                if self.db_manager:
                    await self.db_manager.cleanup_old_data(days_to_keep=30)
                    logger.info("Cleanup periodico completato")
            except Exception as e:
                logger.error(f"Errore nel cleanup periodico: {e}")
    
    async def start_bot(self):
        """Avvia il bot in modalità cloud"""
        if not self.config.TELEGRAM_BOT_TOKEN:
            logger.error("Token del bot non configurato!")
            return
        
        try:
            # Inizializza database
            await self.init_database()
            
            # Crea l'applicazione
            self.application = Application.builder().token(self.config.TELEGRAM_BOT_TOKEN).build()
            
            # Configura gli handler
            self.setup_handlers()
            
            # Avvia health server
            await self.start_health_server()
            
            # Avvia task di cleanup
            asyncio.create_task(self.cleanup_task())
            
            logger.info("🤖 Bot Telegram Cloud avviato correttamente!")
            logger.info(f"🌍 Ambiente: {self.environment}")
            logger.info(f"📊 Database: PostgreSQL")
            logger.info(f"🔍 Health check: http://localhost:{self.port}/health")
            logger.info(f"👤 Admin ID: {self.config.ADMIN_USER_ID}")
            
            # Avvia il bot
            if self.environment == 'production' and os.getenv('WEBHOOK_URL'):
                # Modalità webhook per produzione
                webhook_url = os.getenv('WEBHOOK_URL')
                await self.application.bot.set_webhook(url=webhook_url)
                logger.info(f"Webhook configurato: {webhook_url}")
            else:
                # Modalità polling
                await self.application.run_polling(
                    allowed_updates=Update.ALL_TYPES,
                    drop_pending_updates=True
                )
                
        except Exception as e:
            logger.error(f"Errore critico nell'avvio del bot: {e}")
            raise
        finally:
            # Cleanup
            if self.db_manager:
                await self.db_manager.close_pool()
    
    def run(self):
        """Metodo per avviare il bot in modo sincrono"""
        try:
            asyncio.run(self.start_bot())
        except KeyboardInterrupt:
            logger.info("🛑 Bot fermato dall'utente")
        except Exception as e:
            logger.error(f"❌ Errore critico: {e}")

def main():
    """Funzione principale per cloud deployment"""
    print("🚀 Avvio Bot Telegram Cloud...")
    print("=" * 50)
    
    # Controlla configurazione
    config = Config()
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN non configurato!")
        return
    
    if not os.getenv('DATABASE_URL'):
        logger.warning("⚠️ DATABASE_URL non configurato, uso database locale")
    
    # Avvia il bot
    bot = CloudTelegramBot()
    bot.run()

if __name__ == "__main__":
    main()
