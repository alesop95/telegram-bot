"""
Gestione del database SQLite per il bot Telegram
"""
import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

class DatabaseManager:
    """Classe per gestire il database del bot"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inizializza il database con le tabelle necessarie"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabella utenti
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        language_code TEXT,
                        is_bot BOOLEAN DEFAULT FALSE,
                        is_premium BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                ''')
                
                # Tabella impostazioni utente
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_settings (
                        user_id INTEGER PRIMARY KEY,
                        theme TEXT DEFAULT 'default',
                        notifications BOOLEAN DEFAULT TRUE,
                        language TEXT DEFAULT 'it',
                        timezone TEXT DEFAULT 'Europe/Rome',
                        custom_settings TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Tabella template messaggi
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS message_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        name TEXT NOT NULL,
                        content TEXT NOT NULL,
                        message_type TEXT DEFAULT 'text',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        usage_count INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Tabella messaggi programmati
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scheduled_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        chat_id INTEGER,
                        message_content TEXT NOT NULL,
                        message_type TEXT DEFAULT 'text',
                        scheduled_time TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        sent BOOLEAN DEFAULT FALSE,
                        sent_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Tabella statistiche
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bot_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        command TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        success BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logging.info("Database inizializzato correttamente")
                
        except sqlite3.Error as e:
            logging.error(f"Errore nell'inizializzazione del database: {e}")
    
    def add_user(self, user_data: Dict[str, Any]) -> bool:
        """Aggiunge o aggiorna un utente nel database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, language_code, is_bot, is_premium, last_activity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_data.get('id'),
                    user_data.get('username'),
                    user_data.get('first_name'),
                    user_data.get('last_name'),
                    user_data.get('language_code'),
                    user_data.get('is_bot', False),
                    user_data.get('is_premium', False),
                    datetime.now()
                ))
                
                # Crea impostazioni di default se non esistono
                cursor.execute('''
                    INSERT OR IGNORE INTO user_settings (user_id)
                    VALUES (?)
                ''', (user_data.get('id'),))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logging.error(f"Errore nell'aggiunta dell'utente: {e}")
            return False
    
    def get_user_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Recupera le impostazioni di un utente"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT theme, notifications, language, timezone, custom_settings
                    FROM user_settings WHERE user_id = ?
                ''', (user_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'theme': result[0],
                        'notifications': result[1],
                        'language': result[2],
                        'timezone': result[3],
                        'custom_settings': result[4]
                    }
                return None
                
        except sqlite3.Error as e:
            logging.error(f"Errore nel recupero impostazioni utente: {e}")
            return None
    
    def update_user_settings(self, user_id: int, settings: Dict[str, Any]) -> bool:
        """Aggiorna le impostazioni di un utente"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Costruisce la query dinamicamente basata sui settings forniti
                set_clause = []
                values = []
                
                for key, value in settings.items():
                    if key in ['theme', 'notifications', 'language', 'timezone', 'custom_settings']:
                        set_clause.append(f"{key} = ?")
                        values.append(value)
                
                if set_clause:
                    values.append(user_id)
                    query = f"UPDATE user_settings SET {', '.join(set_clause)} WHERE user_id = ?"
                    cursor.execute(query, values)
                    conn.commit()
                    return True
                
                return False
                
        except sqlite3.Error as e:
            logging.error(f"Errore nell'aggiornamento impostazioni: {e}")
            return False
    
    def save_message_template(self, user_id: int, name: str, content: str, message_type: str = 'text') -> bool:
        """Salva un template di messaggio"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO message_templates (user_id, name, content, message_type)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, name, content, message_type))
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logging.error(f"Errore nel salvataggio template: {e}")
            return False
    
    def get_user_templates(self, user_id: int) -> List[Dict[str, Any]]:
        """Recupera tutti i template di un utente"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, content, message_type, created_at, usage_count
                    FROM message_templates WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
                
                results = cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'name': row[1],
                        'content': row[2],
                        'message_type': row[3],
                        'created_at': row[4],
                        'usage_count': row[5]
                    }
                    for row in results
                ]
                
        except sqlite3.Error as e:
            logging.error(f"Errore nel recupero template: {e}")
            return []
    
    def log_command_usage(self, user_id: int, command: str, success: bool = True):
        """Registra l'uso di un comando per statistiche"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO bot_stats (user_id, command, success)
                    VALUES (?, ?, ?)
                ''', (user_id, command, success))
                conn.commit()
                
        except sqlite3.Error as e:
            logging.error(f"Errore nel log comando: {e}")
    
    def get_bot_stats(self) -> Dict[str, Any]:
        """Recupera statistiche generali del bot"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Numero totale utenti
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = TRUE")
                total_users = cursor.fetchone()[0]
                
                # Utenti attivi oggi
                cursor.execute('''
                    SELECT COUNT(*) FROM users 
                    WHERE DATE(last_activity) = DATE('now') AND is_active = TRUE
                ''')
                active_today = cursor.fetchone()[0]
                
                # Comandi più usati
                cursor.execute('''
                    SELECT command, COUNT(*) as count 
                    FROM bot_stats 
                    WHERE DATE(timestamp) >= DATE('now', '-7 days')
                    GROUP BY command 
                    ORDER BY count DESC 
                    LIMIT 5
                ''')
                top_commands = cursor.fetchall()
                
                return {
                    'total_users': total_users,
                    'active_today': active_today,
                    'top_commands': [{'command': cmd[0], 'count': cmd[1]} for cmd in top_commands]
                }
                
        except sqlite3.Error as e:
            logging.error(f"Errore nel recupero statistiche: {e}")
            return {'total_users': 0, 'active_today': 0, 'top_commands': []}
