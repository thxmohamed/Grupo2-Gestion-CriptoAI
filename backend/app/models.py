from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, func, Numeric, BigInteger
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from app import Base


class Cryptocurrency(Base):
    __tablename__ = "cryptocurrencies"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    name_ = Column(String(100), nullable=False)
    current_price = Column(Numeric(20,8), nullable=False)
    market_cap = Column(Numeric(20,2))
    volume_24h = Column(Numeric(20,2))
    price_change_24h = Column(Numeric(20,8))
    price_change_percentage_24h = Column(Numeric(10,4))
    circulating_supply = Column(Numeric(20,2))
    total_supply = Column(Numeric(20,2))
    ath = Column(Numeric(20,8))  # All time high
    ath_change_percentage = Column(Numeric(10,4))
    atl = Column(Numeric(20,8))  # All time low
    atl_change_percentage = Column(Numeric(10,4))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CryptoMetrics(Base):
    __tablename__ = "crypto_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True, unique=True)
    current_price = Column(Numeric(20,10))
    market_cap = Column(BigInteger)
    price_change_24h = Column(Numeric(10,3))
    price_change_7d = Column(Numeric(10,3))
    price_change_30d = Column(Numeric(10,3))
    volume_24h = Column(BigInteger)  # Cambiado de volume_trend
    expected_return = Column(Numeric(10,3))
    volatility = Column(Numeric(10,2))
    rsi = Column(Numeric(10,2))  # Relative Strength Index
    ma_7 = Column(Numeric(20,8))  # Moving Average 7 days
    ma_30 = Column(Numeric(20,8))  # Moving Average 30 days
    investment_score = Column(Numeric(10,2))
    risk_score = Column(Numeric(10,2))
    risk_level = Column(String(50))  # Ajustada longitud
    liquidity_ratio = Column(Numeric(10,4))  # Agregado
    market_sentiment = Column(String(50))  # Ajustada longitud
    stability_score = Column(Numeric(10,2))  # Score de estabilidad
    growth_potential = Column(Numeric(10,2))  # Potencial de crecimiento
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(100), unique=True, index=True, nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=True)
    risk_tolerance = Column(String(10), nullable=False, default="moderate")
    investment_amount = Column(Numeric(15,2), nullable=False, default=1000.0)
    investment_horizon = Column(String(20), nullable=False, default="medium")
    preferred_sectors = Column(Text)  # JSON string
    is_subscribed = Column(Boolean, default=False)
    wallet_balance = Column(Numeric(15,2), default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class PortfolioRecommendation(Base):
    __tablename__ = "portfolio_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    recommended_coins = Column(Text)  # JSON string with top 5 coins
    allocation_percentages = Column(Text)  # JSON string with allocation %
    expected_return = Column(Numeric(10,4))
    risk_score = Column(Numeric(5,2))
    confidence_level = Column(Numeric(5,2))
    reasoning = Column(Text)  # Explicación de la recomendación
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    email = Column(String(255))
    phone = Column(String(20))
    chat_id = Column(String(50))
    notification_type = Column(String(20))  # email, sms, both
    frequency = Column(String(20))  # daily, weekly, monthly
    is_active = Column(Boolean, default=True)
    telegram_pending = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class HistoricalPrice(Base):
    __tablename__ = "historical_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True, nullable=False)  # Ej: BTC, ETH
    source = Column(String(20), nullable=False)  # 'binance', 'coingecko'
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Numeric(20,8), nullable=True)   # Solo Binance
    high = Column(Numeric(20,8), nullable=True)   # Solo Binance
    low = Column(Numeric(20,8), nullable=True)    # Solo Binance
    close = Column(Numeric(20,8), nullable=False) # Binance (close) o CoinGecko (price)
    volume = Column(Numeric(20,2), nullable=True) # Solo Binance
    market_cap = Column(Numeric(20,2), nullable=True)  # Solo CoinGecko
    created_at = Column(DateTime(timezone=True), server_default=func.now())
