"""
Script para simular generación de tickets automáticos y notificaciones
basado en las reglas de negocio del sistema.
"""
import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal
from random import choice, randint, uniform

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.ticket import Ticket, TipoTicket, EstadoTicket, PrioridadTicket
from models.charola import Charola
from models.merma import Merma, TipoMerma
from models.inventario import Inventario
from models.programacion import ProgramacionMenu
from models.item import Item
from models.proveedor import Proveedor
from modules.crm import tickets_automaticos

def simular_tickets_y_notificaciones():
    """Simula la generación de tickets automáticos y notificaciones."""
    print("=" * 60)
    print("SIMULACIÓN DE TICKETS Y NOTIFICACIONES")
    print("=" * 60)
    
    fecha_simulacion = date.today() - timedelta(days=randint(1, 7))
    
    print(f"\n📅 Fecha de simulación: {fecha_simulacion.strftime('%d/%m/%Y')}")
    print("\n🔍 Verificando reglas de negocio...")
    
    resultado = {
        'fecha': fecha_simulacion.isoformat(),
        'tickets_generados': {
            'charolas': [],
            'mermas': [],
            'inventario': [],
            'programacion': [],
            'reportes_faltantes': []
        },
        'notificaciones': [],
        'total_tickets': 0
    }
    
    # 1. Verificar charolas vs planificación
    print("\n1️⃣ Verificando charolas vs planificación...")
    try:
        tickets_charolas = tickets_automaticos.TicketsAutomaticosService.verificar_charolas_vs_planificacion(db.session, fecha_simulacion)
        resultado['tickets_generados']['charolas'] = [t.id for t in tickets_charolas]
        for ticket in tickets_charolas:
            print(f"  ✓ Ticket #{ticket.id}: {ticket.asunto} - Prioridad: {ticket.prioridad.value}")
            resultado['notificaciones'].append({
                'ticket_id': ticket.id,
                'tipo': 'charola',
                'asunto': ticket.asunto,
                'prioridad': ticket.prioridad.value,
                'canal': 'email' if ticket.prioridad in [PrioridadTicket.URGENTE, PrioridadTicket.ALTA] else 'sistema'
            })
    except Exception as e:
        print(f"  ⚠ Error: {e}")
    
    # 2. Verificar mermas excesivas
    print("\n2️⃣ Verificando mermas excesivas...")
    try:
        tickets_mermas = tickets_automaticos.TicketsAutomaticosService.verificar_mermas_limites(db.session, fecha_simulacion)
        resultado['tickets_generados']['mermas'] = [t.id for t in tickets_mermas]
        for ticket in tickets_mermas:
            print(f"  ✓ Ticket #{ticket.id}: {ticket.asunto} - Prioridad: {ticket.prioridad.value}")
            resultado['notificaciones'].append({
                'ticket_id': ticket.id,
                'tipo': 'merma',
                'asunto': ticket.asunto,
                'prioridad': ticket.prioridad.value,
                'canal': 'email' if ticket.prioridad == PrioridadTicket.ALTA else 'sistema'
            })
    except Exception as e:
        print(f"  ⚠ Error: {e}")
    
    # 3. Verificar inventario bajo mínimo
    print("\n3️⃣ Verificando inventario bajo mínimo...")
    try:
        tickets_inventario = tickets_automaticos.TicketsAutomaticosService.verificar_inventario_seguridad(db.session)
        resultado['tickets_generados']['inventario'] = [t.id for t in tickets_inventario]
        for ticket in tickets_inventario:
            print(f"  ✓ Ticket #{ticket.id}: {ticket.asunto} - Prioridad: {ticket.prioridad.value}")
            resultado['notificaciones'].append({
                'ticket_id': ticket.id,
                'tipo': 'inventario',
                'asunto': ticket.asunto,
                'prioridad': ticket.prioridad.value,
                'canal': 'whatsapp' if ticket.prioridad == PrioridadTicket.URGENTE else 'email',
                'proveedor_id': ticket.proveedor_id
            })
    except Exception as e:
        print(f"  ⚠ Error: {e}")
    
    # 4. Verificar programación faltante
    print("\n4️⃣ Verificando programación faltante...")
    try:
        tickets_programacion = tickets_automaticos.TicketsAutomaticosService.verificar_programacion_faltante(db, fecha_simulacion)
        resultado['tickets_generados']['programacion'] = [t.id for t in tickets_programacion]
        for ticket in tickets_programacion:
            print(f"  ✓ Ticket #{ticket.id}: {ticket.asunto} - Prioridad: {ticket.prioridad.value}")
            resultado['notificaciones'].append({
                'ticket_id': ticket.id,
                'tipo': 'programacion',
                'asunto': ticket.asunto,
                'prioridad': ticket.prioridad.value,
                'canal': 'email'
            })
    except Exception as e:
        print(f"  ⚠ Error: {e}")
    
    # 5. Verificar reportes faltantes
    print("\n5️⃣ Verificando reportes faltantes...")
    try:
        tickets_reportes = tickets_automaticos.TicketsAutomaticosService.verificar_reportes_faltantes(db.session, fecha_simulacion)
        resultado['tickets_generados']['reportes_faltantes'] = [t.id for t in tickets_reportes]
        for ticket in tickets_reportes:
            print(f"  ✓ Ticket #{ticket.id}: {ticket.asunto} - Prioridad: {ticket.prioridad.value}")
            resultado['notificaciones'].append({
                'ticket_id': ticket.id,
                'tipo': 'reporte_faltante',
                'asunto': ticket.asunto,
                'prioridad': ticket.prioridad.value,
                'canal': 'sistema'
            })
    except Exception as e:
        print(f"  ⚠ Error: {e}")
    
    # Calcular total
    resultado['total_tickets'] = (
        len(resultado['tickets_generados']['charolas']) +
        len(resultado['tickets_generados']['mermas']) +
        len(resultado['tickets_generados']['inventario']) +
        len(resultado['tickets_generados']['programacion']) +
        len(resultado['tickets_generados']['reportes_faltantes'])
    )
    
    # Mostrar resumen de notificaciones
    print("\n" + "=" * 60)
    print("📧 RESUMEN DE NOTIFICACIONES")
    print("=" * 60)
    
    notificaciones_por_canal = {}
    for notif in resultado['notificaciones']:
        canal = notif['canal']
        if canal not in notificaciones_por_canal:
            notificaciones_por_canal[canal] = []
        notificaciones_por_canal[canal].append(notif)
    
    for canal, notifs in notificaciones_por_canal.items():
        print(f"\n📱 Canal: {canal.upper()}")
        print(f"   Total: {len(notifs)} notificaciones")
        for notif in notifs[:5]:  # Mostrar primeras 5
            print(f"   - Ticket #{notif['ticket_id']}: {notif['asunto'][:50]}...")
        if len(notifs) > 5:
            print(f"   ... y {len(notifs) - 5} más")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    print(f"✅ Total tickets generados: {resultado['total_tickets']}")
    print(f"   - Charolas: {len(resultado['tickets_generados']['charolas'])}")
    print(f"   - Mermas: {len(resultado['tickets_generados']['mermas'])}")
    print(f"   - Inventario: {len(resultado['tickets_generados']['inventario'])}")
    print(f"   - Programación: {len(resultado['tickets_generados']['programacion'])}")
    print(f"   - Reportes faltantes: {len(resultado['tickets_generados']['reportes_faltantes'])}")
    print(f"\n📧 Total notificaciones: {len(resultado['notificaciones'])}")
    
    return resultado

