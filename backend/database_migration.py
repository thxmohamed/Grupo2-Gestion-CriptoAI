#!/usr/bin/env python3
"""
Migración automática de base de datos para CriptoAI
Este módulo se ejecuta automáticamente al iniciar la aplicación
"""

import sqlite3
import os
import logging
from sqlalchemy import inspect

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_path():
    """Obtener la ruta de la base de datos"""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./criptoai.db")
    if database_url.startswith("sqlite:///"):
        return database_url.replace("sqlite:///", "")
    return "criptoai.db"

def check_and_migrate_user_profiles():
    """
    Verificar y migrar la tabla user_profiles si es necesario
    """
    try:
        # Importar aquí para evitar importaciones circulares
        from app import engine
        
        db_path = get_database_path()
        
        # Usar SQLAlchemy inspector para verificar la estructura
        inspector = inspect(engine)
        
        # Verificar si la tabla existe
        if not inspector.has_table('user_profiles'):
            logger.info("📝 Tabla user_profiles no existe, será creada por SQLAlchemy")
            return True
        
        # Obtener columnas existentes
        existing_columns = inspector.get_columns('user_profiles')
        column_names = [col['name'] for col in existing_columns]
        
        logger.info(f"🔍 Columnas existentes en user_profiles: {column_names}")
        
        # Verificar si faltan columnas requeridas
        required_columns = ['nombre', 'apellido', 'telefono']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            logger.info(f"➕ Agregando columnas faltantes: {missing_columns}")
            add_missing_columns(db_path, missing_columns)
            return True
        
        logger.info("✅ Tabla user_profiles tiene todas las columnas requeridas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando migración: {str(e)}")
        return False

def add_missing_columns(db_path, missing_columns):
    """
    Agregar columnas faltantes a la tabla user_profiles
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        column_definitions = {
            'nombre': 'TEXT NOT NULL DEFAULT ""',
            'apellido': 'TEXT NOT NULL DEFAULT ""', 
            'telefono': 'TEXT'
        }
        
        for column in missing_columns:
            if column in column_definitions:
                sql = f"ALTER TABLE user_profiles ADD COLUMN {column} {column_definitions[column]}"
                cursor.execute(sql)
                logger.info(f"  ✅ Columna {column} agregada")
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Migración de columnas completada")
        
    except Exception as e:
        logger.error(f"❌ Error agregando columnas: {str(e)}")
        raise

def ensure_autoincrement():
    """
    Verificar que el campo ID tenga autoincrement
    Nota: En SQLAlchemy esto se maneja automáticamente cuando se crea la tabla
    """
    try:
        db_path = get_database_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la tabla tiene AUTOINCREMENT
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='user_profiles'
        """)
        
        result = cursor.fetchone()
        if result and 'AUTOINCREMENT' not in result[0].upper():
            logger.warning("⚠️  La tabla no tiene AUTOINCREMENT. Considera ejecutar migrate_user_profile.py")
        else:
            logger.info("✅ Campo ID configurado correctamente")
        
        conn.close()
        
    except Exception as e:
        logger.warning(f"⚠️  No se pudo verificar AUTOINCREMENT: {str(e)}")

def make_user_id_nullable(db_path):
    """
    Hacer que el campo user_id sea nullable
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # En SQLite, para cambiar la definición de una columna necesitamos recrear la tabla
        logger.info("🔄 Haciendo user_id nullable...")
        
        # Verificar la estructura actual
        cursor.execute("PRAGMA table_info(user_profiles)")
        columns_info = cursor.fetchall()
        
        # Buscar si user_id es NOT NULL
        user_id_not_null = False
        for col in columns_info:
            if col[1] == 'user_id' and col[3] == 1:  # col[3] es notnull
                user_id_not_null = True
                break
        
        if user_id_not_null:
            logger.info("  🔄 user_id es NOT NULL, cambiando a nullable...")
            
            # Obtener datos existentes
            cursor.execute("SELECT * FROM user_profiles")
            existing_data = cursor.fetchall()
            
            # Obtener nombres de columnas
            column_names = [col[1] for col in columns_info]
            
            # Crear tabla temporal con user_id nullable
            cursor.execute("""
                CREATE TABLE user_profiles_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    nombre TEXT NOT NULL DEFAULT "",
                    apellido TEXT NOT NULL DEFAULT "",
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
            
            # Copiar datos
            if existing_data:
                placeholders = ','.join(['?' for _ in column_names])
                columns_str = ','.join(column_names)
                cursor.executemany(
                    f"INSERT INTO user_profiles_temp ({columns_str}) VALUES ({placeholders})",
                    existing_data
                )
            
            # Reemplazar tabla original
            cursor.execute("DROP TABLE user_profiles")
            cursor.execute("ALTER TABLE user_profiles_temp RENAME TO user_profiles")
            
            # Crear índices
            cursor.execute("CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id)")
            cursor.execute("CREATE INDEX idx_user_profiles_id ON user_profiles(id)")
            
            logger.info("  ✅ user_id ahora es nullable")
        else:
            logger.info("  ✅ user_id ya es nullable")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Error haciendo user_id nullable: {str(e)}")
        raise

def auto_migrate():
    """
    Función principal de migración automática
    Se ejecuta al iniciar la aplicación
    """
    logger.info("🚀 Iniciando verificación de base de datos...")
    
    try:
        # Importar aquí para evitar importaciones circulares
        from app import engine, Base
        
        # Crear todas las tablas definidas en los modelos
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas/verificadas por SQLAlchemy")
        
        # Verificar y migrar user_profiles específicamente
        check_and_migrate_user_profiles()
        
        # Verificar autoincrement
        ensure_autoincrement()
        
        # Hacer user_id nullable
        db_path = get_database_path()
        make_user_id_nullable(db_path)
        
        logger.info("🎉 Verificación de base de datos completada")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en migración automática: {str(e)}")
        return False

if __name__ == "__main__":
    auto_migrate()
