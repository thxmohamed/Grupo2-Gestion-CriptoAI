from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, func
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from app import Base


class Cryptocurrency(Base):
    __tablename__ = "cryptocurrencies"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True)
    name = Column(String(100), nullable=False)
    current_price = Column(Float, nullable=False)
    market_cap = Column(Float)
    volume_24h = Column(Float)
    price_change_24h = Column(Float)
    price_change_percentage_24h = Column(Float)
    circulating_supply = Column(Float)
    total_supply = Column(Float)
    ath = Column(Float)  # All time high
    ath_change_percentage = Column(Float)
    atl = Column(Float)  # All time low
    atl_change_percentage = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CryptoMetrics(Base):
    __tablename__ = "crypto_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    crypto_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    volatility = Column(Float)
    rsi = Column(Float)  # Relative Strength Index
    ma_7 = Column(Float)  # Moving Average 7 days
    ma_30 = Column(Float)  # Moving Average 30 days
    volume_trend = Column(Float)
    market_sentiment = Column(String(20))  # bullish, bearish, neutral
    stability_score = Column(Float)  # Score de estabilidad (0-100)
    growth_potential = Column(Float)  # Potencial de crecimiento (0-100)
    risk_level = Column(String(10))  # low, medium, high
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
    investment_amount = Column(Float, nullable=False, default=1000.0)
    investment_horizon = Column(String(20), nullable=False, default="medium")
    preferred_sectors = Column(Text)  # JSON string
    is_subscribed = Column(Boolean, default=False)
    wallet_balance = Column(Float, default=0.0)
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
    expected_return = Column(Float)
    risk_score = Column(Float)
    confidence_level = Column(Float)
    reasoning = Column(Text)  # Explicación de la recomendación
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    email = Column(String(255))
    phone = Column(String(20))
    notification_type = Column(String(20))  # email, sms, both
    frequency = Column(String(20))  # daily, weekly, monthly
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

