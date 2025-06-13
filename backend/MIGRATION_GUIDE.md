# Configuración de Migración de Base de Datos - CriptoAI

## ¿Cuándo necesitas ejecutar migraciones?

### ✅ **Migración Automática** (Recomendado)
La aplicación ahora verifica y actualiza automáticamente la base de datos cada vez que se inicia con `python run.py`.

**Lo que hace automáticamente:**
- ✅ Crear tablas que no existen
- ✅ Agregar columnas faltantes
- ✅ Verificar estructura de la base de datos
- ✅ Logging detallado de cambios

### 🔧 **Migración Manual** (Solo si es necesario)

Si tienes problemas con la migración automática o necesitas hacer cambios más complejos:

```bash
# Ejecutar migración manual completa
cd /Users/maxito/Desktop/Codes/GDP/Grupo2-Gestion-CriptoAI/backend
python migrate_user_profile.py
```

### 📋 **Verificar Estado de la Base de Datos**

```bash
# Verificar estructura actual
python -c "
from app.database_migration import auto_migrate
auto_migrate()
"
```

## Escenarios Comunes

### 🆕 **Primera vez ejecutando el proyecto**
```bash
python run.py  # Todo se configura automáticamente
```

### 🔄 **Cambios en modelos existentes**
La migración automática manejará:
- Agregar nuevas columnas
- Crear nuevas tablas
- Actualizar índices

### ⚠️ **Cambios complejos** (requiere migración manual)
- Cambiar tipo de datos de columnas existentes
- Eliminar columnas
- Renombrar columnas
- Cambios en llaves foráneas

## Logs de Migración

Cuando ejecutes `python run.py`, verás logs como:

```
🚀 Iniciando CriptoAI Backend...
🔄 Verificando estado de la base de datos...
📝 Tabla user_profiles no existe, será creada por SQLAlchemy
✅ Tablas creadas/verificadas por SQLAlchemy
✅ Tabla user_profiles tiene todas las columnas requeridas
✅ Campo ID configurado correctamente
🎉 Verificación de base de datos completada
```

## Solución de Problemas

### ❌ Error: "Columna ya existe"
```bash
# La migración automática maneja este caso
# Si persiste, ejecuta migración manual:
python migrate_user_profile.py
```

### ❌ Error: "Tabla bloqueada"
```bash
# Detener el servidor si está corriendo
# Luego ejecutar:
python migrate_user_profile.py
```

### ❌ Error: "No se puede conectar a la BD"
```bash
# Verificar que la ruta de la BD sea correcta
# Verificar permisos de escritura en el directorio
```

## Archivos Importantes

- `app/database_migration.py` - Migración automática
- `migrate_user_profile.py` - Migración manual
- `app/models.py` - Definición de modelos
- `criptoai.db` - Base de datos SQLite

## Flujo Recomendado para Desarrollo

1. **Hacer cambios en `models.py`**
2. **Ejecutar `python run.py`** (migración automática)
3. **Verificar que todo funcione**
4. **Si hay problemas, ejecutar migración manual**

## Backup de Seguridad

Antes de cambios importantes:
```bash
cp criptoai.db criptoai_backup_$(date +%Y%m%d_%H%M%S).db
```

## Estado Actual del Modelo UserProfile

```python
class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # ✅ Autogenerado
    user_id = Column(String(100), unique=True, index=True)                 # ✅ Único
    nombre = Column(String(100), nullable=False)                           # ✅ Nuevo campo
    apellido = Column(String(100), nullable=False)                         # ✅ Nuevo campo  
    telefono = Column(String(20), nullable=True)                           # ✅ Nuevo campo
    risk_tolerance = Column(String(10))                                    # ✅ Existente
    investment_amount = Column(Float)                                      # ✅ Existente
    investment_horizon = Column(String(20))                                # ✅ Existente
    preferred_sectors = Column(Text)                                       # ✅ Existente
    is_subscribed = Column(Boolean, default=False)                        # ✅ Existente
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # ✅ Existente
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())       # ✅ Existente
```
