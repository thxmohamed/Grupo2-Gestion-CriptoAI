# Ejemplos de uso para el CRUD de UserProfile
# Guarda este archivo como: test_user_profile_crud.py

import requests
import json

# URL base de tu API
BASE_URL = "http://localhost:8000/api"

def test_user_profile_crud():
    """
    Función de prueba para demostrar el uso del CRUD de UserProfile
    """
    
    # 1. CREAR un nuevo perfil de usuario
    print("1. Creando nuevo perfil de usuario...")
    create_data = {
        "user_id": "user123",
        "nombre": "Juan",
        "apellido": "Pérez",
        "telefono": "+56912345678",
        "risk_tolerance": "moderate",
        "investment_amount": 5000.0,
        "investment_horizon": "long",
        "preferred_sectors": ["DeFi", "Layer1", "AI"],
        "is_subscribed": True
    }
    
    response = requests.post(f"{BASE_URL}/user-profiles/", json=create_data)
    if response.status_code == 200:
        print("✅ Perfil creado exitosamente:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Error creando perfil: {response.status_code} - {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. LEER el perfil creado
    print("2. Obteniendo perfil de usuario...")
    response = requests.get(f"{BASE_URL}/user-profiles/user123")
    if response.status_code == 200:
        print("✅ Perfil obtenido exitosamente:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Error obteniendo perfil: {response.status_code} - {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. ACTUALIZAR el perfil
    print("3. Actualizando perfil de usuario...")
    update_data = {
        "nombre": "Juan Carlos",
        "apellido": "Pérez González", 
        "telefono": "+56987654321",
        "risk_tolerance": "aggressive",
        "investment_amount": 10000.0,
        "preferred_sectors": ["DeFi", "Layer1", "AI", "Gaming"]
    }
    
    response = requests.put(f"{BASE_URL}/user-profiles/user123", json=update_data)
    if response.status_code == 200:
        print("✅ Perfil actualizado exitosamente:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Error actualizando perfil: {response.status_code} - {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # 4. LISTAR todos los perfiles (con paginación)
    print("4. Obteniendo todos los perfiles...")
    response = requests.get(f"{BASE_URL}/user-profiles/?skip=0&limit=10")
    if response.status_code == 200:
        profiles = response.json()
        print(f"✅ Se encontraron {len(profiles)} perfiles:")
        for profile in profiles:
            print(f"  - {profile['user_id']}: {profile['nombre']} {profile['apellido']}, Tel: {profile.get('telefono', 'N/A')}, Risk: {profile['risk_tolerance']}, ${profile['investment_amount']}")
    else:
        print(f"❌ Error obteniendo perfiles: {response.status_code} - {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # 5. VERIFICAR existencia de perfil
    print("5. Verificando existencia de perfil...")
    response = requests.get(f"{BASE_URL}/user-profiles/user123/exists")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Perfil user123 existe: {result['exists']}")
    else:
        print(f"❌ Error verificando existencia: {response.status_code} - {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # 6. ELIMINAR el perfil
    print("6. Eliminando perfil de usuario...")
    response = requests.delete(f"{BASE_URL}/user-profiles/user123")
    if response.status_code == 200:
        print("✅ Perfil eliminado exitosamente:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Error eliminando perfil: {response.status_code} - {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # 7. VERIFICAR que el perfil ya no existe
    print("7. Verificando que el perfil fue eliminado...")
    response = requests.get(f"{BASE_URL}/user-profiles/user123")
    if response.status_code == 404:
        print("✅ Confirmado: el perfil ya no existe")
    else:
        print(f"❌ Error: el perfil todavía existe o hay un error: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del CRUD de UserProfile")
    print("Asegúrate de que tu servidor FastAPI esté corriendo en http://localhost:8000")
    print("\n" + "="*50 + "\n")
    
    try:
        test_user_profile_crud()
        print("\n🎉 Pruebas del CRUD completadas!")
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor. Asegúrate de que esté corriendo.")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
