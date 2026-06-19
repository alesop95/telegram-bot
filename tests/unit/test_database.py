"""
Test per il database PostgreSQL
"""
import pytest
import asyncio
import os
from src.database.postgres_manager import PostgreSQLManager

# URL di test per database
TEST_DATABASE_URL = os.getenv(
    'TEST_DATABASE_URL', 
    'postgresql://test_user:test_password@localhost:5432/test_db'
)

@pytest.fixture
async def db_manager():
    """Fixture per il database manager"""
    manager = PostgreSQLManager(TEST_DATABASE_URL)
    await manager.init_pool()
    yield manager
    await manager.close_pool()

@pytest.fixture
def sample_user_data():
    """Dati utente di esempio"""
    return {
        'id': 123456789,
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'language_code': 'it',
        'is_bot': False,
        'is_premium': False
    }

class TestPostgreSQLManager:
    """Test per PostgreSQLManager"""
    
    @pytest.mark.asyncio
    async def test_database_initialization(self, db_manager):
        """Test inizializzazione database"""
        health = await db_manager.health_check()
        assert health is True
    
    @pytest.mark.asyncio
    async def test_add_user(self, db_manager, sample_user_data):
        """Test aggiunta utente"""
        result = await db_manager.add_user(sample_user_data)
        assert result is True
        
        # Verifica che l'utente sia stato aggiunto
        settings = await db_manager.get_user_settings(sample_user_data['id'])
        assert settings is not None
        assert settings['theme'] == 'default'
    
    @pytest.mark.asyncio
    async def test_user_settings(self, db_manager, sample_user_data):
        """Test gestione impostazioni utente"""
        # Aggiungi utente
        await db_manager.add_user(sample_user_data)
        
        # Aggiorna impostazioni
        new_settings = {
            'theme': 'dark',
            'notifications': False,
            'language': 'en'
        }
        result = await db_manager.update_user_settings(
            sample_user_data['id'], 
            new_settings
        )
        assert result is True
        
        # Verifica aggiornamento
        settings = await db_manager.get_user_settings(sample_user_data['id'])
        assert settings['theme'] == 'dark'
        assert settings['notifications'] is False
        assert settings['language'] == 'en'
    
    @pytest.mark.asyncio
    async def test_message_templates(self, db_manager, sample_user_data):
        """Test gestione template messaggi"""
        # Aggiungi utente
        await db_manager.add_user(sample_user_data)
        
        # Salva template
        result = await db_manager.save_message_template(
            sample_user_data['id'],
            'test_template',
            'Questo è un template di test',
            'text'
        )
        assert result is True
        
        # Recupera template
        templates = await db_manager.get_user_templates(sample_user_data['id'])
        assert len(templates) == 1
        assert templates[0]['name'] == 'test_template'
        assert templates[0]['content'] == 'Questo è un template di test'
    
    @pytest.mark.asyncio
    async def test_command_logging(self, db_manager, sample_user_data):
        """Test logging comandi"""
        # Aggiungi utente
        await db_manager.add_user(sample_user_data)
        
        # Log comando
        await db_manager.log_command_usage(
            sample_user_data['id'],
            '/start',
            success=True,
            execution_time_ms=150
        )
        
        # Verifica statistiche
        stats = await db_manager.get_bot_stats()
        assert stats['total_users'] >= 1
    
    @pytest.mark.asyncio
    async def test_bot_stats(self, db_manager, sample_user_data):
        """Test statistiche bot"""
        # Aggiungi utente e log alcuni comandi
        await db_manager.add_user(sample_user_data)
        await db_manager.log_command_usage(sample_user_data['id'], '/start')
        await db_manager.log_command_usage(sample_user_data['id'], '/help')
        
        stats = await db_manager.get_bot_stats()
        
        assert 'total_users' in stats
        assert 'active_today' in stats
        assert 'top_commands' in stats
        assert stats['total_users'] >= 1
    
    @pytest.mark.asyncio
    async def test_cleanup_old_data(self, db_manager, sample_user_data):
        """Test pulizia dati vecchi"""
        # Aggiungi alcuni dati
        await db_manager.add_user(sample_user_data)
        await db_manager.log_command_usage(sample_user_data['id'], '/test')
        
        # Esegui cleanup (non dovrebbe rimuovere dati recenti)
        await db_manager.cleanup_old_data(days_to_keep=1)
        
        # Verifica che i dati recenti siano ancora presenti
        stats = await db_manager.get_bot_stats()
        assert stats['total_users'] >= 1

if __name__ == '__main__':
    pytest.main([__file__])
