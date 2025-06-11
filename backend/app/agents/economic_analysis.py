from typing import List, Dict, Any
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import SessionLocal
from app.models import Cryptocurrency, CryptoMetrics

class EconomicAnalysisAgent:
    """
    Agente Análisis económico - Guarda monedas con métricas actualizadas.
    Para cada usuario, optimiza las ganancias posibles de cada moneda según 
    sus métricas y muestra las mejores 5.
    """
    
    def __init__(self):
        self.db = SessionLocal()
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calcular RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return 50.0  # Valor neutral si no hay suficientes datos
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.mean(gains[-period:])
        avg_losses = np.mean(losses[-period:])
        
        if avg_losses == 0:
            return 100.0
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_volatility(self, prices: List[float]) -> float:
        """Calcular volatilidad basada en desviación estándar"""
        if len(prices) < 2:
            return 0.0
        
        returns = np.diff(prices) / prices[:-1]
        return float(np.std(returns) * 100)
    
    def calculate_moving_averages(self, prices: List[float]) -> Dict[str, float]:
        """Calcular promedios móviles"""
        if len(prices) < 7:
            return {'ma_7': prices[-1] if prices else 0, 'ma_30': prices[-1] if prices else 0}
        
        ma_7 = float(np.mean(prices[-7:]))
        ma_30 = float(np.mean(prices[-30:])) if len(prices) >= 30 else ma_7
        
        return {'ma_7': ma_7, 'ma_30': ma_30}
    
    def determine_market_sentiment(self, price_change_24h: float, rsi: float, volume_trend: float) -> str:
        """Determinar sentimiento del mercado"""
        score = 0
        
        # Análisis de precio
        if price_change_24h > 5:
            score += 2
        elif price_change_24h > 0:
            score += 1
        elif price_change_24h < -5:
            score -= 2
        elif price_change_24h < 0:
            score -= 1
        
        # Análisis RSI
        if rsi > 70:
            score -= 1  # Sobrecomprado
        elif rsi < 30:
            score += 1  # Sobrevendido
        
        # Análisis de volumen
        if volume_trend > 20:
            score += 1
        elif volume_trend < -20:
            score -= 1
        
        if score >= 2:
            return "bullish"
        elif score <= -2:
            return "bearish"
        else:
            return "neutral"
    
    def calculate_stability_score(self, volatility: float, price_change_7d: float) -> float:
        """Calcular score de estabilidad (0-100, mayor es más estable)"""
        # Invertir volatilidad (menor volatilidad = mayor estabilidad)
        volatility_score = max(0, 100 - (volatility * 2))
        
        # Penalizar cambios bruscos de precio
        price_stability = max(0, 100 - abs(price_change_7d))
        
        return (volatility_score + price_stability) / 2
    
    def calculate_growth_potential(self, price_change_7d: float, price_change_30d: float, 
                                 market_cap_rank: int, rsi: float) -> float:
        """Calcular potencial de crecimiento (0-100)"""
        score = 50  # Valor base
        
        # Tendencia de precios
        if price_change_7d > 0 and price_change_30d > 0:
            score += 20
        elif price_change_7d > 0 or price_change_30d > 0:
            score += 10
        
        # Ranking de market cap (monedas más pequeñas tienen mayor potencial)
        if market_cap_rank > 100:
            score += 15
        elif market_cap_rank > 50:
            score += 10
        elif market_cap_rank > 20:
            score += 5
        
        # RSI (buscar oportunidades de entrada)
        if 30 <= rsi <= 50:
            score += 15
        elif rsi < 30:
            score += 10
        
        return min(100, max(0, score))
    
    def determine_risk_level(self, volatility: float, stability_score: float) -> str:
        """Determinar nivel de riesgo"""
        if volatility > 15 or stability_score < 30:
            return "high"
        elif volatility > 8 or stability_score < 60:
            return "medium"
        else:
            return "low"
    
    async def analyze_and_store(self, coin_data: Dict[str, Any]) -> None:
        """Analizar datos y guardar métricas en la base de datos"""
        try:
            # Procesar datos de CoinGecko (más completos)
            for coin in coin_data.get('coingecko', []):
                # Actualizar o crear cryptocurrency
                crypto = self.db.query(Cryptocurrency).filter(
                    Cryptocurrency.symbol == coin['symbol'].upper()
                ).first()
                
                if not crypto:
                    crypto = Cryptocurrency(
                        symbol=coin['symbol'].upper(),
                        name=coin['name']
                    )
                    self.db.add(crypto)
                
                # Actualizar datos básicos
                crypto.current_price = coin.get('current_price', 0)
                crypto.market_cap = coin.get('market_cap', 0)
                crypto.volume_24h = coin.get('total_volume', 0)
                crypto.price_change_24h = coin.get('price_change_24h', 0)
                crypto.price_change_percentage_24h = coin.get('price_change_percentage_24h', 0)
                crypto.circulating_supply = coin.get('circulating_supply', 0)
                crypto.total_supply = coin.get('total_supply', 0)
                crypto.ath = coin.get('ath', 0)
                crypto.ath_change_percentage = coin.get('ath_change_percentage', 0)
                crypto.atl = coin.get('atl', 0)
                crypto.atl_change_percentage = coin.get('atl_change_percentage', 0)
                
                # Calcular métricas avanzadas
                # Para este ejemplo, usamos datos simulados de precios históricos
                # En implementación real, necesitarías obtener datos históricos
                historical_prices = [crypto.current_price * (1 + np.random.normal(0, 0.02)) 
                                   for _ in range(30)]
                
                volatility = self.calculate_volatility(historical_prices)
                rsi = self.calculate_rsi(historical_prices)
                ma_data = self.calculate_moving_averages(historical_prices)
                
                # Calcular tendencia de volumen (simplificado)
                volume_trend = coin.get('price_change_percentage_24h', 0) * 0.5
                
                market_sentiment = self.determine_market_sentiment(
                    coin.get('price_change_percentage_24h', 0), rsi, volume_trend
                )
                
                stability_score = self.calculate_stability_score(
                    volatility, coin.get('price_change_percentage_7d_in_currency', 0)
                )
                
                growth_potential = self.calculate_growth_potential(
                    coin.get('price_change_percentage_7d_in_currency', 0),
                    coin.get('price_change_percentage_30d_in_currency', 0),
                    coin.get('market_cap_rank', 999),
                    rsi
                )
                
                risk_level = self.determine_risk_level(volatility, stability_score)
                
                # Actualizar o crear métricas
                metrics = self.db.query(CryptoMetrics).filter(
                    CryptoMetrics.symbol == coin['symbol'].upper()
                ).first()
                
                if not metrics:
                    metrics = CryptoMetrics(
                        crypto_id=crypto.id,
                        symbol=coin['symbol'].upper()
                    )
                    self.db.add(metrics)
                
                metrics.volatility = volatility
                metrics.rsi = rsi
                metrics.ma_7 = ma_data['ma_7']
                metrics.ma_30 = ma_data['ma_30']
                metrics.volume_trend = volume_trend
                metrics.market_sentiment = market_sentiment
                metrics.stability_score = stability_score
                metrics.growth_potential = growth_potential
                metrics.risk_level = risk_level
            
            self.db.commit()
            print(f"Métricas actualizadas para {len(coin_data.get('coingecko', []))} monedas")
            
        except Exception as e:
            self.db.rollback()
            print(f"Error analizando y guardando datos: {e}")
        finally:
            self.db.close()
    
    def get_user_relevant_metrics(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Obtener métricas relevantes para un usuario específico"""
        try:
            risk_tolerance = user_data.get('risk_tolerance', 'moderate')
            investment_horizon = user_data.get('investment_horizon', 'medium')
            
            # Construir query basada en preferencias del usuario
            query = self.db.query(Cryptocurrency, CryptoMetrics).join(
                CryptoMetrics, Cryptocurrency.symbol == CryptoMetrics.symbol
            )
            
            # Filtrar por nivel de riesgo
            if risk_tolerance == 'conservative':
                query = query.filter(CryptoMetrics.risk_level.in_(['low', 'medium']))
                query = query.filter(CryptoMetrics.stability_score >= 60)
            elif risk_tolerance == 'moderate':
                query = query.filter(CryptoMetrics.risk_level.in_(['low', 'medium', 'high']))
            # Para 'aggressive' no filtramos por riesgo
            
            # Ordenar por potencial de crecimiento y estabilidad
            if investment_horizon == 'short':
                query = query.order_by(CryptoMetrics.growth_potential.desc())
            elif investment_horizon == 'long':
                query = query.order_by(CryptoMetrics.stability_score.desc())
            else:  # medium
                query = query.order_by(
                    (CryptoMetrics.growth_potential + CryptoMetrics.stability_score).desc()
                )
            
            results = query.limit(20).all()  # Obtener top 20 para que el optimizador elija
            
            return [
                {
                    'symbol': crypto.symbol,
                    'name': crypto.name,
                    'current_price': crypto.current_price,
                    'market_cap': crypto.market_cap,
                    'price_change_24h': crypto.price_change_percentage_24h,
                    'volatility': metrics.volatility,
                    'rsi': metrics.rsi,
                    'market_sentiment': metrics.market_sentiment,
                    'stability_score': metrics.stability_score,
                    'growth_potential': metrics.growth_potential,
                    'risk_level': metrics.risk_level
                }
                for crypto, metrics in results
            ]
            
        except Exception as e:
            print(f"Error obteniendo métricas para usuario: {e}")
            return []
        finally:
            self.db.close()
