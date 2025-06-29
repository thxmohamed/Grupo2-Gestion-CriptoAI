"""
Utilidades y helpers para integración con APIs de Binance y CoinGecko
"""
import asyncio
import httpx
import hashlib
import hmac
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os
from binance import Client as BinanceClient
from binance.exceptions import BinanceAPIException, BinanceOrderException
import logging
import httpx
from telegram import Bot
import os

logger = logging.getLogger(__name__)

class BinanceAPIHelper:
    """
    Helper para interactuar con la API de Binance
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key or os.getenv('BINANCE_API_KEY', 'YLF6MjQSTmYUTauXNunauPnN82OfjvwqN0kdw7iexEgvx2AQhJT5q6wrDExeuu3S')
        self.api_secret = api_secret or os.getenv('BINANCE_API_SECRET', '')
        
        # URLs base disponibles
        self.base_urls = [
            "https://api.binance.com",
            "https://api-gcp.binance.com", 
            "https://api1.binance.com",
            "https://api2.binance.com",
            "https://api3.binance.com",
            "https://api4.binance.com"
        ]
        self.current_base_url = self.base_urls[0]
        
        # Inicializar cliente de python-binance para operaciones autenticadas
        if self.api_secret:
            self.client = BinanceClient(self.api_key, self.api_secret)
        else:
            self.client = BinanceClient(self.api_key, testnet=False)
    
    async def _make_request(self, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        """Hacer petición HTTP a la API de Binance"""
        url = f"{self.current_base_url}{endpoint}"
        
        if params is None:
            params = {}
        
        if signed and self.api_secret:
            # Agregar timestamp para peticiones firmadas
            params['timestamp'] = int(time.time() * 1000)
            
            # Crear query string y firma
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            params['signature'] = signature
        
        headers = {'X-MBX-APIKEY': self.api_key} if self.api_key else {}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=headers, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"Error de red en petición a Binance: {e}")
                raise
            except httpx.HTTPStatusError as e:
                logger.error(f"Error HTTP en petición a Binance: {e.response.status_code}")
                raise
    
    async def get_exchange_info(self) -> Dict[str, Any]:
        """Obtener información sobre símbolos y reglas de trading"""
        try:
            return await self._make_request("/api/v3/exchangeInfo")
        except Exception as e:
            logger.error(f"Error obteniendo exchange info: {e}")
            return {}
    
    async def get_24hr_ticker(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Obtener estadísticas de precio 24h"""
        try:
            params = {'symbol': symbol} if symbol else {}
            result = await self._make_request("/api/v3/ticker/24hr", params)
            return [result] if symbol else result
        except Exception as e:
            logger.error(f"Error obteniendo ticker 24h: {e}")
            return []
    
    async def get_klines(self, symbol: str, interval: str = "1d", limit: int = 100, 
                        start_time: int = None, end_time: int = None) -> List[List]:
        """
        Obtener datos de velas (OHLCV)
        
        Args:
            symbol: Par de trading (ej: BTCUSDT)
            interval: Intervalo de tiempo (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)
            limit: Número de velas (máximo 1000)
            start_time: Timestamp de inicio
            end_time: Timestamp de fin
        """
        try:
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            if start_time:
                params['startTime'] = start_time
            if end_time:
                params['endTime'] = end_time
            
            return await self._make_request("/api/v3/klines", params)
        except Exception as e:
            logger.error(f"Error obteniendo klines para {symbol}: {e}")
            return []
    
    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Obtener libro de órdenes"""
        try:
            params = {'symbol': symbol, 'limit': limit}
            return await self._make_request("/api/v3/depth", params)
        except Exception as e:
            logger.error(f"Error obteniendo order book para {symbol}: {e}")
            return {}
    
    async def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener últimas operaciones"""
        try:
            params = {'symbol': symbol, 'limit': limit}
            return await self._make_request("/api/v3/trades", params)
        except Exception as e:
            logger.error(f"Error obteniendo trades para {symbol}: {e}")
            return []
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Obtener información de la cuenta (requiere API Secret)"""
        try:
            if not self.api_secret:
                raise ValueError("API Secret requerido para información de cuenta")
            
            return await self._make_request("/api/v3/account", signed=True)
        except Exception as e:
            logger.error(f"Error obteniendo info de cuenta: {e}")
            return {}
    
    async def get_historical_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener historial de trades del usuario (requiere API Secret)"""
        try:
            if not self.api_secret:
                raise ValueError("API Secret requerido para historial de trades")
            
            params = {'symbol': symbol, 'limit': limit}
            return await self._make_request("/api/v3/myTrades", params, signed=True)
        except Exception as e:
            logger.error(f"Error obteniendo historial de trades para {symbol}: {e}")
            return []
    
    def get_top_usdt_pairs(self, limit: int = 50) -> List[str]:
        """Obtener top pares USDT por volumen usando python-binance"""
        try:
            tickers = self.client.get_ticker()
            
            # Filtrar pares USDT y ordenar por volumen
            usdt_pairs = [
                ticker for ticker in tickers 
                if ticker['symbol'].endswith('USDT') and 
                float(ticker['quoteVolume']) > 1000000  # Volumen mínimo
            ]
            
            # Ordenar por volumen descendente
            usdt_pairs.sort(key=lambda x: float(x['quoteVolume']), reverse=True)
            
            return [pair['symbol'] for pair in usdt_pairs[:limit]]
            
        except Exception as e:
            logger.error(f"Error obteniendo top pares USDT: {e}")
            return []

