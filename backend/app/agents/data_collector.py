import asyncio
from typing import List, Dict, Any
from datetime import datetime
import json
import os
from app.utils import binance_helper, coingecko_helper, data_processor, rate_limiter
import logging

logger = logging.getLogger(__name__)

class DataCollectorAgent:
    """
    Agente Recolección datos - Se encarga de obtener datos diarios de monedas
    desde API Binance y API CoinGecko usando los helpers optimizados
    """
    
    def __init__(self):
        self.binance = binance_helper
        self.coingecko = coingecko_helper
        self.processor = data_processor
        self.rate_limiter = rate_limiter
        
    async def collect_binance_data(self) -> List[Dict[str, Any]]:
        """Obtener datos de precios de Binance usando el helper optimizado"""
        try:
            logger.info("Iniciando recolección de datos de Binance")
            
            # Respetar rate limits
            await self.rate_limiter.wait_if_needed('binance')
            
            # Obtener ticker de 24h para todos los pares
            tickers = await self.binance.get_24hr_ticker()
            
            # Filtrar y procesar solo pares USDT con volumen significativo
            processed_data = []
            for ticker in tickers:
                if (ticker.get('symbol', '').endswith('USDT') and 
                    float(ticker.get('quoteVolume', 0)) > 1000000):
                    
                    normalized = self.processor.normalize_binance_ticker(ticker)
                    processed_data.append(normalized)
            
            # Ordenar por volumen y tomar top 100
            processed_data.sort(key=lambda x: x['quote_volume_24h'], reverse=True)
            top_data = processed_data[:100]
            
            logger.info(f"Obtenidos {len(top_data)} pares de Binance")
            return top_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de Binance: {e}")
            return []
    
    async def collect_coingecko_data(self) -> List[Dict[str, Any]]:
        """Obtener datos detallados de CoinGecko usando el helper optimizado"""
        try:
            logger.info("Iniciando recolección de datos de CoinGecko")
            
            # Respetar rate limits
            await self.rate_limiter.wait_if_needed('coingecko')
            
            # Obtener datos de mercado con cambios de precio
            coins_data = await self.coingecko.get_coins_markets(
                vs_currency='usd',
                order='market_cap_desc',
                per_page=100,
                page=1,
                price_change_percentage='1h,24h,7d,30d'
            )
            
            # Normalizar datos
            processed_data = []
            for coin in coins_data:
                normalized = self.processor.normalize_coingecko_coin(coin)
                processed_data.append(normalized)
            
            logger.info(f"Obtenidos {len(processed_data)} coins de CoinGecko")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de CoinGecko: {e}")
            return []
    
    async def collect_all_data(self) -> Dict[str, Any]:
        """Recopilar todos los datos de las APIs de forma optimizada"""
        try:
            logger.info("Iniciando recolección completa de datos")
            
            # Ejecutar recolecciones en paralelo
            binance_task = self.collect_binance_data()
            coingecko_task = self.collect_coingecko_data()
            
            # Esperar a que todas las tareas terminen
            binance_data, coingecko_data = await asyncio.gather(
                binance_task,
                coingecko_task,
                return_exceptions=True
            )
            
            # Manejar excepciones
            if isinstance(binance_data, Exception):
                logger.error(f"Error en datos de Binance: {binance_data}")
                binance_data = []
            
            if isinstance(coingecko_data, Exception):
                logger.error(f"Error en datos de CoinGecko: {coingecko_data}")
                coingecko_data = []
            
            # Combinar datos de ambas fuentes
            merged_coins = self.processor.merge_coin_data(binance_data, coingecko_data)
            
            result = {
                'binance': binance_data,
                'coingecko': coingecko_data,
                'merged_coins': merged_coins,
                'timestamp': datetime.now().isoformat(),
                'stats': {
                    'binance_coins': len(binance_data),
                    'coingecko_coins': len(coingecko_data),
                    'merged_coins': len(merged_coins)
                }
            }
            
            logger.info(f"Recolección completa exitosa: {result['stats']}")
            return result
            
        except Exception as e:
            logger.error(f"Error en recolección completa de datos: {e}")
            return {
                'binance': [],
                'coingecko': [],
                'merged_coins': [],
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
