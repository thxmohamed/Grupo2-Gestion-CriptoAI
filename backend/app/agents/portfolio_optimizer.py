from typing import List, Dict, Any, Tuple
import numpy as np
import pulp # Importar la biblioteca PuLP
import json
import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from app import SessionLocal
from app.models import PortfolioRecommendation

class PortfolioOptimizationAgent:
    """
    Agente Optimizador de Portafolios.
    Utiliza un enfoque de Programación Lineal para determinar la asignación
    óptima de criptomonedas en un portafolio, maximizando la deseabilidad
    sujeta a restricciones de presupuesto y riesgo del usuario.
    """
    
    def __init__(self):
        self.db = SessionLocal()

    def _map_user_profile_to_constraints(self, user_profile: Dict[str, Any]) -> Dict[str, float]:
        """
        Mapea el perfil del usuario a valores numéricos para las restricciones
        de la programación lineal.
        
        Args:
            user_profile (Dict[str, Any]): Perfil del usuario con tolerancia al riesgo,
                                           horizonte de inversión y monto.
        Returns:
            Dict[str, float]: Diccionario con el capital total y el límite de riesgo.
        """
        risk_tolerance = user_profile.get('risk_tolerance', 'moderate')
        investment_amount = user_profile.get('investment_amount', 1000.0) # Asegurar float
        
        # Define el límite de riesgo 'r' basado en la tolerancia del usuario
        # Estos valores son umbrales que deberás ajustar a tus métricas de riesgo.
        # Asumiendo que 'risk_score' de las monedas es de 0 a 100.
        if risk_tolerance == 'conservative':
            max_allowed_risk_score = 30.0 # Bajo riesgo promedio para el portafolio
        elif risk_tolerance == 'moderate':
            max_allowed_risk_score = 60.0 # Riesgo moderado
        else: # 'aggressive'
            max_allowed_risk_score = 90.0 # Alto riesgo
            
        return {
            'total_capital': investment_amount,
            'max_portfolio_risk': max_allowed_risk_score
        }

    def _calculate_v_i_c_i_r_i(self, coin: Dict[str, Any], user_profile: Dict[str, Any]) -> Tuple[float, float, float]:
        """
        Calcula los coeficientes v_i (deseabilidad), c_i (costo), y r_i (riesgo)
        para una criptomoneda específica, ajustados por el perfil del usuario.
        
        Args:
            coin (Dict[str, Any]): Las métricas de una criptomoneda.
            user_profile (Dict[str, Any]): Perfil del usuario.
            
        Returns:
            Tuple[float, float, float]: (v_i, c_i, r_i)
        """
        # === c_i (Costo) ===
        # El costo es simplemente el precio actual de la moneda.
        # Asegúrate de que no sea cero para evitar divisiones por cero.
        c_i = coin.get('current_price', 0.0001) 
        if c_i <= 0: # Evitar costos negativos o cero irreales
            c_i = 0.0001
            
        # === r_i (Riesgo) ===
        # Usamos el 'risk_score' directamente, normalizado a 0-100.
        r_i = coin.get('risk_score', 50.0)
        
        # === v_i (Deseabilidad / Valor) ===
        # Aquí combinaremos investment_score, expected_return, stability_score
        # y market_sentiment, ajustados por el perfil del usuario.
        
        investment_score = coin.get('investment_score', 50.0)
        expected_return = coin.get('expected_return', 0.0) # %
        stability_score = coin.get('stability_score', 50.0)
        market_sentiment = coin.get('market_sentiment', 'neutral')
        
        # Ajuste base de v_i
        v_i = investment_score * 0.4 + stability_score * 0.3 + (expected_return * 10) * 0.3 # Ponderación base
        
        # Ajustes basados en el perfil del usuario (similar a tu lógica de puntuación anterior)
        risk_tolerance = user_profile.get('risk_tolerance', 'moderate')
        investment_horizon = user_profile.get('investment_horizon', 'medium')
        
        if risk_tolerance == 'conservative':
            v_i += stability_score * 0.5 # Conservadores valoran más la estabilidad
            v_i -= r_i * 0.8 # Penalizar más el riesgo
            if market_sentiment == 'bearish': v_i *= 0.5 # Evitar bajistas
            if market_sentiment == 'neutral': v_i *= 1.2 # Preferir neutral
            
        elif risk_tolerance == 'moderate':
            v_i += expected_return * 0.8 # Moderados buscan equilibrio, retorno es importante
            v_i += investment_score * 0.3
            if market_sentiment == 'bullish': v_i *= 1.3 # Bonificar alcistas
            elif market_sentiment == 'bearish': v_i *= 0.7 # Penalizar bajistas
            
        else: # 'aggressive'
            v_i += expected_return * 1.5 # Agresivos priorizan el retorno
            v_i += (100 - r_i) * 0.2 # El riesgo bajo también es un "valor" para agresivos (oportunidad)
            if market_sentiment == 'bullish': v_i *= 1.5 # Más bonificación
            elif market_sentiment == 'bearish': v_i *= 1.1 # Pueden ver oportunidad en bajistas
        
        # Ajustes por horizonte de inversión
        if investment_horizon == 'short':
            v_i += (coin.get('liquidity_ratio', 0) * 20) # Liquidez muy importante
        elif investment_horizon == 'long':
            v_i += (coin.get('market_cap', 0) / 1e9) * 0.05 # Favorecer grandes capitalizaciones para largo plazo
            
        # Asegurarse de que v_i sea positivo para la maximización
        # Un v_i negativo haría que el optimizador no quiera seleccionar esa moneda.
        v_i = max(0.01, v_i) 
            
        return float(v_i), float(c_i), float(r_i)

    def optimize_portfolio_lp(self, available_coins: List[Dict[str, Any]], 
                               user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza el portafolio utilizando Programación Lineal.
        
        Args:
            available_coins (List[Dict[str, Any]]): Lista de criptomonedas con sus métricas.
            user_profile (Dict[str, Any]): Perfil del usuario (capital, tolerancia al riesgo, etc.).
            
        Returns:
            Dict[str, Any]: Un diccionario con la recomendación del portafolio,
                            incluyendo monedas, porcentajes de asignación y métricas esperadas.
        """
        
        if not available_coins:
            return {
                'success': False,
                'message': 'No hay monedas disponibles para optimizar.'
            }

        # 1. Preparar el problema de PL
        prob = pulp.LpProblem("Crypto Portfolio Optimization", pulp.LpMaximize)

        # 2. Definir variables de decisión
        # x_i: porcentaje de inversión en cada moneda (entre 0 y 1)
        # Usamos coin['symbol'] como clave única
        coin_vars = {}
        for coin in available_coins:
            symbol = coin['symbol']
            coin_vars[symbol] = pulp.LpVariable(symbol, 0, 1) # Variable continua entre 0 y 1

        # Mapear métricas a coeficientes para la PL
        coin_data_lp = {} # Para almacenar v_i, c_i, r_i
        for coin in available_coins:
            v_i, c_i, r_i = self._calculate_v_i_c_i_r_i(coin, user_profile)
            coin_data_lp[coin['symbol']] = {
                'v_i': v_i,
                'c_i': c_i, # Costo por unidad de moneda
                'r_i': r_i  # Riesgo por unidad de moneda (asumimos que es una puntuación)
            }
        
        # 3. Función objetivo: Maximizar Z = sum(v_i * x_i)
        prob += pulp.lpSum([coin_data_lp[s]['v_i'] * coin_vars[s] 
                            for s in coin_vars]), "Total Deseability"

        # 4. Restricciones
        user_constraints = self._map_user_profile_to_constraints(user_profile)
        total_capital = user_constraints['total_capital']
        max_portfolio_risk = user_constraints['max_portfolio_risk']
        
        # Restricción 1: Suma de pesos igual a 1 (100% del capital)
        # Esto asegura que todo el capital se asigna.
        prob += pulp.lpSum([coin_vars[s] for s in coin_vars]) == 1, "Sum of Weights Must Be 1"

        # Restricción 2: Restricción de riesgo (riesgo total del portafolio no excede el límite)
        # El riesgo promedio ponderado del portafolio no debe exceder el max_portfolio_risk.
        # Sum(r_i * x_i) <= max_portfolio_risk
        prob += pulp.lpSum([coin_data_lp[s]['r_i'] * coin_vars[s] 
                            for s in coin_vars]) <= max_portfolio_risk, "Total Portfolio Risk"

        # Restricción adicional: Máximo de 4 monedas (para una recomendación más práctica)
        # Para esto, necesitamos variables binarias para indicar si una moneda es seleccionada (x_i > 0).
        # Esto convierte el problema en Programación Lineal Entera Mixta (MILP).
        # Pulp lo soporta, pero puede ser más lento.
        
        # Opcion 1: Sin límite de monedas (más fiel a PL pura, pero puede dar muchas monedas)
        # Opcion 2: Con límite de monedas (MILP, más práctico para recomendaciones)
        # Por ahora, iremos con la Opción 1 para mantenerlo PL puro.
        # Si quieres MILP, descomenta y adapta la siguiente lógica:
        """
        # Crear variables binarias para selección de moneda
        binary_vars = {}
        for coin in available_coins:
            symbol = coin['symbol']
            binary_vars[symbol] = pulp.LpVariable(f"Select_{symbol}", 0, 1, pulp.LpBinary)
            # Si x_i > 0, entonces binary_vars[symbol] debe ser 1
            # Multiplicar por un número grande (M) para forzar la relación
            prob += coin_vars[symbol] <= binary_vars[symbol] * 1 # small epsilon to allow for very small values
            # Puedes ajustar el epsilon o M para tu caso de uso.
            # prob += coin_vars[symbol] <= binary_vars[symbol] # If we dont care about small values near 0
            
        # Suma de variables binarias <= 4
        prob += pulp.lpSum([binary_vars[s] for s in binary_vars]) <= 4, "Max 4 Coins Selected"
        """

        # 5. Resolver el problema
        try:
            prob.solve() 

            if prob.status != pulp.LpStatusOptimal:
                print(f"Advertencia: No se encontró una solución óptima. Estado: {pulp.LpStatus[prob.status]}")
                return {
                    'success': False,
                    'message': f'No se encontró una solución óptima para la optimización. Estado: {pulp.LpStatus[prob.status]}'
                }
            
            # 6. Extraer resultados
            recommended_coins_lp = []
            allocation_percentages_lp = {}
            total_investment = user_profile.get('investment_amount', 1000.0)
            
            for coin in available_coins:
                symbol = coin['symbol']
                weight = coin_vars[symbol].varValue # Obtener el valor de la variable (porcentaje)

                if weight > 0.0001: # Solo incluir monedas con una asignación significativa
                    # Buscar la moneda completa de la lista original
                    original_coin_data = next((c for c in available_coins if c['symbol'] == symbol), None)
                    if original_coin_data:
                        recommended_coins_lp.append((original_coin_data, weight))
                        allocation_percentages_lp[symbol] = round(weight * 100, 2)
            
            # Ordenar por peso descendente y tomar las top N si no usaste la restricción de cantidad.
            # Si no usas la restricción de 4 monedas, PuLP puede devolver muchas,
            # así que puedes tomar las top N aquí basado en el peso.
            recommended_coins_lp = sorted(recommended_coins_lp, key=lambda x: x[1], reverse=True)[:4]
            
            # Re-normalizar los pesos si se seleccionó un subconjunto después de la solución.
            # Esto es importante si PuLP dio más de 4 monedas y tomaste solo las 4 primeras.
            total_final_weight = sum(w for _, w in recommended_coins_lp)
            if total_final_weight > 0:
                recommended_coins_lp = [(c, w / total_final_weight) for c, w in recommended_coins_lp]

            # Calcular métricas del portfolio final
            portfolio_metrics = self.calculate_expected_metrics(recommended_coins_lp)
            reasoning = self.generate_reasoning(recommended_coins_lp, user_profile, portfolio_metrics)
            
            # Preparar la respuesta final
            final_recommended_coins = [
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
                for coin, weight in recommended_coins_lp
            ]

            investment_amounts = {
                coin_data['symbol']: round(total_investment * weight, 2)
                for coin_data, weight in recommended_coins_lp
            }
            
            # Guardar recomendación en base de datos si hay user_id
            recommendation_id = None
            if user_profile.get('user_id'):
                recommendation = PortfolioRecommendation(
                    user_id=user_profile['user_id'],
                    recommended_coins=json.dumps(final_recommended_coins),
                    # ¡CORRECCIÓN AQUÍ!
                    # `recommended_coins_lp` es una lista de (coin_dict, weight_float) tuples.
                    # Necesitamos el símbolo de la moneda y el peso directamente.
                    allocation_percentages=json.dumps({coin_data['symbol']: round(weight * 100, 2) for coin_data, weight in recommended_coins_lp}),
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
                    'user_id': user_profile.get('user_id', 'anonymous'),
                    'risk_tolerance': user_profile.get('risk_tolerance', 'moderate'),
                    'investment_amount': total_investment,
                    'investment_horizon': user_profile.get('investment_horizon', 'medium')
                },
                'portfolio_optimization': {
                    'top_4_coins': final_recommended_coins,
                    'allocation_percentages': allocation_percentages_lp,
                    'investment_amounts': investment_amounts,
                    'total_investment': total_investment
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
            self.db.rollback()
            print(f"Error optimizando portfolio con PL: {e}")
            return {
                'success': False,
                'message': f'Error en optimización (PL): {str(e)}'
            }
        finally:
            self.db.close()

    # MÉTODOS AUXILIARES (mantienen la misma lógica, solo cambian de nombre o se adaptan)
    # Ya no se usa calculate_portfolio_weights ni _calculate_coin_score directamente para la PL,
    # sino que _calculate_v_i_c_i_r_i prepara los coeficientes.

    def calculate_expected_metrics(self, selected_coins: List[Tuple[Dict[str, Any], float]]) -> Dict[str, float]:
        """
        Calcula las métricas esperadas del portafolio final.
        (Esta función se mantiene igual, ya que opera sobre las monedas y pesos resultantes de PL).
        """
        if not selected_coins:
            return {'expected_return': 0, 'risk_score': 50, 'confidence_level': 0}
        
        expected_return = 0
        total_risk = 0
        total_confidence = 0
        
        for coin, weight in selected_coins:
            coin_return = coin.get('expected_return', 0.0) / 100 
            expected_return += coin_return * weight
            
            coin_risk = coin.get('risk_score', 50.0)
            total_risk += coin_risk * weight
            
            investment_score = coin.get('investment_score', 0.0)
            stability_score = coin.get('stability_score', 0.0)
            coin_confidence = (abs(investment_score) + stability_score) / 2
            total_confidence += coin_confidence * weight
        
        return {
            'expected_return': round(expected_return * 100, 2),
            'risk_score': round(total_risk, 2),
            'confidence_level': round(total_confidence, 2)
        }
    
    def generate_reasoning(self, selected_coins: List[Tuple[Dict[str, Any], float]], 
                         user_profile: Dict[str, Any], metrics: Dict[str, float]) -> str:
        """
        Genera una explicación de la recomendación del portafolio.
        (Esta función se mantiene igual).
        """
        risk_tolerance = user_profile.get('risk_tolerance', 'moderate')
        investment_horizon = user_profile.get('investment_horizon', 'medium')
        
        reasoning = f"Recomendación de portfolio para perfil {risk_tolerance} con horizonte {investment_horizon} (Optimización Lineal):\n\n"
        
        if not selected_coins:
            reasoning += "No se pudieron seleccionar monedas óptimas según los criterios."
            return reasoning

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
        reasoning += f"• Score de riesgo promedio: {metrics['risk_score']}/100\n"
        reasoning += f"• Nivel de confianza: {metrics['confidence_level']}%\n"
        
        return reasoning
    
    async def optimize_portfolio_with_economic_metrics(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtiene métricas económicas y luego llama al optimizador PL.
        (Esta función se adapta para usar optimize_portfolio_lp).
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/api/economic-metrics")
                if response.status_code != 200:
                    return {
                        'success': False,
                        'message': 'No se pudieron obtener las métricas económicas'
                    }
                
                metrics_data = response.json()
                available_coins = metrics_data.get('metrics', [])
            
            # Llama a la nueva función de optimización PL
            return self.optimize_portfolio_lp(available_coins, user_data)
            
        except Exception as e:
            if hasattr(self, 'db'):
                self.db.rollback()
            print(f"Error en la preparación para optimización PL: {e}")
            return {
                'success': False,
                'message': f'Error en la preparación de optimización (PL): {str(e)}'
            }
        finally:
            if hasattr(self, 'db'):
                self.db.close()
