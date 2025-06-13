#!/usr/bin/env python3
"""
Migración automática de base de datos para CriptoAI
Este módulo se ejecuta automáticamente al iniciar la aplicación
"""

import sqlite3
import os
import logging
from sqlalchemy import inspect, text

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

def auto_migrate():
    """
    Función principal de migración automática
    Se ejecuta al iniciar la aplicación
    """
    logger.info("🚀 Iniciando verificación de base de datos...")
    
    try:
        # Crear todas las tablas definidas en los modelos
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas/verificadas por SQLAlchemy")
        
        # Verificar y migrar user_profiles específicamente
        check_and_migrate_user_profiles()
        
        # Verificar autoincrement
        ensure_autoincrement()
        
        logger.info("🎉 Verificación de base de datos completada")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en migración automática: {str(e)}")
        return False

if __name__ == "__main__":
    auto_migrate()