class CoinGeckoAPIHelper:
    """
    Helper para interactuar con la API pública de CoinGecko
    """
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = None
    
    async def _make_request(self, endpoint: str, params: Dict = None, use_cache: bool = True, cache_ttl: int = 300) -> Dict:
        """Hacer petición HTTP a la API de CoinGecko con caché y manejo de rate limit"""
        if params is None:
            params = {}
        
        # Verificar caché primero si está habilitado
        if use_cache:
            cached_data = rate_limiter.get_cached_data('coingecko', endpoint, params, cache_ttl)
            if cached_data is not None:
                return cached_data
        
        url = f"{self.base_url}{endpoint}"
        max_retries = 3
        base_delay = 60  # Delay base para 429 errors
        
        for attempt in range(max_retries):
            try:
                # Esperar respetando rate limits
                await rate_limiter.wait_if_needed('coingecko')
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=30.0)
                    
                    if response.status_code == 429:
                        # Rate limit alcanzado
                        delay = base_delay * (2 ** attempt)  # Backoff exponencial
                        logger.warning(f"Rate limit 429 en CoinGecko, intento {attempt + 1}/{max_retries}, esperando {delay}s")
                        
                        # Establecer backoff para futuras peticiones
                        rate_limiter.set_backoff_delay('coingecko', delay)
                        
                        if attempt < max_retries - 1:
                            await asyncio.sleep(delay)
                            continue
                        else:
                            # Último intento fallido, devolver datos de fallback
                            logger.error("Máximo de reintentos alcanzado para CoinGecko")
                            return self._get_fallback_data(endpoint, params)
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    # Guardar en caché si la petición fue exitosa
                    if use_cache and data:
                        rate_limiter.set_cached_data('coingecko', endpoint, params, data, cache_ttl)
                    
                    return data
                    
            except httpx.RequestError as e:
                logger.error(f"Error de red en petición a CoinGecko (intento {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5 * (attempt + 1))
                    continue
                else:
                    return self._get_fallback_data(endpoint, params)
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    continue  # Ya manejado arriba
                
                logger.error(f"Error HTTP en petición a CoinGecko: {e.response.status_code}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5 * (attempt + 1))
                    continue
                else:
                    return self._get_fallback_data(endpoint, params)
        
        return self._get_fallback_data(endpoint, params)
    
    def _get_fallback_data(self, endpoint: str, params: Dict = None) -> Dict:
        """Obtener datos de fallback cuando la API falla"""
        logger.warning(f"Usando datos de fallback para endpoint: {endpoint}")
        
        if endpoint == "/coins/markets":
            # Datos de fallback para market overview
            return [
                {
                    "id": "bitcoin",
                    "symbol": "btc",
                    "name": "Bitcoin",
                    "current_price": 43000,
                    "market_cap": 850000000000,
                    "price_change_percentage_24h": 2.5,
                    "total_volume": 20000000000
                },
                {
                    "id": "ethereum", 
                    "symbol": "eth",
                    "name": "Ethereum",
                    "current_price": 2600,
                    "market_cap": 320000000000,
                    "price_change_percentage_24h": 1.8,
                    "total_volume": 12000000000
                },
                {
                    "id": "tether",
                    "symbol": "usdt", 
                    "name": "Tether",
                    "current_price": 1.0,
                    "market_cap": 95000000000,
                    "price_change_percentage_24h": 0.1,
                    "total_volume": 25000000000
                }
            ]
        
        return {}  # Fallback por defecto
    
    async def get_coins_markets(self, vs_currency: str = 'usd', order: str = 'market_cap_desc',
                               per_page: int = 100, page: int = 1, 
                               price_change_percentage: str = '1h,24h,7d,30d') -> List[Dict[str, Any]]:
        """
        Obtener lista de monedas con datos de mercado
        
        Args:
            vs_currency: Moneda de referencia (usd, eur, etc.)
            order: Orden de resultados (market_cap_desc, volume_desc, id_asc, etc.)
            per_page: Resultados por página (1-250)
            page: Número de página
            price_change_percentage: Períodos para cambio de precio
        """
        try:
            params = {
                'vs_currency': vs_currency,
                'order': order,
                'per_page': per_page,
                'page': page,
                'sparkline': False,
                'price_change_percentage': price_change_percentage
            }
            
            return await self._make_request("/coins/markets", params)
        except Exception as e:
            logger.error(f"Error obteniendo markets de CoinGecko: {e}")
            return []
    
    async def get_coin_by_id(self, coin_id: str, localization: bool = False, 
                            tickers: bool = False, market_data: bool = True,
                            community_data: bool = False, developer_data: bool = False) -> Dict[str, Any]:
        """Obtener información detallada de una moneda específica"""
        try:
            params = {
                'localization': str(localization).lower(),
                'tickers': str(tickers).lower(),
                'market_data': str(market_data).lower(),
                'community_data': str(community_data).lower(),
                'developer_data': str(developer_data).lower()
            }
            
            return await self._make_request(f"/coins/{coin_id}", params)
        except Exception as e:
            logger.error(f"Error obteniendo datos de {coin_id}: {e}")
            return {}
    
    async def get_coin_history(self, coin_id: str, date: str, localization: bool = False) -> Dict[str, Any]:
        """
        Obtener datos históricos de una moneda en una fecha específica
        
        Args:
            coin_id: ID de la moneda en CoinGecko
            date: Fecha en formato dd-mm-yyyy
            localization: Incluir datos localizados
        """
        try:
            params = {'date': date, 'localization': str(localization).lower()}
            return await self._make_request(f"/coins/{coin_id}/history", params)
        except Exception as e:
            logger.error(f"Error obteniendo historial de {coin_id} para {date}: {e}")
            return {}
    
    async def get_coin_market_chart(self, coin_id: str, vs_currency: str = 'usd', 
                                   days: str = '30', interval: str = 'daily') -> Dict[str, Any]:
        """
        Obtener datos históricos de precio, market cap y volumen
        
        Args:
            coin_id: ID de la moneda
            vs_currency: Moneda de referencia
            days: Período (1, 7, 14, 30, 90, 180, 365, max)
            interval: Intervalo de datos (daily para >1 día)
        """
        try:
            params = {
                'vs_currency': vs_currency,
                'days': days,
                'interval': interval
            }
            
            return await self._make_request(f"/coins/{coin_id}/market_chart", params)
        except Exception as e:
            logger.error(f"Error obteniendo chart de {coin_id}: {e}")
            return {}
    
    async def get_global_data(self) -> Dict[str, Any]:
        """Obtener datos globales del mercado de criptomonedas"""
        try:
            return await self._make_request("/global")
        except Exception as e:
            logger.error(f"Error obteniendo datos globales: {e}")
            return {}
    
    async def search_coins(self, query: str) -> Dict[str, Any]:
        """Buscar monedas por nombre o símbolo"""
        try:
            params = {'query': query}
            return await self._make_request("/search", params)
        except Exception as e:
            logger.error(f"Error buscando '{query}': {e}")
            return {}
    
    async def get_trending_coins(self) -> Dict[str, Any]:
        """Obtener monedas en tendencia"""
        try:
            return await self._make_request("/search/trending")
        except Exception as e:
            logger.error(f"Error obteniendo trending coins: {e}")
            return {}

class DataProcessor:
    """
    Helper para procesar y normalizar datos de ambas APIs
    """
    
    @staticmethod
    def normalize_binance_ticker(ticker_data: Dict) -> Dict[str, Any]:
        """Normalizar datos de ticker de Binance"""
        return {
            'symbol': ticker_data.get('symbol', ''),
            'price': float(ticker_data.get('lastPrice', 0)),
            'price_change_24h': float(ticker_data.get('priceChange', 0)),
            'price_change_percentage_24h': float(ticker_data.get('priceChangePercent', 0)),
            'volume_24h': float(ticker_data.get('volume', 0)),
            'quote_volume_24h': float(ticker_data.get('quoteVolume', 0)),
            'high_24h': float(ticker_data.get('highPrice', 0)),
            'low_24h': float(ticker_data.get('lowPrice', 0)),
            'open_price': float(ticker_data.get('openPrice', 0)),
            'close_time': datetime.fromtimestamp(ticker_data.get('closeTime', 0) / 1000),
            'source': 'binance'
        }
    
    @staticmethod
    def normalize_coingecko_coin(coin_data: Dict) -> Dict[str, Any]:
        """Normalizar datos de moneda de CoinGecko"""
        return {
            'id': coin_data.get('id', ''),
            'symbol': coin_data.get('symbol', '').upper(),
            'name': coin_data.get('name', ''),
            'price': coin_data.get('current_price', 0),
            'market_cap': coin_data.get('market_cap', 0),
            'market_cap_rank': coin_data.get('market_cap_rank', 999),
            'volume_24h': coin_data.get('total_volume', 0),
            'price_change_24h': coin_data.get('price_change_24h', 0),
            'price_change_percentage_24h': coin_data.get('price_change_percentage_24h', 0),
            'price_change_percentage_7d': coin_data.get('price_change_percentage_7d_in_currency', 0),
            'price_change_percentage_30d': coin_data.get('price_change_percentage_30d_in_currency', 0),
            'circulating_supply': coin_data.get('circulating_supply', 0),
            'total_supply': coin_data.get('total_supply', 0),
            'max_supply': coin_data.get('max_supply', 0),
            'ath': coin_data.get('ath', 0),
            'ath_change_percentage': coin_data.get('ath_change_percentage', 0),
            'atl': coin_data.get('atl', 0),
            'atl_change_percentage': coin_data.get('atl_change_percentage', 0),
            'last_updated': coin_data.get('last_updated', ''),
            'source': 'coingecko'
        }
    
    @staticmethod
    def process_klines_data(klines: List[List]) -> List[Dict[str, Any]]:
        """
        Procesar datos de velas de Binance
        
        Estructura de klines:
        [timestamp, open, high, low, close, volume, close_time, quote_volume, 
         count, taker_buy_volume, taker_buy_quote_volume, ignore]
        """
        processed = []
        for kline in klines:
            try:
                processed.append({
                    'timestamp': datetime.fromtimestamp(int(kline[0]) / 1000),
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5]),
                    'close_time': datetime.fromtimestamp(int(kline[6]) / 1000),
                    'quote_volume': float(kline[7]),
                    'trades_count': int(kline[8]),
                    'taker_buy_volume': float(kline[9]),
                    'taker_buy_quote_volume': float(kline[10])
                })
            except (ValueError, IndexError) as e:
                logger.warning(f"Error procesando kline: {e}")
                continue
        
        return processed
    
    @staticmethod
    def process_coingecko_prices(prices: List[List], symbol: str) -> List[Dict[str, Any]]:
        """
        Procesa precios de CoinGecko (formato [timestamp, price]) a estructura estándar
        """
        processed = []
        for entry in prices:
            try:
                ts, price = entry
                processed.append({
                    'symbol': symbol.upper(),
                    'source': 'coingecko',
                    'timestamp': datetime.fromtimestamp(ts / 1000),
                    'close': float(price),
                    'open': None,
                    'high': None,
                    'low': None,
                    'volume': None
                })
            except Exception as e:
                logger.warning(f"Error procesando precio CoinGecko: {e}")
        return processed

    
    @staticmethod
    def merge_coin_data(binance_data: List[Dict], coingecko_data: List[Dict]) -> List[Dict[str, Any]]:
        """Combinar datos de Binance y CoinGecko por símbolo"""
        merged = {}
        
        # Procesar datos de CoinGecko (más completos)
        for coin in coingecko_data:
            symbol = coin['symbol']
            merged[symbol] = coin.copy()
        
        # Complementar con datos de Binance
        for ticker in binance_data:
            symbol = ticker['symbol'].replace('USDT', '').upper()
            if symbol in merged:
                # Agregar datos específicos de Binance
                merged[symbol].update({
                    'binance_symbol': ticker['symbol'],
                    'binance_volume_24h': ticker['volume_24h'],
                    'binance_price': ticker['price'],
                    'has_binance_data': True
                })
            else:
                # Crear entrada solo con datos de Binance
                merged[symbol] = {
                    'symbol': symbol,
                    'binance_symbol': ticker['symbol'],
                    'price': ticker['price'],
                    'price_change_percentage_24h': ticker['price_change_percentage_24h'],
                    'volume_24h': ticker['volume_24h'],
                    'has_binance_data': True,
                    'source': 'binance_only'
                }
        
        return list(merged.values())

