"""
Script para inicializar la base de datos y crear las tablas
"""
from sqlalchemy import create_engine
from app import Base, DATABASE_URL
from app.models import Cryptocurrency, CryptoMetrics, UserProfile, PortfolioRecommendation, Subscription
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Crear todas las tablas de la base de datos"""
    try:
        engine = create_engine(DATABASE_URL)
        
        print("🔄 Creando tablas de la base de datos...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente:")
        print("   • cryptocurrencies")
        print("   • crypto_metrics") 
        print("   • user_profiles")
        print("   • portfolio_recommendations")
        print("   • subscriptions")
        
    except Exception as e:
        print(f"❌ Error creando base de datos: {e}")
        print("💡 Asegúrate de que PostgreSQL esté ejecutándose y las credenciales sean correctas")

if __name__ == "__main__":
    create_database()
