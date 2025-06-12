from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import httpx

from app.agents.data_collector import DataCollectorAgent
from app.agents.economic_analysis import EconomicAnalysisAgent
from app.agents.portfolio_optimizer import PortfolioOptimizationAgent
from app.agents.communication import CommunicationAgent

router = APIRouter()

# Inicializar agentes
data_collector = DataCollectorAgent()
economic_analyzer = EconomicAnalysisAgent()
portfolio_optimizer = PortfolioOptimizationAgent()
communication_agent = CommunicationAgent()

# Modelos Pydantic para validación
class UserProfileModel(BaseModel):
    user_id: str
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    investment_amount: float = 1000
    investment_horizon: str = "medium"  # short, medium, long
    preferred_sectors: List[str] = []

class SubscriptionModel(BaseModel):
    user_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notification_type: str = "email"  # email, sms, both
    frequency: str = "daily"  # daily, weekly, monthly
    risk_tolerance: str = "moderate"
    investment_amount: float = 1000
    investment_horizon: str = "medium"
    preferred_sectors: List[str] = []

class PortfolioRequestModel(BaseModel):
    user_id: str
    risk_tolerance: str = "moderate"
    investment_amount: float = 1000
    investment_horizon: str = "medium"
    preferred_sectors: List[str] = []

@router.get("/")
async def root():
    """Endpoint de verificación de estado"""
    return {"message": "CriptoAI Backend API", "status": "active", "timestamp": datetime.now()}

@router.post("/update-data")
async def update_crypto_data(background_tasks: BackgroundTasks):
    """
    Endpoint para actualizar datos de criptomonedas
    Ejecuta el flujo: Recolección de datos -> Análisis económico -> Guardado en BD
    """
    try:
        # Recopilar datos de APIs externas
        crypto_data = await data_collector.collect_all_data()
        
        if not crypto_data.get('coingecko') and not crypto_data.get('binance'):
            raise HTTPException(status_code=500, detail="No se pudieron obtener datos de las APIs")
        
        # Procesar datos en background
        background_tasks.add_task(economic_analyzer.analyze_and_store, crypto_data)
        
        return {
            "success": True,
            "message": "Datos recopilados y análisis iniciado en background",
            "coins_collected": len(crypto_data.get('coingecko', [])),
            "timestamp": crypto_data.get('timestamp')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando datos: {str(e)}")

@router.post("/get-portfolio-recommendation")
async def get_portfolio_recommendation(request: PortfolioRequestModel):
    """
    Endpoint para obtener recomendaciones de portfolio personalizadas
    Ejecuta el flujo: Obtener métricas del usuario -> Optimizar portfolio -> Retornar top 5
    """
    try:
        # Convertir request a diccionario
        user_data = {
            "user_id": request.user_id,
            "risk_tolerance": request.risk_tolerance,
            "investment_amount": request.investment_amount,
            "investment_horizon": request.investment_horizon,
            "preferred_sectors": request.preferred_sectors
        }
        
        # Obtener métricas relevantes para el usuario
        relevant_coins = economic_analyzer.get_user_relevant_metrics(user_data)
        
        if not relevant_coins:
            raise HTTPException(
                status_code=404, 
                detail="No se encontraron monedas adecuadas para tu perfil. Intenta actualizar los datos primero."
            )
        
        # Optimizar portfolio
        optimization_result = await portfolio_optimizer.optimize_portfolio(user_data, relevant_coins)
        
        if not optimization_result.get('success'):
            raise HTTPException(
                status_code=500, 
                detail=optimization_result.get('message', 'Error en optimización de portfolio')
            )
        
        return {
            "success": True,
            "data": {
                "recommendations": optimization_result['recommendations'],
                "expected_return": optimization_result['expected_return'],
                "risk_score": optimization_result['risk_score'],
                "confidence_level": optimization_result['confidence_level'],
                "reasoning": optimization_result['reasoning']
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando recomendación: {str(e)}")

@router.post("/subscribe")
async def subscribe_user(subscription: SubscriptionModel):
    """
    Endpoint para registrar suscripción de usuario
    """
    try:
        # Convertir modelo a diccionario
        user_data = subscription.dict()
        
        # Registrar suscripción
        result = communication_agent.register_subscription(user_data)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('message'))
        
        return {
            "success": True,
            "message": result['message'],
            "subscription_id": result['subscription_id']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registrando suscripción: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Endpoint de verificación de salud del sistema
    """
    try:
        # Verificar conexión a base de datos
        from app import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "data_collector": "active",
                "economic_analyzer": "active", 
                "portfolio_optimizer": "active",
                "communication_agent": "active"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Sistema no saludable: {str(e)}")

@router.get("/market-overview")
async def get_market_overview():
    """
    ✅ ENDPOINT CORREGIDO - Resumen general del mercado con datos reales
    """
    try:
        # Llamada directa a CoinGecko API sin procesamiento intermedio
        async with httpx.AsyncClient() as client:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 10,
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '24h'
            }
            
            response = await client.get(url, params=params, timeout=15.0)
            response.raise_for_status()
            market_data = response.json()
        
        if not market_data:
            raise HTTPException(status_code=503, detail="No se pueden obtener datos del mercado")
        
        # Procesar y resumir datos
        top_10 = market_data[:10]
        
        total_market_cap = sum(coin.get('market_cap', 0) for coin in top_10)
        avg_price_change = sum(coin.get('price_change_percentage_24h', 0) for coin in top_10) / len(top_10)
        
        bullish_count = len([coin for coin in top_10 if coin.get('price_change_percentage_24h', 0) > 0])
        bearish_count = len(top_10) - bullish_count
        
        return {
            "success": True,
            "data": {
                "top_cryptocurrencies": [
                    {
                        "symbol": coin['symbol'].upper(),
                        "name": coin['name'],
                        "current_price": coin.get('current_price', 0),  # ✅ Campo correcto de CoinGecko
                        "market_cap": coin.get('market_cap', 0),
                        "price_change_24h": coin.get('price_change_percentage_24h', 0),
                        "volume_24h": coin.get('total_volume', 0)  # ✅ Campo correcto de CoinGecko
                    }
                    for coin in top_10
                ],
                "market_summary": {
                    "total_market_cap_top10": total_market_cap,
                    "average_price_change_24h": round(avg_price_change, 2),
                    "bullish_coins": bullish_count,
                    "bearish_coins": bearish_count,
                    "market_sentiment": "bullish" if bullish_count > bearish_count else "bearish" if bearish_count > bullish_count else "neutral"
                }
            },
            "timestamp": datetime.now().isoformat(),
            "fixed": True,
            "note": "Datos obtenidos directamente de CoinGecko API"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo resumen del mercado: {str(e)}")

@router.get("/economic-metrics")
async def get_economic_metrics():
    """
    Endpoint que retorna métricas cuantitativas de inversión y riesgo para todas las monedas del market overview.
    """
    try:
        # Obtener datos del market overview (llamada interna)
        async with httpx.AsyncClient() as client:
            url = "http://localhost:8000/api/market-overview"
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        if not data.get("success") or not data["data"].get("top_cryptocurrencies"):
            raise HTTPException(status_code=503, detail="No se pueden obtener datos del market overview")

        coins = data["data"]["top_cryptocurrencies"]
        metrics = economic_analyzer.compute_market_metrics(coins)
        return {"success": True, "metrics": metrics, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo métricas económicas: {str(e)}")
