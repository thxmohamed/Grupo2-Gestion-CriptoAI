"""
Script simple para inicializar y probar el backend de CriptoAI
"""
import os
import sys
import asyncio
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_basic_imports():
    """Probar importaciones básicas"""
    print("🔄 Probando importaciones básicas...")
    
    try:
        # Probar FastAPI
        import fastapi
        print("✅ FastAPI importado")
        
        # Probar SQLAlchemy
        import sqlalchemy
        print("✅ SQLAlchemy importado")
        
        # Probar httpx
        import httpx
        print("✅ HTTPX importado")
        
        # Probar python-binance
        import binance
        print("✅ Python-Binance importado")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error en importación: {e}")
        return False

async def test_app_structure():
    """Probar estructura de la aplicación"""
    print("\n🔄 Probando estructura de la aplicación...")
    
    try:
        # Probar importación del módulo principal
        from app import create_app, Base, SessionLocal
        print("✅ Módulo principal de la app importado")
        
        # Probar modelos
        from app.models import Cryptocurrency, CryptoMetrics, UserProfile
        print("✅ Modelos de base de datos importados")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error en estructura de app: {e}")
        return False

async def test_utilities():
    """Probar utilidades"""
    print("\n🔄 Probando utilidades...")
    
    try:
        from app.utils import BinanceAPIHelper, CoinGeckoAPIHelper, DataProcessor
        print("✅ Clases de utilidades importadas")
        
        # Crear instancias
        binance = BinanceAPIHelper()
        coingecko = CoinGeckoAPIHelper()
        processor = DataProcessor()
        print("✅ Instancias de utilidades creadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en utilidades: {e}")
        return False

async def test_agents():
    """Probar agentes"""
    print("\n🔄 Probando agentes...")
    
    try:
        from app.agents.data_collector import DataCollectorAgent
        from app.agents.economic_analysis import EconomicAnalysisAgent
        from app.agents.portfolio_optimizer import PortfolioOptimizationAgent
        from app.agents.communication import CommunicationAgent
        print("✅ Agentes importados")
        
        # Crear instancias
        collector = DataCollectorAgent()
        analyzer = EconomicAnalysisAgent()
        optimizer = PortfolioOptimizationAgent()
        communicator = CommunicationAgent()
        print("✅ Instancias de agentes creadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en agentes: {e}")
        return False

async def test_api_endpoints():
    """Probar que los endpoints se pueden crear"""
    print("\n🔄 Probando creación de la aplicación FastAPI...")
    
    try:
        from app import create_app
        
        # Crear aplicación
        app = create_app()
        print("✅ Aplicación FastAPI creada exitosamente")
        
        # Verificar que tiene rutas
        routes = [route.path for route in app.routes]
        print(f"✅ Rutas disponibles: {len(routes)} rutas registradas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando aplicación: {e}")
        return False

async def main():
    """Función principal de diagnóstico"""
    print("🚀 Diagnóstico del Backend CriptoAI")
    print("=" * 50)
    
    all_tests = [
        test_basic_imports(),
        test_app_structure(),
        test_utilities(),
        test_agents(),
        test_api_endpoints()
    ]
    
    results = []
    for test in all_tests:
        result = await test
        results.append(result)
    
    print("\n" + "=" * 50)
    
    if all(results):
        print("🎉 ¡Todos los componentes funcionan correctamente!")
        print("\n✨ El backend está listo para ejecutarse")
        print("📝 Para iniciar el servidor:")
        print("   python run.py")
        
    else:
        print("⚠️  Algunos componentes tienen problemas")
        print("🔧 Revisa los errores mostrados arriba")
    
    return all(results)

if __name__ == "__main__":
    asyncio.run(main())
