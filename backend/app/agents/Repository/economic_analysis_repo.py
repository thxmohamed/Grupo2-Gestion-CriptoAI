from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
from app import SessionLocal
from app.models import Cryptocurrency, CryptoMetrics

logger = logging.getLogger(__name__)

class EconomicAnalysisRepo:
    def __init__(self):
        self.db: Session = SessionLocal()

    def save_economic_metrics(self, symbol: str, metrics: Dict[str, Any]) -> None:
        ''' Guarda las métricas económicas de una criptomoneda en la base de datos.
        Args:
            symbol (str): Símbolo de la criptomoneda.
            metrics (Dict[str, Any]): Diccionario con las métricas económicas.
                {
                "symbol": symbol,
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
        '''
        # Ensure the symbol is uppercase for consistency in the database
        metrics['symbol'] = symbol.upper()

        querytext = """
        INSERT INTO crypto_metrics (
            symbol, current_price, market_cap, price_change_24h, 
            price_change_7d, price_change_30d, volume_24h, expected_return, 
            volatility, rsi, ma_7, ma_30, investment_score, risk_score, 
            risk_level, liquidity_ratio, market_sentiment, stability_score, 
            growth_potential
        ) VALUES (
            :symbol, :current_price, :market_cap, :price_change_24h, 
            :price_change_7d, :price_change_30d, :volume_24h, :expected_return, 
            :volatility, :rsi, :ma_7, :ma_30, :investment_score, :risk_score, 
            :risk_level, :liquidity_ratio, :market_sentiment, :stability_score, 
            :growth_potential
        )
        ON CONFLICT (symbol) DO UPDATE SET 
            current_price = EXCLUDED.current_price,
            market_cap = EXCLUDED.market_cap,
            price_change_24h = EXCLUDED.price_change_24h,
            price_change_7d = EXCLUDED.price_change_7d,
            price_change_30d = EXCLUDED.price_change_30d,
            volume_24h = EXCLUDED.volume_24h,
            expected_return = EXCLUDED.expected_return,
            volatility = EXCLUDED.volatility,
            rsi = EXCLUDED.rsi,
            ma_7 = EXCLUDED.ma_7,
            ma_30 = EXCLUDED.ma_30,
            investment_score = EXCLUDED.investment_score,
            risk_score = EXCLUDED.risk_score,
            risk_level = EXCLUDED.risk_level,
            liquidity_ratio = EXCLUDED.liquidity_ratio,
            market_sentiment = EXCLUDED.market_sentiment,
            stability_score = EXCLUDED.stability_score,
            growth_potential = EXCLUDED.growth_potential,
            updated_at = CURRENT_TIMESTAMP;
        """
        try:
            # Execute the query using your repository's method
            # Assuming self.repo.execute_query takes the query string and a dictionary of parameters
            self.db.execute(
                text(querytext),
                {
                    "symbol": metrics['symbol'],
                    "current_price": float(metrics.get('current_price', 0.0)),
                    "market_cap": float(metrics.get('market_cap', 0.0)),
                    "price_change_24h": float(metrics.get('price_change_24h', 0.0)),
                    "price_change_7d": float(metrics.get('price_change_7d', 0.0)),
                    "price_change_30d": float(metrics.get('price_change_30d', 0.0)),
                    "volume_24h": float(metrics.get('volume_24h', 0.0)),
                    "expected_return": float(metrics.get('expected_return', 0.0)),
                    "volatility": float(metrics.get('volatility', 0.0)),
                    "rsi": float(metrics.get('rsi', 50.0)),  # Default RSI to 50 if not provided
                    "ma_7": float(metrics.get('ma_7', 0.0)),
                    "ma_30": float(metrics.get('ma_30', 0.0)),
                    "investment_score": float(metrics.get('investment_score', 0.0)),
                    "risk_score": float(metrics.get('risk_score', 0.0)),
                    "risk_level": metrics.get('risk_level', 'medium'),
                    "liquidity_ratio": float(metrics.get('liquidity_ratio', 0.0)),
                    "market_sentiment": metrics.get('market_sentiment', 'neutral'),
                    "stability_score": float(metrics.get('stability_score', 0.0)),
                    "growth_potential": float(metrics.get('growth_potential', 0.0))
                }
            )
            self.db.commit()  # Hacer commit de los cambios
            print(f"Métricas económicas para {symbol} guardadas/actualizadas con éxito.")
        except Exception as e:
            # Handle any potential database errors
            self.db.rollback()  # Hacer rollback en caso de error
            print(f"Error al guardar métricas económicas para {symbol}: {e}")
            raise  # Re-raise the exception after logging for higher-level handling



    def get_all_symbols(self) -> List[str]:
        """
        Obtiene todos los símbolos únicos de criptomonedas en la base de datos.
        
        Args:

        Returns:
            List[str]: Lista de símbolos únicos.
        """
        try:
            querytext = "SELECT DISTINCT symbol FROM crypto_metrics"
            symbols = self.db.execute(text(querytext)).scalars().all()
            return [symbol.upper() for symbol in symbols]
        except Exception as e:
            logger.error(f"Error obteniendo símbolos de la base de datos: {e}")
            return []
    def get_historical_from_db(self, symbol: str) -> List[Dict[str, float]]:
        """
        Obtiene datos históricos de la base de datos para un símbolo específico.
        """
        try:
            querytext = "SELECT coingecko_close, binance_volume, coingecko_market_cap FROM get_unified_historical_crypto_data(:symbol);"
            historical_data = self.db.execute(
                text(querytext),
                {"symbol": symbol}
            ).fetchall()
            print("Se obtuvo datos históricos de la base de datos")
            return [{"close": float(row[0]), "volume": float(row[1]), "market_cap": float(row[2])} for row in historical_data]
        except Exception as e:
            logger.error(f"Error obteniendo datos de DB para {symbol}: {e}")
            return []
    
    def create_or_update_cryptocurrency(self, crypto_data: Dict[str, Any]) -> int:
        """
        Crea o actualiza una criptomoneda en la base de datos.
        
        Args:
            crypto_data: Diccionario con los datos de la criptomoneda
            
        Returns:
            int: ID de la criptomoneda creada o actualizada
        """
        try:
            # Buscar si existe
            crypto = self.db.query(Cryptocurrency).filter(
                Cryptocurrency.symbol == crypto_data['symbol']
            ).first()
            
            if not crypto:
                # Crear nueva
                crypto = Cryptocurrency(**crypto_data)
                self.db.add(crypto)
                self.db.flush()  # Para obtener el ID
            else:
                # Actualizar existente
                for key, value in crypto_data.items():
                    if hasattr(crypto, key):
                        setattr(crypto, key, value)
            
            self.db.commit()
            return crypto.id
            
        except Exception as e:
            logger.error(f"Error creando/actualizando criptomoneda {crypto_data.get('symbol')}: {e}")
            self.db.rollback()
            raise
    
    def create_or_update_metrics(self, metrics_data: Dict[str, Any]) -> None:
        """
        Crea o actualiza las métricas de una criptomoneda.
        
        Args:
            metrics_data: Diccionario con los datos de las métricas
        """
        try:
            # Buscar si existe
            metrics = self.db.query(CryptoMetrics).filter(
                CryptoMetrics.symbol == metrics_data['symbol']
            ).first()
            
            if not metrics:
                # Crear nueva
                metrics = CryptoMetrics(**metrics_data)
                self.db.add(metrics)
            else:
                # Actualizar existente
                for key, value in metrics_data.items():
                    if hasattr(metrics, key):
                        setattr(metrics, key, value)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error creando/actualizando métricas para {metrics_data.get('symbol')}: {e}")
            self.db.rollback()
            raise
    
    def get_user_relevant_metrics(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Obtiene métricas relevantes para un usuario específico basado en filtros.
        
        Args:
            filters: Diccionario con filtros y criterios de ordenamiento
            
        Returns:
            List[Dict[str, Any]]: Lista de criptomonedas con sus métricas
        """
        try:
            # Construir query base
            query = self.db.query(CryptoMetrics)
            
            # Aplicar filtros
            if 'risk_levels' in filters:
                query = query.filter(CryptoMetrics.risk_level.in_(filters['risk_levels']))
            
            if 'min_stability_score' in filters:
                query = query.filter(CryptoMetrics.stability_score >= filters['min_stability_score'])
            
            # Aplicar ordenamiento
            order_by = filters.get('order_by', 'growth_potential')
            if order_by == 'growth_potential':
                query = query.order_by(CryptoMetrics.growth_potential.desc())
            elif order_by == 'stability_score':
                query = query.order_by(CryptoMetrics.stability_score.desc())
            elif order_by == 'combined':
                query = query.order_by(
                    (CryptoMetrics.growth_potential + CryptoMetrics.stability_score).desc()
                )
            
            # Aplicar límite
            limit = filters.get('limit', 20)
            results = query.limit(limit).all()
            
            # Formatear resultados
            return [
                {
                    'symbol': metrics.symbol,
                    'current_price': float(metrics.current_price) if metrics.current_price else 0,
                    'market_cap': float(metrics.market_cap) if metrics.market_cap else 0,
                    'price_change_24h': float(metrics.price_change_24h) if metrics.price_change_24h else 0,
                    'volatility': float(metrics.volatility) if metrics.volatility else 0,
                    'rsi': float(metrics.rsi) if metrics.rsi else 50,
                    'market_sentiment': metrics.market_sentiment or 'neutral',
                    'stability_score': float(metrics.stability_score) if metrics.stability_score else 0,
                    'growth_potential': float(metrics.growth_potential) if metrics.growth_potential else 0,
                    'risk_level': metrics.risk_level or 'medium',
                    'investment_score': float(metrics.investment_score) if metrics.investment_score else 0,
                    'risk_score': float(metrics.risk_score) if metrics.risk_score else 0,
                    'expected_return': float(metrics.expected_return) if metrics.expected_return else 0
                }
                for metrics in results
            ]
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas para usuario: {e}")
            return []
    
    def get_coin_metrics(self, symbol: str) -> Dict[str, Any]:
        '''Obtiene las métricas de una criptomoneda específica desde la base de datos.'''
        try:
            querytext = """
            SELECT * FROM crypto_metrics WHERE symbol = :symbol;
            """
            result = self.db.execute(text(querytext), {"symbol": symbol.upper()}).fetchone()
            if result:
                # Convertir Row a diccionario usando _asdict() o acceso por columnas
                return result._asdict() if hasattr(result, '_asdict') else dict(zip(result.keys(), result))
            else:
                raise ValueError(f"No se encontraron métricas para el símbolo {symbol}")
        except Exception as e:
            logger.error(f"Error obteniendo métricas para {symbol}: {e}")
            raise

    def __del__(self):
        """Cerrar la sesión al destruir el objeto"""
        if hasattr(self, 'db'):
            self.db.close()