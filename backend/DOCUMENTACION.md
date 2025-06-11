# CriptoAI Backend - Guía Completa

## 🚀 Descripción General

CriptoAI Backend es un sistema completo de análisis y optimización de criptomonedas que utiliza FastAPI y está basado en una arquitectura de agentes especializados.

## 📋 Arquitectura del Sistema

### Agentes Principales

1. **Agente Recolección de Datos** (`data_collector.py`)
   - Obtiene datos de Binance y CoinGecko
   - Normaliza y combina información de ambas fuentes
   - Maneja rate limits automáticamente

2. **Agente Análisis Económico** (`economic_analysis.py`)
   - Calcula métricas técnicas (RSI, volatilidad, promedios móviles)
   - Determina sentimiento de mercado
   - Asigna scores de estabilidad y potencial de crecimiento

3. **Agente Optimización Portfolio** (`portfolio_optimizer.py`)
   - Optimiza portfolios según perfil del usuario
   - Calcula pesos y asignaciones personalizadas
   - Genera recomendaciones top 5

4. **Agente Comunicación** (`communication.py`)
   - Maneja suscripciones de usuarios
   - Envía notificaciones por email
   - Gestiona historial de recomendaciones

## 🔧 Configuración

### Variables de Entorno (.env)

```bash
# APIs
BINANCE_API_KEY=YLF6MjQSTmYUTauXNunauPnN82OfjvwqN0kdw7iexEgvx2AQhJT5q6wrDExeuu3S
BINANCE_API_SECRET=

# Base de datos
DATABASE_URL=postgresql://user:password@localhost/criptoai

# Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password
```

### Instalación

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar base de datos
python init_db.py

# 3. Ejecutar servidor
python run.py
```

## 📡 Endpoints API

### Endpoints Principales

- `GET /api/` - Estado del sistema
- `POST /api/update-data` - Actualizar datos de criptomonedas
- `POST /api/get-portfolio-recommendation` - Obtener recomendación personalizada
- `POST /api/subscribe` - Registrar suscripción
- `GET /api/user/{user_id}/notifications` - Historial de notificaciones
- `GET /api/market-overview` - Resumen del mercado
- `GET /api/health` - Estado de salud del sistema

### Documentación Interactiva

Accede a `http://localhost:8000/docs` para ver la documentación completa de la API con ejemplos interactivos.

## 🎯 Casos de Uso

### 1. Obtener Recomendación de Portfolio

```json
POST /api/get-portfolio-recommendation
{
  "user_id": "usuario123",
  "risk_tolerance": "moderate",
  "investment_amount": 5000,
  "investment_horizon": "medium",
  "preferred_sectors": ["defi", "layer1"]
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "recommended_coins": [
      {
        "symbol": "BTC",
        "name": "Bitcoin",
        "allocation_percentage": 40.5,
        "current_price": 67890.12
      },
      // ... más monedas
    ],
    "expected_return": 15.2,
    "risk_score": 65.3,
    "confidence_level": 78.9
  }
}
```

### 2. Suscribirse a Notificaciones

```json
POST /api/subscribe
{
  "user_id": "usuario123",
  "email": "usuario@example.com",
  "notification_type": "email",
  "frequency": "daily",
  "risk_tolerance": "moderate",
  "investment_amount": 5000
}
```

### 3. Actualizar Datos de Mercado

```json
POST /api/update-data
```

Este endpoint recopila datos frescos de Binance y CoinGecko, los analiza y actualiza la base de datos.

## 🗄️ Base de Datos

### Modelos Principales

1. **Cryptocurrency** - Datos básicos de monedas
2. **CryptoMetrics** - Métricas calculadas (RSI, volatilidad, etc.)
3. **UserProfile** - Perfiles de usuario
4. **PortfolioRecommendation** - Recomendaciones generadas
5. **Subscription** - Suscripciones de usuarios

## ⚙️ Utilidades (`utils.py`)

### BinanceAPIHelper

```python
# Obtener datos de ticker 24h
tickers = await binance_helper.get_24hr_ticker("BTCUSDT")

# Obtener datos de velas (klines)
klines = await binance_helper.get_klines("BTCUSDT", "1d", 30)

# Obtener libro de órdenes
orderbook = await binance_helper.get_order_book("BTCUSDT")
```

### CoinGeckoAPIHelper

```python
# Obtener datos de mercado
markets = await coingecko_helper.get_coins_markets(per_page=100)

# Obtener datos históricos
chart = await coingecko_helper.get_coin_market_chart("bitcoin", days="30")

# Buscar monedas
search = await coingecko_helper.search_coins("ethereum")
```

### DataProcessor

```python
# Normalizar datos de Binance
normalized = data_processor.normalize_binance_ticker(ticker_data)

# Combinar datos de ambas fuentes
merged = data_processor.merge_coin_data(binance_data, coingecko_data)
```

## ⏰ Tareas Programadas

El sistema ejecuta automáticamente:

- **Cada hora**: Actualización de datos de criptomonedas
- **Diariamente (9:00 AM)**: Envío de notificaciones
- **Semanalmente (Domingo 2:00 AM)**: Limpieza de datos antiguos

## 🔍 Monitoreo y Logs

El sistema incluye logging detallado:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Mensaje informativo")
logger.error("Error en el sistema")
```

## 🧪 Pruebas

### Ejecutar Diagnóstico

```bash
python diagnose.py
```

### Probar APIs

```bash
python test_apis.py
```

## 🔒 Seguridad

- Rate limiting automático para APIs externas
- Validación de datos con Pydantic
- Manejo seguro de API keys
- Logs de seguridad

## 📈 Rendimiento

- Peticiones asíncronas para mejor rendimiento
- Cache de datos donde sea apropiado
- Optimización de consultas de base de datos
- Pooling de conexiones

## 🚨 Solución de Problemas

### Problemas Comunes

1. **Error de conexión a base de datos**
   - Verificar DATABASE_URL en .env
   - Asegurar que PostgreSQL esté ejecutándose

2. **Rate limit en APIs**
   - El sistema maneja automáticamente los límites
   - Revisa logs para más detalles

3. **Error en notificaciones de email**
   - Configurar credenciales SMTP en .env
   - Usar app passwords para Gmail

### Logs Útiles

```bash
# Ver logs del servidor
tail -f logs/app.log

# Ver logs específicos de agentes
grep "DataCollectorAgent" logs/app.log
```

## 🔮 Próximas Funcionalidades

- [ ] WebSocket para actualizaciones en tiempo real
- [ ] Dashboard de métricas
- [ ] Integración con más exchanges
- [ ] Análisis de sentimiento de redes sociales
- [ ] Backtesting de estrategias
- [ ] API de trading (simulado)

## 📞 Soporte

Para reportar problemas o solicitar funcionalidades:

1. Revisar los logs del sistema
2. Ejecutar diagnóstico (`python diagnose.py`)
3. Crear issue con detalles del problema

---

**Desarrollado con ❤️ para análisis inteligente de criptomonedas**
