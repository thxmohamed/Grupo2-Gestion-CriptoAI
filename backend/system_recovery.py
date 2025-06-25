#!/usr/bin/env python3
"""
Script de diagnóstico y recuperación para el sistema CriptoAI
Detecta problemas de rate limiting y aplica soluciones automáticas
"""
import asyncio
import logging
import time
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Añadir el directorio padre al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import coingecko_helper, rate_limiter
from app.config import get_api_config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemDiagnostic:
    """Diagnóstico y recuperación del sistema"""
    
    def __init__(self):
        self.config = get_api_config()
        self.issues_found = []
        self.recovery_actions = []
    
    async def diagnose_api_health(self) -> Dict[str, Any]:
        """Diagnosticar salud de las APIs"""
        logger.info("🔍 Iniciando diagnóstico de APIs...")
        
        results = {
            'coingecko': await self._test_coingecko_api(),
            'system_status': await self._check_system_status(),
            'rate_limiter_status': self._check_rate_limiter_status()
        }
        
        return results
    
    async def _test_coingecko_api(self) -> Dict[str, Any]:
        """Probar conectividad con CoinGecko API"""
        try:
            logger.info("🔗 Probando conectividad con CoinGecko...")
            
            # Intentar una petición simple
            start_time = time.time()
            data = await coingecko_helper.get_coins_markets(
                vs_currency='usd',
                per_page=5,
                page=1
            )
            response_time = time.time() - start_time
            
            if data and len(data) > 0:
                return {
                    'status': 'healthy',
                    'response_time': round(response_time, 2),
                    'data_count': len(data),
                    'message': 'API funciona correctamente'
                }
            else:
                self.issues_found.append('CoinGecko API no retorna datos')
                return {
                    'status': 'degraded',
                    'response_time': round(response_time, 2),
                    'data_count': 0,
                    'message': 'API responde pero sin datos'
                }
                
        except Exception as e:
            error_msg = str(e)
            self.issues_found.append(f'Error en CoinGecko API: {error_msg}')
            
            if '429' in error_msg:
                return {
                    'status': 'rate_limited',
                    'message': 'Rate limit alcanzado - esperando recuperación',
                    'suggested_action': 'wait_and_reduce_frequency'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Error de conectividad: {error_msg}',
                    'suggested_action': 'check_network_and_retry'
                }
    
    async def _check_system_status(self) -> Dict[str, Any]:
        """Verificar estado general del sistema"""
        try:
            from app.agents.data_collector import DataCollectorAgent
            from app.agents.economic_analysis import EconomicAnalysisAgent
            
            # Verificar instanciación de agentes
            data_collector = DataCollectorAgent()
            economic_analyzer = EconomicAnalysisAgent()
            
            return {
                'status': 'healthy',
                'agents_loaded': True,
                'message': 'Todos los agentes cargados correctamente'
            }
            
        except Exception as e:
            self.issues_found.append(f'Error cargando agentes: {str(e)}')
            return {
                'status': 'error',
                'agents_loaded': False,
                'message': f'Error en agentes: {str(e)}'
            }
    
    def _check_rate_limiter_status(self) -> Dict[str, Any]:
        """Verificar estado del rate limiter"""
        current_time = time.time()
        
        # Limpiar llamadas antiguas
        rate_limiter.coingecko_calls = [
            call for call in rate_limiter.coingecko_calls 
            if current_time - call < 60
        ]
        
        coingecko_calls_count = len(rate_limiter.coingecko_calls)
        coingecko_remaining = max(0, rate_limiter.coingecko_limit - coingecko_calls_count)
        
        # Verificar backoff activo
        coingecko_backoff = (
            'coingecko' in rate_limiter.backoff_delay and 
            current_time < rate_limiter.backoff_delay['coingecko']
        )
        
        cache_entries = len(rate_limiter.cache)
        
        status = 'healthy'
        if coingecko_backoff:
            status = 'backoff_active'
        elif coingecko_remaining < 2:
            status = 'rate_limit_near'
        
        return {
            'status': status,
            'coingecko_calls_remaining': coingecko_remaining,
            'coingecko_backoff_active': coingecko_backoff,
            'cache_entries': cache_entries,
            'message': f'Rate limiter: {coingecko_calls_count}/{rate_limiter.coingecko_limit} llamadas usadas'
        }
    
    async def apply_recovery_actions(self) -> Dict[str, Any]:
        """Aplicar acciones de recuperación automática"""
        logger.info("🔧 Aplicando acciones de recuperación...")
        
        recovery_results = []
        
        # Limpiar caché expirado
        await self._clear_expired_cache()
        recovery_results.append("Caché limpiado")
        
        # Resetear rate limiter si es necesario
        if self._should_reset_rate_limiter():
            self._reset_rate_limiter()
            recovery_results.append("Rate limiter reseteado")
        
        # Esperar si hay backoff activo
        await self._wait_for_backoff_if_needed()
        
        # Configurar rate limiter más conservador
        self._configure_conservative_limits()
        recovery_results.append("Límites configurados de manera conservadora")
        
        return {
            'actions_applied': recovery_results,
            'timestamp': datetime.now().isoformat(),
            'status': 'recovery_completed'
        }
    
    async def _clear_expired_cache(self):
        """Limpiar entradas de caché expiradas"""
        current_time = time.time()
        expired_keys = []
        
        for key, expiry_time in rate_limiter.cache_ttl.items():
            if current_time >= expiry_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            if key in rate_limiter.cache:
                del rate_limiter.cache[key]
            if key in rate_limiter.cache_ttl:
                del rate_limiter.cache_ttl[key]
        
        logger.info(f"Eliminadas {len(expired_keys)} entradas de caché expiradas")
    
    def _should_reset_rate_limiter(self) -> bool:
        """Determinar si se debe resetear el rate limiter"""
        current_time = time.time()
        
        # Si hay muchas llamadas recientes, no resetear
        recent_calls = [
            call for call in rate_limiter.coingecko_calls 
            if current_time - call < 300  # últimos 5 minutos
        ]
        
        return len(recent_calls) == 0
    
    def _reset_rate_limiter(self):
        """Resetear el rate limiter"""
        rate_limiter.coingecko_calls = []
        rate_limiter.binance_calls = []
        rate_limiter.backoff_delay = {}
        logger.info("Rate limiter reseteado")
    
    async def _wait_for_backoff_if_needed(self):
        """Esperar si hay backoff activo"""
        current_time = time.time()
        
        if 'coingecko' in rate_limiter.backoff_delay:
            wait_time = rate_limiter.backoff_delay['coingecko'] - current_time
            if wait_time > 0:
                logger.info(f"Esperando {wait_time:.1f}s por backoff...")
                await asyncio.sleep(wait_time)
    
    def _configure_conservative_limits(self):
        """Configurar límites más conservadores"""
        # Reducir límite de CoinGecko temporalmente
        rate_limiter.coingecko_limit = 5  # Muy conservador
        logger.info("Límites configurados de manera conservadora")

