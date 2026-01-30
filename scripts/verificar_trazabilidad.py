"""
Script para verificar la trazabilidad completa: Item → Receta → Programación
Ejecutar desde la raíz del proyecto: python scripts/verificar_trazabilidad.py
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Item, Receta, RecetaIngrediente, ProgramacionMenu, ProgramacionMenuItem
from sqlalchemy import func, and_
from datetime import date

def verificar_trazabilidad():
    """Verifica la trazabilidad completa de la cadena Item → Receta → Programación."""
    
    print("=" * 80)
    print("VERIFICACIÓN INTEGRAL DE TRAZABILIDAD")
    print("Item → Receta → Programación")
    print("=" * 80)
    print()
    
    # 1. Verificar estructura básica
    print("1. ESTRUCTURA BÁSICA")
    print("-" * 80)
    
    total_items = db.session.query(Item).count()
    items_activos = db.session.query(Item).filter(Item.activo == True).count()
    
    total_recetas = db.session.query(Receta).count()
    recetas_activas = db.session.query(Receta).filter(Receta.activa == True).count()
    
    total_programaciones = db.session.query(ProgramacionMenu).count()
    
    print(f"Total Items: {total_items} (Activos: {items_activos})")
    print(f"Total Recetas: {total_recetas} (Activas: {recetas_activas})")
    print(f"Total Programaciones: {total_programaciones}")
    print()
    
    # 2. Verificar relaciones Item → Receta
    print("2. RELACIONES ITEM → RECETA")
    print("-" * 80)
    
    items_en_recetas = db.session.query(RecetaIngrediente.item_id).distinct().count()
    recetas_con_ingredientes = db.session.query(RecetaIngrediente.receta_id).distinct().count()
    
    print(f"Items usados en recetas: {items_en_recetas}")
    print(f"Recetas con ingredientes: {recetas_con_ingredientes}")
    
    # Items activos sin uso en recetas activas
    items_sin_uso = db.session.query(Item).filter(
        Item.activo == True,
        ~Item.id.in_(
            db.session.query(RecetaIngrediente.item_id)
            .join(Receta, RecetaIngrediente.receta_id == Receta.id)
            .filter(Receta.activa == True)
        )
    ).count()
    
    print(f"Items activos sin uso en recetas activas: {items_sin_uso}")
    print()
    
    # 3. Verificar relaciones Receta → Programación
    print("3. RELACIONES RECETA → PROGRAMACIÓN")
    print("-" * 80)
    
    recetas_en_programaciones = db.session.query(ProgramacionMenuItem.receta_id).distinct().count()
    programaciones_con_recetas = db.session.query(ProgramacionMenuItem.programacion_id).distinct().count()
    
    print(f"Recetas usadas en programaciones: {recetas_en_programaciones}")
    print(f"Programaciones con recetas: {programaciones_con_recetas}")
    
    # Recetas activas sin uso en programaciones
    recetas_sin_uso = db.session.query(Receta).filter(
        Receta.activa == True,
        ~Receta.id.in_(
            db.session.query(ProgramacionMenuItem.receta_id)
        )
    ).count()
    
    print(f"Recetas activas sin uso en programaciones: {recetas_sin_uso}")
    print()
    
    # 4. Verificar integridad referencial
    print("4. INTEGRIDAD REFERENCIAL")
    print("-" * 80)
    
    # RecetaIngredientes sin Item válido
    ingredientes_sin_item = db.session.query(RecetaIngrediente).filter(
        ~RecetaIngrediente.item_id.in_(db.session.query(Item.id))
    ).count()
    
    # RecetaIngredientes sin Receta válida
    ingredientes_sin_receta = db.session.query(RecetaIngrediente).filter(
        ~RecetaIngrediente.receta_id.in_(db.session.query(Receta.id))
    ).count()
    
    # ProgramacionMenuItems sin ProgramacionMenu válida
    items_sin_programacion = db.session.query(ProgramacionMenuItem).filter(
        ~ProgramacionMenuItem.programacion_id.in_(db.session.query(ProgramacionMenu.id))
    ).count()
    
    # ProgramacionMenuItems sin Receta válida
    items_sin_receta = db.session.query(ProgramacionMenuItem).filter(
        ~ProgramacionMenuItem.receta_id.in_(db.session.query(Receta.id))
    ).count()
    
    print(f"RecetaIngredientes sin Item válido: {ingredientes_sin_item}")
    print(f"RecetaIngredientes sin Receta válida: {ingredientes_sin_receta}")
    print(f"ProgramacionMenuItems sin ProgramacionMenu válida: {items_sin_programacion}")
    print(f"ProgramacionMenuItems sin Receta válida: {items_sin_receta}")
    
    if ingredientes_sin_item == 0 and ingredientes_sin_receta == 0 and items_sin_programacion == 0 and items_sin_receta == 0:
        print("✅ Integridad referencial: OK")
    else:
        print("⚠️ Integridad referencial: PROBLEMAS ENCONTRADOS")
    print()
    
    # 5. Verificar consistencia de datos
    print("5. CONSISTENCIA DE DATOS")
    print("-" * 80)
    
    # Recetas activas con ingredientes inactivos
    recetas_con_ingredientes_inactivos = db.session.query(Receta).join(
        RecetaIngrediente, Receta.id == RecetaIngrediente.receta_id
    ).join(
        Item, RecetaIngrediente.item_id == Item.id
    ).filter(
        Receta.activa == True,
        Item.activo == False
    ).distinct().count()
    
    print(f"Recetas activas con ingredientes inactivos: {recetas_con_ingredientes_inactivos}")
    
    # Recetas sin ingredientes
    recetas_sin_ingredientes = db.session.query(Receta).filter(
        Receta.activa == True,
        ~Receta.id.in_(db.session.query(RecetaIngrediente.receta_id))
    ).count()
    
    print(f"Recetas activas sin ingredientes: {recetas_sin_ingredientes}")
    
    # Programaciones sin recetas
    programaciones_sin_recetas = db.session.query(ProgramacionMenu).filter(
        ~ProgramacionMenu.id.in_(db.session.query(ProgramacionMenuItem.programacion_id))
    ).count()
    
    print(f"Programaciones sin recetas: {programaciones_sin_recetas}")
    print()
    
    # 6. Verificar cálculos
    print("6. VERIFICACIÓN DE CÁLCULOS")
    print("-" * 80)
    
    # Recetas sin totales calculados
    recetas_sin_calorias = db.session.query(Receta).filter(
        Receta.activa == True,
        Receta.calorias_totales.is_(None)
    ).count()
    
    recetas_sin_costo = db.session.query(Receta).filter(
        Receta.activa == True,
        Receta.costo_total.is_(None)
    ).count()
    
    print(f"Recetas activas sin calorías calculadas: {recetas_sin_calorias}")
    print(f"Recetas activas sin costo calculado: {recetas_sin_costo}")
    print()
    
    # 7. Trazabilidad completa: Item → Receta → Programación
    print("7. TRAZABILIDAD COMPLETA")
    print("-" * 80)
    
    # Items que están en recetas que están en programaciones
    items_con_trazabilidad_completa = db.session.query(Item).join(
        RecetaIngrediente, Item.id == RecetaIngrediente.item_id
    ).join(
        Receta, RecetaIngrediente.receta_id == Receta.id
    ).join(
        ProgramacionMenuItem, Receta.id == ProgramacionMenuItem.receta_id
    ).filter(
        Item.activo == True,
        Receta.activa == True
    ).distinct().count()
    
    print(f"Items activos con trazabilidad completa (Item → Receta → Programación): {items_con_trazabilidad_completa}")
    
    # Porcentaje de items con trazabilidad completa
    if items_activos > 0:
        porcentaje = (items_con_trazabilidad_completa / items_activos) * 100
        print(f"Porcentaje de items con trazabilidad completa: {porcentaje:.2f}%")
    print()
    
    # 8. Ejemplo de trazabilidad para un item específico
    print("8. EJEMPLO DE TRAZABILIDAD")
    print("-" * 80)
    
    # Obtener un item que tenga trazabilidad completa
    item_ejemplo = db.session.query(Item).join(
        RecetaIngrediente, Item.id == RecetaIngrediente.item_id
    ).join(
        Receta, RecetaIngrediente.receta_id == Receta.id
    ).join(
        ProgramacionMenuItem, Receta.id == ProgramacionMenuItem.receta_id
    ).filter(
        Item.activo == True,
        Receta.activa == True
    ).first()
    
    if item_ejemplo:
        print(f"Item ejemplo: {item_ejemplo.codigo} - {item_ejemplo.nombre}")
        
        # Recetas que usan este item
        recetas = db.session.query(Receta).join(
            RecetaIngrediente, Receta.id == RecetaIngrediente.receta_id
        ).filter(
            RecetaIngrediente.item_id == item_ejemplo.id,
            Receta.activa == True
        ).distinct().all()
        
        print(f"  Recetas que usan este item: {len(recetas)}")
        for receta in recetas[:3]:  # Mostrar máximo 3
            print(f"    - {receta.nombre} ({receta.tipo.value if receta.tipo else 'N/A'})")
        
        # Programaciones que usan estas recetas
        programaciones = db.session.query(ProgramacionMenu).join(
            ProgramacionMenuItem, ProgramacionMenu.id == ProgramacionMenuItem.programacion_id
        ).filter(
            ProgramacionMenuItem.receta_id.in_([r.id for r in recetas])
        ).distinct().all()
        
        print(f"  Programaciones que usan estas recetas: {len(programaciones)}")
        for prog in programaciones[:3]:  # Mostrar máximo 3
            fecha_repr = prog.fecha_desde_effective.isoformat() if prog.fecha_desde_effective else 'N/A'
            print(f"    - {fecha_repr} - {prog.ubicacion} ({prog.tiempo_comida.value if prog.tiempo_comida else 'N/A'})")
    else:
        print("No se encontró ningún item con trazabilidad completa para mostrar como ejemplo.")
    print()
    
    # 9. Resumen final
    print("=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    
    problemas = []
    if ingredientes_sin_item > 0:
        problemas.append(f"{ingredientes_sin_item} RecetaIngredientes sin Item válido")
    if ingredientes_sin_receta > 0:
        problemas.append(f"{ingredientes_sin_receta} RecetaIngredientes sin Receta válida")
    if items_sin_programacion > 0:
        problemas.append(f"{items_sin_programacion} ProgramacionMenuItems sin ProgramacionMenu válida")
    if items_sin_receta > 0:
        problemas.append(f"{items_sin_receta} ProgramacionMenuItems sin Receta válida")
    if recetas_con_ingredientes_inactivos > 0:
        problemas.append(f"{recetas_con_ingredientes_inactivos} Recetas activas con ingredientes inactivos")
    if recetas_sin_ingredientes > 0:
        problemas.append(f"{recetas_sin_ingredientes} Recetas activas sin ingredientes")
    if programaciones_sin_recetas > 0:
        problemas.append(f"{programaciones_sin_recetas} Programaciones sin recetas")
    
    if problemas:
        print("⚠️ PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"  - {problema}")
    else:
        print("✅ No se encontraron problemas de integridad")
    
    print()
    print(f"Items activos: {items_activos}")
    print(f"Items con trazabilidad completa: {items_con_trazabilidad_completa}")
    print(f"Recetas activas: {recetas_activas}")
    print(f"Recetas en programaciones: {recetas_en_programaciones}")
    print(f"Programaciones: {total_programaciones}")
    print(f"Programaciones con recetas: {programaciones_con_recetas}")
    print()
    print("=" * 80)

if __name__ == '__main__':
    from app import app
    with app.app_context():
        verificar_trazabilidad()
