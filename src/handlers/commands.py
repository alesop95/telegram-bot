"""
Handler per i comandi del bot Telegram
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from src.database.sqlite_manager import DatabaseManager
from src.config.settings import Config

class BotHandlers:
    """Classe che contiene tutti gli handler per i comandi del bot"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.config = Config()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per il comando /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Salva l'utente nel database
        user_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'language_code': user.language_code,
            'is_bot': user.is_bot,
            'is_premium': getattr(user, 'is_premium', False)
        }
        
        self.db.add_user(user_data)
        self.db.log_command_usage(user.id, '/start')
        
        # Keyboard di benvenuto
        keyboard = [
            [KeyboardButton("📝 Messaggi Personalizzati"), KeyboardButton("🎨 Temi Chat")],
            [KeyboardButton("📸 Multimedia"), KeyboardButton("⚙️ Impostazioni")],
            [KeyboardButton("📊 Le Mie Statistiche"), KeyboardButton("❓ Aiuto")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            self.config.WELCOME_MESSAGE,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per il comando /help"""
        user_id = update.effective_user.id
        self.db.log_command_usage(user_id, '/help')
        
        await update.message.reply_text(
            self.config.HELP_MESSAGE,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def custom_message_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per creare messaggi personalizzati"""
        user_id = update.effective_user.id
        self.db.log_command_usage(user_id, '/custom')
        
        keyboard = [
            [InlineKeyboardButton("✨ Testo Formattato", callback_data="custom_formatted")],
            [InlineKeyboardButton("🎯 Con Bottoni", callback_data="custom_buttons")],
            [InlineKeyboardButton("📋 Da Template", callback_data="custom_template")],
            [InlineKeyboardButton("💾 Salva Template", callback_data="custom_save")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎨 *Crea il tuo messaggio personalizzato:*\n\n"
            "Scegli il tipo di messaggio che vuoi creare:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def theme_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per la personalizzazione temi"""
        user_id = update.effective_user.id
        self.db.log_command_usage(user_id, '/theme')
        
        current_settings = self.db.get_user_settings(user_id)
        current_theme = current_settings.get('theme', 'default') if current_settings else 'default'
        
        keyboard = [
            [InlineKeyboardButton("🌟 Default", callback_data="theme_default")],
            [InlineKeyboardButton("🌙 Dark Mode", callback_data="theme_dark")],
            [InlineKeyboardButton("🌈 Colorful", callback_data="theme_colorful")],
            [InlineKeyboardButton("💼 Professional", callback_data="theme_professional")],
            [InlineKeyboardButton("🎮 Gaming", callback_data="theme_gaming")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🎨 *Personalizzazione Tema Chat*\n\n"
            f"Tema attuale: *{current_theme.title()}*\n\n"
            f"Scegli un nuovo tema per personalizzare l'esperienza:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def multimedia_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per contenuti multimediali"""
        user_id = update.effective_user.id
        self.db.log_command_usage(user_id, '/multimedia')
        
        keyboard = [
            [InlineKeyboardButton("📸 Foto con Didascalia", callback_data="media_photo")],
            [InlineKeyboardButton("🎥 Video", callback_data="media_video")],
            [InlineKeyboardButton("🎵 Audio", callback_data="media_audio")],
            [InlineKeyboardButton("📄 Documento", callback_data="media_document")],
            [InlineKeyboardButton("🎭 Sticker", callback_data="media_sticker")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📱 *Gestione Contenuti Multimediali*\n\n"
            "Scegli il tipo di contenuto da gestire:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def templates_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per gestire i template"""
        user_id = update.effective_user.id
        self.db.log_command_usage(user_id, '/templates')
        
        templates = self.db.get_user_templates(user_id)
        
        if not templates:
            keyboard = [[InlineKeyboardButton("➕ Crea Primo Template", callback_data="template_create")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📋 *I Tuoi Template*\n\n"
                "Non hai ancora creato nessun template.\n"
                "I template ti permettono di salvare messaggi riutilizzabili!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            keyboard = []
            message_text = "📋 *I Tuoi Template:*\n\n"
            
            for i, template in enumerate(templates[:10]):  # Mostra max 10 template
                keyboard.append([InlineKeyboardButton(
                    f"{template['name']} ({template['usage_count']} usi)",
                    callback_data=f"template_use_{template['id']}"
                )])
                message_text += f"• *{template['name']}*\n"
            
            keyboard.append([InlineKeyboardButton("➕ Nuovo Template", callback_data="template_create")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per le impostazioni"""
        user_id = update.effective_user.id
        self.db.log_command_usage(user_id, '/settings')
        
        settings = self.db.get_user_settings(user_id)
        
        keyboard = [
            [InlineKeyboardButton("🎨 Tema", callback_data="settings_theme")],
            [InlineKeyboardButton("🔔 Notifiche", callback_data="settings_notifications")],
            [InlineKeyboardButton("🌍 Lingua", callback_data="settings_language")],
            [InlineKeyboardButton("⏰ Fuso Orario", callback_data="settings_timezone")],
            [InlineKeyboardButton("🔄 Reset Impostazioni", callback_data="settings_reset")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if settings:
            settings_text = f"""
⚙️ *Le Tue Impostazioni:*

🎨 Tema: *{settings['theme'].title()}*
🔔 Notifiche: *{'Attive' if settings['notifications'] else 'Disattivate'}*
🌍 Lingua: *{settings['language'].upper()}*
⏰ Fuso Orario: *{settings['timezone']}*
            """
        else:
            settings_text = "⚙️ *Impostazioni non trovate*\nVerranno create le impostazioni di default."
        
        await update.message.reply_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per le statistiche utente"""
        user_id = update.effective_user.id
        self.db.log_command_usage(user_id, '/stats')
        
        # Se è l'admin, mostra statistiche globali
        if user_id == self.config.ADMIN_USER_ID:
            stats = self.db.get_bot_stats()
            
            stats_text = f"""
📊 *Statistiche Bot (Admin):*

👥 Utenti Totali: *{stats['total_users']}*
🟢 Attivi Oggi: *{stats['active_today']}*

📈 *Comandi Più Usati (7 giorni):*
            """
            
            for cmd in stats['top_commands']:
                stats_text += f"• `{cmd['command']}`: {cmd['count']} volte\n"
            
        else:
            # Statistiche personali dell'utente
            templates = self.db.get_user_templates(user_id)
            total_templates = len(templates)
            total_usage = sum(t['usage_count'] for t in templates)
            
            stats_text = f"""
📊 *Le Tue Statistiche:*

📋 Template Creati: *{total_templates}*
🔄 Utilizzi Totali: *{total_usage}*
📅 Membro dal: *{datetime.now().strftime('%d/%m/%Y')}*

💡 *Suggerimento:* Crea più template per velocizzare i tuoi messaggi!
            """
        
        await update.message.reply_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per i callback dei bottoni inline"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data.startswith('theme_'):
            await self.handle_theme_selection(query, context)
        elif data.startswith('custom_'):
            await self.handle_custom_message(query, context)
        elif data.startswith('media_'):
            await self.handle_media_selection(query, context)
        elif data.startswith('template_'):
            await self.handle_template_action(query, context)
        elif data.startswith('settings_'):
            await self.handle_settings_action(query, context)
    
    async def handle_theme_selection(self, query, context):
        """Gestisce la selezione del tema"""
        user_id = query.from_user.id
        theme = query.data.replace('theme_', '')
        
        success = self.db.update_user_settings(user_id, {'theme': theme})
        
        if success:
            theme_messages = {
                'default': "🌟 Tema Default attivato! Esperienza classica e pulita.",
                'dark': "🌙 Dark Mode attivato! Perfetto per l'uso notturno.",
                'colorful': "🌈 Tema Colorful attivato! Più vivace e allegro.",
                'professional': "💼 Tema Professional attivato! Elegante e formale.",
                'gaming': "🎮 Tema Gaming attivato! Per i veri gamer!"
            }
            
            await query.edit_message_text(
                f"✅ *Tema Aggiornato!*\n\n{theme_messages.get(theme, 'Tema applicato con successo!')}",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                "❌ Errore nell'aggiornamento del tema. Riprova più tardi.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_custom_message(self, query, context):
        """Gestisce la creazione di messaggi personalizzati"""
        action = query.data.replace('custom_', '')
        
        if action == 'formatted':
            await query.edit_message_text(
                "✨ *Messaggio Formattato*\n\n"
                "Invia il tuo messaggio usando la formattazione Markdown:\n\n"
                "• `*testo*` per il **grassetto**\n"
                "• `_testo_` per il _corsivo_\n"
                "• `` `testo` `` per il `codice`\n"
                "• `[link](url)` per i [collegamenti](https://telegram.org)\n\n"
                "Esempio: `*Ciao!* _Come stai?_ Visita [Telegram](https://telegram.org)`",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif action == 'buttons':
            keyboard = [
                [InlineKeyboardButton("👍 Mi Piace", callback_data="demo_like")],
                [InlineKeyboardButton("👎 Non Mi Piace", callback_data="demo_dislike")],
                [InlineKeyboardButton("🔗 Vai al Sito", url="https://telegram.org")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🎯 *Messaggio con Bottoni*\n\n"
                "Ecco un esempio di messaggio con bottoni interattivi!\n"
                "Puoi creare bottoni per:\n"
                "• Azioni rapide\n"
                "• Collegamenti esterni\n"
                "• Menu di navigazione",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    
    async def handle_media_selection(self, query, context):
        """Gestisce la selezione dei media"""
        media_type = query.data.replace('media_', '')
        
        instructions = {
            'photo': "📸 *Invio Foto*\n\nInvia una foto e aggiungi una didascalia personalizzata.\nPuoi usare la formattazione Markdown nella didascalia!",
            'video': "🎥 *Invio Video*\n\nInvia un video (max 50MB) con didascalia opzionale.\nSupporta tutti i formati video comuni.",
            'audio': "🎵 *Invio Audio*\n\nInvia file audio o registrazioni vocali.\nPerfetto per podcast o messaggi vocali personalizzati.",
            'document': "📄 *Invio Documento*\n\nInvia qualsiasi tipo di file (max 2GB).\nPDF, Word, Excel, ZIP e molto altro!",
            'sticker': "🎭 *Gestione Sticker*\n\nInvia sticker personalizzati o usa quelli esistenti.\nPuoi anche creare i tuoi pacchetti sticker!"
        }
        
        await query.edit_message_text(
            instructions.get(media_type, "Tipo di media non riconosciuto."),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_template_action(self, query, context):
        """Gestisce le azioni sui template"""
        action_data = query.data.replace('template_', '')
        
        if action_data == 'create':
            await query.edit_message_text(
                "📝 *Crea Nuovo Template*\n\n"
                "Per creare un template, invia un messaggio nel formato:\n\n"
                "`/save_template nome_template`\n"
                "`Il contenuto del tuo template qui`\n\n"
                "Esempio:\n"
                "`/save_template saluto`\n"
                "`Ciao! Come stai oggi? 😊`",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif action_data.startswith('use_'):
            template_id = int(action_data.replace('use_', ''))
            # Qui implementeresti la logica per usare il template
            await query.edit_message_text(
                f"✅ Template #{template_id} utilizzato!\n\n"
                "Il contenuto del template è stato preparato per l'invio.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_settings_action(self, query, context):
        """Gestisce le azioni delle impostazioni"""
        setting = query.data.replace('settings_', '')
        
        if setting == 'notifications':
            user_id = query.from_user.id
            current_settings = self.db.get_user_settings(user_id)
            current_notifications = current_settings.get('notifications', True) if current_settings else True
            
            new_notifications = not current_notifications
            success = self.db.update_user_settings(user_id, {'notifications': new_notifications})
            
            if success:
                status = "attivate" if new_notifications else "disattivate"
                await query.edit_message_text(
                    f"🔔 Notifiche {status} con successo!",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.edit_message_text(
                    "❌ Errore nell'aggiornamento delle notifiche.",
                    parse_mode=ParseMode.MARKDOWN
                )
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler per messaggi di testo generici"""
        text = update.message.text
        user_id = update.effective_user.id
        
        # Gestisce i bottoni della keyboard principale
        if text == "📝 Messaggi Personalizzati":
            await self.custom_message_command(update, context)
        elif text == "🎨 Temi Chat":
            await self.theme_command(update, context)
        elif text == "📸 Multimedia":
            await self.multimedia_command(update, context)
        elif text == "⚙️ Impostazioni":
            await self.settings_command(update, context)
        elif text == "📊 Le Mie Statistiche":
            await self.stats_command(update, context)
        elif text == "❓ Aiuto":
            await self.help_command(update, context)
        else:
            # Messaggio generico di risposta
            await update.message.reply_text(
                "🤖 Messaggio ricevuto! Usa i bottoni del menu o i comandi per interagire con il bot.\n\n"
                "Digita /help per vedere tutti i comandi disponibili.",
                parse_mode=ParseMode.MARKDOWN
            )
