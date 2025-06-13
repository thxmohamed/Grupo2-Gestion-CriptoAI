from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import json
import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from app import SessionLocal
from app.models import PortfolioRecommendation
import httpx

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
        """Calcular score de una moneda basado en perfil del usuario y métricas económicas"""
        
        # Factores base desde economic-metrics
        investment_score = coin.get('investment_score', 0)
        risk_score = coin.get('risk_score', 50)  # FACTOR MÁS IMPORTANTE
        volatility = coin.get('volatility', 10)
        stability_score = coin.get('stability_score', 50)
        expected_return = coin.get('expected_return', 0)
        liquidity_ratio = coin.get('liquidity_ratio', 1)
        market_sentiment = coin.get('market_sentiment', 'neutral')
        price_change_24h = coin.get('price_change_24h', 0)
        
        # COMENZAR CON EL RISK_SCORE COMO FACTOR PRINCIPAL
        # risk_score más bajo = mejor para la mayoría de perfiles
        risk_adjusted_base = 100 - risk_score  # Invertir: risk_score alto = score bajo
        
        # Ajustar score según tolerancia al riesgo - RISK_SCORE ES CENTRAL
        if risk_tolerance == 'conservative':
            # Para conservadores, el riesgo bajo es CRÍTICO
            base_score = risk_adjusted_base * 1.5  # Amplificar importancia del riesgo bajo
            
            # Bonificar estabilidad fuertemente
            base_score += stability_score * 0.8
            
            # Penalizar riesgo alto de forma exponencial
            if risk_score > 30:
                base_score -= (risk_score - 30) ** 1.5  # Penalización exponencial
            
            # Favorecer liquidez para seguridad
            base_score += min(liquidity_ratio * 15, 40)
            
            # Investment score tiene menor peso
            base_score += investment_score * 0.2
            
            # Sentimiento del mercado - conservadores prefieren estabilidad
            if market_sentiment == 'neutral':
                base_score *= 1.4
            elif market_sentiment == 'bullish':
                base_score *= 1.1
            elif market_sentiment == 'bearish':
                base_score *= 0.6  # Evitar mercados bajistas
            
        elif risk_tolerance == 'moderate':
            # Para moderados, BALANCEAR riesgo y crecimiento
            base_score = risk_adjusted_base * 1.2  # Reducir peso del risk_score
            
            # PRIORIZAR expected_return positivo para moderados
            if expected_return > 0:
                base_score += expected_return * 25  # Bonificar fuertemente retornos positivos
            else:
                base_score += expected_return * 8   # Penalizar retornos negativos más fuerte
            
            # Investment score es crucial para crecimiento
            base_score += investment_score * 0.8  # Aumentar peso del investment_score
            
            # Bonificar stablecoins moderadamente solo si expected_return es bajo
            if risk_score < 1 and expected_return >= 0:  # Stablecoins con retorno no negativo
                base_score += 30  # Bonus moderado para stablecoins
            elif risk_score < 20:  # Monedas de bajo riesgo
                base_score += (20 - risk_score) * 1.5  # Bonus reducido para bajo riesgo
            elif risk_score > 60:  # Penalizar riesgo alto
                base_score -= (risk_score - 60) * 2.0
            
            # Estabilidad tiene peso moderado
            base_score += stability_score * 0.6
            
            # Sentimiento del mercado ES CRÍTICO para moderados
            if market_sentiment == 'bullish':
                base_score *= 1.5  # Aumentar bonus para mercados alcistas
            elif market_sentiment == 'neutral':
                base_score *= 1.2
            elif market_sentiment == 'bearish':
                base_score *= 0.5  # PENALIZAR FUERTE mercados bajistas
            
        else:  # aggressive
            # Para agresivos, pueden tolerar más riesgo pero no ignorarlo completamente
            base_score = risk_adjusted_base * 0.7  # Menos peso al riesgo, pero sigue importando
            
            # Priorizar crecimiento y retornos
            base_score += investment_score * 1.0
            base_score += expected_return * 15
            
            # La volatilidad puede ser oportunidad para agresivos
            if volatility > 15:
                base_score += min(volatility * 0.5, 20)
            
            # Penalizar riesgo extremo incluso para agresivos
            if risk_score > 80:
                base_score -= (risk_score - 80) * 0.8
            
            # Sentimiento del mercado - agresivos buscan oportunidades
            if market_sentiment == 'bullish':
                base_score *= 1.6
            elif market_sentiment == 'neutral':
                base_score *= 1.1
            elif market_sentiment == 'bearish':
                base_score *= 1.0  # Pueden ver oportunidades en mercados bajistas
        
        # Ajustar según horizonte de inversión con mayor impacto
        if investment_horizon == 'short':
            # Favorecer liquidez y momentum
            base_score += min(liquidity_ratio * 8, 25)
            
            # Momentum más importante
            if price_change_24h > 0:
                base_score += min(price_change_24h * 3, 25)
            else:
                base_score += price_change_24h * 2  # Penalizar caídas
            
            # Penalizar alta volatilidad para corto plazo más fuerte
            if volatility > 20:
                base_score -= (volatility - 20) * 0.5
                
        elif investment_horizon == 'long':
            # Para horizonte largo, PRIORIZAR crecimiento sobre seguridad
            base_score += stability_score * 0.4  # Reducir peso de estabilidad
            base_score += investment_score * 1.2  # Aumentar peso a investment score
            
            # Expected return es CRÍTICO para largo plazo
            if expected_return > 2:  # Retornos altos
                base_score += expected_return * 25  # Bonificar fuertemente
            elif expected_return > 0:  # Retornos positivos
                base_score += expected_return * 20  # Bonificar retornos positivos
            else:
                base_score += expected_return * 3   # Penalizar MUY POCO retornos negativos a largo plazo
            
            # Casi no penalizar volatilidad a largo plazo
            if volatility > 40:
                base_score -= (volatility - 40) * 0.01  # Penalización mínima
            
            # Bonus significativo por fundamentos sólidos
            if stability_score > 80 and investment_score > 50:
                base_score *= 1.3  # Bonus para fundamentos excelentes
        
        # Asegurar diferenciación mínima y rango válido
        final_score = max(1, min(200, base_score))
        return final_score
    
    def select_top_coins(self, coins: List[Dict[str, Any]], 
                        weights: Dict[str, float]) -> List[Tuple[Dict[str, Any], float]]:
        """Seleccionar las top 4 monedas con sus pesos, aplicando diversificación"""
        
        # Ordenar por peso descendente
        sorted_coins = sorted(
            [(coin, weights.get(coin['symbol'], 0)) for coin in coins],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Clasificar monedas por categorías de riesgo para mejor diversificación
        low_risk_coins = []      # risk_score < 20
        medium_risk_coins = []   # 20 <= risk_score < 60 
        high_risk_coins = []     # risk_score >= 60
        
        for coin, weight in sorted_coins:
            risk_score = coin.get('risk_score', 50)
            if risk_score < 20:
                low_risk_coins.append((coin, weight))
            elif risk_score < 60:
                medium_risk_coins.append((coin, weight))
            else:
                high_risk_coins.append((coin, weight))
        
        # Aplicar diversificación: evitar demasiada concentración en stablecoins
        diversified_selection = []
        stablecoin_count = 0
        max_stablecoins = 1  # Máximo 1 stablecoin para moderados con horizonte largo
        
        # Priorizar monedas de bajo riesgo primero, luego medio, luego alto
        risk_ordered_coins = low_risk_coins + medium_risk_coins + high_risk_coins
        
        for coin, weight in risk_ordered_coins:
            symbol = coin['symbol']
            is_stablecoin = symbol in ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD']
            
            if is_stablecoin and stablecoin_count >= max_stablecoins:
                continue  # Saltar stablecoins adicionales
            
            diversified_selection.append((coin, weight))
            
            if is_stablecoin:
                stablecoin_count += 1
            
            if len(diversified_selection) >= 4:
                break
        
        # Si no tenemos 4 monedas, completar con las siguientes mejores por score original
        if len(diversified_selection) < 4:
            remaining_coins = [(c, w) for c, w in sorted_coins 
                             if (c, w) not in diversified_selection]
            needed = 4 - len(diversified_selection)
            diversified_selection.extend(remaining_coins[:needed])
        
        top_4 = diversified_selection[:4]
        
        # Aplicar ajuste de pesos para mayor diferenciación basado en risk_score
        if len(top_4) >= 2:
            adjusted_weights = []
            total_original_weight = sum(weight for _, weight in top_4)
            
            for i, (coin, weight) in enumerate(top_4):
                risk_score = coin.get('risk_score', 50)
                
                # Ajustar multiplicador basado en posición Y risk_score
                if i == 0:  # Primera moneda (mejor score)
                    base_multiplier = 1.5
                elif i == 1:  # Segunda moneda
                    base_multiplier = 1.2
                elif i == 2:  # Tercera moneda
                    base_multiplier = 0.9
                else:  # Cuarta moneda
                    base_multiplier = 0.7
                
                # Bonus adicional para monedas de bajo riesgo
                if risk_score < 20:
                    base_multiplier *= 1.2  # 20% extra para bajo riesgo
                elif risk_score > 60:
                    base_multiplier *= 0.8  # 20% penalización para alto riesgo
                
                adjusted_weight = weight * base_multiplier
                adjusted_weights.append((coin, adjusted_weight))
            
            # Normalizar pesos ajustados para que sumen 1
            total_adjusted = sum(weight for _, weight in adjusted_weights)
            if total_adjusted > 0:
                top_4 = [(coin, weight/total_adjusted) for coin, weight in adjusted_weights]
        else:
            # Normalizar pesos normalmente si hay pocas monedas
            total_weight = sum(weight for _, weight in top_4)
            if total_weight > 0:
                top_4 = [(coin, weight/total_weight) for coin, weight in top_4]
        
        return top_4
    
    def calculate_expected_metrics(self, selected_coins: List[Tuple[Dict[str, Any], float]]) -> Dict[str, float]:
        """Calcular métricas esperadas del portfolio"""
        
        if not selected_coins:
            return {'expected_return': 0, 'risk_score': 50, 'confidence_level': 0}
        
        # Calcular retorno esperado ponderado
        expected_return = 0
        total_risk = 0
        total_confidence = 0
        
        for coin, weight in selected_coins:
            # Usar retorno esperado de las métricas económicas
            coin_return = coin.get('expected_return', 0) / 100  # Convertir a decimal
            
            expected_return += coin_return * weight
            
            # Calcular riesgo ponderado usando risk_score de las métricas
            coin_risk = coin.get('risk_score', 50)
            total_risk += coin_risk * weight
            
            # Calcular confianza basada en investment_score y stability_score
            investment_score = coin.get('investment_score', 0)
            stability_score = coin.get('stability_score', 0)
            coin_confidence = (abs(investment_score) + stability_score) / 2
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
            reasoning += f"   • Investment Score: {coin.get('investment_score', 0)}\n"
            reasoning += f"   • Estabilidad: {coin.get('stability_score', 0)}/100\n"
            reasoning += f"   • Risk Score: {coin.get('risk_score', 0)}/100\n"
            reasoning += f"   • Retorno esperado: {coin.get('expected_return', 0)}%\n"
            reasoning += f"   • Volatilidad: {coin.get('volatility', 0)}%\n"
            reasoning += f"   • Liquidez: {coin.get('liquidity_ratio', 0)}\n"
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
            
            # Seleccionar top 4 monedas
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
                    'market_cap': coin.get('market_cap', 0),
                    'investment_score': coin.get('investment_score', 0),
                    'risk_score': coin.get('risk_score', 0),
                    'expected_return': coin.get('expected_return', 0),
                    'volatility': coin.get('volatility', 0),
                    'stability_score': coin.get('stability_score', 0),
                    'liquidity_ratio': coin.get('liquidity_ratio', 0),
                    'market_sentiment': coin.get('market_sentiment', 'neutral'),
                    'risk_level': coin.get('risk_level', 'unknown')
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
    
    async def optimize_portfolio_with_economic_metrics(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimizar portfolio usando métricas económicas del endpoint /api/economic-metrics"""
        
        try:
            # Obtener métricas económicas del endpoint
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/api/economic-metrics")
                if response.status_code != 200:
                    return {
                        'success': False,
                        'message': 'No se pudieron obtener las métricas económicas'
                    }
                
                metrics_data = response.json()
                available_coins = metrics_data.get('metrics', [])
            
            if not available_coins:
                return {
                    'success': False,
                    'message': 'No hay métricas disponibles para optimizar'
                }
            
            # Calcular pesos óptimos basados en el perfil del usuario
            weights = self.calculate_portfolio_weights(available_coins, user_data)
            
            # Seleccionar top 4 monedas
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
            
            # Preparar datos de respuesta con todas las métricas
            recommended_coins = [
                {
                    'symbol': coin['symbol'],
                    'name': coin['name'],
                    'allocation_percentage': round(weight * 100, 2),
                    'current_price': coin.get('current_price', 0),
                    'market_cap': coin.get('market_cap', 0),
                    'investment_score': coin.get('investment_score', 0),
                    'risk_score': coin.get('risk_score', 0),
                    'expected_return': coin.get('expected_return', 0),
                    'volatility': coin.get('volatility', 0),
                    'stability_score': coin.get('stability_score', 0),
                    'liquidity_ratio': coin.get('liquidity_ratio', 0),
                    'market_sentiment': coin.get('market_sentiment', 'neutral'),
                    'risk_level': coin.get('risk_level', 'unknown'),
                    'price_change_24h': coin.get('price_change_24h', 0),
                    'volume_24h': coin.get('volume_24h', 0)
                }
                for coin, weight in selected_coins
            ]
            
            allocation_percentages = {
                coin['symbol']: round(weight * 100, 2) 
                for coin, weight in selected_coins
            }
            
            # Calcular monto de inversión por moneda
            investment_amount = user_data.get('investment_amount', 1000)
            investment_amounts = {
                coin['symbol']: round(investment_amount * weight, 2)
                for coin, weight in selected_coins
            }
            
            # Guardar recomendación en base de datos si hay user_id
            recommendation_id = None
            if user_data.get('user_id'):
                recommendation = PortfolioRecommendation(
                    user_id=user_data['user_id'],
                    recommended_coins=json.dumps(recommended_coins),
                    allocation_percentages=json.dumps(allocation_percentages),
                    expected_return=portfolio_metrics['expected_return'],
                    risk_score=portfolio_metrics['risk_score'],
                    confidence_level=portfolio_metrics['confidence_level'],
                    reasoning=reasoning
                )
                
                self.db.add(recommendation)
                self.db.commit()
                recommendation_id = recommendation.id
            
            return {
                'success': True,
                'user_profile': {
                    'user_id': user_data.get('user_id', 'anonymous'),
                    'risk_tolerance': user_data.get('risk_tolerance', 'moderate'),
                    'investment_amount': investment_amount,
                    'investment_horizon': user_data.get('investment_horizon', 'medium')
                },
                'portfolio_optimization': {
                    'top_4_coins': recommended_coins,
                    'allocation_percentages': allocation_percentages,
                    'investment_amounts': investment_amounts,
                    'total_investment': investment_amount
                },
                'portfolio_metrics': {
                    'expected_return': portfolio_metrics['expected_return'],
                    'risk_score': portfolio_metrics['risk_score'],
                    'confidence_level': portfolio_metrics['confidence_level']
                },
                'reasoning': reasoning,
                'recommendation_id': recommendation_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            if hasattr(self, 'db'):
                self.db.rollback()
            print(f"Error optimizando portfolio con métricas económicas: {e}")
            return {
                'success': False,
                'message': f'Error en optimización: {str(e)}'
            }
        finally:
            if hasattr(self, 'db'):
                self.db.close()
    
    def _debug_coin_score_calculation(self, coin: Dict[str, Any], risk_tolerance: str, 
                                     investment_horizon: str) -> Dict[str, Any]:
        """Método de debugging para mostrar cómo se calcula el score de una moneda"""
        
        # Factores base
        investment_score = coin.get('investment_score', 0)
        risk_score = coin.get('risk_score', 50)
        stability_score = coin.get('stability_score', 50)
        expected_return = coin.get('expected_return', 0)
        liquidity_ratio = coin.get('liquidity_ratio', 1)
        market_sentiment = coin.get('market_sentiment', 'neutral')
        
        # Base inicial
        risk_adjusted_base = 100 - risk_score
        
        debug_info = {
            'coin_symbol': coin.get('symbol'),
            'risk_score': risk_score,
            'risk_adjusted_base': risk_adjusted_base,
            'investment_score': investment_score,
            'stability_score': stability_score,
            'expected_return': expected_return,
            'market_sentiment': market_sentiment,
            'user_risk_tolerance': risk_tolerance,
            'calculation_steps': []
        }
        
        # Calcular score usando la misma lógica
        base_score = risk_adjusted_base * (1.5 if risk_tolerance == 'conservative' 
                                         else 1.0 if risk_tolerance == 'moderate' 
                                         else 0.7)
        
        debug_info['calculation_steps'].append(f"Base score (100 - risk_score) * multiplier = {base_score:.2f}")
        
        final_score = self._calculate_coin_score(coin, risk_tolerance, investment_horizon)
        debug_info['final_score'] = final_score
        
        return debug_info
