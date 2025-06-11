import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from app.agents.data_collector import DataCollectorAgent
from app.agents.economic_analysis import EconomicAnalysisAgent
from app.agents.communication import CommunicationAgent

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchedulerService:
    """
    Servicio para manejar tareas programadas del sistema
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.data_collector = DataCollectorAgent()
        self.economic_analyzer = EconomicAnalysisAgent()
        self.communication_agent = CommunicationAgent()
    
    async def update_crypto_data_job(self):
        """
        Tarea programada para actualizar datos de criptomonedas
        Se ejecuta cada hora para mantener datos frescos
        """
        try:
            logger.info("Iniciando actualización programada de datos de criptomonedas")
            
            # Recopilar datos de APIs
            crypto_data = await self.data_collector.collect_all_data()
            
            if crypto_data.get('coingecko') or crypto_data.get('binance'):
                # Analizar y guardar datos
                await self.economic_analyzer.analyze_and_store(crypto_data)
                logger.info(f"Datos actualizados: {len(crypto_data.get('coingecko', []))} monedas procesadas")
            else:
                logger.warning("No se obtuvieron datos de las APIs externas")
                
        except Exception as e:
            logger.error(f"Error en actualización programada de datos: {e}")
    
    async def send_daily_notifications_job(self):
        """
        Tarea programada para enviar notificaciones diarias
        Se ejecuta todos los días a las 9:00 AM
        """
        try:
            logger.info("Iniciando envío de notificaciones diarias")
            
            result = await self.communication_agent.send_daily_recommendations()
            
            if result.get('success'):
                logger.info(f"Notificaciones enviadas: {result.get('sent_count', 0)}")
                if result.get('failed_count', 0) > 0:
                    logger.warning(f"Notificaciones fallidas: {result.get('failed_count', 0)}")
            else:
                logger.error(f"Error enviando notificaciones: {result.get('message')}")
                
        except Exception as e:
            logger.error(f"Error en envío programado de notificaciones: {e}")
    
    async def cleanup_old_data_job(self):
        """
        Tarea programada para limpiar datos antiguos
        Se ejecuta semanalmente para mantener la base de datos optimizada
        """
        try:
            logger.info("Iniciando limpieza de datos antiguos")
            
            from app import SessionLocal
            from app.models import PortfolioRecommendation
            from datetime import timedelta
            
            db = SessionLocal()
            
            # Eliminar recomendaciones más antiguas de 30 días
            cutoff_date = datetime.now() - timedelta(days=30)
            
            old_recommendations = db.query(PortfolioRecommendation).filter(
                PortfolioRecommendation.created_at < cutoff_date
            ).delete()
            
            db.commit()
            db.close()
            
            logger.info(f"Limpieza completada: {old_recommendations} registros antiguos eliminados")
            
        except Exception as e:
            logger.error(f"Error en limpieza programada de datos: {e}")
    
    def start_scheduler(self):
        """Iniciar el programador de tareas"""
        
        # Actualizar datos de criptomonedas cada hora
        self.scheduler.add_job(
            self.update_crypto_data_job,
            CronTrigger(minute=0),  # Cada hora en punto
            id='update_crypto_data',
            name='Actualizar datos de criptomonedas',
            replace_existing=True
        )
        
        # Enviar notificaciones diarias a las 9:00 AM
        self.scheduler.add_job(
            self.send_daily_notifications_job,
            CronTrigger(hour=9, minute=0),  # 9:00 AM todos los días
            id='send_daily_notifications',
            name='Enviar notificaciones diarias',
            replace_existing=True
        )
        
        # Limpiar datos antiguos los domingos a las 2:00 AM
        self.scheduler.add_job(
            self.cleanup_old_data_job,
            CronTrigger(day_of_week=6, hour=2, minute=0),  # Domingo 2:00 AM
            id='cleanup_old_data',
            name='Limpiar datos antiguos',
            replace_existing=True
        )
        
        # Iniciar el scheduler
        self.scheduler.start()
        logger.info("Programador de tareas iniciado")
        
        # Imprimir tareas programadas
        for job in self.scheduler.get_jobs():
            logger.info(f"Tarea programada: {job.name} - Próxima ejecución: {job.next_run_time}")
    
    def stop_scheduler(self):
        """Detener el programador de tareas"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Programador de tareas detenido")

# Instancia global del scheduler
scheduler_service = SchedulerService()
