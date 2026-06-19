"""
Gestione del database PostgreSQL per il bot Telegram (versione cloud)
"""
import os
import logging
import asyncpg
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

logger = logging.getLogger(__name__)

class PostgreSQLManager:
    """Classe per gestire il database PostgreSQL in cloud"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def init_pool(self):
        """Inizializza il pool di connessioni"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Pool di connessioni PostgreSQL inizializzato")
            await self.init_database()
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione del pool: {e}")
            raise
    
    async def close_pool(self):
        """Chiude il pool di connessioni"""
        if self.pool:
            await self.pool.close()
            logger.info("Pool di connessioni chiuso")
    
    async def init_database(self):
        """Inizializza il database con le tabelle necessarie"""
        try:
            async with self.pool.acquire() as conn:
                # Tabella utenti
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
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
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_settings (
                        user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
                        theme TEXT DEFAULT 'default',
                        notifications BOOLEAN DEFAULT TRUE,
                        language TEXT DEFAULT 'it',
                        timezone TEXT DEFAULT 'Europe/Rome',
                        custom_settings JSONB DEFAULT '{}'::jsonb,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Tabella template messaggi
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS message_templates (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                        name TEXT NOT NULL,
                        content TEXT NOT NULL,
                        message_type TEXT DEFAULT 'text',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        usage_count INTEGER DEFAULT 0,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                ''')
                
                # Tabella messaggi programmati
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS scheduled_messages (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                        chat_id BIGINT,
                        message_content TEXT NOT NULL,
                        message_type TEXT DEFAULT 'text',
                        scheduled_time TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        sent BOOLEAN DEFAULT FALSE,
                        sent_at TIMESTAMP,
                        error_message TEXT
                    )
                ''')
                
                # Tabella statistiche
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS bot_stats (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                        command TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        success BOOLEAN DEFAULT TRUE,
                        execution_time_ms INTEGER,
                        metadata JSONB DEFAULT '{}'::jsonb
                    )
                ''')
                
                # Indici per performance
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_templates_user_id ON message_templates(user_id)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_stats_user_command ON bot_stats(user_id, command)')
                await conn.execute('CREATE INDEX IF NOT EXISTS idx_scheduled_time ON scheduled_messages(scheduled_time) WHERE NOT sent')
                
                logger.info("Database PostgreSQL inizializzato correttamente")
                
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione del database: {e}")
            raise
    
    async def add_user(self, user_data: Dict[str, Any]) -> bool:
        """Aggiunge o aggiorna un utente nel database"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    # Inserisce o aggiorna l'utente
                    await conn.execute('''
                        INSERT INTO users 
                        (user_id, username, first_name, last_name, language_code, is_bot, is_premium, last_activity)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (user_id) DO UPDATE SET
                            username = EXCLUDED.username,
                            first_name = EXCLUDED.first_name,
                            last_name = EXCLUDED.last_name,
                            language_code = EXCLUDED.language_code,
                            is_premium = EXCLUDED.is_premium,
                            last_activity = EXCLUDED.last_activity
                    ''', 
                        user_data.get('id'),
                        user_data.get('username'),
                        user_data.get('first_name'),
                        user_data.get('last_name'),
                        user_data.get('language_code'),
                        user_data.get('is_bot', False),
                        user_data.get('is_premium', False),
                        datetime.now()
                    )
                    
                    # Crea impostazioni di default se non esistono
                    await conn.execute('''
                        INSERT INTO user_settings (user_id)
                        VALUES ($1)
                        ON CONFLICT (user_id) DO NOTHING
                    ''', user_data.get('id'))
                    
                return True
                
        except Exception as e:
            logger.error(f"Errore nell'aggiunta dell'utente: {e}")
            return False
    
    async def get_user_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Recupera le impostazioni di un utente"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow('''
                    SELECT theme, notifications, language, timezone, custom_settings
                    FROM user_settings WHERE user_id = $1
                ''', user_id)
                
                if row:
                    return {
                        'theme': row['theme'],
                        'notifications': row['notifications'],
                        'language': row['language'],
                        'timezone': row['timezone'],
                        'custom_settings': row['custom_settings']
                    }
                return None
                
        except Exception as e:
            logger.error(f"Errore nel recupero impostazioni utente: {e}")
            return None
    
    async def update_user_settings(self, user_id: int, settings: Dict[str, Any]) -> bool:
        """Aggiorna le impostazioni di un utente"""
        try:
            async with self.pool.acquire() as conn:
                # Costruisce la query dinamicamente
                set_clauses = []
                values = []
                param_count = 1
                
                for key, value in settings.items():
                    if key in ['theme', 'notifications', 'language', 'timezone', 'custom_settings']:
                        set_clauses.append(f"{key} = ${param_count}")
                        values.append(value)
                        param_count += 1
                
                if set_clauses:
                    set_clauses.append(f"updated_at = ${param_count}")
                    values.append(datetime.now())
                    values.append(user_id)
                    
                    query = f"""
                        UPDATE user_settings 
                        SET {', '.join(set_clauses)}
                        WHERE user_id = ${param_count + 1}
                    """
                    
                    await conn.execute(query, *values)
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento impostazioni: {e}")
            return False
    
    async def save_message_template(self, user_id: int, name: str, content: str, message_type: str = 'text') -> bool:
        """Salva un template di messaggio"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO message_templates (user_id, name, content, message_type)
                    VALUES ($1, $2, $3, $4)
                ''', user_id, name, content, message_type)
                return True
                
        except Exception as e:
            logger.error(f"Errore nel salvataggio template: {e}")
            return False
    
    async def get_user_templates(self, user_id: int) -> List[Dict[str, Any]]:
        """Recupera tutti i template di un utente"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch('''
                    SELECT id, name, content, message_type, created_at, usage_count
                    FROM message_templates 
                    WHERE user_id = $1 AND is_active = TRUE
                    ORDER BY created_at DESC
                ''', user_id)
                
                return [
                    {
                        'id': row['id'],
                        'name': row['name'],
                        'content': row['content'],
                        'message_type': row['message_type'],
                        'created_at': row['created_at'],
                        'usage_count': row['usage_count']
                    }
                    for row in rows
                ]
                
        except Exception as e:
            logger.error(f"Errore nel recupero template: {e}")
            return []
    
    async def log_command_usage(self, user_id: int, command: str, success: bool = True, execution_time_ms: int = 0, metadata: Dict = None):
        """Registra l'uso di un comando per statistiche"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO bot_stats (user_id, command, success, execution_time_ms, metadata)
                    VALUES ($1, $2, $3, $4, $5)
                ''', user_id, command, success, execution_time_ms, json.dumps(metadata or {}))
                
        except Exception as e:
            logger.error(f"Errore nel log comando: {e}")
    
    async def get_bot_stats(self) -> Dict[str, Any]:
        """Recupera statistiche generali del bot"""
        try:
            async with self.pool.acquire() as conn:
                # Numero totale utenti
                total_users = await conn.fetchval(
                    "SELECT COUNT(*) FROM users WHERE is_active = TRUE"
                )
                
                # Utenti attivi oggi
                active_today = await conn.fetchval('''
                    SELECT COUNT(*) FROM users 
                    WHERE DATE(last_activity) = CURRENT_DATE AND is_active = TRUE
                ''')
                
                # Comandi più usati (ultimi 7 giorni)
                top_commands = await conn.fetch('''
                    SELECT command, COUNT(*) as count 
                    FROM bot_stats 
                    WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
                    GROUP BY command 
                    ORDER BY count DESC 
                    LIMIT 5
                ''')
                
                # Performance media
                avg_response_time = await conn.fetchval('''
                    SELECT AVG(execution_time_ms) 
                    FROM bot_stats 
                    WHERE timestamp >= CURRENT_DATE - INTERVAL '24 hours'
                    AND execution_time_ms > 0
                ''')
                
                return {
                    'total_users': total_users or 0,
                    'active_today': active_today or 0,
                    'top_commands': [
                        {'command': cmd['command'], 'count': cmd['count']} 
                        for cmd in top_commands
                    ],
                    'avg_response_time_ms': round(avg_response_time or 0, 2)
                }
                
        except Exception as e:
            logger.error(f"Errore nel recupero statistiche: {e}")
            return {'total_users': 0, 'active_today': 0, 'top_commands': [], 'avg_response_time_ms': 0}
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Pulisce i dati vecchi per ottimizzare le performance"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    # Rimuove statistiche vecchie
                    deleted_stats = await conn.fetchval('''
                        DELETE FROM bot_stats 
                        WHERE timestamp < CURRENT_DATE - INTERVAL '%s days'
                        RETURNING COUNT(*)
                    ''', days_to_keep)
                    
                    # Rimuove messaggi programmati inviati e vecchi
                    deleted_messages = await conn.fetchval('''
                        DELETE FROM scheduled_messages 
                        WHERE sent = TRUE AND sent_at < CURRENT_DATE - INTERVAL '%s days'
                        RETURNING COUNT(*)
                    ''', days_to_keep)
                    
                    logger.info(f"Cleanup completato: {deleted_stats} statistiche, {deleted_messages} messaggi rimossi")
                    
        except Exception as e:
            logger.error(f"Errore nel cleanup: {e}")
    
    async def health_check(self) -> bool:
        """Controlla lo stato di salute del database"""
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval('SELECT 1')
                return True
        except Exception as e:
            logger.error(f"Health check fallito: {e}")
            return False
