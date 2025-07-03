import asyncio
from typing import List, Dict, Any
from datetime import datetime
import logging
from app.models import HistoricalPrice
from app.utils import binance_helper, coingecko_helper, data_processor, rate_limiter
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class DataCollectorAgent:
    """
    Agente que recolecta datos actuales y datos históricos de criptomonedas
    desde Binance y CoinGecko.
    """
    def __init__(self):
        self.binance = binance_helper
        self.coingecko = coingecko_helper
        self.processor = data_processor
        self.rate_limiter = rate_limiter

    def save_historical_prices(self, db: Session, price_list: List[Dict[str, Any]]):
        """
        Guarda los precios históricos eliminando previamente los registros existentes
        para las mismas fechas, símbolo y fuente.
        """
        if not price_list:
            return

        # Determinar rangos y símbolo común
        symbol = price_list[0]['symbol']
        source = price_list[0]['source']
        timestamps = [p['timestamp'] for p in price_list]

        # Eliminar datos existentes para las fechas que vamos a insertar
        try:
            db.query(HistoricalPrice).filter(
                HistoricalPrice.symbol == symbol,
                HistoricalPrice.source == source,
                HistoricalPrice.timestamp.in_(timestamps)
            ).delete(synchronize_session=False)

            for p in price_list:
                record = HistoricalPrice(
                    symbol=p['symbol'],
                    source=p['source'],
                    timestamp=p['timestamp'],
                    open=p.get('open'),
                    high=p.get('high'),
                    low=p.get('low'),
                    close=p.get('close') or p.get('price'),
                    volume=p.get('volume')
                )
                db.add(record)

            db.commit()
            logger.info(f"[✔] Guardados {len(price_list)} registros para {symbol} ({source})")
        except Exception as e:
            logger.error(f"[❌] Error guardando históricos para {symbol} ({source}): {e}")
            db.rollback()


    # ══════════════════════════════
    # DATOS ACTUALES
    # ══════════════════════════════
    async def collect_binance_data(self, top_n: int = 100) -> List[Dict[str, Any]]:
        try:
            logger.info("Recolectando datos actuales de Binance")
            await self.rate_limiter.wait_if_needed('binance')
            tickers = await self.binance.get_24hr_ticker()

            processed = []
            for ticker in tickers:
                if ticker.get('symbol', '').endswith('USDT') and float(ticker.get('quoteVolume', 0)) > 1_000_000:
                    normalized = self.processor.normalize_binance_ticker(ticker)
                    processed.append(normalized)

            processed.sort(key=lambda x: x['quote_volume_24h'], reverse=True)
            return processed[:top_n]

        except Exception as e:
            logger.error(f"Error en Binance actual: {e}")
            return []

    async def collect_coingecko_data(self) -> List[Dict[str, Any]]:
        try:
            logger.info("Recolectando datos actuales de CoinGecko")
            await self.rate_limiter.wait_if_needed('coingecko')
            coins_data = await self.coingecko.get_coins_markets(
                vs_currency='usd',
                order='market_cap_desc',
                per_page=100,
                page=1,
                price_change_percentage='1h,24h,7d,30d'
            )
            return [self.processor.normalize_coingecko_coin(c) for c in coins_data]
        except Exception as e:
            logger.error(f"Error en CoinGecko actual: {e}")
            return []

    async def collect_current_data(self) -> Dict[str, Any]:
        try:
            logger.info("Recolectando datos actuales completos")
            binance_data, coingecko_data = await asyncio.gather(
                self.collect_binance_data(),
                self.collect_coingecko_data(),
                return_exceptions=True
            )

            if isinstance(binance_data, Exception):
                logger.error(f"Error Binance actual: {binance_data}")
                binance_data = []

            if isinstance(coingecko_data, Exception):
                logger.error(f"Error CoinGecko actual: {coingecko_data}")
                coingecko_data = []

            merged = self.processor.merge_coin_data(binance_data, coingecko_data)

            return {
                "timestamp": datetime.now().isoformat(),
                "binance": binance_data,
                "coingecko": coingecko_data,
                "merged_coins": merged,
                "stats": {
                    "binance_coins": len(binance_data),
                    "coingecko_coins": len(coingecko_data),
                    "merged_coins": len(merged)
                }
            }

        except Exception as e:
            logger.error(f"Error en recolección actual: {e}")
            return {}

    # ══════════════════════════════
    # DATOS HISTÓRICOS
    # ══════════════════════════════
    async def collect_coingecko_history(self, coin_id: str, symbol: str, days: int = 13) -> List[Dict[str, Any]]:
        try:
            logger.info(f"Recolectando histórico CoinGecko: {symbol}")
            await self.rate_limiter.wait_if_needed('coingecko')
            history = await self.coingecko.get_coin_market_chart(
                coin_id=coin_id,
                vs_currency='usd',
                days=str(days),
                interval='daily'
            )
            return self.processor.process_coingecko_prices(history['prices'], symbol)
        except Exception as e:
            logger.error(f"Error histórico CoinGecko para {symbol}: {e}")
            return []

    async def collect_binance_history(self, symbol: str, days: int = 14) -> List[Dict[str, Any]]:
        try:
            logger.info(f"Recolectando histórico Binance: {symbol}")
            await self.rate_limiter.wait_if_needed('binance')
            klines = await self.binance.get_klines(
                symbol=symbol,
                interval='1d',
                limit=days
            )
            processed = self.processor.process_klines_data(klines)
            for d in processed:
                d.update({
                    'symbol': symbol.replace('USDT', ''),
                    'source': 'binance'
                })
            return processed
        except Exception as e:
            logger.error(f"Error histórico Binance para {symbol}: {e}")
            return []

    async def collect_historical_data(self, db: Session, days: int = 14, limit: int = 10):
        logger.info("Iniciando recolección histórica automática")

        # Limpiar toda la tabla una sola vez
        try:
            deleted = db.query(HistoricalPrice).delete()
            db.commit()
            logger.info(f"[🧹] Tabla historical_prices limpiada ({deleted} registros eliminados)")
        except Exception as cleanup_error:
            logger.error(f"[❌] Error limpiando la tabla historical_prices: {cleanup_error}")
            db.rollback()
            return

        stablecoins = {'USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'FDUSD'}
        try:
            await self.rate_limiter.wait_if_needed('coingecko')
            top_coins = await self.coingecko.get_coins_markets(
                vs_currency='usd',
                order='market_cap_desc',
                per_page=limit,
                page=1
            )

            # Obtener lista de pares válidos en Binance
            exchange_info = await self.binance.get_exchange_info()
            available_pairs = {s['symbol'] for s in exchange_info.get('symbols', [])}

            for coin in top_coins:
                coin_id = coin.get('id')
                symbol = coin.get('symbol', '').upper()

                if symbol in stablecoins:
                    logger.info(f"Saltando moneda estable: {symbol}")
                    continue

                binance_symbol = f"{symbol}USDT"
                if binance_symbol not in available_pairs:
                    logger.info(f"Par no disponible en Binance: {binance_symbol}")
                    continue

                try:
                    #cg = await self.collect_coingecko_history(coin_id, symbol)
                    #self.save_historical_prices(db, cg)

                    bn = await self.collect_binance_history(binance_symbol, days)
                    self.save_historical_prices(db, bn)

                    logger.info(f"Históricos guardados para {symbol}")
                except Exception as e:
                    logger.warning(f"Error recolectando históricos para {symbol}: {e}")
            return "Históricos guardados correctamente"
        except Exception as outer:
            logger.error(f"Fallo la recolección automática de top monedas: {outer}")

    def get_data_from_db(self, db: Session, symbol: str, source: str) -> List[float]:
        """
        Obtiene datos históricos de la base de datos para un símbolo y fuente específicos.
        """
        try:
            querytext = "SELECT close FROM historical_prices WHERE symbol = :symbol AND source = :source ORDER BY timestamp"
            economic_metrics_decimal = db.execute(
                text(querytext),
                {"symbol": symbol, "source": source}
            ).scalars().all()
            return [float(price) for price in economic_metrics_decimal]
        except Exception as e:
            logger.error(f"Error obteniendo datos de DB para {symbol} ({source}): {e}")
            return []