# 🚀 Guía de Despliegue - CriptoAI Backend

## ✅ Estado Actual del Proyecto

### Completado
- ✅ Backend FastAPI completamente funcional
- ✅ Base de datos SQLite configurada con datos de prueba
- ✅ 4 Agentes especializados implementados
- ✅ Integración con APIs de Binance y CoinGecko
- ✅ Sistema de tareas programadas (APScheduler)
- ✅ Endpoints REST completamente funcionales
- ✅ Documentación Swagger automática
- ✅ Servidor ejecutándose en http://localhost:8000

### Agentes Implementados
1. **DataCollectorAgent** - Recolección de datos de criptomonedas
2. **EconomicAnalysisAgent** - Análisis técnico y métricas
3. **PortfolioOptimizationAgent** - Recomendaciones personalizadas
4. **CommunicationAgent** - Notificaciones y suscripciones

## 🔧 Configuración Requerida

### 1. Variables de Entorno (.env)
```bash
# APIs
BINANCE_API_KEY=tu_api_key_binance
BINANCE_API_SECRET=tu_api_secret_binance

# Email (opcional para notificaciones)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password

# Base de datos (SQLite por defecto para desarrollo)
DATABASE_URL=sqlite:///./criptoai.db
```

### 2. Instalación de Dependencias
```bash
cd backend
pip install -r requirements.txt
```

### 3. Inicialización de Base de Datos
```bash
python init_db_sqlite.py
```

## 🚀 Ejecución

### Desarrollo
```bash
python run.py
# o
uvicorn run:app --host 0.0.0.0 --port 8000 --reload
```

### Producción
```bash
uvicorn run:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📊 Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/health` | GET | Estado del sistema |
| `/api/market-overview` | GET | Resumen del mercado |
| `/api/update-data` | POST | Actualizar datos de criptomonedas |
| `/api/get-portfolio-recommendation` | POST | Obtener recomendaciones |
| `/api/subscribe` | POST | Crear suscripción |
| `/docs` | GET | Documentación Swagger |

## 🧪 Pruebas

### Pruebas Integradas
```bash
python test_integration.py
```

### Pruebas de APIs
```bash
python test_apis.py
```

## 📈 Monitoreo

### Logs del Sistema
El sistema registra automáticamente:
- Recolección de datos cada hora
- Notificaciones diarias a las 9:00 AM
- Limpieza de datos antiguos semanalmente

### Verificar Estado
```bash
curl http://localhost:8000/api/health
```

## 🔒 Producción

### Para PostgreSQL (Producción)
1. Instalar PostgreSQL
2. Crear base de datos: `createdb criptoai`
3. Actualizar .env: `DATABASE_URL=postgresql://user:password@localhost/criptoai`
4. Ejecutar: `python init_db.py`

### Docker (Opcional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📧 Configuración de Email

### Gmail
1. Activar autenticación de 2 pasos
2. Generar App Password
3. Usar App Password en EMAIL_PASSWORD

### Otros Proveedores
- Outlook: `smtp-mail.outlook.com:587`
- Yahoo: `smtp.mail.yahoo.com:587`

## 🔧 Troubleshooting

### Problema: Error de Base de Datos
```bash
rm criptoai.db
python init_db_sqlite.py
```

### Problema: API Rate Limits
- Binance: 1200 requests/minute
- CoinGecko: 50 calls/minute (gratis)

### Problema: Puertos Ocupados
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## 📋 Checklist Final

- [ ] Variables de entorno configuradas
- [ ] Base de datos inicializada
- [ ] Servidor ejecutándose correctamente
- [ ] Endpoints respondiendo
- [ ] Tareas programadas activas
- [ ] (Opcional) Email configurado
- [ ] (Opcional) PostgreSQL para producción

## 🎯 Próximos Pasos Sugeridos

1. **Frontend**: Desarrollar interfaz de usuario
2. **Autenticación**: Implementar sistema de usuarios
3. **Cache**: Agregar Redis para mejor rendimiento
4. **Alertas**: Notificaciones en tiempo real
5. **Backtesting**: Simulación de estrategias históricas

---

**¡El backend CriptoAI está completamente funcional y listo para desarrollo/producción!** 🎉
