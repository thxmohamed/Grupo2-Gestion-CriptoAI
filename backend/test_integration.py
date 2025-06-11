"""
Script de pruebas integradas para verificar todas las funcionalidades del backend CriptoAI
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

async def test_endpoints():
    """Ejecutar pruebas de todos los endpoints principales"""
    
    print("🔍 Iniciando pruebas del backend CriptoAI...")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # 1. Test Health Check
        print("1️⃣  Probando endpoint de salud...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Sistema saludable - Estado: {data['status']}")
                print(f"   📊 Base de datos: {data['database']}")
            else:
                print(f"   ❌ Error en health check: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        
        # 2. Test Market Overview
        print("2️⃣  Probando resumen de mercado...")
        try:
            response = await client.get(f"{BASE_URL}/market-overview")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Datos obtenidos exitosamente")
                if data.get('success'):
                    crypto_count = len(data['data']['top_cryptocurrencies'])
                    print(f"   📈 Criptomonedas disponibles: {crypto_count}")
                    
                    # Mostrar top 3
                    for i, crypto in enumerate(data['data']['top_cryptocurrencies'][:3]):
                        print(f"      {i+1}. {crypto['name']} ({crypto['symbol']}) - ${crypto.get('current_price', 'N/A')}")
            else:
                print(f"   ❌ Error en market overview: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        
        # 3. Test Data Update
        print("3️⃣  Probando actualización de datos...")
        try:
            response = await client.post(f"{BASE_URL}/update-data")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Actualización iniciada")
                print(f"   📊 Monedas recopiladas: {data.get('coins_collected', 'N/A')}")
            else:
                print(f"   ❌ Error en actualización: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        
        # 4. Test Portfolio Recommendation
        print("4️⃣  Probando recomendación de portfolio...")
        portfolio_request = {
            "user_id": "test_user_001",
            "investment_amount": 5000,
            "risk_tolerance": "moderate"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/get-portfolio-recommendation",
                json=portfolio_request
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Recomendación generada exitosamente")
                if data.get('success'):
                    recommendations = data['data']['recommendations']
                    print(f"   🎯 Monedas recomendadas: {len(recommendations)}")
                    for i, rec in enumerate(recommendations[:3]):
                        print(f"      {i+1}. {rec['symbol']} - {rec['allocation_percentage']}%")
            else:
                error_data = response.json()
                print(f"   ⚠️  {error_data.get('detail', 'Error desconocido')}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        
        # 5. Test Subscription
        print("5️⃣  Probando sistema de suscripciones...")
        subscription_data = {
            "user_id": "test_user_001", 
            "email": "test@example.com",
            "notification_type": "email",
            "frequency": "daily"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/subscribe",
                json=subscription_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Suscripción creada exitosamente")
                print(f"   📧 Email: {subscription_data['email']}")
                print(f"   📅 Frecuencia: {subscription_data['frequency']}")
            else:
                error_data = response.json()
                print(f"   ⚠️  {error_data.get('detail', 'Error en suscripción')}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("=" * 60)
    print("🎉 Pruebas completadas!")
    print(f"⏰ Ejecutado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("🚀 CriptoAI Backend - Suite de Pruebas Integradas")
    print("🌐 Servidor debe estar ejecutándose en http://localhost:8000")
    print()
    
    asyncio.run(test_endpoints())
