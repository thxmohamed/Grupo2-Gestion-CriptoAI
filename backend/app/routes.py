from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import asyncio
import httpx
import json

from app.agents.data_collector import DataCollectorAgent
from app.agents.economic_analysis import EconomicAnalysisAgent
from app.agents.portfolio_optimizer import PortfolioOptimizationAgent
from app.agents.communication import CommunicationAgent
from app.models import UserProfile
from app import SessionLocal

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

# Modelos Pydantic para validación de UserProfile
class UserProfileCreate(BaseModel):
    user_id: Optional[str] = None  # Ahora es opcional
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    investment_amount: float = 1000
    investment_horizon: str = "medium"  # short, medium, long
    preferred_sectors: List[str] = []
    is_subscribed: bool = False

class UserProfileUpdate(BaseModel):
    user_id: Optional[str] = None  # También opcional en updates
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    risk_tolerance: Optional[str] = None
    investment_amount: Optional[float] = None
    investment_horizon: Optional[str] = None
    preferred_sectors: Optional[List[str]] = None
    is_subscribed: Optional[bool] = None

class UserProfileResponse(BaseModel):
    id: int
    user_id: Optional[str] = None  # También opcional en responses
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    risk_tolerance: str
    investment_amount: float
    investment_horizon: str
    preferred_sectors: List[str]
    is_subscribed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Modelo Pydantic para el request de optimización de portfolio
class PortfolioOptimizationRequest(BaseModel):
    user_id: Optional[str] = None
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    investment_amount: float = 1000
    investment_horizon: str = "medium"  # short, medium, long

# Modelo Pydantic simplificado para optimización de portfolio (solo id numérico)
class PortfolioOptimizeRequest(BaseModel):
    id: int

# Modelo Pydantic para el request del reporte de portfolio
class PortfolioReportRequest(BaseModel):
    id: int

# Dependency para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
                'per_page': 20,
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
        top_10 = market_data[:20]
        
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

# ================================
# CRUD ENDPOINTS FOR USER PROFILE
# ================================

