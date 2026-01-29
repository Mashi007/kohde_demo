"""
Funciones helper para rutas API.
Proporciona utilidades comunes para manejo de transacciones, validación y respuestas.
"""
from functools import wraps
from flask import jsonify, request, make_response
from datetime import datetime, date
from typing import Optional, Dict, Any, Callable
from models import db


def handle_db_transaction(func: Callable) -> Callable:
    """
    Decorador para manejar transacciones de base de datos con rollback automático.
    
    Usage:
        @bp.route('/endpoint', methods=['POST'])
        @handle_db_transaction
        def crear_algo():
            # código que modifica BD
            db.session.commit()
            return jsonify(...)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    return wrapper


def parse_date(date_str: Optional[str], format_str: str = '%Y-%m-%d') -> Optional[date]:
    """
    Convierte string a date object.
    
    Args:
        date_str: String de fecha a convertir
        format_str: Formato esperado (default: '%Y-%m-%d')
        
    Returns:
        date object o None si date_str es None/vacío
        
    Raises:
        ValueError: Si el formato es inválido
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, format_str).date()
    except ValueError:
        raise ValueError(f'Formato de fecha inválido. Use {format_str}')


def parse_datetime(datetime_str: Optional[str]) -> Optional[datetime]:
    """
    Convierte string ISO a datetime object.
    
    Args:
        datetime_str: String ISO datetime
        
    Returns:
        datetime object o None si datetime_str es None/vacío
        
    Raises:
        ValueError: Si el formato es inválido
    """
    if not datetime_str:
        return None
    try:
        # Manejar formato ISO con o sin Z
        datetime_str_clean = datetime_str.replace('Z', '+00:00')
        return datetime.fromisoformat(datetime_str_clean)
    except ValueError:
        raise ValueError('Formato de datetime inválido. Use formato ISO 8601')


def require_field(data: Dict[str, Any], field_name: str, field_type: type = str) -> Any:
    """
    Valida que un campo requerido exista en los datos.
    
    Args:
        data: Diccionario con datos
        field_name: Nombre del campo requerido
        field_type: Tipo esperado del campo
        
    Returns:
        Valor del campo
        
    Raises:
        ValueError: Si el campo no existe o es inválido
    """
    if field_name not in data:
        raise ValueError(f'Campo requerido faltante: {field_name}')
    
    value = data[field_name]
    
    if value is None:
        raise ValueError(f'Campo {field_name} no puede ser None')
    
    if field_type == int and not isinstance(value, int):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValueError(f'Campo {field_name} debe ser un número entero')
    
    if field_type == float and not isinstance(value, (int, float)):
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValueError(f'Campo {field_name} debe ser un número')
    
    if field_type == str and not isinstance(value, str):
        raise ValueError(f'Campo {field_name} debe ser texto')
    
    if field_type == bool and not isinstance(value, bool):
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        return bool(value)
    
    return value


def validate_positive_int(value: Any, field_name: str = 'valor') -> int:
    """
    Valida que un valor sea un entero positivo.
    
    Args:
        value: Valor a validar
        field_name: Nombre del campo para mensajes de error
        
    Returns:
        int positivo
        
    Raises:
        ValueError: Si el valor no es un entero positivo
    """
    try:
        int_value = int(value)
        if int_value < 0:
            raise ValueError(f'{field_name} debe ser un número positivo')
        return int_value
    except (ValueError, TypeError):
        raise ValueError(f'{field_name} debe ser un número entero válido')


def validate_file_upload(file, allowed_extensions: tuple = ('.jpg', '.jpeg', '.png', '.pdf'), 
                        max_size_mb: int = 16) -> tuple[str, str]:
    """
    Valida un archivo subido.
    
    Args:
        file: Archivo de Flask request.files
        allowed_extensions: Extensiones permitidas
        max_size_mb: Tamaño máximo en MB
        
    Returns:
        Tuple (filename, temp_path)
        
    Raises:
        ValueError: Si el archivo es inválido
    """
    from werkzeug.utils import secure_filename
    import os
    from config import Config
    
    if not file or file.filename == '':
        raise ValueError('No se proporcionó archivo o el archivo está vacío')
    
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in allowed_extensions:
        raise ValueError(f'Extensión de archivo no permitida. Permitidas: {", ".join(allowed_extensions)}')
    
    # Verificar tamaño antes de guardar
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Resetear posición
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise ValueError(f'Archivo demasiado grande. Tamaño máximo: {max_size_mb}MB')
    
    temp_path = os.path.join(Config.UPLOAD_FOLDER, f"temp_{filename}")
    file.save(temp_path)
    
    return filename, temp_path


def success_response(data: Any, status_code: int = 200, message: Optional[str] = None) -> tuple:
    """
    Crea una respuesta JSON exitosa estandarizada con headers apropiados para el frontend.
    
    Args:
        data: Datos a retornar
        status_code: Código HTTP
        message: Mensaje opcional
        
    Returns:
        Tuple (jsonify response, status_code)
    """
    response_data = {'data': data}
    if message:
        response_data['message'] = message
    
    response = make_response(jsonify(response_data), status_code)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response


def error_response(message: str, status_code: int = 400, error_code: Optional[str] = None, 
                  details: Optional[Dict] = None) -> tuple:
    """
    Crea una respuesta JSON de error estandarizada con headers apropiados para el frontend.
    
    Args:
        message: Mensaje de error
        status_code: Código HTTP
        error_code: Código de error opcional
        details: Detalles adicionales opcionales
        
    Returns:
        Tuple (jsonify response, status_code)
    """
    error = {
        'error': {
            'message': message
        }
    }
    
    if error_code:
        error['error']['code'] = error_code
    
    if details:
        error['error']['details'] = details
    
    response = make_response(jsonify(error), status_code)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response


def paginated_response(items: list, total: Optional[int] = None, skip: int = 0, 
                      limit: int = 100) -> tuple:
    """
    Crea una respuesta JSON paginada estandarizada con headers apropiados para el frontend.
    
    Args:
        items: Lista de items
        total: Total de items (opcional)
        skip: Items saltados
        limit: Límite de items
        
    Returns:
        Tuple (jsonify response, status_code)
    """
    response_data = {
        'data': items,
        'pagination': {
            'skip': skip,
            'limit': limit,
            'count': len(items)
        }
    }
    
    if total is not None:
        response_data['pagination']['total'] = total
    
    response = make_response(jsonify(response_data), 200)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    # Headers útiles para paginación en el frontend
    response.headers['X-Total-Count'] = str(total if total is not None else len(items))
    response.headers['X-Page-Size'] = str(limit)
    response.headers['X-Page-Offset'] = str(skip)
    return response
