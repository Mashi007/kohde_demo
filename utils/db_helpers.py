"""
Funciones helper para gestión de base de datos.
Proporciona utilidades para verificación y manejo de BD.
"""
from sqlalchemy import text
from models import db
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def verify_db_connection() -> Dict[str, Any]:
    """
    Verifica la conexión a la base de datos y obtiene información del pool.
    
    Returns:
        Dict con información de la conexión y estadísticas del pool
    """
    try:
        import time
        inicio = time.time()
        db.session.execute(text('SELECT 1'))
        tiempo_respuesta = time.time() - inicio
        
        # Obtener información del pool de conexiones
        pool_info = {}
        try:
            pool = db.engine.pool
            pool_info = {
                'size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            }
        except Exception as pool_error:
            logger.debug(f"No se pudo obtener información del pool: {pool_error}")
        
        return {
            'connected': True,
            'status': 'ok',
            'message': 'Conexión a base de datos exitosa',
            'response_time_ms': round(tiempo_respuesta * 1000, 2),
            'pool': pool_info
        }
    except Exception as e:
        logger.error(f"Error de conexión a BD: {e}", exc_info=True)
        return {
            'connected': False,
            'status': 'error',
            'message': str(e)
        }


def check_table_exists(table_name: str) -> bool:
    """
    Verifica si una tabla existe en la base de datos.
    
    Args:
        table_name: Nombre de la tabla
        
    Returns:
        True si la tabla existe, False en caso contrario
    """
    try:
        result = db.session.execute(
            text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')")
        )
        return result.scalar()
    except Exception as e:
        logger.error(f"Error al verificar tabla {table_name}: {e}", exc_info=True)
        return False


def get_table_count(table_name: str) -> int:
    """
    Obtiene el número de registros en una tabla.
    
    Args:
        table_name: Nombre de la tabla
        
    Returns:
        Número de registros o -1 si hay error
    """
    try:
        result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return result.scalar()
    except Exception as e:
        logger.error(f"Error al contar registros en {table_name}: {e}", exc_info=True)
        return -1


def get_pool_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas del pool de conexiones.
    
    Returns:
        Dict con estadísticas del pool
    """
    try:
        pool = db.engine.pool
        return {
            'status': 'ok',
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'invalid': pool.invalid(),
            'total_connections': pool.size() + pool.overflow()
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del pool: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e)
        }


def verify_foreign_keys() -> Dict[str, Any]:
    """
    Verifica la integridad de las foreign keys en la base de datos.
    
    Returns:
        Dict con información de verificación
    """
    try:
        # Verificar foreign keys rotas
        query = text("""
            SELECT 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE constraint_type = 'FOREIGN KEY'
        """)
        
        result = db.session.execute(query)
        foreign_keys = result.fetchall()
        
        return {
            'status': 'ok',
            'foreign_keys_count': len(foreign_keys),
            'foreign_keys': [
                {
                    'table': fk[0],
                    'column': fk[1],
                    'references_table': fk[2],
                    'references_column': fk[3]
                }
                for fk in foreign_keys
            ]
        }
    except Exception as e:
        logger.error(f"Error al verificar foreign keys: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': str(e)
        }
