#!/usr/bin/env python3
"""
Script para migrar la tabla user_profiles agregando los nuevos campos:
- nombre
- apellido  
- telefono
- autoincrement en id

Este script actualiza la estructura de la tabla existente.
"""

import sqlite3
import os
from pathlib import Path

def migrate_user_profiles():
    """
    Migra la tabla user_profiles para agregar los nuevos campos
    """
    # Encontrar la base de datos
    db_paths = [
        "/Users/maxito/Desktop/Codes/GDP/Grupo2-Gestion-CriptoAI/backend/criptoai.db",
        "/Users/maxito/Desktop/Codes/GDP/Grupo2-Gestion-CriptoAI/criptoai.db",
        "criptoai.db"
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No se encontró la base de datos criptoai.db")
        print("Creando nueva base de datos...")
        db_path = "criptoai.db"
    
    print(f"🔄 Conectando a base de datos: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_profiles'
        """)
        
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("📝 Tabla user_profiles no existe, creando nueva tabla...")
            create_new_table(cursor)
        else:
            print("🔍 Tabla user_profiles existe, verificando estructura...")
            migrate_existing_table(cursor)
        
        conn.commit()
        print("✅ Migración completada exitosamente!")
        
        # Verificar la estructura final
        cursor.execute("PRAGMA table_info(user_profiles)")
        columns = cursor.fetchall()
        print("\n📋 Estructura final de la tabla user_profiles:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'} {'PRIMARY KEY' if col[5] else ''}")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {str(e)}")
        return False
    finally:
        conn.close()
    
    return True

def create_new_table(cursor):
    """Crear la tabla user_profiles desde cero con la nueva estructura"""
    cursor.execute("""
        CREATE TABLE user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            telefono TEXT,
            risk_tolerance TEXT,
            investment_amount REAL,
            investment_horizon TEXT,
            preferred_sectors TEXT,
            is_subscribed BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME
        )
    """)
    
    # Crear índices
    cursor.execute("CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id)")
    cursor.execute("CREATE INDEX idx_user_profiles_id ON user_profiles(id)")
    
    print("✅ Tabla user_profiles creada con nueva estructura")

def migrate_existing_table(cursor):
    """Migrar tabla existente agregando los nuevos campos"""
    
    # Obtener información de columnas existentes
    cursor.execute("PRAGMA table_info(user_profiles)")
    existing_columns = {col[1]: col for col in cursor.fetchall()}
    
    print(f"📊 Columnas existentes: {list(existing_columns.keys())}")
    
    # Verificar qué columnas necesitamos agregar
    required_columns = {
        'nombre': 'TEXT NOT NULL DEFAULT ""',
        'apellido': 'TEXT NOT NULL DEFAULT ""',
        'telefono': 'TEXT'
    }
    
    columns_to_add = []
    for col_name, col_def in required_columns.items():
        if col_name not in existing_columns:
            columns_to_add.append((col_name, col_def))
    
    if columns_to_add:
        print(f"➕ Agregando columnas: {[col[0] for col in columns_to_add]}")
        
        for col_name, col_def in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE user_profiles ADD COLUMN {col_name} {col_def}")
                print(f"  ✅ Columna {col_name} agregada")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"  ⚠️  Columna {col_name} ya existe")
                else:
                    raise e
    else:
        print("✅ Todas las columnas requeridas ya existen")
    
    # Verificar que el ID tenga autoincrement
    # En SQLite, para verificar AUTOINCREMENT necesitamos revisar el SQL de creación
    cursor.execute("""
        SELECT sql FROM sqlite_master 
        WHERE type='table' AND name='user_profiles'
    """)
    table_sql = cursor.fetchone()
    
    if table_sql and 'AUTOINCREMENT' not in table_sql[0].upper():
        print("🔄 Recreando tabla para agregar AUTOINCREMENT...")
        recreate_table_with_autoincrement(cursor)
    else:
        print("✅ Campo ID ya tiene AUTOINCREMENT")

def recreate_table_with_autoincrement(cursor):
    """Recrear la tabla para agregar AUTOINCREMENT al campo id"""
    
    # Respaldar datos existentes
    cursor.execute("SELECT * FROM user_profiles")
    existing_data = cursor.fetchall()
    
    # Obtener nombres de columnas
    cursor.execute("PRAGMA table_info(user_profiles)")
    columns_info = cursor.fetchall()
    column_names = [col[1] for col in columns_info]
    
    print(f"💾 Respaldando {len(existing_data)} registros existentes...")
    
    # Renombrar tabla actual
    cursor.execute("ALTER TABLE user_profiles RENAME TO user_profiles_backup")
    
    # Crear nueva tabla con AUTOINCREMENT
    create_new_table(cursor)
    
    # Restaurar datos (excluyendo el ID para que se autogenere)
    if existing_data:
        # Preparar datos sin el campo ID
        data_columns = [col for col in column_names if col != 'id']
        placeholders = ','.join(['?' for _ in data_columns])
        columns_str = ','.join(data_columns)
        
        # Encontrar índices de las columnas (excluyendo id)
        id_index = column_names.index('id')
        data_without_id = []
        
        for row in existing_data:
            row_data = []
            for i, value in enumerate(row):
                if i != id_index:  # Saltar el campo ID
                    row_data.append(value)
            data_without_id.append(tuple(row_data))
        
        cursor.executemany(
            f"INSERT INTO user_profiles ({columns_str}) VALUES ({placeholders})",
            data_without_id
        )
        
        print(f"✅ Restaurados {len(data_without_id)} registros con nuevos IDs autogenerados")
    
    # Eliminar tabla de respaldo
    cursor.execute("DROP TABLE user_profiles_backup")
    print("🗑️  Tabla de respaldo eliminada")

def test_migration():
    """Probar que la migración funcionó correctamente"""
    print("\n🧪 Probando la migración...")
    
    try:
        import sys
        sys.path.append('/Users/maxito/Desktop/Codes/GDP/Grupo2-Gestion-CriptoAI/backend')
        
        from app.models import UserProfile
        from app import SessionLocal
        
        db = SessionLocal()
        
        # Probar crear un perfil con los nuevos campos
        test_profile = UserProfile(
            user_id="test_migration_user",
            nombre="Juan",
            apellido="Pérez",
            telefono="+56912345678",
            risk_tolerance="moderate",
            investment_amount=5000.0,
            investment_horizon="long",
            preferred_sectors='["DeFi", "AI"]',
            is_subscribed=True
        )
        
        db.add(test_profile)
        db.commit()
        db.refresh(test_profile)
        
        print(f"✅ Perfil de prueba creado con ID autogenerado: {test_profile.id}")
        print(f"   - Nombre: {test_profile.nombre} {test_profile.apellido}")
        print(f"   - Teléfono: {test_profile.telefono}")
        print(f"   - User ID: {test_profile.user_id}")
        
        # Limpiar el perfil de prueba
        db.delete(test_profile)
        db.commit()
        db.close()
        
        print("✅ Prueba de migración exitosa!")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de migración: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando migración de tabla user_profiles")
    print("=" * 50)
    
    success = migrate_user_profiles()
    
    if success:
        print("\n" + "=" * 50)
        test_migration()
        
        print("\n🎉 Migración completada!")
        print("\nLos cambios realizados:")
        print("  ✅ Campo 'id' ahora es AUTOINCREMENT")
        print("  ✅ Agregado campo 'nombre' (requerido)")
        print("  ✅ Agregado campo 'apellido' (requerido)")
        print("  ✅ Agregado campo 'telefono' (opcional)")
        print("\nAhora puedes usar el CRUD con los nuevos campos.")
    else:
        print("\n❌ La migración falló. Revisa los errores arriba.")
