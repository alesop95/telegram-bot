"""
Utility functions per il bot Telegram
"""
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

class MessageFormatter:
    """Classe per formattare messaggi con stili personalizzati"""
    
    @staticmethod
    def format_with_theme(message: str, theme: str = 'default') -> str:
        """Applica uno stile basato sul tema selezionato"""
        
        theme_styles = {
            'default': {
                'prefix': '🤖',
                'accent': '•',
                'separator': '─' * 30
            },
            'dark': {
                'prefix': '🌙',
                'accent': '▪',
                'separator': '━' * 30
            },
            'colorful': {
                'prefix': '🌈',
                'accent': '🔸',
                'separator': '🔹' * 15
            },
            'professional': {
                'prefix': '💼',
                'accent': '▫',
                'separator': '▬' * 30
            },
            'gaming': {
                'prefix': '🎮',
                'accent': '⚡',
                'separator': '═' * 30
            }
        }
        
        style = theme_styles.get(theme, theme_styles['default'])
        
        # Applica lo stile al messaggio
        formatted_message = f"{style['prefix']} {message}"
        
        # Sostituisce i bullet point con l'accento del tema
        formatted_message = formatted_message.replace('•', style['accent'])
        
        return formatted_message
    
    @staticmethod
    def create_progress_bar(percentage: int, length: int = 20) -> str:
        """Crea una barra di progresso testuale"""
        filled = int(length * percentage / 100)
        bar = '█' * filled + '░' * (length - filled)
        return f"[{bar}] {percentage}%"
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Formatta la dimensione del file in modo leggibile"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Formatta la durata in formato leggibile"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            seconds = seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"

class KeyboardBuilder:
    """Classe per costruire keyboard personalizzate"""
    
    @staticmethod
    def create_inline_keyboard(buttons: List[Dict[str, str]], columns: int = 2) -> InlineKeyboardMarkup:
        """Crea una keyboard inline con il numero specificato di colonne"""
        keyboard = []
        row = []
        
        for i, button in enumerate(buttons):
            row.append(InlineKeyboardButton(
                text=button['text'],
                callback_data=button.get('callback_data'),
                url=button.get('url')
            ))
            
            if len(row) == columns or i == len(buttons) - 1:
                keyboard.append(row)
                row = []
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_pagination_keyboard(current_page: int, total_pages: int, prefix: str = "page") -> InlineKeyboardMarkup:
        """Crea una keyboard per la paginazione"""
        keyboard = []
        
        # Prima riga: navigazione pagine
        nav_row = []
        if current_page > 1:
            nav_row.append(InlineKeyboardButton("⬅️ Precedente", callback_data=f"{prefix}_{current_page-1}"))
        
        nav_row.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="current_page"))
        
        if current_page < total_pages:
            nav_row.append(InlineKeyboardButton("Successiva ➡️", callback_data=f"{prefix}_{current_page+1}"))
        
        keyboard.append(nav_row)
        
        # Seconda riga: vai a prima/ultima pagina
        if total_pages > 2:
            jump_row = []
            if current_page > 2:
                jump_row.append(InlineKeyboardButton("⏮️ Prima", callback_data=f"{prefix}_1"))
            if current_page < total_pages - 1:
                jump_row.append(InlineKeyboardButton("Ultima ⏭️", callback_data=f"{prefix}_{total_pages}"))
            
            if jump_row:
                keyboard.append(jump_row)
        
        return InlineKeyboardMarkup(keyboard)

class TextValidator:
    """Classe per validare e pulire il testo"""
    
    @staticmethod
    def clean_markdown(text: str) -> str:
        """Pulisce il testo da markdown non valido"""
        # Rimuove markdown malformato
        text = re.sub(r'\*{3,}', '**', text)  # Troppi asterischi
        text = re.sub(r'_{3,}', '__', text)   # Troppi underscore
        text = re.sub(r'`{3,}', '```', text)  # Troppi backtick
        
        return text
    
    @staticmethod
    def validate_template_name(name: str) -> tuple[bool, str]:
        """Valida il nome di un template"""
        if not name:
            return False, "Il nome del template non può essere vuoto"
        
        if len(name) > 50:
            return False, "Il nome del template non può superare i 50 caratteri"
        
        if not re.match(r'^[a-zA-Z0-9_\s]+$', name):
            return False, "Il nome può contenere solo lettere, numeri, underscore e spazi"
        
        return True, ""
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 4000) -> str:
        """Tronca il testo se supera la lunghezza massima"""
        if len(text) <= max_length:
            return text
        
        return text[:max_length-3] + "..."

