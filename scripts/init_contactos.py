"""
Script para generar datos mock de contactos (proveedores y colaboradores).
"""
import sys
import os
from datetime import datetime
from random import choice, randint

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.contacto import Contacto, TipoContacto
from models.proveedor import Proveedor

def generar_contactos_mock():
    """Genera contactos mock (proveedores y colaboradores)."""
    print("=" * 70)
    print("GENERACIÓN DE CONTACTOS MOCK")
    print("=" * 70)
    print()
    
    # Verificar si ya hay contactos
    contactos_existentes = db.session.query(Contacto).count()
    if contactos_existentes > 0:
        print(f"⚠️  Ya existen {contactos_existentes} contactos en la base de datos.")
        print("   Agregando contactos adicionales...")
    
    # Obtener proveedores existentes
    proveedores = db.session.query(Proveedor).all()
    
    contactos_creados = []
    
    # Datos mock para proveedores
    proveedores_mock = [
        {
            'nombre': 'Juan Pérez',
            'email': 'juan.perez@proveedor-alimentos.com',
            'whatsapp': '+521234567890',
            'telefono': '+52 55 1234 5678',
            'cargo': 'Gerente de Ventas',
            'proyecto': 'Suministro de Alimentos',
            'tipo': TipoContacto.PROVEEDOR
        },
        {
            'nombre': 'María González',
            'email': 'maria.gonzalez@distribuidora.com',
            'whatsapp': '+521234567891',
            'telefono': '+52 55 2345 6789',
            'cargo': 'Coordinadora de Compras',
            'proyecto': 'Distribución de Productos',
            'tipo': TipoContacto.PROVEEDOR
        },
        {
            'nombre': 'Carlos Rodríguez',
            'email': 'carlos.rodriguez@carnes-premium.com',
            'whatsapp': '+521234567892',
            'telefono': '+52 55 3456 7890',
            'cargo': 'Director Comercial',
            'proyecto': 'Carnes y Proteínas',
            'tipo': TipoContacto.PROVEEDOR
        },
        {
            'nombre': 'Ana Martínez',
            'email': 'ana.martinez@verduras-frescas.com',
            'whatsapp': '+521234567893',
            'telefono': '+52 55 4567 8901',
            'cargo': 'Ejecutiva de Cuentas',
            'proyecto': 'Verduras y Hortalizas',
            'tipo': TipoContacto.PROVEEDOR
        },
        {
            'nombre': 'Roberto Sánchez',
            'email': 'roberto.sanchez@bebidas.com',
            'whatsapp': '+521234567894',
            'telefono': '+52 55 5678 9012',
            'cargo': 'Gerente Regional',
            'proyecto': 'Bebidas y Líquidos',
            'tipo': TipoContacto.PROVEEDOR
        },
        {
            'nombre': 'Laura Fernández',
            'email': 'laura.fernandez@lacteos.com',
            'whatsapp': '+521234567895',
            'telefono': '+52 55 6789 0123',
            'cargo': 'Supervisora de Ventas',
            'proyecto': 'Lácteos y Derivados',
            'tipo': TipoContacto.PROVEEDOR
        },
        {
            'nombre': 'Miguel Torres',
            'email': 'miguel.torres@granos.com',
            'whatsapp': '+521234567896',
            'telefono': '+52 55 7890 1234',
            'cargo': 'Representante Comercial',
            'proyecto': 'Granos y Cereales',
            'tipo': TipoContacto.PROVEEDOR
        },
        {
            'nombre': 'Patricia López',
            'email': 'patricia.lopez@especias.com',
            'whatsapp': '+521234567897',
            'telefono': '+52 55 8901 2345',
            'cargo': 'Coordinadora de Exportaciones',
            'proyecto': 'Especias y Condimentos',
            'tipo': TipoContacto.PROVEEDOR
        }
    ]
    
    # Datos mock para colaboradores
    colaboradores_mock = [
        {
            'nombre': 'Sofía Ramírez',
            'email': 'sofia.ramirez@restaurante.com',
            'whatsapp': '+521234567898',
            'telefono': '+52 55 9012 3456',
            'cargo': 'Chef Ejecutivo',
            'proyecto': 'Cocina Principal',
            'tipo': TipoContacto.COLABORADOR
        },
        {
            'nombre': 'Diego Morales',
            'email': 'diego.morales@restaurante.com',
            'whatsapp': '+521234567899',
            'telefono': '+52 55 0123 4567',
            'cargo': 'Gerente de Operaciones',
            'proyecto': 'Administración',
            'tipo': TipoContacto.COLABORADOR
        },
        {
            'nombre': 'Valentina Castro',
            'email': 'valentina.castro@restaurante.com',
            'whatsapp': '+521234567900',
            'telefono': '+52 55 1234 5678',
            'cargo': 'Supervisora de Inventario',
            'proyecto': 'Logística',
            'tipo': TipoContacto.COLABORADOR
        },
        {
            'nombre': 'Andrés Herrera',
            'email': 'andres.herrera@restaurante.com',
            'whatsapp': '+521234567901',
            'telefono': '+52 55 2345 6789',
            'cargo': 'Coordinador de Compras',
            'proyecto': 'Compras',
            'tipo': TipoContacto.COLABORADOR
        }
    ]
    
    # Crear contactos de proveedores
    print("\n1️⃣ Creando contactos de proveedores...")
    for i, datos in enumerate(proveedores_mock):
        proveedor_id = None
        if i < len(proveedores):
            proveedor_id = proveedores[i].id
        
        contacto = Contacto(
            nombre=datos['nombre'],
            email=datos['email'],
            whatsapp=datos['whatsapp'],
            telefono=datos['telefono'],
            cargo=datos['cargo'],
            proyecto=datos['proyecto'],
            tipo=datos['tipo'],
            proveedor_id=proveedor_id,
            activo=True,
            notas=f"Contacto creado automáticamente - {datos['cargo']}"
        )
        
        db.session.add(contacto)
        contactos_creados.append(contacto)
        print(f"  ✓ {datos['nombre']} - {datos['cargo']}")
    
    # Crear contactos de colaboradores
    print("\n2️⃣ Creando contactos de colaboradores...")
    for datos in colaboradores_mock:
        contacto = Contacto(
            nombre=datos['nombre'],
            email=datos['email'],
            whatsapp=datos['whatsapp'],
            telefono=datos['telefono'],
            cargo=datos['cargo'],
            proyecto=datos['proyecto'],
            tipo=datos['tipo'],
            proveedor_id=None,
            activo=True,
            notas=f"Colaborador - {datos['cargo']}"
        )
        
        db.session.add(contacto)
        contactos_creados.append(contacto)
        print(f"  ✓ {datos['nombre']} - {datos['cargo']}")
    
    # Guardar todos los contactos
    db.session.commit()
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE CONTACTOS GENERADOS")
    print("=" * 70)
    print(f"✅ Total contactos creados: {len(contactos_creados)}")
    
    # Estadísticas por tipo
    proveedores_count = sum(1 for c in contactos_creados if c.tipo == TipoContacto.PROVEEDOR)
    colaboradores_count = sum(1 for c in contactos_creados if c.tipo == TipoContacto.COLABORADOR)
    
    print(f"   • Proveedores: {proveedores_count}")
    print(f"   • Colaboradores: {colaboradores_count}")
    
    # Estadísticas por canal
    con_email = sum(1 for c in contactos_creados if c.email)
    con_whatsapp = sum(1 for c in contactos_creados if c.whatsapp)
    
    print(f"\n   • Con Email: {con_email}")
    print(f"   • Con WhatsApp: {con_whatsapp}")
    
    print("\n✅ Contactos mock generados exitosamente!")
    print("💡 Puedes verlos en: /contactos")
    
    return contactos_creados

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        try:
            contactos = generar_contactos_mock()
            print(f"\n✅ Proceso completado exitosamente!")
            print(f"📧 Total: {len(contactos)} contactos generados")
        except Exception as e:
            import traceback
            print(f"\n❌ Error: {str(e)}")
            print(traceback.format_exc())
            db.session.rollback()
