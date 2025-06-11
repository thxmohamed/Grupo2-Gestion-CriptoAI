"""
Script de prueba para verificar la conexión con las APIs de Binance y CoinGecko
"""
import asyncio
import sys
import os

# Agregar el directorio de la aplicación al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils import binance_helper, coingecko_helper
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_binance_api():
    """Probar conexión con API de Binance"""
    print("🔄 Probando API de Binance...")
    
    try:
        # Probar endpoint público de ticker 24h
        tickers = await binance_helper.get_24hr_ticker("BTCUSDT")
        if tickers:
            ticker = tickers[0]
            print(f"✅ Binance conectado - BTC/USDT: ${float(ticker['lastPrice']):,.2f}")
            return True
        else:
            print("❌ No se recibieron datos de Binance")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con Binance: {e}")
        return False

async def test_coingecko_api():
    """Probar conexión con API de CoinGecko"""
    print("🔄 Probando API de CoinGecko...")
    
    try:
        # Probar endpoint de mercados
        markets = await coingecko_helper.get_coins_markets(per_page=5)
        if markets:
            bitcoin = next((coin for coin in markets if coin['id'] == 'bitcoin'), None)
            if bitcoin:
                print(f"✅ CoinGecko conectado - Bitcoin: ${bitcoin['current_price']:,.2f}")
                return True
            else:
                print("✅ CoinGecko conectado - Datos recibidos")
                return True
        else:
            print("❌ No se recibieron datos de CoinGecko")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con CoinGecko: {e}")
        return False

async def test_data_collection():
    """Probar recolección completa de datos"""
    print("🔄 Probando recolección completa de datos...")
    
    try:
        from app.agents.data_collector import DataCollectorAgent
        
        collector = DataCollectorAgent()
        data = await collector.collect_all_data()
        
        if data and 'stats' in data:
            stats = data['stats']
            print(f"✅ Recolección exitosa:")
            print(f"   - Binance: {stats['binance_coins']} monedas")
            print(f"   - CoinGecko: {stats['coingecko_coins']} monedas")
            print(f"   - Combinadas: {stats['merged_coins']} monedas")
            return True
        else:
            print("❌ Error en recolección de datos")
            return False
            
    except Exception as e:
        print(f"❌ Error en recolección de datos: {e}")
        return False

async def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de APIs CriptoAI")
    print("=" * 50)
    
    # Pruebas individuales
    binance_ok = await test_binance_api()
    print()
    
    coingecko_ok = await test_coingecko_api()
    print()
    
    # Prueba de recolección completa solo si las APIs funcionan
    if binance_ok and coingecko_ok:
        collection_ok = await test_data_collection()
        print()
        
        if collection_ok:
            print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        else:
            print("⚠️  APIs funcionan pero hay problemas en la recolección")
    else:
        print("❌ Problemas de conectividad con las APIs")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