class DateTimeHelper:
    """Classe per gestire date e orari"""
    
    @staticmethod
    def format_timestamp(timestamp: datetime, format_type: str = 'full') -> str:
        """Formatta un timestamp in base al tipo richiesto"""
        formats = {
            'full': '%d/%m/%Y %H:%M:%S',
            'date': '%d/%m/%Y',
            'time': '%H:%M',
            'datetime': '%d/%m/%Y %H:%M',
            'relative': None  # Gestito separatamente
        }
        
        if format_type == 'relative':
            return DateTimeHelper.get_relative_time(timestamp)
        
        return timestamp.strftime(formats.get(format_type, formats['full']))
    
    @staticmethod
    def get_relative_time(timestamp: datetime) -> str:
        """Restituisce il tempo relativo (es. '2 ore fa')"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} giorni fa"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} ore fa"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minuti fa"
        else:
            return "Ora"
    
    @staticmethod
    def parse_schedule_time(time_str: str) -> Optional[datetime]:
        """Analizza una stringa di tempo per la programmazione"""
        try:
            # Formati supportati: HH:MM, DD/MM HH:MM, DD/MM/YYYY HH:MM
            now = datetime.now()
            
            if ':' in time_str and '/' not in time_str:
                # Solo orario (oggi)
                time_part = datetime.strptime(time_str, '%H:%M').time()
                scheduled_time = datetime.combine(now.date(), time_part)
                
                # Se l'orario è già passato oggi, programma per domani
                if scheduled_time <= now:
                    scheduled_time += timedelta(days=1)
                
                return scheduled_time
            
            elif time_str.count('/') == 1:
                # Giorno/mese orario
                scheduled_time = datetime.strptime(f"{time_str}/{now.year}", '%d/%m/%Y %H:%M')
                
                # Se la data è già passata, programma per l'anno prossimo
                if scheduled_time <= now:
                    scheduled_time = scheduled_time.replace(year=now.year + 1)
                
                return scheduled_time
            
            elif time_str.count('/') == 2:
                # Data completa
                return datetime.strptime(time_str, '%d/%m/%Y %H:%M')
            
        except ValueError:
            pass
        
        return None

class ConfigManager:
    """Classe per gestire configurazioni personalizzate"""
    
    @staticmethod
    def load_user_config(config_str: Optional[str]) -> Dict[str, Any]:
        """Carica la configurazione personalizzata di un utente"""
        if not config_str:
            return {}
        
        try:
            return json.loads(config_str)
        except json.JSONDecodeError:
            logger.warning(f"Configurazione utente non valida: {config_str}")
            return {}
    
    @staticmethod
    def save_user_config(config: Dict[str, Any]) -> str:
        """Salva la configurazione personalizzata di un utente"""
        try:
            return json.dumps(config, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            logger.error(f"Errore nel salvataggio configurazione: {e}")
            return "{}"
    
    @staticmethod
    def merge_configs(default_config: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Unisce la configurazione di default con quella dell'utente"""
        merged = default_config.copy()
        merged.update(user_config)
        return merged

class SecurityHelper:
    """Classe per funzioni di sicurezza"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Pulisce un nome file da caratteri pericolosi"""
        # Rimuove caratteri non sicuri
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Rimuove spazi multipli e li sostituisce con underscore
        filename = re.sub(r'\s+', '_', filename)
        
        # Limita la lunghezza
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:95] + ('.' + ext if ext else '')
        
        return filename
    
    @staticmethod
    def is_admin(user_id: int, admin_ids: List[int]) -> bool:
        """Controlla se un utente è amministratore"""
        return user_id in admin_ids
    
    @staticmethod
    def rate_limit_check(user_id: int, command: str, limit_per_minute: int = 10) -> bool:
        """Controlla il rate limiting per un utente (implementazione semplificata)"""
        # Questa è una implementazione base
        # In produzione dovresti usare Redis o un sistema più robusto
        return True  # Per ora sempre True

class StatsCalculator:
    """Classe per calcolare statistiche"""
    
    @staticmethod
    def calculate_usage_stats(templates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcola statistiche di utilizzo dei template"""
        if not templates:
            return {
                'total_templates': 0,
                'total_usage': 0,
                'average_usage': 0,
                'most_used': None
            }
        
        total_templates = len(templates)
        total_usage = sum(t.get('usage_count', 0) for t in templates)
        average_usage = total_usage / total_templates if total_templates > 0 else 0
        most_used = max(templates, key=lambda t: t.get('usage_count', 0))
        
        return {
            'total_templates': total_templates,
            'total_usage': total_usage,
            'average_usage': round(average_usage, 2),
            'most_used': most_used
        }
    
    @staticmethod
    def get_activity_summary(user_activity: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcola un riassunto dell'attività dell'utente"""
        if not user_activity:
            return {
                'total_commands': 0,
                'unique_commands': 0,
                'most_used_command': None,
                'activity_by_day': {}
            }
        
        total_commands = len(user_activity)
        unique_commands = len(set(activity.get('command', '') for activity in user_activity))
        
        # Comando più usato
        command_counts = {}
        for activity in user_activity:
            cmd = activity.get('command', '')
            command_counts[cmd] = command_counts.get(cmd, 0) + 1
        
        most_used_command = max(command_counts.items(), key=lambda x: x[1]) if command_counts else None
        
        # Attività per giorno
        activity_by_day = {}
        for activity in user_activity:
            timestamp = activity.get('timestamp', '')
            if timestamp:
                try:
                    date = datetime.fromisoformat(timestamp).date()
                    day_str = date.strftime('%Y-%m-%d')
                    activity_by_day[day_str] = activity_by_day.get(day_str, 0) + 1
                except (ValueError, AttributeError):
                    continue
        
        return {
            'total_commands': total_commands,
            'unique_commands': unique_commands,
            'most_used_command': most_used_command,
            'activity_by_day': activity_by_day
        }
