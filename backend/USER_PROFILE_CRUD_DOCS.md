# CRUD UserProfile - Documentación de APIs (ACTUALIZADO)

Este documento describe cómo usar las APIs CRUD para el modelo UserProfile con los nuevos campos agregados.

## ✅ **Campos Actualizados del Modelo UserProfile**

- `id`: Integer, autogenerado (autoincrement) ✨ **NUEVO**
- `user_id`: String único, requerido
- `nombre`: String, requerido ✨ **NUEVO**
- `apellido`: String, requerido ✨ **NUEVO**
- `telefono`: String, opcional ✨ **NUEVO**
- `risk_tolerance`: String (conservative/moderate/aggressive)
- `investment_amount`: Float
- `investment_horizon`: String (short/medium/long)
- `preferred_sectors`: Array de strings (almacenado como JSON)
- `is_subscribed`: Boolean
- `created_at`: DateTime, autogenerado
- `updated_at`: DateTime, autogenerado en actualizaciones

## Endpoints disponibles

### 1. Crear Perfil de Usuario
**POST** `/api/user-profiles/`

Crea un nuevo perfil de usuario en el sistema.

#### Request Body:
```json
{
  "user_id": "string",
  "nombre": "string",
  "apellido": "string", 
  "telefono": "string (opcional)",
  "risk_tolerance": "conservative|moderate|aggressive",
  "investment_amount": 1000.0,
  "investment_horizon": "short|medium|long",
  "preferred_sectors": ["DeFi", "Layer1", "AI"],
  "is_subscribed": false
}
```

#### Ejemplo con curl:
```bash
curl -X POST "http://localhost:8000/api/user-profiles/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "nombre": "Juan",
    "apellido": "Pérez",
    "telefono": "+56912345678",
    "risk_tolerance": "moderate",
    "investment_amount": 5000.0,
    "investment_horizon": "long",
    "preferred_sectors": ["DeFi", "Layer1", "AI"],
    "is_subscribed": true
  }'
```

#### Response:
```json
{
  "id": 1,
  "user_id": "user123",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+56912345678",
  "risk_tolerance": "moderate",
  "investment_amount": 5000.0,
  "investment_horizon": "long",
  "preferred_sectors": ["DeFi", "Layer1", "AI"],
  "is_subscribed": true,
  "created_at": "2025-06-12T10:30:00Z",
  "updated_at": null
}
```

---

### 2. Obtener Perfil por User ID
**GET** `/api/user-profiles/{user_id}`

Obtiene un perfil específico por su user_id.

#### Ejemplo con curl:
```bash
curl -X GET "http://localhost:8000/api/user-profiles/user123"
```

#### Response:
```json
{
  "id": 1,
  "user_id": "user123",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+56912345678",
  "risk_tolerance": "moderate",
  "investment_amount": 5000.0,
  "investment_horizon": "long",
  "preferred_sectors": ["DeFi", "Layer1", "AI"],
  "is_subscribed": true,
  "created_at": "2025-06-12T10:30:00Z",
  "updated_at": null
}
```

---

### 3. Obtener Todos los Perfiles
**GET** `/api/user-profiles/`

Obtiene todos los perfiles con paginación opcional.

#### Query Parameters:
- `skip`: Número de registros a omitir (default: 0)
- `limit`: Número máximo de registros a retornar (default: 100)

#### Ejemplo con curl:
```bash
curl -X GET "http://localhost:8000/api/user-profiles/?skip=0&limit=10"
```

#### Response:
```json
[
  {
    "id": 1,
    "user_id": "user123",
    "nombre": "Juan",
    "apellido": "Pérez",
    "telefono": "+56912345678",
    "risk_tolerance": "moderate",
    "investment_amount": 5000.0,
    "investment_horizon": "long",
    "preferred_sectors": ["DeFi", "Layer1", "AI"],
    "is_subscribed": true,
    "created_at": "2025-06-12T10:30:00Z",
    "updated_at": null
  }
]
```

---

### 4. Actualizar Perfil de Usuario
**PUT** `/api/user-profiles/{user_id}`

Actualiza un perfil existente. Solo se necesan proporcionar los campos que se desean actualizar.

#### Request Body (todos los campos son opcionales):
```json
{
  "nombre": "Juan Carlos",
  "apellido": "Pérez González",
  "telefono": "+56987654321",
  "risk_tolerance": "aggressive",
  "investment_amount": 10000.0,
  "investment_horizon": "medium",
  "preferred_sectors": ["DeFi", "Gaming", "Metaverse"],
  "is_subscribed": false
}
```