@router.post("/user-profiles/", response_model=UserProfileResponse)
async def create_user_profile(profile: UserProfileCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo perfil de usuario
    """
    try:
        # Verificar si el user_id ya existe (solo si se proporciona)
        if profile.user_id:
            existing_profile = db.query(UserProfile).filter(UserProfile.user_id == profile.user_id).first()
            if existing_profile:
                raise HTTPException(status_code=400, detail="Ya existe un perfil para este user_id")
        
        # Convertir preferred_sectors a JSON string
        preferred_sectors_json = json.dumps(profile.preferred_sectors)
        
        # Crear nuevo perfil
        db_profile = UserProfile(
            user_id=profile.user_id,  # Puede ser None
            nombre=profile.nombre,
            apellido=profile.apellido,
            telefono=profile.telefono,
            risk_tolerance=profile.risk_tolerance,
            investment_amount=profile.investment_amount,
            investment_horizon=profile.investment_horizon,
            preferred_sectors=preferred_sectors_json,
            is_subscribed=profile.is_subscribed
        )
        
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        
        # Convertir JSON string back to list para response
        response_profile = UserProfileResponse(
            id=db_profile.id,
            user_id=db_profile.user_id,
            nombre=db_profile.nombre,
            apellido=db_profile.apellido,
            telefono=db_profile.telefono,
            risk_tolerance=db_profile.risk_tolerance,
            investment_amount=db_profile.investment_amount,
            investment_horizon=db_profile.investment_horizon,
            preferred_sectors=json.loads(db_profile.preferred_sectors) if db_profile.preferred_sectors else [],
            is_subscribed=db_profile.is_subscribed,
            created_at=db_profile.created_at,
            updated_at=db_profile.updated_at
        )
        
        return response_profile
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creando perfil de usuario: {str(e)}")

@router.get("/user-profiles/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """
    Obtener un perfil de usuario por user_id
    """
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil de usuario no encontrado")
        
        # Convertir JSON string to list para response
        response_profile = UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            nombre=profile.nombre,
            apellido=profile.apellido,
            telefono=profile.telefono,
            risk_tolerance=profile.risk_tolerance,
            investment_amount=profile.investment_amount,
            investment_horizon=profile.investment_horizon,
            preferred_sectors=json.loads(profile.preferred_sectors) if profile.preferred_sectors else [],
            is_subscribed=profile.is_subscribed,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
        
        return response_profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo perfil de usuario: {str(e)}")

@router.get("/user-profiles/", response_model=List[UserProfileResponse])
async def get_all_user_profiles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtener todos los perfiles de usuario con paginación
    """
    try:
        profiles = db.query(UserProfile).offset(skip).limit(limit).all()
        
        response_profiles = []
        for profile in profiles:
            response_profile = UserProfileResponse(
                id=profile.id,
                user_id=profile.user_id,
                nombre=profile.nombre,
                apellido=profile.apellido,
                telefono=profile.telefono,
                risk_tolerance=profile.risk_tolerance,
                investment_amount=profile.investment_amount,
                investment_horizon=profile.investment_horizon,
                preferred_sectors=json.loads(profile.preferred_sectors) if profile.preferred_sectors else [],
                is_subscribed=profile.is_subscribed,
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )
            response_profiles.append(response_profile)
        
        return response_profiles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo perfiles de usuario: {str(e)}")

@router.put("/user-profiles/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(user_id: str, profile_update: UserProfileUpdate, db: Session = Depends(get_db)):
    """
    Actualizar un perfil de usuario existente
    """
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil de usuario no encontrado")
        
        # Actualizar solo los campos proporcionados
        update_data = profile_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "preferred_sectors" and value is not None:
                # Convertir list a JSON string
                setattr(profile, field, json.dumps(value))
            elif value is not None:
                setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        
        # Convertir JSON string back to list para response
        response_profile = UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            nombre=profile.nombre,
            apellido=profile.apellido,
            telefono=profile.telefono,
            risk_tolerance=profile.risk_tolerance,
            investment_amount=profile.investment_amount,
            investment_horizon=profile.investment_horizon,
            preferred_sectors=json.loads(profile.preferred_sectors) if profile.preferred_sectors else [],
            is_subscribed=profile.is_subscribed,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
        
        return response_profile
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error actualizando perfil de usuario: {str(e)}")

@router.delete("/user-profiles/{user_id}")
async def delete_user_profile(user_id: str, db: Session = Depends(get_db)):
    """
    Eliminar un perfil de usuario
    """
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil de usuario no encontrado")
        
        db.delete(profile)
        db.commit()
        
        return {"message": f"Perfil de usuario {user_id} eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error eliminando perfil de usuario: {str(e)}")

@router.get("/user-profiles/{user_id}/exists")
async def check_user_profile_exists(user_id: str, db: Session = Depends(get_db)):
    """
    Verificar si existe un perfil para un user_id específico
    """
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        return {"exists": profile is not None, "user_id": user_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verificando existencia de perfil: {str(e)}")

# ================================
# ENDPOINTS ALTERNATIVOS USANDO ID
# ================================

@router.get("/user-profiles/by-id/{profile_id}", response_model=UserProfileResponse)
async def get_user_profile_by_id(profile_id: int, db: Session = Depends(get_db)):
    """
    Obtener un perfil de usuario por ID numérico
    """
    try:
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil de usuario no encontrado")
        
        # Convertir JSON string to list para response
        response_profile = UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            nombre=profile.nombre,
            apellido=profile.apellido,
            telefono=profile.telefono,
            risk_tolerance=profile.risk_tolerance,
            investment_amount=profile.investment_amount,
            investment_horizon=profile.investment_horizon,
            preferred_sectors=json.loads(profile.preferred_sectors) if profile.preferred_sectors else [],
            is_subscribed=profile.is_subscribed,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
        
        return response_profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo perfil de usuario: {str(e)}")

@router.put("/user-profiles/by-id/{profile_id}", response_model=UserProfileResponse)
async def update_user_profile_by_id(profile_id: int, profile_update: UserProfileUpdate, db: Session = Depends(get_db)):
    """
    Actualizar un perfil de usuario existente por ID numérico
    """
    try:
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil de usuario no encontrado")
        
        # Actualizar solo los campos proporcionados
        update_data = profile_update.dict(exclude_unset=True)
        
        # Verificar unicidad de user_id si se está actualizando
        if "user_id" in update_data and update_data["user_id"]:
            existing_profile = db.query(UserProfile).filter(
                UserProfile.user_id == update_data["user_id"],
                UserProfile.id != profile_id
            ).first()
            if existing_profile:
                raise HTTPException(status_code=400, detail="Ya existe un perfil con este user_id")
        
        for field, value in update_data.items():
            if field == "preferred_sectors" and value is not None:
                # Convertir list a JSON string
                setattr(profile, field, json.dumps(value))
            elif value is not None:
                setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        
        # Convertir JSON string back to list para response
        response_profile = UserProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            nombre=profile.nombre,
            apellido=profile.apellido,
            telefono=profile.telefono,
            risk_tolerance=profile.risk_tolerance,
            investment_amount=profile.investment_amount,
            investment_horizon=profile.investment_horizon,
            preferred_sectors=json.loads(profile.preferred_sectors) if profile.preferred_sectors else [],
            is_subscribed=profile.is_subscribed,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
        
        return response_profile
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error actualizando perfil de usuario: {str(e)}")

@router.delete("/user-profiles/by-id/{profile_id}")
async def delete_user_profile_by_id(profile_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un perfil de usuario por ID numérico
    """
    try:
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil de usuario no encontrado")
        
        db.delete(profile)
        db.commit()
        
        return {"message": f"Perfil de usuario con ID {profile_id} eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error eliminando perfil de usuario: {str(e)}")

@router.post("/optimize-portfolio")
async def optimize_portfolio(request: PortfolioOptimizeRequest, db: Session = Depends(get_db)):
    """
    Endpoint para optimizar portfolio basado en métricas económicas y perfil del usuario
    Solo requiere el id numérico, obtiene automáticamente el perfil del usuario de la BD
    Retorna las 4 mejores monedas con porcentajes de asignación y métricas completas
    """
    try:
        # Buscar el perfil del usuario en la base de datos por ID numérico
        user_profile = db.query(UserProfile).filter(UserProfile.id == request.id).first()
        
        if not user_profile:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontró el perfil del usuario con ID: {request.id}"
            )
        
        # Convertir el perfil del usuario a diccionario
        user_data = {
            "user_id": user_profile.user_id,
            "risk_tolerance": user_profile.risk_tolerance,
            "investment_amount": user_profile.investment_amount,
            "investment_horizon": user_profile.investment_horizon,
            "preferred_sectors": json.loads(user_profile.preferred_sectors) if user_profile.preferred_sectors else []
        }
        
        # Optimizar portfolio usando métricas económicas
        optimization_result = await portfolio_optimizer.optimize_portfolio_with_economic_metrics(user_data)
        
        if not optimization_result.get('success'):
            raise HTTPException(
                status_code=500, 
                detail=optimization_result.get('message', 'Error en optimización de portfolio')
            )
        
        return optimization_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizando portfolio: {str(e)}")

@router.post("/generate-portfolio-report")
async def generate_portfolio_report(request: PortfolioReportRequest, db: Session = Depends(get_db)):
    """
    Endpoint para generar un reporte explicativo en lenguaje natural del resultado de optimización de portfolio
    usando Gemini AI. Toma un id numérico, obtiene la optimización de portfolio y genera un reporte detallado.
    """
    try:
        # Buscar el perfil del usuario en la base de datos por ID numérico para validar que existe
        user_profile = db.query(UserProfile).filter(UserProfile.id == request.id).first()
        
        if not user_profile:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontró el perfil del usuario con ID: {request.id}"
            )
        
        # Llamada interna al endpoint de optimización de portfolio
        async with httpx.AsyncClient() as client:
            url = "http://localhost:8000/api/optimize-portfolio"
            payload = {"id": request.id}
            
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            portfolio_data = response.json()
        
        if not portfolio_data.get("success"):
            raise HTTPException(
                status_code=500, 
                detail=f"Error obteniendo optimización de portfolio: {portfolio_data.get('message', 'Error desconocido')}"
            )
        
        # Generar reporte explicativo usando Gemini AI
        ai_report_result = communication_agent.generate_portfolio_report_with_ai(portfolio_data)
        
        if not ai_report_result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=f"Error generando reporte con IA: {ai_report_result.get('error', 'Error desconocido')}"
            )
        
        return {
            "success": True,
            "profile_id": request.id,
            "user_id": user_profile.user_id,  # Incluir también el user_id para referencia
            "ai_report": ai_report_result['ai_report'],
            "portfolio_summary": ai_report_result['portfolio_summary'],
            "original_portfolio_data": portfolio_data,
            "generated_at": ai_report_result['generated_at'],
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte de portfolio: {str(e)}")
