"""
Configuración centralizada para el sistema CriptoAI
"""
import os
from typing import Dict, Any

class APIConfig:
    """Configuración para APIs externas"""
    
    # CoinGecko API
    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
    COINGECKO_RATE_LIMIT = 10  # Peticiones por minuto (conservador)
    COINGECKO_CACHE_TTL = 300  # 5 minutos
    COINGECKO_TIMEOUT = 30
    COINGECKO_MAX_RETRIES = 3
    COINGECKO_BACKOFF_MULTIPLIER = 2
    
    # Binance API  
    BINANCE_BASE_URL = "https://api.binance.com"
    BINANCE_RATE_LIMIT = 1200  # Peticiones por minuto
    BINANCE_CACHE_TTL = 60  # 1 minuto
    BINANCE_TIMEOUT = 15
    BINANCE_MAX_RETRIES = 3
    
    # Configuración de caché
    CACHE_ENABLED = True
    CACHE_DEFAULT_TTL = 300
    CACHE_MAX_SIZE = 1000
    
    # Configuración de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class DatabaseConfig:
    """Configuración de base de datos"""
    
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./criptoai.db")
    DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"

class AppConfig:
    """Configuración general de la aplicación"""
    
    APP_NAME = "CriptoAI Backend"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Configuración del servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    RELOAD = os.getenv("RELOAD", "True").lower() == "true"
    
    # Configuración de CORS
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

# Configuración global
config = {
    'api': APIConfig,
    'database': DatabaseConfig,
    'app': AppConfig
}

def get_config() -> Dict[str, Any]:
    """Obtener toda la configuración"""
    return config

def get_api_config() -> APIConfig:
    """Obtener configuración de APIs"""
    return APIConfig

def get_database_config() -> DatabaseConfig:
    """Obtener configuración de base de datos"""
    return DatabaseConfig

def get_app_config() -> AppConfig:
    """Obtener configuración de la aplicación"""
    return AppConfig
