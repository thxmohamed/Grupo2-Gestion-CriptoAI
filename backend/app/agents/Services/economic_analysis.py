from typing import List, Dict, Any
import pandas as pd
from ..Repository.economic_analysis_repo import EconomicAnalysisRepo
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EconomicAnalysisAgent:
    """
    Agente Análisis económico - Guarda monedas con métricas actualizadas.
    Para cada usuario, optimiza las ganancias posibles de cada moneda según 
    sus métricas y muestra las mejores 5.
    """
    
    def __init__(self):
        self.repo = EconomicAnalysisRepo()
    
    def calculate_ema(self, data: List[float], period: int = 14) -> float:
        """
        Calcula la última Exponential Moving Average (EMA) de una lista de datos.
        
        Args:
            data (List[float]): La lista de valores sobre los que calcular la EMA (e.g., log-retornos).
            period (int): El período de la EMA (N en la fórmula alfa = 2 / (N + 1)).
            
        Returns:
            float: El último valor de la EMA.
        """
        if not data:
            return 0.0
        
        # Necesitamos al menos 'period' puntos para inicializar la EMA correctamente.
        # Si no hay suficientes, calculamos una media simple de los datos disponibles
        # o devolvemos el último valor si es posible.
        if len(data) < period:
            return np.mean(data) if data else 0.0 # O podrías lanzar un error/retornar 0

        # El primer valor de la EMA se inicializa con la media simple de los primeros 'period' datos
        ema = np.mean(data[:period])
        alpha = 2 / (period + 1)

        # Aplicar la fórmula EMA para el resto de los datos
        for i in range(period, len(data)):
            ema = (data[i] * alpha) + (ema * (1 - alpha))
            
        return float(ema)

    def calculate_expected_return(self, prices_list: List[float], ema_period: int = 14) -> float:
        """
        Calcula el retorno esperado utilizando una Media Exponencial Suavizada (EMA)
        de los log-retornos históricos.
        
        Args:
            prices_list (List[float]): Una lista de precios históricos.
            ema_period (int): El período para la EMA de los log-retornos (por defecto 30 días).
            
        Returns:
            float: El retorno esperado calculado como el último valor de la EMA de los log-retornos,
                   expresado como porcentaje.
        """
        if len(prices_list) < 2:
            return 0.0 # No se pueden calcular retornos con menos de 2 precios

        # Calcular los log-retornos para todo el historial disponible
        log_returns = np.diff(np.log(prices_list))
        
        # Si no hay suficientes log-retornos para el período EMA,
        # calculamos la media simple de los log-retornos disponibles.
        # Esto sucede si len(prices_list) es menor que (ema_period + 1).
        if len(log_returns) < ema_period:
            expected_return_raw = np.mean(log_returns) if log_returns.size > 0 else 0.0
        else:
            # Calcular la EMA de los log-retornos
            expected_return_raw = self.calculate_ema(log_returns.tolist(), ema_period)
        
        # Multiplicar por 100 para expresarlo como porcentaje
        return float(expected_return_raw * 100)
    
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
        """Analizar datos y guardar métricas en la base de datos usando el repositorio"""
        try:
            # Procesar datos de CoinGecko (más completos)
            for coin in coin_data.get('coingecko', []):
                symbol = coin['symbol'].upper()
                
                # Usar repositorio para crear/actualizar cryptocurrency
                crypto_data = {
                    'symbol': symbol,
                    'name': coin['name'],
                    'current_price': coin.get('current_price', 0),
                    'market_cap': coin.get('market_cap', 0),
                    'volume_24h': coin.get('total_volume', 0),
                    'price_change_24h': coin.get('price_change_24h', 0),
                    'price_change_percentage_24h': coin.get('price_change_percentage_24h', 0),
                    'circulating_supply': coin.get('circulating_supply', 0),
                    'total_supply': coin.get('total_supply', 0),
                    'ath': coin.get('ath', 0),
                    'ath_change_percentage': coin.get('ath_change_percentage', 0),
                    'atl': coin.get('atl', 0),
                    'atl_change_percentage': coin.get('atl_change_percentage', 0)
                }
                
                crypto_id = self.repo.create_or_update_cryptocurrency(crypto_data)
                
                # Calcular métricas avanzadas
                # Para este ejemplo, usamos datos simulados de precios históricos
                # En implementación real, necesitarías obtener datos históricos
                historical_prices = [crypto_data['current_price'] * (1 + np.random.normal(0, 0.02)) 
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
                
                # Usar repositorio para crear/actualizar métricas
                metrics_data = {
                    'crypto_id': crypto_id,
                    'symbol': symbol,
                    'volatility': volatility,
                    'rsi': rsi,
                    'ma_7': ma_data['ma_7'],
                    'ma_30': ma_data['ma_30'],
                    'volume_trend': volume_trend,
                    'market_sentiment': market_sentiment,
                    'stability_score': stability_score,
                    'growth_potential': growth_potential,
                    'risk_level': risk_level
                }
                
                self.repo.create_or_update_metrics(metrics_data)
            
            print(f"Métricas actualizadas para {len(coin_data.get('coingecko', []))} monedas")
            
        except Exception as e:
            print(f"Error analizando y guardando datos: {e}")
    
    def get_user_relevant_metrics(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Obtener métricas relevantes para un usuario específico usando el repositorio
        Args:
            user_data (Dict[str, Any]): Datos del usuario que incluyen preferencias de inversión.
        Returns:
            List[Dict[str, Any]]: Lista de métricas filtradas relevantes para el usuario.
        """
        print("Obteniendo métricas relevantes para el usuario...")
        try:
            risk_tolerance = user_data.get('risk_tolerance', 'moderate')
            investment_horizon = user_data.get('investment_horizon', 'medium')
            
            # Construir filtros basados en preferencias del usuario
            filters = {}
            
            # Filtrar por nivel de riesgo
            if risk_tolerance == 'conservative':
                filters['risk_levels'] = ['low', 'medium']
                filters['min_stability_score'] = 60
            elif risk_tolerance == 'moderate':
                filters['risk_levels'] = ['low', 'medium', 'high']
            # Para 'aggressive' no filtramos por riesgo
            
            # Definir ordenamiento
            if investment_horizon == 'short':
                filters['order_by'] = 'growth_potential'
            elif investment_horizon == 'long':
                filters['order_by'] = 'stability_score'
            else:  # medium
                filters['order_by'] = 'combined'
            
            filters['limit'] = 20  # Obtener top 20 para que el optimizador elija
            # Usar repositorio para obtener métricas filtradas
            results = self.repo.get_user_relevant_metrics(filters)
            return results
            
        except Exception as e:
            print(f"Error obteniendo métricas para usuario: {e}")
            return []
    
    def get_historical_from_db(self, symbol: str, source: str) -> List[float]:
        """
        Obtiene datos históricos de la base de datos para un símbolo y fuente específicos.
        Retorna una lista de precios (close) para compatibilidad con métodos existentes.
        """
        historical_data = self.repo.get_historical_from_db(symbol, source)
        return [data['close'] for data in historical_data]

    def calculate_economic_metrics_from_db(self, symbol: str, source: str) -> Dict[str, Any]:
        """
        Calcula métricas económicas avanzadas a partir de datos históricos obtenidos de la base de datos.
        
        Args:
            symbol (str): Símbolo de la criptomoneda.
            source (str): Fuente de los datos históricos (e.g., "binance").

        Returns:
            Dict[str, Any]: Diccionario con métricas calculadas.
        """
        historical_data = self.repo.get_historical_from_db(symbol, source)
        return self.calculate_economic_metrics(historical_data, {})
    def save_economic_metrics(self, symbol: str, metrics: Dict[str, Any]) -> None:
        """
        Guarda las métricas económicas en la base de datos.
        """
        return self.repo.save_economic_metrics(symbol, metrics)
    def get_all_symbols(self) -> List[str]:
        """
        Obtiene todos los símbolos únicos de criptomonedas en la base de datos.
        
        Args:

        Returns:
            List[str]: Lista de símbolos únicos.
        """
        return self.repo.get_all_symbols()
    def calculate_and_save_metrics(self) -> str:
        """
        Calcula y guarda las métricas económicas para todos los símbolos usando el repositorio.
        Args:
            source (str): Fuente de datos para los precios históricos. Por defecto es "binance".
        """
        try:
            symbols = self.get_all_symbols()
        except Exception as e:
            logger.error(f"Error obteniendo símbolos de la base de datos: {e}")
            return
            
        for symbol in symbols:
            
            # Obtener datos históricos como lista de diccionarios
            historical_data = self.repo.get_historical_from_db(symbol)
            
            if historical_data:
                # Usar el método que espera el formato correcto
                metrics = self.compute_single_coin_metrics(historical_data, symbol)
                self.save_economic_metrics(symbol, metrics)
                logger.info(f"Métricas económicas guardadas para {symbol}")
            else:
                logger.warning(f"No hay datos históricos para {symbol}")
        return "Métricas económicas calculadas y guardadas para todos los símbolos."
    def compute_single_coin_metrics(self, historical_data: List[Dict[str, Any]], symbol: str) -> Dict[str, Any]:
        """
        Calcula métricas cuantitativas de inversión y riesgo para una ÚNICA moneda,
        basándose en sus datos históricos, utilizando una volatilidad más precisa.
        """
        if not historical_data:
            return {}

        df = pd.DataFrame(historical_data)
        print("se obtuvo el dataframe")
        min_required_data = 14
        df['price'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        if len(df['price']) < min_required_data:
            print(f"Advertencia: No hay suficientes datos históricos ({len(df)} puntos) para cálculos completos. Se necesitan al menos {min_required_data}.")
            return {}

        prices_list = df['price'].tolist()
        volumes_list = df['volume'].tolist() 
        print("se obtuvieron las listas de precios y volumenes")
        latest_data = df.iloc[-1]
        current_price = latest_data.get('price', 0)
        market_cap = latest_data.get('market_cap', 0)
        volume_24h = latest_data.get('volume', 0)
        name = latest_data.get("name", "")
        print("se obtuvieron los datos mas recientes")
        price_change_24h = ((df['price'].iloc[-1] - df['price'].iloc[-2]) / df['price'].iloc[-2]) * 100 if len(df) >= 2 and df['price'].iloc[-2] != 0 else 0
        price_change_7d = ((df['price'].iloc[-1] - df['price'].iloc[-min(7, len(df))] ) / df['price'].iloc[-min(7, len(df))]) * 100 if len(df) >= 7 and df['price'].iloc[-min(7, len(df))] != 0 else 0
        price_change_30d = ((df['price'].iloc[-1] - df['price'].iloc[-min(30, len(df))] ) / df['price'].iloc[-min(30, len(df))]) * 100 if len(df) >= 30 and df['price'].iloc[-min(30, len(df))] != 0 else 0
        print("se calcularon los cambios de precio")
        # --- Calcular métricas intermedias usando las nuevas funciones ---
        rsi = self.calculate_rsi(prices_list)
        volatility = self.calculate_volatility(prices_list)
        mas = self.calculate_moving_averages(prices_list)
        print("se calcularon las medias moviles")
        volume_trend = ((volumes_list[-1] - volumes_list[-2]) / volumes_list[-2]) * 100 if len(volumes_list) >= 2 and volumes_list[-2] != 0 else 0
        print("se calculo la tendencia de volumen")
        market_sentiment = self.determine_market_sentiment(price_change_24h, rsi, volume_trend)
        stability_score = self.calculate_stability_score(volatility, price_change_7d)
        print("se determinaron el sentimiento del mercado y el score de estabilidad")
        market_cap_rank = latest_data.get("market_cap_rank", 1000)
        print("se obtuvo el market cap rank")
        growth_potential = self.calculate_growth_potential(price_change_7d, price_change_30d, market_cap_rank, rsi)
        risk_level = self.determine_risk_level(volatility, stability_score)
        print("se calcularon el potencial de crecimiento y el nivel de riesgo")
        # === RETORNO ESPERADO ===
        expected_return = self.calculate_expected_return(prices_list)
        print("se calculo el retorno esperado")
        max_market_cap = df['market_cap'].max() if 'market_cap' in df.columns and df['market_cap'].max() > 0 else 1
        max_volume = df['volume'].max() if df['volume'].max() > 0 else 1
        print("se obtuvieron los maximos de market cap y volumen")
        # === SCORE DE INVERSIÓN ===
        market_cap_score = min(30, (market_cap / max_market_cap) * 30) if max_market_cap > 1 else 0
        momentum_score = max(-15, min(15, price_change_24h * 2))
        liquidity_score = min(25, (volume_24h / max_volume) * 25) if max_volume > 1 else 0
        print("se calcularon los scores de market cap, momentum y liquidez")
        investment_score = momentum_score + liquidity_score + (stability_score / 3.33) + (growth_potential / 100 * 20) #+ market_cap_score
        investment_score = min(100.0, max(0.0, investment_score))
        print("se calculo el score de inversion")
        # === SCORE DE RIESGO ===
        volatility_risk = volatility * 1.5 
        market_cap_risk = (1 - market_cap / max_market_cap) * 25 if max_market_cap > 1 else 25
        volume_ratio = volume_24h / max(market_cap, 1)
        liquidity_risk = max(0, 10 - (volume_ratio * 1000000))
        momentum_risk = max(0, abs(price_change_24h) - 3) * 2
        print("se calcularon los scores de riesgo")
        is_stablecoin = symbol in ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'USDD', 'FRAX', 'LUSD']
        if is_stablecoin:
            risk_score = volatility_risk * 0.5 + momentum_risk * 0.3
            risk_score = min(8.0, risk_score)
        else:
            risk_score = volatility_risk + momentum_risk +market_cap_risk + liquidity_risk
            risk_score = min(100.0, risk_score)
        print("se calcularon los datos")
        return {
            "symbol": symbol,
            "name": name,
            "current_price": current_price,
            "market_cap": market_cap,
            "price_change_24h": round(price_change_24h, 3),
            "price_change_7d": round(price_change_7d, 3),
            "price_change_30d": round(price_change_30d, 3),
            "volume_24h": volume_24h,
            "expected_return": round(expected_return, 3),
            "volatility": round(volatility, 2),
            "rsi": round(rsi, 2),
            "ma_7": round(mas['ma_7'], 2),
            "ma_30": round(mas['ma_30'], 2),
            "investment_score": round(investment_score, 2),
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "liquidity_ratio": round(volume_ratio * 100, 4),
            "market_sentiment": market_sentiment,
            "stability_score": round(stability_score, 2),
            "growth_potential": round(growth_potential, 2)
        }
    def compute_single_coin_metrics_from_db(self, symbol: str) -> Dict[str, Any]:
        """
        Calcula métricas cuantitativas de inversión y riesgo para una ÚNICA moneda,
        basándose en sus datos históricos obtenidos de la base de datos.
        """
        historical_data = self.repo.get_historical_from_db(symbol)
        print(f"Se obtuvo: {len(historical_data)} datos de la base de datos para {symbol}")
        return self.compute_single_coin_metrics(historical_data, symbol)
    def get_coins_metrics(self) -> Dict[str, Any]:
        """
        Obtiene las métricas de todas las monedas desde la base de datos.
        Returns:
            Dict[str, Any]: Un diccionario con las métricas de todas las monedas.
        """
        logger.info("Obteniendo métricas de todas las monedas desde la base de datos...")
        symbols = self.get_all_symbols()
        metrics = {}
        symbols_not_found = []
        
        for symbol in symbols:
            try:
                metrics[symbol] = self.repo.get_coin_metrics(symbol)
                logger.debug(f"Métricas obtenidas exitosamente para {symbol}")
            except ValueError as e:
                symbols_not_found.append(symbol)
                logger.warning(f"No se encontraron métricas para {symbol}: {e}")
                continue
            except Exception as e:
                symbols_not_found.append(symbol)
                logger.error(f"Error inesperado obteniendo métricas para {symbol}: {e}")
                continue
        
        logger.info(f"Métricas obtenidas para {len(metrics)} de {len(symbols)} símbolos")
        if symbols_not_found:
            logger.warning(f"Símbolos sin métricas: {symbols_not_found}")
            
        return metrics
    def get_coin_metrics(self, symbol: str):
        """
        Obtiene las métricas de una única moneda desde la base de datos.
        Args:
            symbol (str): El símbolo de la moneda.
        Returns:
            Dict[str, Any]: Un diccionario con las métricas de la moneda.
        """
        return self.repo.get_coin_metrics(symbol)