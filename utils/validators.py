"""
Validadores para el sistema ERP.
"""
import re
from datetime import datetime
from typing import Optional

def validate_ruc(ruc: str) -> bool:
    """
    Valida formato de RUC ecuatoriano.
    
    Args:
        ruc: RUC a validar
        
    Returns:
        True si es válido, False en caso contrario
    """
    if not ruc:
        return False
    
    # RUC ecuatoriano tiene 13 dígitos
    ruc_clean = re.sub(r'[^0-9]', '', ruc)
    return len(ruc_clean) == 13

def validate_email(email: str) -> bool:
    """
    Valida formato de email.
    
    Args:
        email: Email a validar
        
    Returns:
        True si es válido, False en caso contrario
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Valida formato de teléfono.
    
    Args:
        phone: Teléfono a validar
        
    Returns:
        True si es válido, False en caso contrario
    """
    if not phone:
        return False
    
    # Eliminar espacios y caracteres especiales
    phone_clean = re.sub(r'[^0-9+]', '', phone)
    # Debe tener al menos 7 dígitos
    return len(phone_clean) >= 7

def validate_date(date_string: str, format: str = '%Y-%m-%d') -> bool:
    """
    Valida formato de fecha.
    
    Args:
        date_string: Fecha en formato string
        format: Formato esperado
        
    Returns:
        True si es válido, False en caso contrario
    """
    try:
        datetime.strptime(date_string, format)
        return True
    except (ValueError, TypeError):
        return False

def validate_positive_number(value: float) -> bool:
    """
    Valida que un número sea positivo.
    
    Args:
        value: Valor a validar
        
    Returns:
        True si es positivo, False en caso contrario
    """
    try:
        return float(value) >= 0
    except (ValueError, TypeError):
        return False

def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitiza un string eliminando caracteres peligrosos.
    
    Args:
        value: String a sanitizar
        max_length: Longitud máxima permitida
        
    Returns:
        String sanitizado
    """
    if not value:
        return ""
    
    # Eliminar caracteres de control
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    
    # Limitar longitud si se especifica
    if max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()
