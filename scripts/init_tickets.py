"""
Script para generar tickets mock basados en reglas de negocio.
Los tickets reflejan situaciones reales como consumo mayor al planeado, mermas excesivas, etc.
"""
import sys
import os
from datetime import datetime, date, timedelta
from random import choice, randint, uniform
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.ticket import Ticket, TipoTicket, EstadoTicket, PrioridadTicket
from models.charola import Charola
from models.merma import Merma, TipoMerma
from models.inventario import Inventario
from models.programacion import ProgramacionMenu, TiempoComida
from models.item import Item
from models.proveedor import Proveedor

def generar_tickets_mock():
    """Genera tickets mock basados en reglas de negocio."""
    print("=" * 70)
    print("GENERACIÓN DE TICKETS MOCK - REGLAS DE NEGOCIO")
    print("=" * 70)
    print()
    
    tickets_creados = []
    
    # Obtener datos necesarios
    programaciones = db.session.query(ProgramacionMenu).limit(10).all()
    items = db.session.query(Item).filter(Item.activo == True).limit(15).all()
    inventarios = db.session.query(Inventario).limit(10).all()
    proveedores = db.session.query(Proveedor).limit(5).all()
    
    # Fechas para generar tickets (últimos 7 días)
    fecha_base = date.today()
    
    # 1. TICKETS DE DESVIACIÓN EN CHAROLAS (Consumo mayor/menor al planeado)
    print("\n1️⃣ Generando tickets de desviación en charolas...")
    for i in range(7):
        fecha_ticket = fecha_base - timedelta(days=i)
        
        if programaciones:
            programacion = choice(programaciones)
            charolas_planificadas = programacion.charolas_planificadas or 50
            
            # Simular diferentes escenarios
            escenarios = [
                {'nombre': 'Consumo mayor al planeado', 'factor': uniform(1.15, 1.35), 'tipo': TipoTicket.QUEJA},
                {'nombre': 'Consumo menor al planeado', 'factor': uniform(0.65, 0.85), 'tipo': TipoTicket.CONSULTA},
                {'nombre': 'Consumo significativamente mayor', 'factor': uniform(1.35, 1.50), 'tipo': TipoTicket.QUEJA},
                {'nombre': 'Consumo muy bajo', 'factor': uniform(0.50, 0.70), 'tipo': TipoTicket.CONSULTA},
            ]
            
            escenario = choice(escenarios)
            charolas_servidas = int(charolas_planificadas * escenario['factor'])
            diferencia = charolas_servidas - charolas_planificadas
            porcentaje_desviacion = (diferencia / charolas_planificadas * 100) if charolas_planificadas > 0 else 0
            
            # Solo crear ticket si la desviación es significativa
            if abs(diferencia) > max(5, charolas_planificadas * 0.1):
                prioridad = PrioridadTicket.ALTA if abs(porcentaje_desviacion) > 20 else PrioridadTicket.MEDIA
                
                asunto = f"Desviación en charolas - {programacion.tiempo_comida.value.capitalize()}"
                descripcion = (
                    f"Desviación detectada en el servicio de {programacion.tiempo_comida.value} "
                    f"del {fecha_ticket.strftime('%d/%m/%Y')} en {programacion.ubicacion}.\n\n"
                    f"📊 ANÁLISIS DE CONSUMO:\n"
                    f"• Charolas planificadas: {charolas_planificadas}\n"
                    f"• Charolas servidas: {charolas_servidas}\n"
                    f"• Diferencia: {diferencia:+d} charolas ({porcentaje_desviacion:+.1f}%)\n\n"
                )
                
                if diferencia > 0:
                    descripcion += (
                        f"⚠️ CONSUMO MAYOR AL PLANEADO\n"
                        f"Se consumieron {diferencia} charolas más de las planificadas.\n"
                        f"Esto puede indicar:\n"
                        f"- Mayor demanda de la esperada\n"
                        f"- Necesidad de ajustar la planificación\n"
                        f"- Posible impacto en inventario y costos\n\n"
                    )
                else:
                    descripcion += (
                        f"⚠️ CONSUMO MENOR AL PLANEADO\n"
                        f"Se consumieron {abs(diferencia)} charolas menos de las planificadas.\n"
                        f"Esto puede indicar:\n"
                        f"- Menor demanda de la esperada\n"
                        f"- Posible desperdicio de alimentos preparados\n"
                        f"- Necesidad de revisar la planificación\n\n"
                    )
                
                descripcion += f"Programación ID: {programacion.id}"
                
                ticket = Ticket(
                    cliente_id=0,
                    tipo=escenario['tipo'],
                    asunto=asunto,
                    descripcion=descripcion,
                    estado=EstadoTicket.ABIERTO if i < 3 else choice([EstadoTicket.ABIERTO, EstadoTicket.EN_PROCESO]),
                    prioridad=prioridad,
                    programacion_id=programacion.id,
                    origen_modulo='charola',
                    auto_generado='true',
                    fecha_creacion=datetime.combine(fecha_ticket, datetime.min.time()) + timedelta(hours=randint(14, 18))
                )
                
                db.session.add(ticket)
                tickets_creados.append(ticket)
                print(f"  ✓ {escenario['nombre']}: {diferencia:+d} charolas ({porcentaje_desviacion:+.1f}%)")
    
    # 2. TICKETS DE MERMAS EXCESIVAS
    print("\n2️⃣ Generando tickets de mermas excesivas...")
    for i in range(5):
        if not items:
            break
        
        item = choice(items)
        inventario = db.session.query(Inventario).filter(Inventario.item_id == item.id).first()
        
        if inventario:
            cantidad_referencia = max(
                float(inventario.cantidad_actual),
                float(inventario.cantidad_minima)
            )
            
            # Simular merma excesiva (8-15% del inventario)
            porcentaje_merma = uniform(8, 15)
            cantidad_merma = cantidad_referencia * (porcentaje_merma / 100)
            costo_unitario = float(item.costo_unitario_actual) if item.costo_unitario_actual else uniform(10, 50)
            costo_total = cantidad_merma * costo_unitario
            
            fecha_merma = fecha_base - timedelta(days=randint(1, 5))
            
            asunto = f"Merma excesiva - {item.nombre}"
            descripcion = (
                f"Merma excesiva detectada para el item '{item.nombre}' "
                f"el {fecha_merma.strftime('%d/%m/%Y')}.\n\n"
                f"📉 ANÁLISIS DE MERMA:\n"
                f"• Cantidad de merma: {cantidad_merma:.2f} {item.unidad}\n"
                f"• Costo total: ${costo_total:.2f}\n"
                f"• Porcentaje vs referencia: {porcentaje_merma:.2f}%\n"
                f"• Límite estándar: 5%\n"
                f"• Exceso: {porcentaje_merma - 5:.2f}% sobre el límite\n\n"
                f"⚠️ IMPACTO:\n"
                f"Esta merma excede el límite estándar del 5% del inventario.\n"
                f"Posibles causas:\n"
                f"- Vencimiento de productos\n"
                f"- Deterioro por mal almacenamiento\n"
                f"- Errores en preparación\n"
                f"- Sobrestock inicial\n\n"
                f"Item ID: {item.id}\n"
                f"Inventario ID: {inventario.id}"
            )
            
            prioridad = PrioridadTicket.ALTA if porcentaje_merma > 10 else PrioridadTicket.MEDIA
            
            ticket = Ticket(
                cliente_id=None,
                tipo=TipoTicket.QUEJA,
                asunto=asunto,
                descripcion=descripcion,
                estado=EstadoTicket.ABIERTO if i < 2 else choice([EstadoTicket.ABIERTO, EstadoTicket.EN_PROCESO]),
                prioridad=prioridad,
                inventario_id=inventario.id,
                origen_modulo='merma',
                auto_generado='true',
                fecha_creacion=datetime.combine(fecha_merma, datetime.min.time()) + timedelta(hours=randint(16, 20))
            )
            
            db.session.add(ticket)
            tickets_creados.append(ticket)
            print(f"  ✓ Merma excesiva: {item.nombre} ({porcentaje_merma:.1f}%)")
    
    # 3. TICKETS DE INVENTARIO BAJO MÍNIMO
    print("\n3️⃣ Generando tickets de inventario bajo mínimo...")
    for i, inventario in enumerate(inventarios[:8]):
        if float(inventario.cantidad_actual) >= float(inventario.cantidad_minima):
            # Simular inventario bajo mínimo
            cantidad_minima = float(inventario.cantidad_minima)
            cantidad_actual = cantidad_minima * uniform(0.3, 0.9)  # 30-90% del mínimo
            diferencia = cantidad_minima - cantidad_actual
            porcentaje_faltante = (diferencia / cantidad_minima * 100) if cantidad_minima > 0 else 0
        
            item = inventario.item
            
            asunto = f"Inventario bajo mínimo - {item.nombre}"
            descripcion = (
                f"El inventario del item '{item.nombre}' está por debajo del mínimo de seguridad.\n\n"
                f"📦 SITUACIÓN ACTUAL:\n"
                f"• Cantidad actual: {cantidad_actual:.2f} {inventario.unidad}\n"
                f"• Cantidad mínima: {cantidad_minima:.2f} {inventario.unidad}\n"
                f"• Faltante: {diferencia:.2f} {inventario.unidad} ({porcentaje_faltante:.1f}%)\n\n"
                f"⚠️ ACCIÓN REQUERIDA:\n"
                f"Se requiere realizar un pedido urgente para reponer el stock.\n"
                f"Sin stock suficiente, se puede afectar:\n"
                f"- La preparación de menús programados\n"
                f"- La continuidad del servicio\n"
                f"- La calidad de los productos servidos\n\n"
            )
            
            if item.proveedor_autorizado:
                descripcion += f"Proveedor autorizado: {item.proveedor_autorizado.nombre}\n"
            
            descripcion += f"Inventario ID: {inventario.id}\nItem ID: {item.id}"
            
            prioridad = PrioridadTicket.URGENTE if porcentaje_faltante > 50 else PrioridadTicket.ALTA
            
            ticket = Ticket(
                cliente_id=None,
                tipo=TipoTicket.CONSULTA,
                asunto=asunto,
                descripcion=descripcion,
                estado=EstadoTicket.ABIERTO if i < 3 else choice([EstadoTicket.ABIERTO, EstadoTicket.EN_PROCESO]),
                prioridad=prioridad,
                inventario_id=inventario.id,
                proveedor_id=item.proveedor_autorizado_id if item.proveedor_autorizado else None,
                origen_modulo='inventario',
                auto_generado='true',
                fecha_creacion=datetime.now() - timedelta(days=randint(0, 3), hours=randint(0, 12))
            )
            
            db.session.add(ticket)
            tickets_creados.append(ticket)
            print(f"  ✓ Inventario bajo: {item.nombre} ({porcentaje_faltante:.1f}% faltante)")
    
    # 4. TICKETS DE CONSUMO EXCESIVO DE INGREDIENTES
    print("\n4️⃣ Generando tickets de consumo excesivo de ingredientes...")
    for i in range(4):
        if not items:
            break
        
        item = choice(items)
        inventario = db.session.query(Inventario).filter(Inventario.item_id == item.id).first()
        
        if inventario and programaciones:
            programacion = choice(programaciones)
            consumo_esperado = uniform(10, 30)
            consumo_real = consumo_esperado * uniform(1.25, 1.60)  # 25-60% más de lo esperado
            diferencia = consumo_real - consumo_esperado
            
            fecha_ticket = fecha_base - timedelta(days=randint(1, 4))
            
            asunto = f"Consumo excesivo de ingrediente - {item.nombre}"
            descripcion = (
                f"Se detectó consumo excesivo del ingrediente '{item.nombre}' "
                f"en el servicio de {programacion.tiempo_comida.value} "
                f"del {fecha_ticket.strftime('%d/%m/%Y')}.\n\n"
                f"📊 ANÁLISIS DE CONSUMO:\n"
                f"• Consumo esperado: {consumo_esperado:.2f} {item.unidad}\n"
                f"• Consumo real: {consumo_real:.2f} {item.unidad}\n"
                f"• Exceso: {diferencia:.2f} {item.unidad} ({(diferencia/consumo_esperado*100):.1f}% más)\n\n"
                f"⚠️ POSIBLES CAUSAS:\n"
                f"- Porciones más grandes de lo estándar\n"
                f"- Desperdicio en preparación\n"
                f"- Errores en medición\n"
                f"- Merma no registrada\n\n"
                f"Item ID: {item.id}\n"
                f"Programación ID: {programacion.id}"
            )
            
            ticket = Ticket(
                cliente_id=0,
                tipo=TipoTicket.QUEJA,
                asunto=asunto,
                descripcion=descripcion,
                estado=EstadoTicket.ABIERTO if i < 2 else EstadoTicket.EN_PROCESO,
                prioridad=PrioridadTicket.ALTA,
                programacion_id=programacion.id,
                inventario_id=inventario.id,
                origen_modulo='charola',
                auto_generado='true',
                fecha_creacion=datetime.combine(fecha_ticket, datetime.min.time()) + timedelta(hours=randint(15, 19))
            )
            
            db.session.add(ticket)
            tickets_creados.append(ticket)
            print(f"  ✓ Consumo excesivo: {item.nombre} ({(diferencia/consumo_esperado*100):.1f}% más)")
    
    # 5. TICKETS DE COSTOS MAYORES A LO ESPERADO
    print("\n5️⃣ Generando tickets de costos mayores a lo esperado...")
    for i in range(3):
        if not programaciones:
            break
        
        programacion = choice(programaciones)
        costo_esperado = uniform(800, 1500)
        costo_real = costo_esperado * uniform(1.20, 1.45)  # 20-45% más
        diferencia = costo_real - costo_esperado
        
        fecha_ticket = fecha_base - timedelta(days=randint(1, 5))
        
        asunto = f"Costos mayores a lo esperado - {programacion.tiempo_comida.value.capitalize()}"
        descripcion = (
            f"Los costos del servicio de {programacion.tiempo_comida.value} "
            f"del {fecha_ticket.strftime('%d/%m/%Y')} superaron lo esperado.\n\n"
            f"💰 ANÁLISIS DE COSTOS:\n"
            f"• Costo esperado: ${costo_esperado:.2f}\n"
            f"• Costo real: ${costo_real:.2f}\n"
            f"• Diferencia: ${diferencia:.2f} ({(diferencia/costo_esperado*100):.1f}% más)\n\n"
            f"⚠️ IMPACTO:\n"
            f"Este incremento en costos afecta la rentabilidad del servicio.\n"
            f"Posibles causas:\n"
            f"- Aumento en precios de proveedores\n"
            f"- Consumo mayor de ingredientes\n"
            f"- Mermas no contabilizadas\n"
            f"- Ineficiencias en preparación\n\n"
            f"Programación ID: {programacion.id}"
        )
        
        ticket = Ticket(
            cliente_id=0,
            tipo=TipoTicket.QUEJA,
            asunto=asunto,
            descripcion=descripcion,
            estado=EstadoTicket.ABIERTO if i < 1 else EstadoTicket.EN_PROCESO,
            prioridad=PrioridadTicket.ALTA,
            programacion_id=programacion.id,
            origen_modulo='charola',
            auto_generado='true',
            fecha_creacion=datetime.combine(fecha_ticket, datetime.min.time()) + timedelta(hours=randint(16, 20))
        )
        
        db.session.add(ticket)
        tickets_creados.append(ticket)
        print(f"  ✓ Costos mayores: {programacion.tiempo_comida.value} ({(diferencia/costo_esperado*100):.1f}% más)")
    
    # 6. TICKETS DE REPORTES FALTANTES
    print("\n6️⃣ Generando tickets de reportes faltantes...")
    for i in range(3):
        if not programaciones:
            break
        
        programacion = choice(programaciones)
        fecha_ticket = fecha_base - timedelta(days=randint(2, 5))
        
        asunto = f"Reporte faltante - {programacion.tiempo_comida.value.capitalize()} - {programacion.ubicacion}"
        descripcion = (
            f"No se ha ingresado el reporte de charolas para el servicio de {programacion.tiempo_comida.value} "
            f"del {fecha_ticket.strftime('%d/%m/%Y')} en {programacion.ubicacion}.\n\n"
            f"⏰ SITUACIÓN:\n"
            f"• Tiempo límite: 2 horas después del servicio\n"
            f"• Charolas planificadas: {programacion.charolas_planificadas}\n"
            f"• Charolas reportadas: 0\n\n"
            f"⚠️ IMPACTO:\n"
            f"Sin el reporte no se puede:\n"
            f"- Verificar consumo real vs planificado\n"
            f"- Calcular costos reales\n"
            f"- Identificar desviaciones\n"
            f"- Mejorar la planificación futura\n\n"
            f"Programación ID: {programacion.id}"
        )
        
        ticket = Ticket(
            cliente_id=0,
            tipo=TipoTicket.CONSULTA,
            asunto=asunto,
            descripcion=descripcion,
            estado=EstadoTicket.ABIERTO,
            prioridad=PrioridadTicket.MEDIA,
            programacion_id=programacion.id,
            origen_modulo='charola',
            auto_generado='true',
            fecha_creacion=datetime.combine(fecha_ticket, datetime.min.time()) + timedelta(hours=randint(15, 17))
        )
        
        db.session.add(ticket)
        tickets_creados.append(ticket)
        print(f"  ✓ Reporte faltante: {programacion.tiempo_comida.value}")
    
    # 7. TICKETS DE ITEMS INSUFICIENTES PARA PROGRAMACIÓN
    print("\n7️⃣ Generando tickets de items insuficientes...")
    for i in range(4):
        if not items or not proveedores or not programaciones:
            break
        
        item = choice(items)
        proveedor = choice(proveedores)
        programacion = choice(programaciones)
        
        cantidad_necesaria = uniform(50, 150)
        cantidad_actual = cantidad_necesaria * uniform(0.4, 0.7)  # 40-70% de lo necesario
        cantidad_faltante = cantidad_necesaria - cantidad_actual
        
        fecha_ticket = fecha_base - timedelta(days=randint(0, 2))
        
        asunto = f"Items insuficientes - {item.nombre}"
        descripcion = (
            f"Al programar el menú del {programacion.fecha_desde.strftime('%d/%m/%Y')} "
            f"se detectó que faltan items que requieren compra.\n\n"
            f"📦 ANÁLISIS DE STOCK:\n"
            f"• Item: {item.nombre}\n"
            f"• Cantidad necesaria: {cantidad_necesaria:.2f} {item.unidad}\n"
            f"• Cantidad actual: {cantidad_actual:.2f} {item.unidad}\n"
            f"• Cantidad faltante: {cantidad_faltante:.2f} {item.unidad} "
            f"({(cantidad_faltante/cantidad_necesaria*100):.1f}%)\n\n"
            f"⚠️ ACCIÓN REQUERIDA:\n"
            f"Se requiere realizar un pedido urgente al proveedor.\n"
            f"Sin este item no se puede completar la programación del menú.\n\n"
            f"Proveedor: {proveedor.nombre}\n"
            f"Programación ID: {programacion.id}\n"
            f"Item ID: {item.id}"
        )
        
        ticket = Ticket(
            cliente_id=None,
            tipo=TipoTicket.CONSULTA,
            asunto=asunto,
            descripcion=descripcion,
            estado=EstadoTicket.ABIERTO,
            prioridad=PrioridadTicket.ALTA,
            programacion_id=programacion.id,
            proveedor_id=proveedor.id,
            origen_modulo='proveedor',
            auto_generado='true',
            fecha_creacion=datetime.combine(fecha_ticket, datetime.min.time()) + timedelta(hours=randint(8, 12))
        )
        
        db.session.add(ticket)
        tickets_creados.append(ticket)
        print(f"  ✓ Items insuficientes: {item.nombre} ({(cantidad_faltante/cantidad_necesaria*100):.1f}% faltante)")
    
    # 8. TICKETS RESUELTOS (con respuestas)
    print("\n8️⃣ Generando tickets resueltos con respuestas...")
    tickets_resueltos = []
    for i, ticket in enumerate(tickets_creados[:5]):
        if ticket.estado == EstadoTicket.ABIERTO:
            ticket.estado = EstadoTicket.RESUELTO
            ticket.fecha_resolucion = ticket.fecha_creacion + timedelta(hours=randint(2, 24))
            
            # Generar respuesta según el tipo de ticket
            if 'Desviación' in ticket.asunto:
                ticket.respuesta = (
                    f"Se revisó la desviación y se identificó que fue causada por "
                    f"una mayor demanda de la esperada. Se ajustará la planificación "
                    f"para los próximos días similares."
                )
            elif 'Merma' in ticket.asunto:
                ticket.respuesta = (
                    f"Se investigó la merma excesiva y se encontró que fue causada por "
                    f"vencimiento de productos. Se implementarán controles de rotación "
                    f"de inventario más estrictos."
                )
            elif 'Inventario bajo' in ticket.asunto:
                ticket.respuesta = (
                    f"Se realizó un pedido urgente al proveedor. El stock será repuesto "
                    f"en las próximas 24 horas. Se recomienda ajustar el mínimo de seguridad."
                )
            else:
                ticket.respuesta = (
                    f"Ticket resuelto. Se tomaron las medidas correctivas necesarias."
                )
            
            tickets_resueltos.append(ticket)
            print(f"  ✓ Ticket resuelto: {ticket.asunto[:40]}...")
    
    # Guardar todos los tickets
    db.session.commit()
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE TICKETS GENERADOS")
    print("=" * 70)
    print(f"✅ Total tickets creados: {len(tickets_creados)}")
    
    # Estadísticas por tipo
    por_tipo = {}
    por_estado = {}
    por_prioridad = {}
    por_origen = {}
    
    for ticket in tickets_creados:
        tipo = ticket.tipo.value if ticket.tipo else 'desconocido'
        estado = ticket.estado.value if ticket.estado else 'desconocido'
        prioridad = ticket.prioridad.value if ticket.prioridad else 'desconocido'
        origen = ticket.origen_modulo or 'desconocido'
        
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
        por_estado[estado] = por_estado.get(estado, 0) + 1
        por_prioridad[prioridad] = por_prioridad.get(prioridad, 0) + 1
        por_origen[origen] = por_origen.get(origen, 0) + 1
    
    print(f"\n   Por tipo:")
    for tipo, cantidad in por_tipo.items():
        print(f"   • {tipo.capitalize()}: {cantidad}")
    
    print(f"\n   Por estado:")
    for estado, cantidad in por_estado.items():
        print(f"   • {estado.capitalize()}: {cantidad}")
    
    print(f"\n   Por prioridad:")
    for prioridad, cantidad in por_prioridad.items():
        print(f"   • {prioridad.capitalize()}: {cantidad}")
    
    print(f"\n   Por origen:")
    for origen, cantidad in por_origen.items():
        print(f"   • {origen.capitalize()}: {cantidad}")
    
    print("\n✅ Tickets mock generados exitosamente!")
    print("💡 Puedes verlos en: /tickets")
    
    return tickets_creados

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        try:
            tickets = generar_tickets_mock()
            print(f"\n✅ Proceso completado exitosamente!")
            print(f"🎫 Total: {len(tickets)} tickets generados")
        except Exception as e:
            import traceback
            print(f"\n❌ Error: {str(e)}")
            print(traceback.format_exc())
            db.session.rollback()
