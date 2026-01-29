"""
Servicio de Chat AI con integración a OpenAI.
"""
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
import os
import json

from models import Conversacion, Mensaje
from models.chat import TipoMensaje
from config import Config

class ChatService:
    """Servicio para gestión de chat AI."""
    
    def __init__(self):
        """Inicializa el servicio de chat."""
        self.api_key = Config.OPENAI_API_KEY
        self.model = Config.OPENAI_MODEL or "gpt-3.5-turbo"
        self.base_url = Config.OPENAI_BASE_URL or "https://api.openai.com/v1"
    
    def _obtener_cliente_openai(self):
        """Obtiene el cliente de OpenAI."""
        try:
            import openai
            if self.api_key:
                openai.api_key = self.api_key
                if self.base_url != "https://api.openai.com/v1":
                    openai.api_base = self.base_url
            return openai
        except ImportError:
            raise Exception("OpenAI no está instalado. Ejecuta: pip install openai")
    
    def crear_conversacion(
        self,
        db: Session,
        titulo: Optional[str] = None,
        usuario_id: Optional[int] = None,
        contexto_modulo: Optional[str] = None
    ) -> Conversacion:
        """
        Crea una nueva conversación.
        
        Args:
            db: Sesión de base de datos
            titulo: Título de la conversación
            usuario_id: ID del usuario
            contexto_modulo: Módulo del ERP (crm, logistica, etc.)
            
        Returns:
            Conversación creada
        """
        conversacion = Conversacion(
            titulo=titulo or f"Conversación {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            usuario_id=usuario_id,
            contexto_modulo=contexto_modulo
        )
        
        db.add(conversacion)
        db.commit()
        db.refresh(conversacion)
        return conversacion
    
    def obtener_conversacion(self, db: Session, conversacion_id: int) -> Optional[Conversacion]:
        """Obtiene una conversación por ID."""
        return db.query(Conversacion).filter(Conversacion.id == conversacion_id).first()
    
    def listar_conversaciones(
        self,
        db: Session,
        usuario_id: Optional[int] = None,
        activa: Optional[bool] = True,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversacion]:
        """
        Lista conversaciones.
        
        Args:
            db: Sesión de base de datos
            usuario_id: Filtrar por usuario
            activa: Filtrar por estado activo
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de conversaciones
        """
        query = db.query(Conversacion)
        
        if usuario_id is not None:
            query = query.filter(Conversacion.usuario_id == usuario_id)
        
        if activa is not None:
            query = query.filter(Conversacion.activa == activa)
        
        return query.order_by(Conversacion.fecha_actualizacion.desc()).offset(skip).limit(limit).all()
    
    def enviar_mensaje(
        self,
        db: Session,
        conversacion_id: int,
        contenido: str,
        usuario_id: Optional[int] = None
    ) -> Dict:
        """
        Envía un mensaje y obtiene respuesta del AI.
        
        Args:
            db: Sesión de base de datos
            conversacion_id: ID de la conversación
            contenido: Contenido del mensaje del usuario
            usuario_id: ID del usuario
            
        Returns:
            Diccionario con el mensaje del usuario y la respuesta del AI
        """
        # Obtener conversación
        conversacion = self.obtener_conversacion(db, conversacion_id)
        if not conversacion:
            raise ValueError("Conversación no encontrada")
        
        # Guardar mensaje del usuario
        mensaje_usuario = Mensaje(
            conversacion_id=conversacion_id,
            tipo=TipoMensaje.USUARIO,
            contenido=contenido
        )
        db.add(mensaje_usuario)
        db.flush()
        
        # Obtener historial de mensajes
        historial = db.query(Mensaje).filter(
            Mensaje.conversacion_id == conversacion_id
        ).order_by(Mensaje.fecha_envio.asc()).all()
        
        # Construir contexto del sistema basado en el módulo
        sistema_prompt = self._construir_prompt_sistema(conversacion.contexto_modulo)
        
        # Preparar mensajes para OpenAI
        mensajes_openai = [{"role": "system", "content": sistema_prompt}]
        
        for msg in historial:
            if msg.tipo == TipoMensaje.USUARIO:
                mensajes_openai.append({"role": "user", "content": msg.contenido})
            elif msg.tipo == TipoMensaje.ASISTENTE:
                mensajes_openai.append({"role": "assistant", "content": msg.contenido})
        
        # Agregar el nuevo mensaje del usuario
        mensajes_openai.append({"role": "user", "content": contenido})
        
        # Llamar a OpenAI
        try:
            respuesta_ai = self._llamar_openai(mensajes_openai)
            respuesta_contenido = respuesta_ai.get('content', '')
            tokens_usados = respuesta_ai.get('tokens', None)
        except Exception as e:
            respuesta_contenido = f"Error al obtener respuesta del AI: {str(e)}"
            tokens_usados = None
        
        # Guardar respuesta del asistente
        mensaje_asistente = Mensaje(
            conversacion_id=conversacion_id,
            tipo=TipoMensaje.ASISTENTE,
            contenido=respuesta_contenido,
            tokens_usados=tokens_usados
        )
        db.add(mensaje_asistente)
        
        # Actualizar fecha de actualización de la conversación
        conversacion.fecha_actualizacion = datetime.utcnow()
        if not conversacion.titulo or conversacion.titulo.startswith("Conversación"):
            # Generar título automático del primer mensaje
            conversacion.titulo = contenido[:50] + "..." if len(contenido) > 50 else contenido
        
        db.commit()
        db.refresh(mensaje_usuario)
        db.refresh(mensaje_asistente)
        
        return {
            'mensaje_usuario': mensaje_usuario.to_dict(),
            'mensaje_asistente': mensaje_asistente.to_dict()
        }
    
    def _construir_prompt_sistema(self, contexto_modulo: Optional[str] = None) -> str:
        """
        Construye el prompt del sistema basado en el contexto del módulo.
        
        Args:
            contexto_modulo: Módulo del ERP
            
        Returns:
            Prompt del sistema
        """
        base_prompt = """Eres un asistente virtual experto en sistemas ERP para restaurantes. 
Ayudas a los usuarios con consultas sobre gestión de restaurantes, inventario, facturas, pedidos, proveedores y más.
Responde de manera clara, concisa y profesional en español."""
        
        modulos_contexto = {
            'crm': "Te especializas en gestión de relaciones con clientes, proveedores, tickets y notificaciones.",
            'logistica': "Te especializas en gestión de inventario, items, facturas, pedidos y requerimientos.",
            'contabilidad': "Te especializas en contabilidad, facturas, cuentas contables y reportes financieros.",
            'planificacion': "Te especializas en planificación de menús, recetas y programación.",
            'reportes': "Te especializas en reportes de charolas, mermas y análisis de datos.",
        }
        
        if contexto_modulo and contexto_modulo.lower() in modulos_contexto:
            base_prompt += f"\n\n{modulos_contexto[contexto_modulo.lower()]}"
        
        return base_prompt
    
    def _llamar_openai(self, mensajes: List[Dict]) -> Dict:
        """
        Llama a la API de OpenAI.
        
        Args:
            mensajes: Lista de mensajes en formato OpenAI
            
        Returns:
            Diccionario con la respuesta y tokens usados
        """
        if not self.api_key:
            return {
                'content': 'Error: No se ha configurado OPENAI_API_KEY. Por favor, configura tu API key de OpenAI en las variables de entorno.',
                'tokens': None
            }
        
        try:
            import openai
            
            # Configurar API key
            openai.api_key = self.api_key
            if self.base_url != "https://api.openai.com/v1":
                openai.api_base = self.base_url
            
            # Llamar a la API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=mensajes,
                temperature=0.7,
                max_tokens=1000
            )
            
            return {
                'content': response.choices[0].message.content,
                'tokens': response.usage.total_tokens if hasattr(response, 'usage') else None
            }
        except Exception as e:
            # Si falla, intentar con requests directamente
            try:
                import requests
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": self.model,
                    "messages": mensajes,
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        'content': result['choices'][0]['message']['content'],
                        'tokens': result.get('usage', {}).get('total_tokens')
                    }
                else:
                    return {
                        'content': f'Error al llamar a OpenAI: {response.status_code} - {response.text}',
                        'tokens': None
                    }
            except Exception as e2:
                return {
                    'content': f'Error al conectar con OpenAI: {str(e2)}',
                    'tokens': None
                }
    
    def eliminar_conversacion(self, db: Session, conversacion_id: int) -> bool:
        """
        Elimina una conversación (marca como inactiva).
        
        Args:
            db: Sesión de base de datos
            conversacion_id: ID de la conversación
            
        Returns:
            True si se eliminó correctamente
        """
        conversacion = self.obtener_conversacion(db, conversacion_id)
        if not conversacion:
            return False
        
        conversacion.activa = False
        db.commit()
        return True

# Instancia global del servicio
chat_service = ChatService()
