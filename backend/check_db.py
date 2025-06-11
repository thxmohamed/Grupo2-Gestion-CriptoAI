"""
Script para verificar las tablas de la base de datos
"""
from app import SessionLocal, engine
from sqlalchemy import text, inspect
from app.models import Cryptocurrency, CryptoMetrics, UserProfile, PortfolioRecommendation, Subscription

def check_database():
    """Verificar estructura de la base de datos"""
    print("🔍 Verificando estructura de la base de datos...")
    
    # Crear inspector
    inspector = inspect(engine)
    
    # Obtener nombres de tablas
    table_names = inspector.get_table_names()
    print(f"📊 Tablas encontradas: {table_names}")
    
    # Verificar cada tabla
    expected_tables = ['cryptocurrencies', 'crypto_metrics', 'user_profiles', 'portfolio_recommendations', 'subscriptions']
    
    for table in expected_tables:
        if table in table_names:
            columns = inspector.get_columns(table)
            print(f"✅ Tabla '{table}' - {len(columns)} columnas")
        else:
            print(f"❌ Tabla '{table}' NO ENCONTRADA")
    
    # Probar consulta directa
    print("\n🔧 Probando consultas directas...")
    db = SessionLocal()
    
    try:
        # Test subscription table specifically
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='subscriptions';")).fetchone()
        if result:
            print("✅ Tabla 'subscriptions' existe en SQLite")
            
            # Count records
            count = db.execute(text("SELECT COUNT(*) FROM subscriptions")).fetchone()[0]
            print(f"📊 Registros en subscriptions: {count}")
            
        else:
            print("❌ Tabla 'subscriptions' NO existe en SQLite")
            
    except Exception as e:
        print(f"❌ Error en consulta: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
