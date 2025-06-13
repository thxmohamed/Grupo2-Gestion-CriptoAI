import asyncio
import uvicorn
from contextlib import asynccontextmanager
from app import create_app
from app.scheduler import scheduler_service
from database_migration import auto_migrate

@asynccontextmanager
async def lifespan(app):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print("🚀 Iniciando CriptoAI Backend...")
    
    # Ejecutar migración automática de base de datos
    print("🔄 Verificando estado de la base de datos...")
    migration_success = auto_migrate()
    if not migration_success:
        print("⚠️  Advertencia: Algunos problemas en la migración de BD")
    
    # Iniciar scheduler para tareas programadas
    scheduler_service.start_scheduler()
    
    yield
    
    # Shutdown
    print("🛑 Deteniendo CriptoAI Backend...")
    scheduler_service.stop_scheduler()

# Crear aplicación con gestión de ciclo de vida
app = create_app()
app.router.lifespan_context = lifespan

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 CriptoAI Backend - Sistema de Análisis de Criptomonedas")
    print("=" * 50)
    print("📊 Agentes activos:")
    print("   • Agente Recolección de datos (Binance + CoinGecko)")
    print("   • Agente Análisis económico (Métricas y indicadores)")
    print("   • Agente Optimización Portfolio (Recomendaciones personalizadas)")
    print("   • Agente Comunicación (Notificaciones y suscripciones)")
    print("=" * 50)
    
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