class APIRateLimiter:
    """
    Rate limiter avanzado para controlar las peticiones a las APIs con caché y backoff exponencial
    """
    
    def __init__(self):
        self.binance_calls = []
        self.coingecko_calls = []
        self.binance_limit = 1200  # peticiones por minuto
        self.coingecko_limit = 10  # Reducido para ser más conservador
        self.cache = {}
        self.cache_ttl = {}
        self.backoff_delay = {}
        
    def _get_cache_key(self, api: str, endpoint: str, params: Dict = None) -> str:
        """Generar clave de caché para una petición"""
        if params:
            sorted_params = sorted(params.items())
            params_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            return f"{api}:{endpoint}:{params_str}"
        return f"{api}:{endpoint}"
    
    def get_cached_data(self, api: str, endpoint: str, params: Dict = None, ttl: int = 300):
        """Obtener datos del caché si están disponibles y válidos"""
        cache_key = self._get_cache_key(api, endpoint, params)
        now = time.time()
        
        if cache_key in self.cache and cache_key in self.cache_ttl:
            if now < self.cache_ttl[cache_key]:
                logger.info(f"Usando datos en caché para {cache_key}")
                return self.cache[cache_key]
            else:
                # Limpiar caché expirado
                del self.cache[cache_key]
                del self.cache_ttl[cache_key]
        
        return None
    
    def set_cached_data(self, api: str, endpoint: str, params: Dict = None, data: Any = None, ttl: int = 300):
        """Guardar datos en caché"""
        cache_key = self._get_cache_key(api, endpoint, params)
        now = time.time()
        
        self.cache[cache_key] = data
        self.cache_ttl[cache_key] = now + ttl
        logger.debug(f"Datos guardados en caché para {cache_key} por {ttl}s")
    
    async def wait_if_needed(self, api: str):
        """Esperar si es necesario para respetar rate limits con backoff exponencial"""
        now = time.time()
        
        # Verificar si hay un delay de backoff activo
        if api in self.backoff_delay and now < self.backoff_delay[api]:
            wait_time = self.backoff_delay[api] - now
            logger.warning(f"Backoff activo para {api}, esperando {wait_time:.2f} segundos")
            await asyncio.sleep(wait_time)
        
        if api == 'binance':
            # Limpiar llamadas antiguas (últimos 60 segundos)
            self.binance_calls = [call for call in self.binance_calls if now - call < 60]
            
            if len(self.binance_calls) >= self.binance_limit:
                wait_time = 60 - (now - self.binance_calls[0])
                if wait_time > 0:
                    logger.info(f"Rate limit Binance alcanzado, esperando {wait_time:.2f} segundos")
                    await asyncio.sleep(wait_time)
            
            self.binance_calls.append(now)
        
        elif api == 'coingecko':
            # Limpiar llamadas antiguas
            self.coingecko_calls = [call for call in self.coingecko_calls if now - call < 60]
            
            if len(self.coingecko_calls) >= self.coingecko_limit:
                wait_time = 60 - (now - self.coingecko_calls[0])
                if wait_time > 0:
                    logger.info(f"Rate limit CoinGecko alcanzado, esperando {wait_time:.2f} segundos")
                    await asyncio.sleep(wait_time)
            
            self.coingecko_calls.append(now)
    
    def set_backoff_delay(self, api: str, delay: float = 60):
        """Establecer un delay de backoff exponencial para un API"""
        now = time.time()
        self.backoff_delay[api] = now + delay
        logger.warning(f"Backoff establecido para {api} por {delay} segundos")


async def send_telegram_message(chat_id: str, text: str, parse_mode="HTML"):
    try:
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}





# Instancias globales
binance_helper = BinanceAPIHelper()
coingecko_helper = CoinGeckoAPIHelper()
data_processor = DataProcessor()
rate_limiter = APIRateLimiter()
