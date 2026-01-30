"""
Script para generar conversaciones mock operativas:
- Colaboradores enviando facturas por OCR (WhatsApp/Email)
- Colaboradores reportando salidas de bodega por WhatsApp
"""
import sys
import os
from datetime import datetime, timedelta
from random import choice, randint, uniform

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.conversacion_contacto import ConversacionContacto, TipoMensajeContacto, DireccionMensaje
from models.contacto import Contacto, TipoContacto
from models.factura import Factura, EstadoFactura, TipoFactura
from models.inventario import Inventario
from models.item import Item

def generar_conversaciones_operativas():
    """Genera conversaciones mock operativas de colaboradores."""
    print("=" * 70)
    print("GENERACIÓN DE CONVERSACIONES OPERATIVAS MOCK")
    print("=" * 70)
    print()
    
    # Obtener colaboradores existentes
    colaboradores = db.session.query(Contacto).filter(
        Contacto.tipo == TipoContacto.COLABORADOR,
        Contacto.activo == True
    ).all()
    
    if not colaboradores:
        print("⚠️  No hay colaboradores activos. Creando colaboradores de ejemplo...")
        colaboradores = crear_colaboradores_ejemplo()
    
    print(f"✓ Encontrados {len(colaboradores)} colaboradores activos")
    
    # Obtener datos necesarios
    facturas = db.session.query(Factura).limit(10).all()
    items = db.session.query(Item).filter(Item.activo == True).limit(15).all()
    inventarios = db.session.query(Inventario).limit(10).all()
    
    conversaciones_creadas = []
    
    # 1. CONVERSACIONES DE FACTURAS ENVIADAS POR OCR (WhatsApp)
    print("\n1️⃣ Generando conversaciones de facturas enviadas por OCR (WhatsApp)...")
    
    mensajes_facturas_ocr = [
        {
            'contenido': 'Hola! 📸 Acabo de recibir una factura del proveedor. La estoy enviando por WhatsApp para que la procesen con OCR.\n\nProveedor: Distribuidora Alimentos S.A.\nMonto: $1,245.50\nFecha: Hoy\n\nAdjunto la foto de la factura.',
            'contexto': 'factura_ocr_whatsapp'
        },
        {
            'contenido': 'Buenos días! 📄 Tengo una factura nueva que necesito que procesen:\n\n• Proveedor: Carnicería El Buen Corte\n• Número: FAC-2024-089\n• Total: $856.30\n• Items: Pollo, Carne de res\n\nEnviando imagen de la factura ahora.',
            'contexto': 'factura_ocr_whatsapp'
        },
        {
            'contenido': 'Hola equipo! 📷 Factura recibida:\n\nProveedor: Bebidas y Licores del Ecuador\nFactura #: FAC-2024-156\nMonto: $2,150.00\nFecha recepción: Hoy 10:30 AM\n\nLa foto está adjunta. Por favor procesar con OCR.',
            'contexto': 'factura_ocr_whatsapp'
        },
        {
            'contenido': 'Factura nueva para procesar:\n\n📋 Detalles:\n- Proveedor: Lácteos Frescos del Valle\n- Número: FAC-2024-201\n- Total: $1,890.75\n- Items: Leche, Queso, Yogurt\n\nAdjunto imagen para OCR.',
            'contexto': 'factura_ocr_whatsapp'
        },
        {
            'contenido': 'Hola! 📸 Factura recibida de Suministros de Limpieza Pro:\n\n• Número: FAC-2024-234\n• Monto: $456.20\n• Fecha: Hoy\n• Concepto: Artículos de limpieza\n\nEnviando foto para procesamiento OCR.',
            'contexto': 'factura_ocr_whatsapp'
        }
    ]
    
    for i, mensaje_data in enumerate(mensajes_facturas_ocr):
        colaborador = choice(colaboradores)
        fecha_envio = datetime.now() - timedelta(hours=randint(1, 48))
        
        conversacion = ConversacionContacto(
            contacto_id=colaborador.id,
            tipo_mensaje=TipoMensajeContacto.WHATSAPP,
            direccion=DireccionMensaje.RECIBIDO,  # Recibido del colaborador
            contenido=mensaje_data['contenido'],
            mensaje_id_externo=f'WA_{randint(100000, 999999)}',
            estado='leido',
            fecha_envio=fecha_envio,
            fecha_creacion=fecha_envio
        )
        
        db.session.add(conversacion)
        conversaciones_creadas.append(conversacion)
        print(f"  ✓ WhatsApp recibido de {colaborador.nombre}: Factura OCR")
    
    # 2. CONVERSACIONES DE FACTURAS ENVIADAS POR EMAIL CON OCR
    print("\n2️⃣ Generando conversaciones de facturas enviadas por Email con OCR...")
    
    mensajes_facturas_email = [
        {
            'asunto': 'Factura nueva - Procesar con OCR',
            'contenido': 'Buenos días,\n\nHe recibido una nueva factura del proveedor que necesita ser procesada:\n\n• Proveedor: Distribuidora Alimentos S.A.\n• Número de factura: FAC-2024-089\n• Monto total: $1,245.50\n• Fecha de emisión: 28/01/2026\n• Items principales: Verduras, frutas, lácteos\n\nAdjunto la imagen escaneada de la factura para procesamiento OCR.\n\nPor favor confirmar recepción.\n\nSaludos,\n{nombre_colaborador}'
        },
        {
            'asunto': 'Factura para revisión - OCR',
            'contenido': 'Hola equipo,\n\nNueva factura recibida:\n\n📋 Información:\n- Proveedor: Carnicería El Buen Corte\n- Factura #: FAC-2024-156\n- Total: $856.30\n- Fecha recepción: 29/01/2026\n- Concepto: Carnes y embutidos\n\nAdjunto la factura escaneada. Por favor procesar con OCR y revisar.\n\nGracias,\n{nombre_colaborador}'
        },
        {
            'asunto': 'Factura adjunta - Requiere procesamiento OCR',
            'contenido': 'Buen día,\n\nFactura nueva del proveedor:\n\n• Proveedor: Bebidas y Licores del Ecuador\n• Número: FAC-2024-201\n• Monto: $2,150.00\n• Fecha: 30/01/2026\n• Items: Bebidas gaseosas, jugos, licores\n\nLa imagen de la factura está adjunta. Necesita procesamiento OCR.\n\nQuedo atento a confirmación.\n\nSaludos cordiales,\n{nombre_colaborador}'
        }
    ]
    
    for mensaje_data in mensajes_facturas_email:
        colaborador = choice(colaboradores)
        fecha_envio = datetime.now() - timedelta(hours=randint(2, 72))
        
        contenido = mensaje_data['contenido'].format(nombre_colaborador=colaborador.nombre)
        
        conversacion = ConversacionContacto(
            contacto_id=colaborador.id,
            tipo_mensaje=TipoMensajeContacto.EMAIL,
            direccion=DireccionMensaje.RECIBIDO,  # Recibido del colaborador
            asunto=mensaje_data['asunto'],
            contenido=contenido,
            mensaje_id_externo=f'EMAIL_{randint(100000, 999999)}',
            estado='leido',
            fecha_envio=fecha_envio,
            fecha_creacion=fecha_envio
        )
        
        db.session.add(conversacion)
        conversaciones_creadas.append(conversacion)
        print(f"  ✓ Email recibido de {colaborador.nombre}: Factura OCR")
    
    # 3. CONVERSACIONES DE SALIDAS DE BODEGA REPORTADAS POR WHATSAPP
    print("\n3️⃣ Generando conversaciones de salidas de bodega reportadas por WhatsApp...")
    
    # Generar mensajes realistas de salidas de bodega
    for i in range(8):
        colaborador = choice(colaboradores)
        item = choice(items) if items else None
        inventario = choice(inventarios) if inventarios else None
        
        if item and inventario:
            cantidad_salida = randint(5, 50)
            fecha_salida = datetime.now() - timedelta(hours=randint(1, 24))
            
            mensajes_salidas = [
                f'📦 Salida de bodega reportada:\n\n• Item: {item.nombre}\n• Cantidad: {cantidad_salida} {item.unidad}\n• Hora: {fecha_salida.strftime("%H:%M")}\n• Motivo: Salida para producción\n• Responsable: {colaborador.nombre}\n\nConfirmado ✅',
                f'Buen día! Reportando salida:\n\n📋 Detalles:\n- Producto: {item.nombre}\n- Cantidad retirada: {cantidad_salida} {item.unidad}\n- Fecha/hora: {fecha_salida.strftime("%d/%m/%Y %H:%M")}\n- Destino: Cocina principal\n- Autorizado por: {colaborador.nombre}\n\nSalida registrada correctamente.',
                f'Salida de inventario:\n\n• Item: {item.nombre}\n• Cantidad: {cantidad_salida} {item.unidad}\n• Stock antes: {float(inventario.cantidad_actual) + cantidad_salida:.2f}\n• Stock después: {inventario.cantidad_actual:.2f}\n• Hora: {fecha_salida.strftime("%H:%M")}\n\nReporte completado ✅',
                f'📤 Reporte de salida:\n\nProducto: {item.nombre}\nCantidad: {cantidad_salida} {item.unidad}\nFecha: {fecha_salida.strftime("%d/%m/%Y")}\nHora: {fecha_salida.strftime("%H:%M")}\nÁrea destino: Producción\n\nRegistrado en sistema.',
                f'Salida de bodega:\n\n• {item.nombre}: {cantidad_salida} {item.unidad}\n• Hora: {fecha_salida.strftime("%H:%M")}\n• Responsable: {colaborador.nombre}\n• Observaciones: Salida normal para servicio\n\n✅ Confirmado'
            ]
            
            contenido = choice(mensajes_salidas)
        else:
            # Mensaje genérico si no hay items
            contenido = f'📦 Reporte de salida de bodega:\n\n• Hora: {datetime.now().strftime("%H:%M")}\n• Responsable: {colaborador.nombre}\n• Motivo: Salida para producción\n\nRegistrado ✅'
        
        fecha_envio = datetime.now() - timedelta(hours=randint(1, 24))
        
        conversacion = ConversacionContacto(
            contacto_id=colaborador.id,
            tipo_mensaje=TipoMensajeContacto.WHATSAPP,
            direccion=DireccionMensaje.RECIBIDO,  # Recibido del colaborador
            contenido=contenido,
            mensaje_id_externo=f'WA_SALIDA_{randint(100000, 999999)}',
            estado='leido',
            fecha_envio=fecha_envio,
            fecha_creacion=fecha_envio
        )
        
        db.session.add(conversacion)
        conversaciones_creadas.append(conversacion)
        print(f"  ✓ WhatsApp recibido de {colaborador.nombre}: Salida de bodega")
    
    # 4. CONVERSACIONES DE ACTUALIZACIONES DE INVENTARIO (WhatsApp)
    print("\n4️⃣ Generando conversaciones de actualizaciones de inventario...")
    
    for i in range(5):
        colaborador = choice(colaboradores)
        item = choice(items) if items else None
        inventario = choice(inventarios) if inventarios else None
        
        if item and inventario:
            cantidad_actual = float(inventario.cantidad_actual)
            cantidad_minima = float(inventario.cantidad_minima)
            
            mensajes_inventario = [
                f'📊 Actualización de inventario:\n\n• Item: {item.nombre}\n• Stock actual: {cantidad_actual:.2f} {item.unidad}\n• Stock mínimo: {cantidad_minima:.2f} {item.unidad}\n• Estado: {"⚠️ Bajo mínimo" if cantidad_actual < cantidad_minima else "✅ Normal"}\n\nActualizado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                f'Inventario actualizado:\n\n{item.nombre}:\n- Actual: {cantidad_actual:.2f} {item.unidad}\n- Mínimo: {cantidad_minima:.2f} {item.unidad}\n- Diferencia: {cantidad_actual - cantidad_minima:.2f} {item.unidad}\n\nReporte: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                f'✅ Verificación de inventario:\n\n• {item.nombre}\n• Cantidad disponible: {cantidad_actual:.2f} {item.unidad}\n• Nivel mínimo requerido: {cantidad_minima:.2f} {item.unidad}\n\n{"⚠️ Requiere reposición" if cantidad_actual < cantidad_minima else "✅ Stock suficiente"}'
            ]
            
            contenido = choice(mensajes_inventario)
        else:
            contenido = f'📊 Actualización de inventario realizada.\n\nFecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}\nResponsable: {colaborador.nombre}\n\n✅ Procesado'
        
        fecha_envio = datetime.now() - timedelta(hours=randint(2, 48))
        
        conversacion = ConversacionContacto(
            contacto_id=colaborador.id,
            tipo_mensaje=TipoMensajeContacto.WHATSAPP,
            direccion=DireccionMensaje.RECIBIDO,
            contenido=contenido,
            mensaje_id_externo=f'WA_INV_{randint(100000, 999999)}',
            estado='leido',
            fecha_envio=fecha_envio,
            fecha_creacion=fecha_envio
        )
        
        db.session.add(conversacion)
        conversaciones_creadas.append(conversacion)
        print(f"  ✓ WhatsApp recibido de {colaborador.nombre}: Actualización inventario")
    
    # 5. CONVERSACIONES DE CONFIRMACIÓN DE RECEPCIÓN DE FACTURAS (Email)
    print("\n5️⃣ Generando conversaciones de confirmación de recepción de facturas...")
    
    for factura in facturas[:3]:
        colaborador = choice(colaboradores)
        fecha_envio = datetime.now() - timedelta(hours=randint(1, 24))
        
        contenido = f'Buen día,\n\nConfirmo la recepción y procesamiento de la siguiente factura:\n\n• Número: {factura.numero_factura}\n• Proveedor: {factura.proveedor.nombre if factura.proveedor else "N/A"}\n• Monto: ${factura.total:.2f}\n• Estado: {factura.estado.value if factura.estado else "N/A"}\n• Fecha procesamiento: {fecha_envio.strftime("%d/%m/%Y %H:%M")}\n\nLa factura ha sido procesada correctamente mediante OCR y está disponible en el sistema.\n\nSaludos,\n{colaborador.nombre}'
        
        conversacion = ConversacionContacto(
            contacto_id=colaborador.id,
            tipo_mensaje=TipoMensajeContacto.EMAIL,
            direccion=DireccionMensaje.RECIBIDO,
            asunto=f'Confirmación: Factura {factura.numero_factura} procesada',
            contenido=contenido,
            mensaje_id_externo=f'EMAIL_CONF_{randint(100000, 999999)}',
            estado='leido',
            fecha_envio=fecha_envio,
            fecha_creacion=fecha_envio
        )
        
        db.session.add(conversacion)
        conversaciones_creadas.append(conversacion)
        print(f"  ✓ Email recibido de {colaborador.nombre}: Confirmación factura {factura.numero_factura}")
    
    db.session.commit()
    print(f"\n✅ Total conversaciones operativas creadas: {len(conversaciones_creadas)}")
    return conversaciones_creadas

