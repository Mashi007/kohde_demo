"""
Script para inicializar inventario basado en facturas aprobadas y consumos realistas.
Requiere: Items activos y Facturas (opcional, pero recomendado)
"""
import sys
import os
from datetime import datetime
from decimal import Decimal

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.item import Item
from models.inventario import Inventario
from models.factura import Factura, EstadoFactura

def init_inventario():
    """Inicializa inventario realista basado en facturas aprobadas y consumos simulados."""
    print("=" * 60)
    print("INICIALIZACIÓN DE INVENTARIO")
    print("=" * 60)
    
    # Verificar items
    items = Item.query.filter_by(activo=True).all()
    if not items:
        print("\n⚠ No hay items activos.")
        print("  Ejecuta primero: python scripts/init_items.py")
        return
    
    print(f"\n✓ Encontrados {len(items)} items activos")
    
    # Obtener facturas aprobadas y parciales
    facturas_aprobadas = Factura.query.filter_by(estado=EstadoFactura.APROBADA).all()
    facturas_parciales = Factura.query.filter_by(estado=EstadoFactura.PARCIAL).all()
    
    if facturas_aprobadas or facturas_parciales:
        print(f"✓ Encontradas {len(facturas_aprobadas)} facturas aprobadas y {len(facturas_parciales)} parciales")
    else:
        print("⚠ No hay facturas aprobadas. El inventario se generará con stock inicial.")
        print("  Para inventario basado en facturas, ejecuta primero: python scripts/init_facturas.py")
    
    print("\n3. INICIALIZANDO INVENTARIO (BASADO EN FACTURAS Y CONSUMOS REALES)...")
    
    # Calcular inventario inicial basado en facturas aprobadas
    inventario_base = {}  # item_id -> cantidad acumulada
    
    # Procesar facturas aprobadas (100% de cantidad aprobada)
    for factura in facturas_aprobadas:
        for factura_item in factura.items:
            if factura_item.item_id and factura_item.cantidad_aprobada:
                if factura_item.item_id not in inventario_base:
                    inventario_base[factura_item.item_id] = Decimal('0')
                inventario_base[factura_item.item_id] += factura_item.cantidad_aprobada
    
    # Procesar facturas parciales (cantidad aprobada parcial)
    for factura in facturas_parciales:
        for factura_item in factura.items:
            if factura_item.item_id and factura_item.cantidad_aprobada:
                if factura_item.item_id not in inventario_base:
                    inventario_base[factura_item.item_id] = Decimal('0')
                inventario_base[factura_item.item_id] += factura_item.cantidad_aprobada
    
    # Definir niveles mínimos realistas según categoría
    def calcular_nivel_minimo(item):
        """Calcula nivel mínimo realista según tipo de item."""
        categoria = item.categoria.lower() if item.categoria else ''
        nombre_lower = item.nombre.lower()
        
        # Items perecederos (verduras, frutas, carnes frescas) - stock mínimo bajo
        if any(x in categoria or x in nombre_lower for x in ['verdura', 'hortaliza', 'fruta', 'lechuga', 'tomate', 'cebolla']):
            return Decimal('5.0')
        if any(x in categoria or x in nombre_lower for x in ['pollo', 'carne', 'res', 'cerdo', 'pescado']):
            return Decimal('10.0')
        
        # Lácteos - stock mínimo medio
        if any(x in categoria or x in nombre_lower for x in ['leche', 'queso', 'huevo', 'yogurt', 'mantequilla', 'crema']):
            return Decimal('15.0')
        
        # Productos secos (arroz, pasta, harina) - stock mínimo alto
        if any(x in categoria or x in nombre_lower for x in ['arroz', 'pasta', 'harina', 'azucar', 'frijol', 'lenteja']):
            return Decimal('20.0')
        
        # Condimentos y especias - stock mínimo bajo (se usan poco)
        if any(x in categoria or x in nombre_lower for x in ['sal', 'pimienta', 'comino', 'oregano', 'aceite', 'vinagre']):
            return Decimal('2.0')
        
        # Bebidas - stock mínimo medio
        if categoria == 'bebida':
            return Decimal('24.0')  # Cajas/botellas
        
        # Limpieza - stock mínimo medio
        if categoria == 'limpieza':
            return Decimal('10.0')
        
        # Panadería - stock mínimo bajo (perecedero)
        if any(x in categoria or x in nombre_lower for x in ['pan', 'tortilla', 'levadura']):
            return Decimal('5.0')
        
        # Default
        return Decimal('10.0')
    
    # Simular consumos realistas (algunos items se consumen más rápido)
    def simular_consumo(item, cantidad_base):
        """Simula consumo realista según tipo de item."""
        categoria = item.categoria.lower() if item.categoria else ''
        nombre_lower = item.nombre.lower()
        
        # Items de alto consumo (verduras básicas, carnes, lácteos básicos)
        if any(x in nombre_lower for x in ['cebolla', 'tomate', 'papa', 'pollo', 'res', 'leche', 'huevo']):
            consumo_percent = Decimal('0.60')  # Se consume 60% del stock inicial
        # Items de consumo medio (arroz, pasta, quesos)
        elif any(x in nombre_lower for x in ['arroz', 'pasta', 'queso', 'harina']):
            consumo_percent = Decimal('0.40')  # Se consume 40%
        # Items de bajo consumo (especias, condimentos)
        elif any(x in nombre_lower for x in ['sal', 'pimienta', 'comino', 'oregano', 'aceite', 'vinagre']):
            consumo_percent = Decimal('0.20')  # Se consume 20%
        # Bebidas
        elif categoria == 'bebida':
            consumo_percent = Decimal('0.50')  # Se consume 50%
        # Limpieza
        elif categoria == 'limpieza':
            consumo_percent = Decimal('0.30')  # Se consume 30%
        else:
            consumo_percent = Decimal('0.35')  # Default
        
        consumo = cantidad_base * consumo_percent
        cantidad_actual = cantidad_base - consumo
        
        # Asegurar que no sea negativo
        return max(cantidad_actual, Decimal('0'))
    
    inventario_creado = 0
    inventario_actualizado = 0
    
    for item in items:
        existing = Inventario.query.filter_by(item_id=item.id).first()
        
        # Calcular cantidad inicial basada en facturas
        cantidad_base = inventario_base.get(item.id, Decimal('0'))
        
        # Si no hay facturas para este item, generar stock inicial realista según tipo
        if cantidad_base == 0:
            categoria = item.categoria.lower() if item.categoria else ''
            nombre_lower = item.nombre.lower()
            
            # Generar stock inicial según tipo de item
            if categoria == 'MATERIA_PRIMA':
                if any(x in nombre_lower for x in ['verdura', 'hortaliza', 'fruta', 'lechuga', 'tomate', 'cebolla', 'zanahoria']):
                    cantidad_base = Decimal('30.0')  # Verduras frescas
                elif any(x in nombre_lower for x in ['carne', 'pollo', 'res', 'cerdo', 'pescado', 'ternera']):
                    cantidad_base = Decimal('25.0')  # Carnes
                elif any(x in nombre_lower for x in ['leche', 'queso', 'huevo', 'yogurt', 'mantequilla', 'crema']):
                    cantidad_base = Decimal('40.0')  # Lácteos
                elif any(x in nombre_lower for x in ['arroz', 'pasta', 'harina', 'azucar', 'frijol', 'lenteja', 'avena']):
                    cantidad_base = Decimal('50.0')  # Productos secos
                elif any(x in nombre_lower for x in ['sal', 'pimienta', 'comino', 'oregano', 'aceite', 'vinagre']):
                    cantidad_base = Decimal('10.0')  # Condimentos (se usan poco)
                elif any(x in nombre_lower for x in ['pan', 'tortilla', 'levadura']):
                    cantidad_base = Decimal('20.0')  # Panadería
                else:
                    cantidad_base = Decimal('20.0')  # Otros
            elif categoria == 'bebida':
                cantidad_base = Decimal('48.0')  # Cajas/botellas
            elif categoria == 'limpieza':
                cantidad_base = Decimal('15.0')
            else:
                cantidad_base = Decimal('20.0')
        
        # Simular consumo realista
        cantidad_actual = simular_consumo(item, cantidad_base)
        
        # Calcular nivel mínimo
        cantidad_minima = calcular_nivel_minimo(item)
        
        # Obtener último costo de facturas aprobadas o usar costo actual del item
        ultimo_costo = item.costo_unitario_actual
        if facturas_aprobadas or facturas_parciales:
            # Buscar último precio de factura aprobada para este item
            for factura in list(facturas_aprobadas) + list(facturas_parciales):
                for factura_item in factura.items:
                    if factura_item.item_id == item.id and factura_item.precio_unitario:
                        ultimo_costo = factura_item.precio_unitario
                        break
                if ultimo_costo != item.costo_unitario_actual:
                    break
        
        if not existing:
            inventario = Inventario(
                item_id=item.id,
                ubicacion='bodega_principal',
                cantidad_actual=cantidad_actual,
                cantidad_minima=cantidad_minima,
                unidad=item.unidad,
                ultimo_costo_unitario=ultimo_costo
            )
            db.session.add(inventario)
            inventario_creado += 1
            
            # Determinar estado del stock
            estado_stock = "✓"
            if cantidad_actual < cantidad_minima:
                estado_stock = "⚠ BAJO"
            elif cantidad_actual < cantidad_minima * Decimal('1.5'):
                estado_stock = "⚠ CRÍTICO"
            
            print(f"  {estado_stock} Inventario creado: {item.nombre} - Actual: {cantidad_actual:.2f} {item.unidad} (Mín: {cantidad_minima:.2f})")
        else:
            # Actualizar inventario existente si hay facturas nuevas
            if cantidad_base > 0:
                existing.cantidad_actual = cantidad_actual
                existing.cantidad_minima = cantidad_minima
                existing.ultimo_costo_unitario = ultimo_costo
                existing.ultima_actualizacion = datetime.utcnow()
                inventario_actualizado += 1
                
                estado_stock = "✓"
                if cantidad_actual < cantidad_minima:
                    estado_stock = "⚠ BAJO"
                elif cantidad_actual < cantidad_minima * Decimal('1.5'):
                    estado_stock = "⚠ CRÍTICO"
                
                print(f"  {estado_stock} Inventario actualizado: {item.nombre} - Actual: {cantidad_actual:.2f} {item.unidad} (Mín: {cantidad_minima:.2f})")
            else:
                print(f"  ↻ Ya existe inventario para: {item.nombre}")
    
    db.session.commit()
    print(f"\n  Resumen:")
    print(f"    - Inventarios creados: {inventario_creado}")
    print(f"    - Inventarios actualizados: {inventario_actualizado}")
    print(f"    - Facturas procesadas: {len(facturas_aprobadas)} aprobadas, {len(facturas_parciales)} parciales")
    print(f"\n{'='*60}")
    print(f"✓ Proceso completado")
    print(f"{'='*60}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        init_inventario()
