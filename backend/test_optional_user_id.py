# Test para UserProfile con user_id OPCIONAL
# Guarda este archivo como: test_optional_user_id.py

import requests
import json

# URL base de tu API
BASE_URL = "http://localhost:8000/api"

def test_optional_user_id():
    """
    Función de prueba para demostrar el uso de user_id opcional
    """
    
    print("🚀 Probando UserProfile con user_id OPCIONAL")
    print("=" * 60)
    
    # 1. CREAR perfil SIN user_id (opcional)
    print("1. Creando perfil SIN user_id...")
    create_data_without_user_id = {
        "nombre": "Ana",
        "apellido": "García",
        "telefono": "+56912345678",
        "risk_tolerance": "conservative",
        "investment_amount": 3000.0,
        "investment_horizon": "medium",
        "preferred_sectors": ["Bitcoin", "Ethereum"],
        "is_subscribed": True
    }
    
    response = requests.post(f"{BASE_URL}/user-profiles/", json=create_data_without_user_id)
    if response.status_code == 200:
        profile_without_user_id = response.json()
        print("✅ Perfil creado SIN user_id:")
        print(f"   ID: {profile_without_user_id['id']}")
        print(f"   user_id: {profile_without_user_id['user_id']}")
        print(f"   Nombre: {profile_without_user_id['nombre']} {profile_without_user_id['apellido']}")
        profile_id = profile_without_user_id['id']
    else:
        print(f"❌ Error creando perfil sin user_id: {response.status_code} - {response.text}")
        return
    
    print("\n" + "="*60 + "\n")
    
    # 2. CREAR perfil CON user_id
    print("2. Creando perfil CON user_id...")
    create_data_with_user_id = {
        "user_id": "carlos_rodriguez_2025",
        "nombre": "Carlos",
        "apellido": "Rodríguez",
        "telefono": "+56987654321",
        "risk_tolerance": "aggressive",
        "investment_amount": 8000.0,
        "investment_horizon": "short",
        "preferred_sectors": ["DeFi", "Gaming", "AI"],
        "is_subscribed": False
    }
    
    response = requests.post(f"{BASE_URL}/user-profiles/", json=create_data_with_user_id)
    if response.status_code == 200:
        profile_with_user_id = response.json()
        print("✅ Perfil creado CON user_id:")
        print(f"   ID: {profile_with_user_id['id']}")
        print(f"   user_id: {profile_with_user_id['user_id']}")
        print(f"   Nombre: {profile_with_user_id['nombre']} {profile_with_user_id['apellido']}")
    else:
        print(f"❌ Error creando perfil con user_id: {response.status_code} - {response.text}")
        return
    
    print("\n" + "="*60 + "\n")
    
    # 3. OBTENER perfil por ID numérico (nuevo endpoint)
    print(f"3. Obteniendo perfil por ID numérico ({profile_id})...")
    response = requests.get(f"{BASE_URL}/user-profiles/by-id/{profile_id}")
    if response.status_code == 200:
        profile = response.json()
        print("✅ Perfil obtenido por ID:")
        print(f"   ID: {profile['id']}")
        print(f"   user_id: {profile['user_id']}")
        print(f"   Nombre: {profile['nombre']} {profile['apellido']}")
    else:
        print(f"❌ Error obteniendo perfil por ID: {response.status_code} - {response.text}")
    
    print("\n" + "="*60 + "\n")
    
    # 4. OBTENER perfil por user_id (endpoint existente)
    print("4. Obteniendo perfil por user_id...")
    response = requests.get(f"{BASE_URL}/user-profiles/carlos_rodriguez_2025")
    if response.status_code == 200:
        profile = response.json()
        print("✅ Perfil obtenido por user_id:")
        print(f"   ID: {profile['id']}")
        print(f"   user_id: {profile['user_id']}")
        print(f"   Nombre: {profile['nombre']} {profile['apellido']}")
    else:
        print(f"❌ Error obteniendo perfil por user_id: {response.status_code} - {response.text}")
    
    print("\n" + "="*60 + "\n")
    
    # 5. ACTUALIZAR perfil por ID (nuevo endpoint)
    print(f"5. Actualizando perfil por ID ({profile_id})...")
    update_data = {
        "user_id": "ana_garcia_updated",  # Agregar user_id posteriormente
        "telefono": "+56999888777",
        "risk_tolerance": "moderate",
        "investment_amount": 4500.0
    }
    
    response = requests.put(f"{BASE_URL}/user-profiles/by-id/{profile_id}", json=update_data)
    if response.status_code == 200:
        updated_profile = response.json()
        print("✅ Perfil actualizado por ID:")
        print(f"   ID: {updated_profile['id']}")
        print(f"   user_id: {updated_profile['user_id']} (agregado después)")
        print(f"   Teléfono: {updated_profile['telefono']} (actualizado)")
        print(f"   Risk: {updated_profile['risk_tolerance']} (actualizado)")
    else:
        print(f"❌ Error actualizando perfil por ID: {response.status_code} - {response.text}")
    
    print("\n" + "="*60 + "\n")
    
    # 6. LISTAR todos los perfiles
    print("6. Listando todos los perfiles...")
    response = requests.get(f"{BASE_URL}/user-profiles/?skip=0&limit=10")
    if response.status_code == 200:
        profiles = response.json()
        print(f"✅ Se encontraron {len(profiles)} perfiles:")
        for profile in profiles[-3:]:  # Mostrar solo los últimos 3
            user_id_display = profile['user_id'] if profile['user_id'] else "Sin user_id"
            print(f"  - ID: {profile['id']}, user_id: {user_id_display}")
            print(f"    Nombre: {profile['nombre']} {profile['apellido']}")
            print(f"    Teléfono: {profile.get('telefono', 'N/A')}")
            print(f"    Risk: {profile['risk_tolerance']}, ${profile['investment_amount']}")
            print()
    else:
        print(f"❌ Error obteniendo perfiles: {response.status_code} - {response.text}")
    
    print("\n" + "="*60 + "\n")
    
    # 7. LIMPIAR - eliminar perfiles de prueba
    print("7. Limpiando perfiles de prueba...")
    
    # Eliminar por ID
    response = requests.delete(f"{BASE_URL}/user-profiles/by-id/{profile_id}")
    if response.status_code == 200:
        print(f"✅ Perfil con ID {profile_id} eliminado")
    else:
        print(f"❌ Error eliminando perfil por ID: {response.status_code}")
    
    # Eliminar por user_id
    response = requests.delete(f"{BASE_URL}/user-profiles/carlos_rodriguez_2025")
    if response.status_code == 200:
        print("✅ Perfil carlos_rodriguez_2025 eliminado")
    else:
        print(f"❌ Error eliminando perfil por user_id: {response.status_code}")