def crear_colaboradores_ejemplo():
    """Crea colaboradores de ejemplo si no existen."""
    colaboradores_data = [
        {
            'nombre': 'María González',
            'email': 'maria.gonzalez@empresa.com',
            'whatsapp': '+593 99 123-4567',
            'tipo': TipoContacto.COLABORADOR,
            'cargo': 'Supervisora de Bodega',
            'activo': True
        },
        {
            'nombre': 'Carlos Rodríguez',
            'email': 'carlos.rodriguez@empresa.com',
            'whatsapp': '+593 99 234-5678',
            'tipo': TipoContacto.COLABORADOR,
            'cargo': 'Auxiliar de Logística',
            'activo': True
        },
        {
            'nombre': 'Ana Martínez',
            'email': 'ana.martinez@empresa.com',
            'whatsapp': '+593 99 345-6789',
            'tipo': TipoContacto.COLABORADOR,
            'cargo': 'Coordinadora de Compras',
            'activo': True
        },
        {
            'nombre': 'Luis Fernández',
            'email': 'luis.fernandez@empresa.com',
            'whatsapp': '+593 99 456-7890',
            'tipo': TipoContacto.COLABORADOR,
            'cargo': 'Encargado de Inventario',
            'activo': True
        }
    ]
    
    colaboradores_creados = []
    for colab_data in colaboradores_data:
        existing = Contacto.query.filter_by(email=colab_data['email']).first()
        if not existing:
            colaborador = Contacto(**colab_data)
            db.session.add(colaborador)
            colaboradores_creados.append(colaborador)
        else:
            colaboradores_creados.append(existing)
    
    db.session.commit()
    return colaboradores_creados

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        conversaciones = generar_conversaciones_operativas()
        print(f"\n{'='*70}")
        print(f"✅ Proceso completado: {len(conversaciones)} conversaciones operativas creadas")
        print(f"{'='*70}")
