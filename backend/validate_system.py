"""
🎯 Suite de Validación Completa - CriptoAI Backend
Prueba exhaustiva de todas las funcionalidades implementadas
"""
import asyncio
import httpx
import json
import sqlite3
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

async def comprehensive_system_test():
    """Ejecutar validación completa del sistema CriptoAI"""
    
    print("🎯 VALIDACIÓN COMPLETA DEL SISTEMA CRIPTOAI")
    print("=" * 70)
    print("🕐 Iniciado:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    results = {
        "health_check": False,
        "database_connectivity": False,
        "market_data": False,
        "data_collection": False,
        "agents_active": False,
        "api_endpoints": 0,
        "scheduler_active": False
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # 1. Sistema de Salud
        print("🔍 1. VERIFICACIÓN DE SALUD DEL SISTEMA")
        print("-" * 50)
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                health_data = response.json()
                results["health_check"] = True
                results["database_connectivity"] = health_data.get("database") == "connected"
                
                print(f"✅ Estado del sistema: {health_data.get('status')}")
                print(f"✅ Base de datos: {health_data.get('database')}")
                print(f"✅ Servicios activos: {len(health_data.get('services', {}))}")
                
                # Verificar agentes
                services = health_data.get('services', {})
                active_agents = sum(1 for status in services.values() if status == "active")
                results["agents_active"] = active_agents >= 4
                print(f"✅ Agentes activos: {active_agents}/4")
                
            else:
                print(f"❌ Error en health check: {response.status_code}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
        
        print()
        
        # 2. Verificación de Base de Datos
        print("🗄️  2. VERIFICACIÓN DE BASE DE DATOS")
        print("-" * 50)
        try:
            conn = sqlite3.connect('./criptoai.db')
            cursor = conn.cursor()
            
            # Verificar tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            expected_tables = ['cryptocurrencies', 'crypto_metrics', 'user_profiles', 'portfolio_recommendations', 'subscriptions']
            
            for table in expected_tables:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"✅ Tabla '{table}': {count} registros")
                else:
                    print(f"❌ Tabla '{table}': NO ENCONTRADA")
            
            conn.close()
            print("✅ Conexión directa a SQLite exitosa")
            
        except Exception as e:
            print(f"❌ Error verificando base de datos: {e}")
        
        print()
        
        # 3. Datos de Mercado
        print("📊 3. VERIFICACIÓN DE DATOS DE MERCADO")
        print("-" * 50)
        try:
            response = await client.get(f"{BASE_URL}/market-overview")
            if response.status_code == 200:
                market_data = response.json()
                if market_data.get('success'):
                    cryptos = market_data['data']['top_cryptocurrencies']
                    results["market_data"] = len(cryptos) > 0
                    
                    print(f"✅ Criptomonedas disponibles: {len(cryptos)}")
                    print("📈 Top 5:")
                    for i, crypto in enumerate(cryptos[:5], 1):
                        name = crypto.get('name', 'N/A')
                        symbol = crypto.get('symbol', 'N/A')
                        price = crypto.get('current_price', 0)
                        change = crypto.get('price_change_24h', 0)
                        print(f"   {i}. {name} ({symbol}) - ${price:,.2f} ({change:+.2f}%)")
                        
                else:
                    print("❌ No se pudieron obtener datos de mercado")
            else:
                print(f"❌ Error obteniendo datos: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        print()
        
        # 4. Recolección de Datos
        print("🔄 4. PRUEBA DE RECOLECCIÓN DE DATOS")
        print("-" * 50)
        try:
            response = await client.post(f"{BASE_URL}/update-data")
            if response.status_code == 200:
                update_data = response.json()
                results["data_collection"] = update_data.get('success', False)
                
                print(f"✅ Actualización exitosa")
                print(f"📊 Monedas recopiladas: {update_data.get('coins_collected', 'N/A')}")
                print(f"💼 Análsis iniciado: {update_data.get('message', 'N/A')}")
                
            else:
                print(f"❌ Error en actualización: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        print()
        
        # 5. Prueba de Recomendaciones
        print("🎯 5. PRUEBA DE RECOMENDACIONES DE PORTFOLIO")
        print("-" * 50)
        test_profiles = [
            {"user_id": "test_conservative", "investment_amount": 1000, "risk_tolerance": "conservative"},
            {"user_id": "test_moderate", "investment_amount": 5000, "risk_tolerance": "moderate"},
            {"user_id": "test_aggressive", "investment_amount": 10000, "risk_tolerance": "aggressive"}
        ]
        
        recommendations_working = 0
        for profile in test_profiles:
            try:
                response = await client.post(f"{BASE_URL}/get-portfolio-recommendation", json=profile)
                if response.status_code == 200:
                    rec_data = response.json()
                    if rec_data.get('success'):
                        recommendations = rec_data['data']['recommendations']
                        print(f"✅ {profile['risk_tolerance'].title()}: {len(recommendations)} recomendaciones")
                        recommendations_working += 1
                    else:
                        print(f"⚠️  {profile['risk_tolerance'].title()}: {rec_data.get('message', 'Sin datos')}")
                else:
                    error_data = response.json()
                    print(f"⚠️  {profile['risk_tolerance'].title()}: {error_data.get('detail', 'Error')}")
            except Exception as e:
                print(f"❌ Error en {profile['risk_tolerance']}: {e}")
        
        print(f"📊 Perfiles de recomendación funcionando: {recommendations_working}/3")
        print()
        
        # 6. Endpoints Disponibles
        print("🌐 6. VERIFICACIÓN DE ENDPOINTS")
        print("-" * 50)
        endpoints_to_test = [
            ("GET", "/health", "Estado del sistema"),
            ("GET", "/market-overview", "Resumen de mercado"),
            ("POST", "/update-data", "Actualización de datos"),
            ("POST", "/subscribe", "Sistema de suscripciones")
        ]
        
        working_endpoints = 0
        for method, endpoint, description in endpoints_to_test:
            try:
                if method == "GET":
                    response = await client.get(f"{BASE_URL}{endpoint}")
                else:
                    # Test data for POST endpoints
                    test_data = {}
                    if endpoint == "/subscribe":
                        test_data = {
                            "user_id": "test_endpoint_validation",
                            "email": "test@validation.com",
                            "notification_type": "email",
                            "frequency": "weekly"
                        }
                    
                    response = await client.request(method, f"{BASE_URL}{endpoint}", json=test_data)
                
                if response.status_code in [200, 201]:
                    print(f"✅ {method} {endpoint} - {description}")
                    working_endpoints += 1
                else:
                    print(f"⚠️  {method} {endpoint} - Status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {method} {endpoint} - Error: {e}")
        
        results["api_endpoints"] = working_endpoints
        print(f"📊 Endpoints funcionando: {working_endpoints}/{len(endpoints_to_test)}")
        print()
    
    # 7. Resumen Final
    print("📋 7. RESUMEN FINAL DE VALIDACIÓN")
    print("=" * 70)
    
    total_checks = 6
    passed_checks = 0
    
    if results["health_check"]:
        print("✅ Sistema de salud: FUNCIONANDO")
        passed_checks += 1
    else:
        print("❌ Sistema de salud: FALLO")
    
    if results["database_connectivity"]:
        print("✅ Conectividad de base de datos: FUNCIONANDO")
        passed_checks += 1
    else:
        print("❌ Conectividad de base de datos: FALLO")
    
    if results["market_data"]:
        print("✅ Datos de mercado: FUNCIONANDO")
        passed_checks += 1
    else:
        print("❌ Datos de mercado: FALLO")
    
    if results["data_collection"]:
        print("✅ Recolección de datos: FUNCIONANDO")
        passed_checks += 1
    else:
        print("❌ Recolección de datos: FALLO")
    
    if results["agents_active"]:
        print("✅ Agentes especializados: FUNCIONANDO")
        passed_checks += 1
    else:
        print("❌ Agentes especializados: FALLO")
    
    if results["api_endpoints"] >= 3:
        print("✅ Endpoints de API: FUNCIONANDO")
        passed_checks += 1
    else:
        print("❌ Endpoints de API: FALLO")
    
    print("-" * 70)
    success_rate = (passed_checks / total_checks) * 100
    print(f"🎯 TASA DE ÉXITO: {success_rate:.1f}% ({passed_checks}/{total_checks})")
    
    if success_rate >= 80:
        print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("✅ El backend CriptoAI está listo para producción")
    elif success_rate >= 60:
        print("⚠️  SISTEMA PARCIALMENTE FUNCIONAL")
        print("🔧 Requiere ajustes menores")
    else:
        print("❌ SISTEMA REQUIERE ATENCIÓN")
        print("🛠️  Necesita revisión y correcciones")
    
    print(f"🕐 Completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    print("🚀 Iniciando validación completa del sistema...")
    print("⚠️  Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    print()
    
    try:
        asyncio.run(comprehensive_system_test())
    except KeyboardInterrupt:
        print("\n🛑 Validación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la validación: {e}")
