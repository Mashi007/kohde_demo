"""
Servicio para conversión de unidades compatibles.
"""
from typing import Optional, Dict, Tuple

# Factores de conversión a unidades base
CONVERSIONES = {
    # Peso: base = kg
    'kg': 1.0,
    'g': 0.001,
    'gramo': 0.001,
    'gramos': 0.001,
    'ton': 1000.0,
    'tonelada': 1000.0,
    'toneladas': 1000.0,
    'lb': 0.453592,  # libras a kg
    'libras': 0.453592,
    'oz': 0.0283495,  # onzas a kg
    'onzas': 0.0283495,
    'qq': 45.3592,  # quintal a kg (1 quintal = 100 libras = 45.3592 kg)
    'quintal': 45.3592,
    'quintales': 45.3592,
    'arrobas': 11.3398,  # arroba a kg (1 arroba = 25 libras = 11.3398 kg)
    'arroba': 11.3398,
    
    # Volumen: base = l (litros)
    'l': 1.0,
    'litro': 1.0,
    'litros': 1.0,
    'ml': 0.001,
    'mililitro': 0.001,
    'mililitros': 0.001,
    'cl': 0.01,
    'centilitro': 0.01,
    'centilitros': 0.01,
    'dl': 0.1,
    'decilitro': 0.1,
    'decilitros': 0.1,
    'gal': 3.78541,  # galones a litros
    'galon': 3.78541,
    'galones': 3.78541,
    'fl_oz': 0.0295735,  # onzas fluidas a litros
    'onza_fluida': 0.0295735,
    'onzas_fluidas': 0.0295735,
    
    # Unidades discretas: base = unidad
    'unidad': 1.0,
    'unidades': 1.0,
    'caja': 1.0,  # Se mantiene como está
    'cajas': 1.0,
    'paquete': 1.0,  # Se mantiene como está
    'paquetes': 1.0,
    'docena': 12.0,
    'docenas': 12.0,
    'centena': 100.0,
    'centenas': 100.0,
}

# Grupos de unidades compatibles
GRUPOS_UNIDADES = {
    'peso': ['kg', 'g', 'ton', 'lb', 'oz'],
    'volumen': ['l', 'ml', 'cl', 'dl', 'gal', 'fl_oz'],
    'discreto': ['unidad', 'caja', 'paquete', 'docena', 'centena'],
}

def obtener_grupo_unidad(unidad: str) -> Optional[str]:
    """
    Obtiene el grupo al que pertenece una unidad.
    
    Args:
        unidad: Unidad a verificar
        
    Returns:
        Grupo de unidad o None si no se encuentra
    """
    unidad_lower = unidad.lower()
    for grupo, unidades in GRUPOS_UNIDADES.items():
        if unidad_lower in unidades:
            return grupo
    return None

def son_unidades_compatibles(unidad1: str, unidad2: str) -> bool:
    """
    Verifica si dos unidades son compatibles (mismo grupo).
    
    Args:
        unidad1: Primera unidad
        unidad2: Segunda unidad
        
    Returns:
        True si son compatibles, False en caso contrario
    """
    grupo1 = obtener_grupo_unidad(unidad1)
    grupo2 = obtener_grupo_unidad(unidad2)
    
    if grupo1 is None or grupo2 is None:
        return False
    
    return grupo1 == grupo2

def convertir_a_unidad_base(cantidad: float, unidad_origen: str) -> Optional[Tuple[float, str]]:
    """
    Convierte una cantidad a su unidad base.
    
    Args:
        cantidad: Cantidad a convertir
        unidad_origen: Unidad de origen
        
    Returns:
        Tupla (cantidad_convertida, unidad_base) o None si no se puede convertir
    """
    unidad_lower = unidad_origen.lower()
    
    if unidad_lower not in CONVERSIONES:
        return None
    
    factor = CONVERSIONES[unidad_lower]
    cantidad_base = cantidad * factor
    
    # Determinar unidad base según el grupo
    grupo = obtener_grupo_unidad(unidad_origen)
    if grupo == 'peso':
        unidad_base = 'kg'
    elif grupo == 'volumen':
        unidad_base = 'l'
    elif grupo == 'discreto':
        unidad_base = 'unidad'
    else:
        return None
    
    return (cantidad_base, unidad_base)

def convertir_unidad(cantidad: float, unidad_origen: str, unidad_destino: str) -> Optional[float]:
    """
    Convierte una cantidad de una unidad a otra compatible.
    
    Args:
        cantidad: Cantidad a convertir
        unidad_origen: Unidad de origen
        unidad_destino: Unidad de destino
        
    Returns:
        Cantidad convertida o None si no se puede convertir
    """
    if not son_unidades_compatibles(unidad_origen, unidad_destino):
        return None
    
    unidad_origen_lower = unidad_origen.lower()
    unidad_destino_lower = unidad_destino.lower()
    
    if unidad_origen_lower not in CONVERSIONES or unidad_destino_lower not in CONVERSIONES:
        return None
    
    # Convertir a unidad base primero
    factor_origen = CONVERSIONES[unidad_origen_lower]
    cantidad_base = cantidad * factor_origen
    
    # Convertir de unidad base a destino
    factor_destino = CONVERSIONES[unidad_destino_lower]
    cantidad_destino = cantidad_base / factor_destino
    
    return cantidad_destino

def calcular_costo_unitario_estandarizado(
    cantidad: float,
    costo_total: float,
    unidad_origen: str,
    unidad_estandar: str
) -> Optional[float]:
    """
    Calcula el costo unitario estandarizado.
    
    Args:
        cantidad: Cantidad en unidad origen
        costo_total: Costo total
        unidad_origen: Unidad de origen
        unidad_estandar: Unidad estandarizada
        
    Returns:
        Costo unitario estandarizado o None si no se puede convertir
    """
    if not son_unidades_compatibles(unidad_origen, unidad_estandar):
        return None
    
    # Convertir cantidad a unidad estandarizada
    cantidad_estandarizada = convertir_unidad(cantidad, unidad_origen, unidad_estandar)
    if cantidad_estandarizada is None or cantidad_estandarizada == 0:
        return None
    
    # Calcular costo unitario
    costo_unitario = costo_total / cantidad_estandarizada
    return costo_unitario
