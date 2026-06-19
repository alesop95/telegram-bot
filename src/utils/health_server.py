"""
Server per health checks e monitoring del bot
"""
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from typing import Optional

logger = logging.getLogger(__name__)

# Metriche Prometheus
REQUEST_COUNT = Counter('bot_requests_total', 'Total bot requests', ['command', 'status'])
REQUEST_DURATION = Histogram('bot_request_duration_seconds', 'Request duration')
ACTIVE_USERS = Counter('bot_active_users_total', 'Total active users')

class HealthServer:
    """Server FastAPI per health checks e metriche"""
    
    def __init__(self, bot_instance=None):
        self.app = FastAPI(
            title="Telegram Bot Health Check",
            description="Health check e monitoring per il bot Telegram",
            version="1.0.0"
        )
        self.bot_instance = bot_instance
        self.start_time = datetime.now()
        self.setup_routes()
    
    def setup_routes(self):
        """Configura le route del server"""
        
        @self.app.get("/health")
        async def health_check():
            """Endpoint per health check"""
            try:
                health_status = {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                    "version": "1.0.0"
                }
                
                # Controlla il database se disponibile
                if hasattr(self.bot_instance, 'db_manager') and self.bot_instance.db_manager:
                    try:
                        if hasattr(self.bot_instance.db_manager, 'health_check'):
                            db_healthy = await self.bot_instance.db_manager.health_check()
                            health_status["database"] = "healthy" if db_healthy else "unhealthy"
                        else:
                            health_status["database"] = "unknown"
                    except Exception as e:
                        health_status["database"] = f"error: {str(e)}"
                        health_status["status"] = "degraded"
                
                # Controlla lo stato del bot
                if self.bot_instance and hasattr(self.bot_instance, 'application'):
                    if self.bot_instance.application and self.bot_instance.application.running:
                        health_status["bot"] = "running"
                    else:
                        health_status["bot"] = "stopped"
                        health_status["status"] = "unhealthy"
                
                status_code = 200 if health_status["status"] == "healthy" else 503
                return JSONResponse(content=health_status, status_code=status_code)
                
            except Exception as e:
                logger.error(f"Errore nel health check: {e}")
                return JSONResponse(
                    content={
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    },
                    status_code=500
                )
        
        @self.app.get("/metrics")
        async def metrics():
            """Endpoint per metriche Prometheus"""
            try:
                return generate_latest()
            except Exception as e:
                logger.error(f"Errore nella generazione metriche: {e}")
                raise HTTPException(status_code=500, detail="Errore nella generazione metriche")
        
        @self.app.get("/stats")
        async def bot_stats():
            """Endpoint per statistiche del bot"""
            try:
                if not self.bot_instance or not hasattr(self.bot_instance, 'db_manager'):
                    raise HTTPException(status_code=503, detail="Database non disponibile")
                
                stats = await self.bot_instance.db_manager.get_bot_stats()
                stats.update({
                    "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                    "start_time": self.start_time.isoformat(),
                    "current_time": datetime.now().isoformat()
                })
                
                return JSONResponse(content=stats)
                
            except Exception as e:
                logger.error(f"Errore nel recupero statistiche: {e}")
                raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")
        
        @self.app.get("/")
        async def root():
            """Endpoint root con informazioni base"""
            return {
                "service": "Telegram Bot",
                "status": "running",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/health",
                    "metrics": "/metrics", 
                    "stats": "/stats"
                }
            }
        
        @self.app.post("/webhook/{token}")
        async def webhook_handler(token: str, update: dict):
            """Handler per webhook Telegram (opzionale)"""
            try:
                if not self.bot_instance:
                    raise HTTPException(status_code=503, detail="Bot non disponibile")
                
                # Verifica token (implementa la tua logica di sicurezza)
                expected_token = getattr(self.bot_instance.config, 'WEBHOOK_TOKEN', '')
                if token != expected_token:
                    raise HTTPException(status_code=401, detail="Token non valido")
                
                # Processa l'update (implementa se usi webhook)
                # await self.bot_instance.process_update(update)
                
                return {"status": "ok"}
                
            except Exception as e:
                logger.error(f"Errore nel webhook: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Avvia il server health check"""
        try:
            config = uvicorn.Config(
                app=self.app,
                host=host,
                port=port,
                log_level="info",
                access_log=True
            )
            server = uvicorn.Server(config)
            
            logger.info(f"Health server avviato su {host}:{port}")
            await server.serve()
            
        except Exception as e:
            logger.error(f"Errore nell'avvio del server: {e}")
            raise

def record_request(command: str, success: bool, duration: float):
    """Registra una richiesta nelle metriche"""
    status = "success" if success else "error"
    REQUEST_COUNT.labels(command=command, status=status).inc()
    REQUEST_DURATION.observe(duration)

def record_active_user():
    """Registra un utente attivo"""
    ACTIVE_USERS.inc()
