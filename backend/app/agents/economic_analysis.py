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
        """
        Calcula el RSI (Relative Strength Index) siguiendo el planteamiento matemático
        con promedios suavizados exponencialmente (SMMA).

        Args:
            prices (List[float]): Una lista de precios de cierre.
            period (int): El período para el cálculo del RSI (N en la fórmula matemática).
                          Por defecto es 14.

        Returns:
            float: El valor del RSI. Retorna 50.0 si no hay suficientes datos
                   para el primer cálculo del promedio, y 100.0 si las pérdidas
                   promedio son cero.
        """
        if len(prices) < period + 1:
            return 50.0  # Valor neutral si no hay suficientes datos para el primer cálculo

        # Calcula las ganancias (U) y pérdidas (D) para cada período
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        # Inicializa las medias suavizadas (SMMA)
        # Para el primer período (t <= N), se usa un promedio simple
        initial_gains = np.mean(gains[:period])
        initial_losses = np.mean(losses[:period])

        # Si las pérdidas iniciales son 0, RS es infinito, RSI es 100
        if initial_losses == 0:
            current_avg_gains = initial_gains
            current_avg_losses = 0.0 # Aseguramos que sea 0.0 para el cálculo posterior
        else:
            current_avg_gains = initial_gains
            current_avg_losses = initial_losses

        # Aplica la media móvil exponencial suavizada para t > N
        for i in range(period, len(gains)):
            current_avg_gains = ((period - 1) * current_avg_gains + gains[i]) / period
            current_avg_losses = ((period - 1) * current_avg_losses + losses[i]) / period

        # Calcula la fuerza relativa (RS)
        if current_avg_losses == 0:
            return 100.0  # Si las pérdidas suavizadas son 0, RSI es 100

        rs = current_avg_gains / current_avg_losses

        # Finalmente, calcula el RSI
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_volatility(self, prices: List[float]) -> float:
        """
        Calcula la volatilidad basada en la desviación estándar de los log-retornos,
        siguiendo el planteamiento matemático.

        Args:
            prices (List[float]): Una lista de precios de cierre.

        Returns:
            float: La volatilidad calculada como el porcentaje de la desviación estándar
                   de los log-retornos. Retorna 0.0 si no hay suficientes datos.
        """
        if len(prices) < 2:
            return 0.0 # No se puede calcular el retorno con menos de 2 precios

        # Calcula los log-retornos
        # r(t) = ln(P(t) / P(t-1))
        # np.log(prices[1:] / prices[:-1]) calcula ln(P(t)) para t de 1 a N
        # dividido por ln(P(t-1)) para t de 1 a N
        log_returns = np.diff(np.log(prices))
        
        # Calcula la desviación estándar de los log-retornos
        # Multiplica por 100 para expresarlo como porcentaje, si así se desea
        volatility = float(np.std(log_returns) * 100)
        
        return volatility
    
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
                                   for _ in range(30)] #NO SE OBTIENE HISTÓRICOS, SIMULADOS
                
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
        print("Obteniendo métricas relevantes para el usuario...")
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
    
    def compute_market_metrics(self, coins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calcula métricas cuantitativas de inversión y riesgo para cada moneda del market overview.
        Algoritmo mejorado que usa únicamente: current_price, market_cap, price_change_24h, volume_24h
        """
        results = []
        
        # Calcular percentiles para normalización relativa
        market_caps = [coin.get('market_cap', 0) for coin in coins]
        volumes = [coin.get('volume_24h', 0) for coin in coins]
        price_changes = [abs(coin.get('price_change_24h', 0)) for coin in coins]
        
        max_market_cap = max(market_caps) if market_caps else 1
        max_volume = max(volumes) if volumes else 1
        max_price_change = max(price_changes) if price_changes else 1
        
        for coin in coins:
            symbol = coin.get("symbol", "")
            name = coin.get("name", "")
            current_price = coin.get("current_price", 0)
            market_cap = coin.get("market_cap", 0)
            price_change_24h = coin.get("price_change_24h", 0)
            volume_24h = coin.get("volume_24h", 0)
            
            # === RENTABILIDAD ESPERADA ===
            # Momentum: price_change_24h ajustado por tendencia del mercado
            expected_return = price_change_24h * 1.1 if price_change_24h > 0 else price_change_24h * 0.9
            
            # === VOLATILIDAD AVANZADA ===
            # Combina: cambio de precio absoluto + ratio volumen/market_cap + factor de market cap
            abs_price_change = abs(price_change_24h)
            volume_ratio = volume_24h / max(market_cap, 1)  # Liquidez relativa
            market_cap_factor = 1 - (market_cap / max_market_cap)  # Monedas pequeñas = más volátiles
            
            # Detectar stablecoins (ajuste económico realista)
            is_stablecoin = symbol in ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'USDD', 'FRAX', 'LUSD']
            
            if is_stablecoin:
                # Stablecoins: volatilidad muy baja, basada solo en price_change
                volatility = abs_price_change * 0.2  # Factor muy bajo para stablecoins
                volatility = min(1.0, volatility)    # Máximo 1% para stablecoins
            else:
                volatility = (
                    abs_price_change * 2 +                    # Base: movimiento de precio
                    min(volume_ratio * 50, 5) +               # Liquidez factor reducido
                    market_cap_factor * 6 +                   # Market cap factor reducido
                    (3 if volume_24h < market_cap * 0.01 else 0)  # Penalizar bajo volumen
                )
                volatility = min(30.0, volatility)  # Máximo 30% para no-stablecoins
            
            # === SCORE DE INVERSIÓN ===
            # Combina: estabilidad market cap + momentum + liquidez + fundamentales
            market_cap_score = min(30, (market_cap / max_market_cap) * 30)  # Max 30 puntos
            momentum_score = max(-15, min(15, price_change_24h * 2))        # -15 a +15 puntos
            liquidity_score = min(25, (volume_24h / max_volume) * 25)       # Max 25 puntos
            stability_score = max(0, 30 - volatility)                       # Max 30 puntos
            
            investment_score = market_cap_score + momentum_score + liquidity_score + stability_score
            
            # === SCORE DE RIESGO ===
            # Factores de riesgo: volatilidad + market cap inverso + liquidez baja
            volatility_risk = volatility * 1.5                              # Peso alto a volatilidad
            market_cap_risk = (1 - market_cap / max_market_cap) * 25        # Market cap bajo = riesgo
            liquidity_risk = max(0, 10 - (volume_ratio * 1000000))          # Baja liquidez = riesgo
            momentum_risk = max(0, abs(price_change_24h) - 3) * 2           # Movimientos extremos
            
            # Ajuste especial para stablecoins
            if is_stablecoin:
                # Stablecoins tienen riesgo muy bajo por diseño
                risk_score = volatility_risk * 0.5 + momentum_risk * 0.3    # Factores muy reducidos
                risk_score = min(8.0, risk_score)                           # Máximo risk_score bajo para stablecoins
            else:
                risk_score = volatility_risk + market_cap_risk + liquidity_risk + momentum_risk
                risk_score = min(100.0, risk_score)
            
            # === NIVEL DE RIESGO ===
            # Umbrales ajustados para distribución más realista
            if risk_score >= 15 or volatility >= 10:
                risk_level = "high"
            elif risk_score >= 8 or volatility >= 5:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # === MÉTRICAS ADICIONALES ===
            # Ratio de liquidez (volumen/market_cap como %)
            liquidity_ratio = (volume_24h / max(market_cap, 1)) * 100
            
            # Market sentiment basado en price_change_24h
            if price_change_24h > 2:
                market_sentiment = "bullish"
            elif price_change_24h < -2:
                market_sentiment = "bearish"
            else:
                market_sentiment = "neutral"
            
            # Estabilidad (inverso de volatilidad, 0-100)
            stability_score = max(0, 100 - (volatility * 2))
            
            results.append({
                "symbol": symbol,
                "name": name,
                "current_price": current_price,
                "market_cap": market_cap,
                "price_change_24h": price_change_24h,
                "volume_24h": volume_24h,
                "expected_return": round(expected_return, 3),
                "volatility": round(volatility, 2),
                "investment_score": round(investment_score, 2),
                "risk_score": round(risk_score, 2),
                "risk_level": risk_level,
                "liquidity_ratio": round(liquidity_ratio, 4),
                "market_sentiment": market_sentiment,
                "stability_score": round(stability_score, 2)
            })
        
        return results