#### Ejemplo con curl:
```bash
curl -X PUT "http://localhost:8000/api/user-profiles/user123" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Carlos",
    "apellido": "Pérez González",
    "telefono": "+56987654321",
    "risk_tolerance": "aggressive",
    "investment_amount": 10000.0,
    "preferred_sectors": ["DeFi", "Gaming", "Metaverse"]
  }'
```

#### Response:
```json
{
  "id": 1,
  "user_id": "user123",
  "nombre": "Juan Carlos",
  "apellido": "Pérez González",
  "telefono": "+56987654321",
  "risk_tolerance": "aggressive",
  "investment_amount": 10000.0,
  "investment_horizon": "long",
  "preferred_sectors": ["DeFi", "Gaming", "Metaverse"],
  "is_subscribed": true,
  "created_at": "2025-06-12T10:30:00Z",
  "updated_at": "2025-06-12T11:45:00Z"
}
```

---

### 5. Eliminar Perfil de Usuario
**DELETE** `/api/user-profiles/{user_id}`

Elimina permanentemente un perfil de usuario.

#### Ejemplo con curl:
```bash
curl -X DELETE "http://localhost:8000/api/user-profiles/user123"
```

#### Response:
```json
{
  "message": "Perfil de usuario user123 eliminado exitosamente"
}
```

---

### 6. Verificar Existencia de Perfil
**GET** `/api/user-profiles/{user_id}/exists`

Verifica si existe un perfil para un user_id específico sin retornar los datos completos.

#### Ejemplo con curl:
```bash
curl -X GET "http://localhost:8000/api/user-profiles/user123/exists"
```

#### Response:
```json
{
  "exists": true,
  "user_id": "user123"
}
```

---

## Códigos de Estado HTTP

- **200 OK**: Operación exitosa
- **201 Created**: Perfil creado exitosamente
- **400 Bad Request**: Datos inválidos o user_id ya existe
- **404 Not Found**: Perfil no encontrado
- **500 Internal Server Error**: Error interno del servidor

## Validaciones

### Campos obligatorios para crear:
- `user_id`: String único, no puede estar vacío
- `nombre`: String, no puede estar vacío
- `apellido`: String, no puede estar vacío

### Valores válidos:
- `telefono`: String opcional (ej: "+56912345678")
- `risk_tolerance`: "conservative", "moderate", "aggressive"
- `investment_horizon`: "short", "medium", "long"
- `investment_amount`: Número positivo
- `preferred_sectors`: Array de strings (ej: ["DeFi", "Layer1", "AI", "Gaming", "Metaverse"])
- `is_subscribed`: Boolean

### Reglas de negocio:
- El `user_id` debe ser único en el sistema
- El `id` es autogenerado por la base de datos (autoincrement)
- Los campos `nombre` y `apellido` son obligatorios
- El campo `telefono` es opcional
- Los `preferred_sectors` se almacenan como JSON string en la base de datos
- Las fechas `created_at` y `updated_at` se manejan automáticamente

## Ejemplos de Integración

### Ejemplo con JavaScript/Fetch:
```javascript
// Crear perfil
const createProfile = async (userData) => {
  const response = await fetch('http://localhost:8000/api/user-profiles/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData)
  });
  return response.json();
};

// Obtener perfil
const getProfile = async (userId) => {
  const response = await fetch(`http://localhost:8000/api/user-profiles/${userId}`);
  return response.json();
};

// Actualizar perfil
const updateProfile = async (userId, updateData) => {
  const response = await fetch(`http://localhost:8000/api/user-profiles/${userId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updateData)
  });
  return response.json();
};
```

### Ejemplo con Python/Requests:
```python
import requests

BASE_URL = "http://localhost:8000/api"

# Crear perfil
def create_profile(user_data):
    response = requests.post(f"{BASE_URL}/user-profiles/", json=user_data)
    return response.json()

# Obtener perfil
def get_profile(user_id):
    response = requests.get(f"{BASE_URL}/user-profiles/{user_id}")
    return response.json()

# Actualizar perfil
def update_profile(user_id, update_data):
    response = requests.put(f"{BASE_URL}/user-profiles/{user_id}", json=update_data)
    return response.json()
```

## Casos de Uso Comunes

1. **Registro de nuevo usuario**: Usar POST para crear el perfil inicial
2. **Carga de perfil en dashboard**: Usar GET para obtener los datos del usuario
3. **Actualización de preferencias**: Usar PUT para modificar configuraciones
4. **Verificación antes de mostrar onboarding**: Usar GET exists para saber si mostrar formulario inicial
5. **Eliminación de cuenta**: Usar DELETE cuando el usuario cancele su cuenta