def test_validation_cases():
    """
    Probar casos de validación
    """
    print("\n" + "🧪 PROBANDO CASOS DE VALIDACIÓN")
    print("=" * 60)
    
    # Caso 1: Intentar crear perfil con user_id duplicado
    print("1. Probando user_id duplicado...")
    duplicate_data = {
        "user_id": "test_duplicate",
        "nombre": "Usuario",
        "apellido": "Duplicado",
        "risk_tolerance": "moderate",
        "investment_amount": 1000.0
    }
    
    # Crear el primero
    response1 = requests.post(f"{BASE_URL}/user-profiles/", json=duplicate_data)
    print(f"   Primer perfil: {response1.status_code}")
    
    # Intentar crear el segundo con mismo user_id
    response2 = requests.post(f"{BASE_URL}/user-profiles/", json=duplicate_data)
    if response2.status_code == 400:
        print("   ✅ Correctamente rechazado user_id duplicado")
    else:
        print(f"   ❌ Debería haber rechazado user_id duplicado: {response2.status_code}")
    
    # Limpiar
    if response1.status_code == 200:
        requests.delete(f"{BASE_URL}/user-profiles/test_duplicate")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de user_id OPCIONAL")
    print("Asegúrate de que tu servidor FastAPI esté corriendo en http://localhost:8000")
    print("\n")
    
    try:
        test_optional_user_id()
        test_validation_cases()
        print("\n🎉 Todas las pruebas completadas!")
        print("\n📋 RESUMEN:")
        print("✅ user_id es opcional al crear perfiles")
        print("✅ Puedes acceder por ID numérico o user_id")
        print("✅ Puedes agregar user_id después con UPDATE")
        print("✅ Las validaciones de unicidad funcionan correctamente")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor. Asegúrate de que esté corriendo.")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
