"""
Script de prueba para verificar la eliminación de conversaciones.
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from models import db
from modules.chat.chat_service import chat_service

def main():
    """Prueba la eliminación de conversaciones."""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("PRUEBA DE ELIMINACIÓN DE CONVERSACIONES")
        print("=" * 70)
        print()
        
        # Listar conversaciones activas
        print("📋 Conversaciones activas:")
        conversaciones = chat_service.listar_conversaciones(
            db.session,
            activa=True,
            limit=10
        )
        
        if not conversaciones:
            print("  No hay conversaciones activas para eliminar.")
            print()
            print("💡 Crea una conversación primero desde el chat.")
            return
        
        for conv in conversaciones:
            print(f"  - ID: {conv.id}, Título: {conv.titulo}, Activa: {conv.activa}")
        
        print()
        
        # Intentar eliminar la primera conversación
        if conversaciones:
            conv_id = conversaciones[0].id
            print(f"🗑️  Intentando eliminar conversación ID: {conv_id}")
            
            try:
                eliminada = chat_service.eliminar_conversacion(db.session, conv_id)
                
                if eliminada:
                    db.session.commit()
                    print(f"✅ Conversación {conv_id} eliminada correctamente")
                    
                    # Verificar que esté inactiva
                    conv_verificada = chat_service.obtener_conversacion(db.session, conv_id)
                    if conv_verificada:
                        print(f"   Estado después de eliminar: activa={conv_verificada.activa}")
                    else:
                        print(f"   ⚠️  Conversación no encontrada después de eliminar")
                else:
                    print(f"❌ No se pudo eliminar la conversación {conv_id}")
                    
            except Exception as e:
                print(f"❌ Error al eliminar conversación: {str(e)}")
                import traceback
                traceback.print_exc()
                db.session.rollback()
        
        print()
        print("=" * 70)

if __name__ == '__main__':
    main()
