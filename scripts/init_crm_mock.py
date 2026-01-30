"""
Script maestro para generar datos mock de CRM (contactos y notificaciones).
Ejecuta ambos scripts en secuencia.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def init_crm_mock():
    """Inicializa datos mock de CRM."""
    print("=" * 70)
    print("GENERACIÓN DE DATOS MOCK - CRM")
    print("=" * 70)
    print()
    
    app = create_app()
    
    with app.app_context():
        # 1. Generar contactos
        print("\n" + "=" * 70)
        print("PASO 1: Generando Contactos Mock")
        print("=" * 70)
        try:
            from scripts.init_contactos import generar_contactos_mock
            contactos = generar_contactos_mock()
            print(f"\n✅ {len(contactos)} contactos procesados")
        except Exception as e:
            import traceback
            print(f"\n⚠️  Error generando contactos: {str(e)}")
            print(traceback.format_exc())
            contactos = []
        
        # 2. Generar notificaciones
        print("\n" + "=" * 70)
        print("PASO 2: Generando Notificaciones Mock")
        print("=" * 70)
        try:
            from scripts.init_notificaciones import generar_notificaciones_mock
            notificaciones = generar_notificaciones_mock()
            print(f"\n✅ {len(notificaciones)} notificaciones procesadas")
        except Exception as e:
            import traceback
            print(f"\n⚠️  Error generando notificaciones: {str(e)}")
            print(traceback.format_exc())
            notificaciones = []
        
        # 3. Generar tickets
        print("\n" + "=" * 70)
        print("PASO 3: Generando Tickets Mock")
        print("=" * 70)
        try:
            from scripts.init_tickets import generar_tickets_mock
            tickets = generar_tickets_mock()
            print(f"\n✅ {len(tickets)} tickets procesados")
        except Exception as e:
            import traceback
            print(f"\n⚠️  Error generando tickets: {str(e)}")
            print(traceback.format_exc())
            tickets = []
        
        print("\n" + "=" * 70)
        print("✅ PROCESO COMPLETADO")
        print("=" * 70)
        print(f"📇 Contactos: {len(contactos)}")
        print(f"📧 Notificaciones: {len(notificaciones)}")
        print(f"🎫 Tickets: {len(tickets)}")
        print("\n💡 Puedes ver los datos en:")
        print("   • Contactos: /contactos")
        print("   • Notificaciones: /notificaciones")
        print("   • Tickets: /tickets")

if __name__ == '__main__':
    try:
        init_crm_mock()
    except Exception as e:
        import traceback
        print(f"\n❌ Error crítico: {str(e)}")
        print(traceback.format_exc())
