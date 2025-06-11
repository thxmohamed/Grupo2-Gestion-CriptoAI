"""
Script para inicializar la base de datos SQLite para desarrollo
"""
from sqlalchemy import create_engine
from app import Base
from app.models import Cryptocurrency, CryptoMetrics, UserProfile, PortfolioRecommendation, Subscription
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite for development
SQLITE_DATABASE_URL = "sqlite:///./criptoai.db"

def create_database():
    """Crear todas las tablas de la base de datos SQLite"""
    try:
        engine = create_engine(
            SQLITE_DATABASE_URL, 
            connect_args={"check_same_thread": False}
        )
        
        print("🔄 Creando base de datos SQLite para desarrollo...")
        Base.metadata.create_all(bind=engine)
        print("✅ Base de datos SQLite creada exitosamente:")
        print("   • Archivo: criptoai.db")
        print("   • Tablas creadas:")
        print("     - cryptocurrencies")
        print("     - crypto_metrics") 
        print("     - user_profiles")
        print("     - portfolio_recommendations")
        print("     - subscriptions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando base de datos: {e}")
        return False

def populate_sample_data():
    """Poblar la base de datos con datos de muestra"""
    from sqlalchemy.orm import sessionmaker
    from datetime import datetime
    
    try:
        engine = create_engine(
            SQLITE_DATABASE_URL, 
            connect_args={"check_same_thread": False}
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("🔄 Poblando base de datos con datos de muestra...")
          # Crear usuarios de prueba
        sample_users = [
            UserProfile(
                user_id="user_conservador",
                risk_tolerance="conservative",
                investment_amount=1000.0,
                investment_horizon="long",
                preferred_sectors='["bitcoin", "ethereum"]',
                is_subscribed=True
            ),
            UserProfile(
                user_id="user_moderado",
                risk_tolerance="moderate",
                investment_amount=5000.0,
                investment_horizon="medium", 
                preferred_sectors='["defi", "smart-contracts"]',
                is_subscribed=True
            ),
            UserProfile(
                user_id="user_agresivo",
                risk_tolerance="aggressive",
                investment_amount=10000.0,
                investment_horizon="short",
                preferred_sectors='["altcoins", "gaming"]',
                is_subscribed=False
            )
        ]
        
        for user in sample_users:
            db.add(user)
          # Crear criptomonedas de prueba
        sample_cryptos = [
            Cryptocurrency(
                symbol="BTC",
                name="Bitcoin",
                current_price=50000.0,
                market_cap=1000000000000.0,
                volume_24h=20000000000.0,
                price_change_24h=2.5,
                price_change_percentage_24h=2.5,
                circulating_supply=19000000.0,
                total_supply=21000000.0,
                ath=69000.0,
                ath_change_percentage=-27.5,
                atl=0.01,
                atl_change_percentage=50000000.0
            ),
            Cryptocurrency(
                symbol="ETH", 
                name="Ethereum",
                current_price=3000.0,
                market_cap=400000000000.0,
                volume_24h=15000000000.0,
                price_change_24h=1.8,
                price_change_percentage_24h=1.8,
                circulating_supply=120000000.0,
                total_supply=120000000.0,
                ath=4800.0,
                ath_change_percentage=-37.5,
                atl=0.42,
                atl_change_percentage=714185.7
            ),
            Cryptocurrency(
                symbol="BNB",
                name="Binance Coin", 
                current_price=400.0,
                market_cap=60000000000.0,
                volume_24h=2000000000.0,
                price_change_24h=-0.5,
                price_change_percentage_24h=-0.5,
                circulating_supply=150000000.0,
                total_supply=200000000.0,
                ath=690.0,
                ath_change_percentage=-42.0,
                atl=0.1,
                atl_change_percentage=400000.0
            )
        ]
        
        for crypto in sample_cryptos:
            db.add(crypto)
              # Crear suscripciones de prueba
        sample_subscriptions = [
            Subscription(
                user_id="user_conservador",
                email="conservador@test.com",
                notification_type="email",
                frequency="daily",
                is_active=True
            ),
            Subscription(
                user_id="user_moderado",
                email="moderado@test.com", 
                notification_type="email",
                frequency="weekly",
                is_active=True
            )
        ]
        
        for subscription in sample_subscriptions:
            db.add(subscription)
        
        db.commit()
        db.close()
        
        print("✅ Datos de muestra agregados exitosamente:")
        print("   • 3 usuarios de prueba")
        print("   • 3 criptomonedas (BTC, ETH, BNB)")
        print("   • 2 suscripciones de prueba")
        
        return True
        
    except Exception as e:
        print(f"❌ Error poblando datos de muestra: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

if __name__ == "__main__":
    print("🚀 Inicializando base de datos de desarrollo...")
    if create_database():
        if populate_sample_data():
            print("\n🎉 Base de datos lista para desarrollo!")
            print("📁 Ubicación: ./criptoai.db")
        else:
            print("\n⚠️  Base de datos creada pero falló la población de datos")
    else:
        print("\n❌ Falló la creación de la base de datos")
