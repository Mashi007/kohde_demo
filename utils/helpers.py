"""
Funciones auxiliares del sistema ERP.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

def calcular_iva(subtotal: float, porcentaje_iva: float = 0.15) -> float:
    """
    Calcula el IVA sobre un subtotal.
    
    Args:
        subtotal: Subtotal sin IVA
        porcentaje_iva: Porcentaje de IVA (default 15%)
        
    Returns:
        Monto del IVA
    """
    return float(Decimal(str(subtotal)) * Decimal(str(porcentaje_iva)))

def calcular_total(subtotal: float, iva: float) -> float:
    """
    Calcula el total sumando subtotal e IVA.
    
    Args:
        subtotal: Subtotal sin IVA
        iva: Monto del IVA
        
    Returns:
        Total con IVA
    """
    return float(Decimal(str(subtotal)) + Decimal(str(iva)))

def formatear_moneda(valor: float) -> str:
    """
    Formatea un valor numérico como moneda.
    
    Args:
        valor: Valor a formatear
        
    Returns:
        String formateado como moneda
    """
    return f"${valor:,.2f}"

def obtener_fecha_entrega_esperada(dias_entrega: int, fecha_base: Optional[datetime] = None) -> datetime:
    """
    Calcula la fecha de entrega esperada sumando días hábiles.
    
    Args:
        dias_entrega: Días de entrega
        fecha_base: Fecha base (default: hoy)
        
    Returns:
        Fecha de entrega esperada
    """
    if fecha_base is None:
        fecha_base = datetime.utcnow()
    
    return fecha_base + timedelta(days=dias_entrega)

def verificar_stock_suficiente(
    cantidad_necesaria: float,
    cantidad_actual: float,
    cantidad_minima: float
) -> Dict[str, any]:
    """
    Verifica si hay stock suficiente para una cantidad necesaria.
    
    Args:
        cantidad_necesaria: Cantidad que se necesita
        cantidad_actual: Cantidad actual en inventario
        cantidad_minima: Cantidad mínima requerida (amortiguador)
        
    Returns:
        Diccionario con resultado de la verificación
    """
    disponible = cantidad_actual - cantidad_minima
    suficiente = disponible >= cantidad_necesaria
    faltante = max(0, cantidad_necesaria - disponible) if not suficiente else 0
    
    return {
        'suficiente': suficiente,
        'cantidad_disponible': disponible,
        'cantidad_faltante': faltante,
        'cantidad_necesaria': cantidad_necesaria,
        'cantidad_actual': cantidad_actual,
        'cantidad_minima': cantidad_minima,
    }

def agrupar_items_por_proveedor(items: List[Dict]) -> Dict[int, List[Dict]]:
    """
    Agrupa items por proveedor autorizado.
    
    Args:
        items: Lista de items con proveedor_autorizado_id
        
    Returns:
        Diccionario agrupado por proveedor_id
    """
    agrupados = {}
    
    for item in items:
        proveedor_id = item.get('proveedor_autorizado_id')
        if proveedor_id:
            if proveedor_id not in agrupados:
                agrupados[proveedor_id] = []
            agrupados[proveedor_id].append(item)
    
    return agrupados

def calcular_calorias_totales(ingredientes: List[Dict]) -> float:
    """
    Calcula calorías totales de una lista de ingredientes.
    
    Args:
        ingredientes: Lista de ingredientes con cantidad y calorias_por_unidad
        
    Returns:
        Calorías totales
    """
    total = Decimal('0')
    
    for ing in ingredientes:
        cantidad = Decimal(str(ing.get('cantidad', 0)))
        calorias_por_unidad = Decimal(str(ing.get('calorias_por_unidad', 0)))
        total += cantidad * calorias_por_unidad
    
    return float(total)

def calcular_costo_total(items: List[Dict]) -> float:
    """
    Calcula costo total de una lista de items.
    
    Args:
        items: Lista de items con cantidad y precio_unitario
        
    Returns:
        Costo total
    """
    total = Decimal('0')
    
    for item in items:
        cantidad = Decimal(str(item.get('cantidad', 0)))
        precio = Decimal(str(item.get('precio_unitario', 0)))
        total += cantidad * precio
    
    return float(total)
