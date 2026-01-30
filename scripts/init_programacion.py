"""
Script para inicializar programaciones de menú de prueba.
Requiere: Recetas activas
"""
import sys
import os
from datetime import datetime, date, timedelta
from random import choice, randint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.programacion import ProgramacionMenu, ProgramacionMenuItem, TiempoComida
from models.receta import Receta

def init_programacion():
    """Inicializa programaciones de menú variadas."""
    print("=" * 60)
    print("INICIALIZACIÓN DE PROGRAMACIONES DE MENÚ")
    print("=" * 60)
    
    # Verificar recetas
    recetas = Receta.query.filter_by(activa=True).all()
    if not recetas:
        print("\n⚠ No hay recetas activas.")
        print("  Ejecuta primero: python scripts/init_recetas.py")
        return []
    
    print(f"\n✓ Encontradas {len(recetas)} recetas activas")
    
    # Agrupar recetas por tipo
    recetas_por_tipo = {
        'DESAYUNO': [r for r in recetas if r.tipo and r.tipo.value == 'desayuno'],
        'ALMUERZO': [r for r in recetas if r.tipo and r.tipo.value == 'almuerzo'],
        'CENA': [r for r in recetas if r.tipo and r.tipo.value == 'cena']
    }
    
    # Si no hay recetas por tipo, usar todas
    for tipo in recetas_por_tipo:
        if not recetas_por_tipo[tipo]:
            recetas_por_tipo[tipo] = recetas[:3]  # Usar primeras 3 recetas
    
    print("\n2. INICIALIZANDO PROGRAMACIONES...")
    
    ubicaciones = ['restaurante_A', 'restaurante_B', 'restaurante_C']
    tiempos_comida = [TiempoComida.DESAYUNO, TiempoComida.ALMUERZO, TiempoComida.CENA]
    
    programaciones_data = []
    fecha_base = date.today()
    
    # Generar programaciones para los últimos 7 días y próximos 7 días
    for i in range(-7, 8):  # -7 a 7 días
        fecha_programacion = fecha_base + timedelta(days=i)
        
        # Crear programaciones para cada tiempo de comida y ubicación
        for tiempo in tiempos_comida:
            for ubicacion in ubicaciones:
                # Solo crear algunas programaciones (no todas para evitar demasiados datos)
                if randint(1, 3) == 1:  # 33% de probabilidad
                    tiempo_nombre = tiempo.name  # DESAYUNO, ALMUERZO, CENA
                    recetas_disponibles = recetas_por_tipo.get(tiempo_nombre, recetas[:2])
                    
                    if recetas_disponibles:
                        personas_estimadas = randint(50, 200)
                        charolas_planificadas = randint(20, 80)
                        charolas_producidas = randint(int(charolas_planificadas * 0.8), charolas_planificadas)
                        
                        programaciones_data.append({
                            'fecha': fecha_programacion,
                            'fecha_desde': fecha_programacion,
                            'fecha_hasta': fecha_programacion,
                            'tiempo_comida': tiempo_nombre,  # Usar nombre del enum (DESAYUNO, ALMUERZO, CENA)
                            'ubicacion': ubicacion,
                            'personas_estimadas': personas_estimadas,
                            'charolas_planificadas': charolas_planificadas,
                            'charolas_producidas': charolas_producidas,
                            'recetas': [
                                {
                                    'receta_id': choice(recetas_disponibles).id,
                                    'cantidad_porciones': randint(10, 30)
                                }
                                for _ in range(min(2, len(recetas_disponibles)))
                            ]
                        })
    
    programaciones_creadas = []
    for prog_data in programaciones_data:
        # Verificar si ya existe una programación similar
        existing = ProgramacionMenu.query.filter_by(
            fecha_desde=prog_data['fecha_desde'],
            tiempo_comida=prog_data['tiempo_comida'],
            ubicacion=prog_data['ubicacion']
        ).first()
        
        if existing:
            programaciones_creadas.append(existing)
            continue
        
        # Separar recetas de los datos de programación
        recetas_data = prog_data.pop('recetas', [])
        
        try:
            programacion = ProgramacionMenu(**prog_data)
            db.session.add(programacion)
            db.session.flush()  # Para obtener el ID
            
            # Crear items de programación (recetas)
            for receta_data in recetas_data:
                receta = Receta.query.get(receta_data['receta_id'])
                if receta:
                    programacion_item = ProgramacionMenuItem(
                        programacion_id=programacion.id,
                        receta_id=receta.id,
                        cantidad_porciones=receta_data['cantidad_porciones']
                    )
                    db.session.add(programacion_item)
            
            programaciones_creadas.append(programacion)
            tiempo_str = prog_data['tiempo_comida']
            print(f"  ✓ Creada: {prog_data['fecha_desde']} - {tiempo_str} - {prog_data['ubicacion']} ({len(recetas_data)} recetas)")
        except Exception as e:
            print(f"  ❌ Error al crear programación: {e}")
            db.session.rollback()
    
    db.session.commit()
    print(f"\n✓ Total programaciones creadas: {len(programaciones_creadas)}")
    return programaciones_creadas

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        programaciones = init_programacion()
        print(f"\n{'='*60}")
        print(f"✓ Proceso completado: {len(programaciones)} programaciones disponibles")
        print(f"{'='*60}")