def crear_escenarios_adicionales():
    """Crea escenarios adicionales para simular más tickets."""
    print("\n" + "=" * 60)
    print("CREANDO ESCENARIOS ADICIONALES")
    print("=" * 60)
    
    tickets_creados = []
    
    # Escenario 1: Crear charolas con desviación intencional
    print("\n📋 Escenario 1: Desviación en charolas...")
    programaciones = ProgramacionMenu.query.limit(3).all()
    fecha_escenario = date.today() - timedelta(days=2)
    
    for programacion in programaciones:
        # Crear charolas con desviación significativa
        charolas_planificadas = programacion.charolas_planificadas or 100
        desviacion = randint(-20, -10)  # Desviación negativa (menos charolas)
        charolas_a_crear = max(1, charolas_planificadas + desviacion)
        
        # Verificar si ya hay charolas para esta fecha
        charolas_existentes = Charola.query.filter(
            Charola.fecha_servicio >= datetime.combine(fecha_escenario, datetime.min.time()),
            Charola.fecha_servicio < datetime.combine(fecha_escenario + timedelta(days=1), datetime.min.time()),
            Charola.tiempo_comida == programacion.tiempo_comida.value,
            Charola.ubicacion == programacion.ubicacion
        ).count()
        
        if charolas_existentes == 0:
            print(f"  ✓ Creando {charolas_a_crear} charolas (planificadas: {charolas_planificadas}) para {programacion.tiempo_comida.value}")
            # Nota: No creamos las charolas aquí, solo simulamos que faltan
    
    # Escenario 2: Crear mermas excesivas
    print("\n📋 Escenario 2: Mermas excesivas...")
    items = Item.query.filter_by(activo=True).limit(5).all()
    fecha_merma = datetime.now() - timedelta(days=1)
    
    for item in items:
        inventario = Inventario.query.filter_by(item_id=item.id).first()
        if inventario:
            # Crear merma que supera el 5% del inventario
            cantidad_referencia = max(float(inventario.cantidad_actual), float(inventario.cantidad_minima))
            merma_excesiva = Decimal(str(cantidad_referencia)) * Decimal('0.08')  # 8% (supera el 5%)
            
            # Verificar si ya existe merma para este item hoy
            merma_existente = Merma.query.filter(
                Merma.item_id == item.id,
                Merma.fecha_merma >= datetime.combine(fecha_merma.date(), datetime.min.time()),
                Merma.fecha_merma < datetime.combine(fecha_merma.date() + timedelta(days=1), datetime.min.time())
            ).first()
            
            if not merma_existente and merma_excesiva > 10:
                merma = Merma(
                    item_id=item.id,
                    fecha_merma=fecha_merma,
                    tipo=choice([TipoMerma.VENCIMIENTO, TipoMerma.DETERIORO, TipoMerma.PREPARACION]),
                    cantidad=merma_excesiva,
                    unidad=item.unidad,
                    costo_unitario=item.costo_unitario_actual or Decimal('5'),
                    costo_total=merma_excesiva * (item.costo_unitario_actual or Decimal('5')),
                    motivo=f"Merma simulada para prueba - {choice(['Vencimiento', 'Deterioro', 'Preparación'])}",
                    ubicacion='restaurante_A',
                    registrado_por=1,
                    fecha_registro=fecha_merma
                )
                db.session.add(merma)
                print(f"  ✓ Merma excesiva creada para {item.nombre}: {merma_excesiva:.2f} {item.unidad}")
    
    db.session.commit()
    
    # Escenario 3: Reducir inventario bajo mínimo
    print("\n📋 Escenario 3: Inventario bajo mínimo...")
    inventarios = Inventario.query.limit(5).all()
    
    for inventario in inventarios:
        if float(inventario.cantidad_actual) > float(inventario.cantidad_minima):
            # Reducir inventario a menos del mínimo
            nuevo_stock = Decimal(str(inventario.cantidad_minima)) * Decimal('0.6')  # 60% del mínimo
            inventario.cantidad_actual = nuevo_stock
            print(f"  ✓ Inventario reducido para {inventario.item.nombre}: {nuevo_stock:.2f} (mínimo: {inventario.cantidad_minima})")
    
    db.session.commit()
    
    return tickets_creados

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Crear escenarios adicionales primero
        crear_escenarios_adicionales()
        
        # Ejecutar simulación
        resultado = simular_tickets_y_notificaciones()
        
        print(f"\n{'='*60}")
        print(f"✅ Simulación completada")
        print(f"{'='*60}")
        print(f"\n📝 Resumen:")
        print(f"   - Tickets generados: {resultado['total_tickets']}")
        print(f"   - Notificaciones: {len(resultado['notificaciones'])}")
        print(f"\n💡 Los tickets están disponibles en la base de datos")
        print(f"💡 Las notificaciones se enviarían según la configuración del sistema")