async def main():
    """Función principal del diagnóstico"""
    print("=" * 60)
    print("🏥 CriptoAI - Diagnóstico y Recuperación del Sistema")
    print("=" * 60)
    
    diagnostic = SystemDiagnostic()
    
    # Ejecutar diagnóstico
    print("\n📋 Ejecutando diagnóstico completo...")
    results = await diagnostic.diagnose_api_health()
    
    # Mostrar resultados
    print("\n📊 Resultados del diagnóstico:")
    print("-" * 40)
    
    for component, status in results.items():
        print(f"\n🔍 {component.upper()}:")
        for key, value in status.items():
            print(f"   {key}: {value}")
    
    # Aplicar recuperación si es necesario
    if diagnostic.issues_found:
        print(f"\n⚠️  Problemas encontrados: {len(diagnostic.issues_found)}")
        for issue in diagnostic.issues_found:
            print(f"   • {issue}")
        
        print("\n🔧 Aplicando recuperación automática...")
        recovery_results = await diagnostic.apply_recovery_actions()
        
        print("\n✅ Acciones de recuperación aplicadas:")
        for action in recovery_results['actions_applied']:
            print(f"   • {action}")
    else:
        print("\n✅ Sistema saludable - no se requiere recuperación")
    
    # Verificación post-recuperación
    print("\n🔄 Verificación post-recuperación...")
    post_results = await diagnostic.diagnose_api_health()
    
    coingecko_status = post_results['coingecko']['status']
    if coingecko_status == 'healthy':
        print("✅ Sistema totalmente recuperado")
    elif coingecko_status == 'rate_limited':
        print("⏳ Sistema en recuperación - esperando reducción de rate limit")
    else:
        print("❌ Sistema aún presenta problemas")
    
    print("\n" + "=" * 60)
    print("Diagnóstico completado")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
