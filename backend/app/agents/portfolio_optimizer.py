from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app import SessionLocal
from app.models import PortfolioRecommendation

class PortfolioOptimizationAgent:
    """
    Agente Optimización Portfolio - Envía datos del usuario y métricas de monedas
    pertinentes al usuario. Entrega mejores monedas para usuario.
    Para la optimización importan los datos del usuario, por ejemplo, si este 
    quiere ser inversionista riesgoso, métricas que dicen que una moneda es 
    inestable, no tienen mucho peso negativo para la optimización.
    """
    
    def __init__(self):
        self.db = SessionLocal()
    
    def calculate_portfolio_weights(self, coins: List[Dict[str, Any]], 
                                  user_profile: Dict[str, Any]) -> Dict[str, float]:
        """Calcular pesos óptimos para el portfolio basado en perfil del usuario"""
        
        risk_tolerance = user_profile.get('risk_tolerance', 'moderate')
        investment_horizon = user_profile.get('investment_horizon', 'medium')
        investment_amount = user_profile.get('investment_amount', 1000)
        
        scores = []
        for coin in coins:
            score = self._calculate_coin_score(coin, risk_tolerance, investment_horizon)
            scores.append(score)
        
        # Normalizar scores para obtener pesos
        total_score = sum(scores)
        if total_score == 0:
            # Distribución equitativa si no hay scores válidos
            weight = 1.0 / len(coins)
            return {coin['symbol']: weight for coin in coins}
        
        weights = {}
        for i, coin in enumerate(coins):
            weights[coin['symbol']] = scores[i] / total_score
        
        return weights
    
    def _calculate_coin_score(self, coin: Dict[str, Any], risk_tolerance: str, 
                            investment_horizon: str) -> float:
        """Calcular score de una moneda basado en perfil del usuario"""
        
        base_score = 50.0
        
        # Factores base
        growth_potential = coin.get('growth_potential', 50)
        stability_score = coin.get('stability_score', 50)
        volatility = coin.get('volatility', 10)
        rsi = coin.get('rsi', 50)
        market_sentiment = coin.get('market_sentiment', 'neutral')
        
        # Ajustar score según tolerancia al riesgo
        if risk_tolerance == 'conservative':
            # Priorizar estabilidad y bajo riesgo
            base_score += stability_score * 0.4
            base_score += (100 - volatility) * 0.3  # Penalizar alta volatilidad
            base_score += growth_potential * 0.2
            
            # Bonificación por sentimiento positivo pero estable
            if market_sentiment == 'bullish':
                base_score += 10
            elif market_sentiment == 'neutral':
                base_score += 5
            
        elif risk_tolerance == 'moderate':
            # Balance entre crecimiento y estabilidad
            base_score += growth_potential * 0.35
            base_score += stability_score * 0.35
            base_score += (100 - volatility) * 0.2
            
            # Sentimiento del mercado
            if market_sentiment == 'bullish':
                base_score += 15
            elif market_sentiment == 'neutral':
                base_score += 5
            
        else:  # aggressive
            # Priorizar crecimiento y oportunidades de alto riesgo
            base_score += growth_potential * 0.5
            base_score += volatility * 0.2  # La volatilidad puede ser buena para traders agresivos
            base_score += stability_score * 0.1
            
            # Mayor peso al sentimiento alcista
            if market_sentiment == 'bullish':
                base_score += 25
            elif market_sentiment == 'neutral':
                base_score += 10
        
        # Ajustar según horizonte de inversión
        if investment_horizon == 'short':
            # Favorecer momentum y RSI
            if 30 <= rsi <= 70:  # RSI en rango favorable
                base_score += 15
            
            # Bonificar crecimiento reciente
            price_change = coin.get('price_change_24h', 0)
            if price_change > 0:
                base_score += min(price_change, 20)
                
        elif investment_horizon == 'long':
            # Favorecer fundamentales sólidos
            base_score += stability_score * 0.2
            
            # Penalizar menos la volatilidad a largo plazo
            if volatility > 20:
                base_score -= (volatility - 20) * 0.1
        
        # Asegurar que el score esté en rango válido
        return max(0, min(100, base_score))
    
    def select_top_coins(self, coins: List[Dict[str, Any]], 
                        weights: Dict[str, float]) -> List[Tuple[Dict[str, Any], float]]:
        """Seleccionar las top 5 monedas con sus pesos"""
        
        # Ordenar por peso descendente
        sorted_coins = sorted(
            [(coin, weights.get(coin['symbol'], 0)) for coin in coins],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Tomar top 5
        top_5 = sorted_coins[:5]
        
        # Normalizar pesos para que sumen 1
        total_weight = sum(weight for _, weight in top_5)
        if total_weight > 0:
            top_5 = [(coin, weight/total_weight) for coin, weight in top_5]
        
        return top_5
    
    def calculate_expected_metrics(self, selected_coins: List[Tuple[Dict[str, Any], float]]) -> Dict[str, float]:
        """Calcular métricas esperadas del portfolio"""
        
        if not selected_coins:
            return {'expected_return': 0, 'risk_score': 50, 'confidence_level': 0}
        
        # Calcular retorno esperado ponderado
        expected_return = 0
        total_risk = 0
        total_confidence = 0
        
        for coin, weight in selected_coins:
            # Estimar retorno basado en potencial de crecimiento y sentimiento
            coin_return = coin.get('growth_potential', 50) / 100 * 0.2  # 20% máximo esperado
            
            # Ajustar por sentimiento del mercado
            sentiment = coin.get('market_sentiment', 'neutral')
            if sentiment == 'bullish':
                coin_return *= 1.2
            elif sentiment == 'bearish':
                coin_return *= 0.8
            
            expected_return += coin_return * weight
            
            # Calcular riesgo ponderado
            volatility = coin.get('volatility', 10)
            stability = coin.get('stability_score', 50)
            coin_risk = (volatility + (100 - stability)) / 2
            total_risk += coin_risk * weight
            
            # Calcular confianza basada en datos disponibles
            coin_confidence = min(100, coin.get('growth_potential', 0) + coin.get('stability_score', 0)) / 2
            total_confidence += coin_confidence * weight
        
        return {
            'expected_return': round(expected_return * 100, 2),  # Como porcentaje
            'risk_score': round(total_risk, 2),
            'confidence_level': round(total_confidence, 2)
        }
    
    def generate_reasoning(self, selected_coins: List[Tuple[Dict[str, Any], float]], 
                         user_profile: Dict[str, Any], metrics: Dict[str, float]) -> str:
        """Generar explicación de la recomendación"""
        
        risk_tolerance = user_profile.get('risk_tolerance', 'moderate')
        investment_horizon = user_profile.get('investment_horizon', 'medium')
        
        reasoning = f"Recomendación de portfolio para perfil {risk_tolerance} con horizonte {investment_horizon}:\n\n"
        
        for i, (coin, weight) in enumerate(selected_coins, 1):
            percentage = round(weight * 100, 1)
            reasoning += f"{i}. {coin['name']} ({coin['symbol']}) - {percentage}%\n"
            reasoning += f"   • Potencial de crecimiento: {coin.get('growth_potential', 0)}/100\n"
            reasoning += f"   • Estabilidad: {coin.get('stability_score', 0)}/100\n"
            reasoning += f"   • Riesgo: {coin.get('risk_level', 'unknown')}\n"
            reasoning += f"   • Sentimiento: {coin.get('market_sentiment', 'neutral')}\n\n"
        
        reasoning += f"Métricas del portfolio:\n"
        reasoning += f"• Retorno esperado: {metrics['expected_return']}%\n"
        reasoning += f"• Score de riesgo: {metrics['risk_score']}/100\n"
        reasoning += f"• Nivel de confianza: {metrics['confidence_level']}%\n"
        
        return reasoning
    
    async def optimize_portfolio(self, user_data: Dict[str, Any], 
                               available_coins: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimizar portfolio para el usuario"""
        
        try:
            if not available_coins:
                return {
                    'success': False,
                    'message': 'No hay monedas disponibles para optimizar'
                }
            
            # Calcular pesos óptimos
            weights = self.calculate_portfolio_weights(available_coins, user_data)
            
            # Seleccionar top 5 monedas
            selected_coins = self.select_top_coins(available_coins, weights)
            
            if not selected_coins:
                return {
                    'success': False,
                    'message': 'No se pudieron seleccionar monedas adecuadas'
                }
            
            # Calcular métricas del portfolio
            portfolio_metrics = self.calculate_expected_metrics(selected_coins)
            
            # Generar explicación
            reasoning = self.generate_reasoning(selected_coins, user_data, portfolio_metrics)
            
            # Preparar datos para almacenar
            recommended_coins = [
                {
                    'symbol': coin['symbol'],
                    'name': coin['name'],
                    'allocation_percentage': round(weight * 100, 2),
                    'current_price': coin.get('current_price', 0),
                    'market_cap': coin.get('market_cap', 0)
                }
                for coin, weight in selected_coins
            ]
            
            allocation_percentages = {
                coin['symbol']: round(weight * 100, 2) 
                for coin, weight in selected_coins
            }
            
            # Guardar recomendación en base de datos
            recommendation = PortfolioRecommendation(
                user_id=user_data.get('user_id', 'anonymous'),
                recommended_coins=json.dumps(recommended_coins),
                allocation_percentages=json.dumps(allocation_percentages),
                expected_return=portfolio_metrics['expected_return'],
                risk_score=portfolio_metrics['risk_score'],
                confidence_level=portfolio_metrics['confidence_level'],
                reasoning=reasoning
            )
            
            self.db.add(recommendation)
            self.db.commit()
            
            return {
                'success': True,
                'recommended_coins': recommended_coins,
                'allocation_percentages': allocation_percentages,
                'expected_return': portfolio_metrics['expected_return'],
                'risk_score': portfolio_metrics['risk_score'],
                'confidence_level': portfolio_metrics['confidence_level'],
                'reasoning': reasoning,
                'recommendation_id': recommendation.id
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"Error optimizando portfolio: {e}")
            return {
                'success': False,
                'message': f'Error en optimización: {str(e)}'
            }
        finally:
            self.db.close()
