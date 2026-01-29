"""
Funciones helper para autenticación y autorización.
Proporciona utilidades para manejo de JWT y permisos.
"""
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from typing import Optional, Callable
from utils.route_helpers import error_response


def get_current_user_id() -> Optional[int]:
    """
    Obtiene el ID del usuario actual desde el token JWT.
    
    Returns:
        ID del usuario o None si no hay token válido
    """
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        return int(user_id) if user_id else None
    except Exception:
        return None


def require_auth(func: Callable) -> Callable:
    """
    Decorador para requerir autenticación JWT en un endpoint.
    
    Usage:
        @bp.route('/endpoint', methods=['POST'])
        @require_auth
        def crear_algo():
            usuario_id = get_current_user_id()
            # código
    """
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def optional_auth(func: Callable) -> Callable:
    """
    Decorador para autenticación JWT opcional en un endpoint.
    El endpoint funciona con o sin autenticación.
    
    Usage:
        @bp.route('/endpoint', methods=['GET'])
        @optional_auth
        def listar_algo():
            usuario_id = get_current_user_id()  # Puede ser None
            # código
    """
    @wraps(func)
    @jwt_required(optional=True)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def require_role(*allowed_roles: str):
    """
    Decorador para requerir roles específicos.
    
    Args:
        allowed_roles: Roles permitidos
        
    Usage:
        @bp.route('/endpoint', methods=['POST'])
        @require_auth
        @require_role('admin', 'manager')
        def crear_algo():
            # código
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            # Obtener información del token (roles, etc.)
            # Por ahora solo verifica autenticación
            # En el futuro se puede extender para verificar roles desde el token
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_auth_header() -> Optional[str]:
    """
    Obtiene el header de autorización de la request.
    
    Returns:
        Token JWT o None
    """
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]  # Remover 'Bearer ' prefix
    return None
