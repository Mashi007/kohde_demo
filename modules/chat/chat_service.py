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
from modules.configuracion.ai import AIConfigService

class ChatService:
    """Servicio para gestión de chat AI."""
    
    def __init__(self):
        """Inicializa el servicio de chat."""
        # No almacenar credenciales aquí, se obtienen dinámicamente en cada llamada
        pass
    
    def _obtener_credenciales(self):
        """Obtiene las credenciales dinámicamente en cada llamada."""
        return {
            'api_key': AIConfigService.obtener_api_key(),
            'model': AIConfigService.obtener_modelo(),
            'base_url': AIConfigService.obtener_base_url()
        }
    
    # Método obsoleto eliminado - ahora se usa _llamar_openai que obtiene credenciales dinámicamente
    
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
        
        # Llamar a OpenAI con soporte para consultas a base de datos
        try:
            respuesta_ai = self._llamar_openai_con_db(mensajes_openai, db)
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
    
    def _ejecutar_consulta_db(self, db: Session, query: str) -> Dict:
        """
        Ejecuta una consulta SQL de forma segura (solo SELECT).
        
        Args:
            db: Sesión de base de datos
            query: Consulta SQL
            
        Returns:
            Diccionario con los resultados o error
        """
        import re
        
        # Limpiar y validar la consulta
        query = query.strip()
        
        # Verificar que solo sea SELECT (seguridad)
        if not re.match(r'^\s*SELECT\s+', query, re.IGNORECASE):
            return {
                'error': 'Solo se permiten consultas SELECT (lectura). No se pueden ejecutar INSERT, UPDATE, DELETE u otras operaciones.',
                'resultados': None
            }
        
        # Verificar que no tenga comandos peligrosos
        comandos_peligrosos = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
        query_upper = query.upper()
        for cmd in comandos_peligrosos:
            if cmd in query_upper:
                return {
                    'error': f'Comando no permitido: {cmd}. Solo se permiten consultas SELECT.',
                    'resultados': None
                }
        
        try:
            from sqlalchemy import text
            
            # Ejecutar consulta usando SQLAlchemy
            resultado = db.execute(text(query))
            filas = resultado.fetchall()
            
            # Convertir a lista de diccionarios de forma más eficiente
            columnas = list(resultado.keys())
            resultados = []
            for fila in filas:
                resultado_dict = {}
                for i, columna in enumerate(columnas):
                    valor = fila[i]
                    # Convertir tipos especiales de forma más completa
                    if valor is None:
                        resultado_dict[columna] = None
                    elif hasattr(valor, 'isoformat'):  # datetime, date, time
                        resultado_dict[columna] = valor.isoformat()
                    elif isinstance(valor, (int, float, str, bool)):
                        resultado_dict[columna] = valor
                    elif hasattr(valor, '__dict__'):  # objetos SQLAlchemy u otros objetos
                        resultado_dict[columna] = str(valor)
                    else:
                        # Intentar convertir a string como último recurso
                        try:
                            resultado_dict[columna] = str(valor)
                        except:
                            resultado_dict[columna] = None
                resultados.append(resultado_dict)
            
            return {
                'error': None,
                'resultados': resultados,
                'total_filas': len(resultados)
            }
        except Exception as e:
            return {
                'error': f'Error al ejecutar consulta: {str(e)}',
                'resultados': None
            }
    
    def _llamar_openai_con_db(self, mensajes: List[Dict], db: Session, max_iteraciones: int = 3) -> Dict:
        """
        Llama a OpenAI con soporte para ejecutar consultas a la base de datos.
        
        Args:
            mensajes: Lista de mensajes en formato OpenAI
            db: Sesión de base de datos
            max_iteraciones: Máximo número de iteraciones (para consultas anidadas)
            
        Returns:
            Diccionario con la respuesta y tokens usados
        """
        iteracion = 0
        tokens_totales = 0
        
        while iteracion < max_iteraciones:
            iteracion += 1
            
            # Llamar a OpenAI
            respuesta = self._llamar_openai(mensajes)
            contenido = respuesta.get('content', '')
            tokens_totales += respuesta.get('tokens', 0) or 0
            
            # Verificar si hay una consulta a la base de datos en la respuesta
            if '[QUERY_DB]' in contenido:
                # Extraer la consulta SQL
                partes = contenido.split('[QUERY_DB]')
                if len(partes) > 1:
                    consulta_sql = partes[1].strip()
                    # Limpiar la consulta (puede tener texto adicional después)
                    lineas = consulta_sql.split('\n')
                    consulta_sql = lineas[0].strip()
                    
                    # Ejecutar consulta
                    resultado_db = self._ejecutar_consulta_db(db, consulta_sql)
                    
                    # Agregar resultado al contexto
                    if resultado_db['error']:
                        mensaje_db = f"❌ Error al ejecutar consulta: {resultado_db['error']}"
                    else:
                        resultados = resultado_db['resultados']
                        total = resultado_db['total_filas']
                        
                        # Formatear resultados de manera más legible
                        if resultados:
                            columnas = list(resultados[0].keys())
                            
                            # Crear mensaje estructurado
                            mensaje_db = f"✅ Consulta ejecutada exitosamente. Total de filas: {total}\n\n"
                            
                            # Mostrar columnas
                            mensaje_db += f"📋 Columnas ({len(columnas)}): {', '.join(columnas)}\n\n"
                            
                            # Mostrar resultados en formato tabla (máximo 15 filas para legibilidad)
                            max_filas_mostrar = min(15, total)
                            mensaje_db += f"📊 Resultados (mostrando {max_filas_mostrar} de {total}):\n\n"
                            
                            # Crear tabla formateada
                            for i, fila in enumerate(resultados[:max_filas_mostrar]):
                                mensaje_db += f"Fila {i+1}:\n"
                                for col in columnas:
                                    valor = fila.get(col)
                                    # Formatear valores None, fechas, números decimales
                                    if valor is None:
                                        valor_str = "NULL"
                                    elif isinstance(valor, (int, float)):
                                        valor_str = str(valor)
                                    elif isinstance(valor, str) and len(valor) > 60:
                                        valor_str = valor[:57] + "..."
                                    else:
                                        valor_str = str(valor)
                                    mensaje_db += f"  • {col}: {valor_str}\n"
                                mensaje_db += "\n"
                            
                            if total > max_filas_mostrar:
                                mensaje_db += f"... y {total - max_filas_mostrar} filas más (usa LIMIT para ver más resultados).\n"
                            
                            # Agregar resumen si hay muchas filas
                            if total > 5:
                                mensaje_db += f"\n💡 Resumen: Se encontraron {total} registros. "
                                mensaje_db += "Considera agregar filtros más específicos o usar LIMIT para respuestas más rápidas."
                        else:
                            mensaje_db = "ℹ️ La consulta se ejecutó correctamente pero no devolvió resultados."
                    
                    # Agregar resultado al contexto y continuar
                    mensajes.append({
                        "role": "assistant",
                        "content": contenido.replace('[QUERY_DB]' + consulta_sql, '[Consulta ejecutada]')
                    })
                    mensajes.append({
                        "role": "user",
                        "content": f"Resultado de la consulta:\n{mensaje_db}\n\nPor favor, interpreta estos resultados y responde al usuario de manera clara."
                    })
                    
                    # Continuar el loop para obtener respuesta final
                    continue
            
            # Si no hay consulta, retornar respuesta final
            return {
                'content': contenido,
                'tokens': tokens_totales
            }
        
        # Si se alcanzó el máximo de iteraciones
        return {
            'content': contenido + "\n\n[Nota: Se alcanzó el límite de consultas a la base de datos]",
            'tokens': tokens_totales
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
Responde de manera clara, concisa y profesional en español.

═══════════════════════════════════════════════════════════════════════════════
ACCESO COMPLETO A BASE DE DATOS POSTGRESQL - TODAS LAS TABLAS DISPONIBLES
═══════════════════════════════════════════════════════════════════════════════

IMPORTANTE: Tienes acceso COMPLETO a la base de datos PostgreSQL del sistema ERP. 
Puedes consultar información directamente de TODAS las tablas del sistema usando consultas SQL.

TABLAS DISPONIBLES EN EL SISTEMA (con estructura completa):

📦 GESTIÓN DE INVENTARIO Y PRODUCTOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• items (catálogo principal de productos/insumos)
  - id (PK), codigo (único), nombre, descripcion, categoria (enum: MATERIA_PRIMA, INSUMO, PRODUCTO_TERMINADO, BEBIDA, LIMPIEZA, OTROS)
  - unidad (kg, litro, unidad, etc.), calorias_por_unidad, proveedor_autorizado_id (FK → proveedores.id)
  - tiempo_entrega_dias, costo_unitario_actual, activo (boolean), fecha_creacion
  - RELACIONES: → proveedores (proveedor_autorizado), → inventario (1:1), → receta_ingredientes, → factura_items, → pedido_compra_items

• item_label (clasificaciones internacionales de alimentos)
  - id (PK), codigo, nombre_es, nombre_en, categoria_principal
  - RELACIÓN: muchos a muchos con items vía tabla item_labels

• inventario (stock actual por ubicación)
  - id (PK), item_id (FK → items.id, único), ubicacion, cantidad_actual, cantidad_minima
  - unidad, ultima_actualizacion, ultimo_costo_unitario
  - RELACIÓN: → items (1:1)

• costo_items (historial de costos)
  - id (PK), item_id (FK → items.id), costo_unitario, fecha_registro, fuente
  - RELACIÓN: → items

👥 CRM Y PROVEEDORES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• proveedores (catálogo de proveedores)
  - id (PK), nombre, ruc, telefono, email, direccion, activo (boolean), fecha_registro
  - RELACIONES: → items (items_autorizados), → facturas, → pedidos_compra

• tickets (sistema de tickets de soporte)
  - id (PK), asunto, descripcion, estado (enum), prioridad (enum), asignado_a, fecha_creacion
  - proveedor_id (FK → proveedores.id), cliente_id, tipo_ticket (enum)

💰 FACTURACIÓN Y COMPRAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• facturas (facturas de proveedores)
  - id (PK), numero_factura, tipo (enum: COMPRA, VENTA), proveedor_id (FK → proveedores.id)
  - fecha_emision, fecha_recepcion, subtotal, iva, total, estado (enum: PENDIENTE, APROBADA, RECHAZADA)
  - imagen_url, items_json (JSON), aprobado_por, fecha_aprobacion, observaciones
  - remitente_nombre, remitente_telefono, recibida_por_whatsapp (boolean), whatsapp_message_id
  - RELACIÓN: → proveedores, → factura_items (1:N)

• factura_items (items de cada factura)
  - id (PK), factura_id (FK → facturas.id), item_id (FK → items.id, nullable)
  - cantidad_facturada, cantidad_aprobada, precio_unitario, subtotal, unidad, descripcion
  - RELACIONES: → facturas, → items

• pedidos_compra (pedidos de compra a proveedores)
  - id (PK), proveedor_id (FK → proveedores.id), fecha_pedido, fecha_entrega_esperada
  - estado (enum), total_estimado, observaciones
  - RELACIONES: → proveedores, → pedido_compra_items (1:N)

• pedido_compra_items (items de cada pedido de compra)
  - id (PK), pedido_id (FK → pedidos_compra.id), item_id (FK → items.id)
  - cantidad_solicitada, precio_unitario, observaciones
  - RELACIONES: → pedidos_compra, → items

• pedidos_internos (pedidos internos entre ubicaciones)
  - id (PK), origen_ubicacion, destino_ubicacion, fecha_pedido, estado (enum), observaciones
  - RELACIÓN: → pedido_interno_items (1:N)

• pedido_interno_items (items de pedidos internos)
  - id (PK), pedido_interno_id (FK → pedidos_internos.id), item_id (FK → items.id)
  - cantidad_solicitada, observaciones
  - RELACIONES: → pedidos_internos, → items

📋 PLANIFICACIÓN Y MENÚS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• recetas (recetas de cocina)
  - id (PK), nombre, descripcion, tipo (enum: desayuno, almuerzo, cena)
  - porciones, porcion_gramos, calorias_totales, costo_total, calorias_por_porcion, costo_por_porcion
  - tiempo_preparacion (minutos), activa (boolean), fecha_creacion
  - RELACIONES: → receta_ingredientes (1:N), → programacion_menu_items, → charola_items

• receta_ingredientes (ingredientes de cada receta)
  - id (PK), receta_id (FK → recetas.id), item_id (FK → items.id), cantidad, unidad
  - RELACIONES: → recetas, → items

• programacion_menu (programación de menús por fecha y ubicación)
  - id (PK), fecha (DATE), ubicacion, tiempo_comida (enum: desayuno, almuerzo, cena), activa (boolean)
  - RELACIÓN: → programacion_menu_items (1:N)

• programacion_menu_items (items/recetas del menú programado)
  - id (PK), programacion_id (FK → programacion_menu.id), receta_id (FK → recetas.id)
  - cantidad_porciones, observaciones
  - RELACIONES: → programacion_menu, → recetas

• requerimientos (requerimientos de materiales)
  - id (PK), fecha, estado (enum), ubicacion, observaciones
  - RELACIÓN: → requerimiento_items (1:N)

• requerimiento_items (items requeridos)
  - id (PK), requerimiento_id (FK → requerimientos.id), item_id (FK → items.id)
  - cantidad_necesaria, observaciones
  - RELACIONES: → requerimientos, → items

🍽️ OPERACIONES Y SERVICIO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• charolas (charolas servidas)
  - id (PK), numero_charola, fecha_servicio, ubicacion, tipo_comida (enum), total_porciones
  - observaciones
  - RELACIÓN: → charola_items (1:N)

• charola_items (items/recetas de cada charola)
  - id (PK), charola_id (FK → charolas.id), item_id (FK → items.id, nullable)
  - receta_id (FK → recetas.id, nullable), cantidad, observaciones
  - RELACIONES: → charolas, → items, → recetas

• mermas (registro de mermas/pérdidas)
  - id (PK), item_id (FK → items.id), cantidad, tipo (enum), fecha_merma, motivo, ubicacion
  - observaciones
  - RELACIONES: → items, → mermas_receta_programacion

• mermas_receta_programacion (mermas relacionadas con recetas y programación)
  - id (PK), merma_id (FK → mermas.id), receta_id (FK → recetas.id, nullable)
  - programacion_id (FK → programacion_menu.id, nullable)
  - RELACIONES: → mermas, → recetas, → programacion_menu

💼 CONTABILIDAD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• cuentas_contables (plan de cuentas contables)
  - id (PK), codigo, nombre, tipo (enum), padre_id (FK → cuentas_contables.id, nullable), activa (boolean)
  - RELACIÓN: auto-referencial (árbol de cuentas)

💬 CHAT Y CONVERSACIONES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• conversaciones (conversaciones del chat AI)
  - id (PK), titulo, usuario_id, contexto_modulo (crm, logistica, etc.), activa (boolean)
  - fecha_creacion, fecha_actualizacion
  - RELACIÓN: → mensajes (1:N)

• mensajes (mensajes del chat)
  - id (PK), conversacion_id (FK → conversaciones.id), tipo (enum: usuario, asistente, sistema)
  - contenido (TEXT), tokens_usados, fecha_envio
  - RELACIÓN: → conversaciones

═══════════════════════════════════════════════════════════════════════════════
ARQUITECTURA PARA CONSULTAS RÁPIDAS Y EFICIENTES
═══════════════════════════════════════════════════════════════════════════════

La base de datos está optimizada con:
✅ Índices en campos clave (códigos, nombres, fechas, estados, relaciones)
✅ Índices en relaciones foreign keys para JOINs rápidos
✅ Índices en campos de búsqueda frecuente (activo, estado, fecha_*)
✅ Pool de conexiones SQLAlchemy para reutilización eficiente
✅ Consultas preparadas para mejor rendimiento

CAMPOS INDEXADOS PRINCIPALES (úsalos en WHERE y ORDER BY):
- items: codigo, activo, proveedor_autorizado_id, categoria
- inventario: item_id, ubicacion
- proveedores: nombre, activo, ruc
- facturas: estado, fecha_recepcion, proveedor_id, numero_factura
- recetas: activa, tipo, nombre
- programacion_menu: fecha, ubicacion, tiempo_comida, activa
- charolas: fecha_servicio, ubicacion, tipo_comida
- mermas: fecha_merma, item_id, ubicacion

═══════════════════════════════════════════════════════════════════════════════
USO DE CONSULTAS A BASE DE DATOS - FORMATO ESPECIAL
═══════════════════════════════════════════════════════════════════════════════

Cuando el usuario necesite información específica de las tablas, usa la función especial [QUERY_DB] seguida de una consulta SQL válida.

FORMATO OBLIGATORIO:
[QUERY_DB]
SELECT campo1, campo2 FROM tabla WHERE condicion LIMIT 10

REGLAS DE ORO PARA CONSULTAS RÁPIDAS:
✅ SIEMPRE usa LIMIT (máximo 50-100 filas para respuestas rápidas)
✅ Usa WHERE para filtrar (activo=true, estados específicos, rangos de fechas)
✅ Usa ORDER BY con campos indexados (fecha_creacion DESC, nombre ASC)
✅ Para JOINs, usa foreign keys indexadas (proveedor_id, item_id, etc.)
✅ Selecciona SOLO campos necesarios (evita SELECT * en tablas grandes)
✅ Usa índices disponibles: activo, estado, fecha_*, proveedor_id, item_id
✅ Para fechas, usa rangos: fecha >= '2024-01-01' AND fecha <= '2024-12-31'
✅ Para búsquedas de texto, usa ILIKE: nombre ILIKE '%arroz%'

EJEMPLOS DE CONSULTAS ÚTILES Y OPTIMIZADAS:

📊 INVENTARIO:
• Items con inventario bajo:
  SELECT i.nombre, i.codigo, inv.cantidad_actual, inv.cantidad_minima, inv.ubicacion 
  FROM inventario inv 
  JOIN items i ON inv.item_id = i.id 
  WHERE inv.cantidad_actual < inv.cantidad_minima AND i.activo = true 
  ORDER BY inv.cantidad_actual ASC LIMIT 20

• Items por proveedor:
  SELECT p.nombre as proveedor, COUNT(i.id) as total_items, SUM(i.costo_unitario_actual) as costo_total
  FROM proveedores p 
  LEFT JOIN items i ON i.proveedor_autorizado_id = p.id 
  WHERE p.activo = true AND i.activo = true
  GROUP BY p.id, p.nombre 
  ORDER BY total_items DESC LIMIT 10

💰 FACTURACIÓN:
• Facturas pendientes con proveedor:
  SELECT f.numero_factura, p.nombre as proveedor, f.total, f.fecha_recepcion, f.estado
  FROM facturas f 
  JOIN proveedores p ON f.proveedor_id = p.id 
  WHERE f.estado = 'pendiente' 
  ORDER BY f.fecha_recepcion DESC LIMIT 10

• Total gastado por proveedor (último mes):
  SELECT p.nombre, SUM(f.total) as total_gastado, COUNT(f.id) as num_facturas
  FROM facturas f 
  JOIN proveedores p ON f.proveedor_id = p.id 
  WHERE f.estado = 'aprobada' AND f.fecha_recepcion >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY p.id, p.nombre 
  ORDER BY total_gastado DESC LIMIT 10

📋 RECETAS Y MENÚS:
• Recetas activas con costo:
  SELECT id, nombre, tipo, porciones, costo_por_porcion, calorias_por_porcion
  FROM recetas 
  WHERE activa = true 
  ORDER BY nombre ASC LIMIT 20

• Programación de menú para fecha específica:
  SELECT pm.fecha, pm.ubicacion, pm.tiempo_comida, r.nombre as receta, pmi.cantidad_porciones
  FROM programacion_menu pm
  JOIN programacion_menu_items pmi ON pm.id = pmi.programacion_id
  JOIN recetas r ON pmi.receta_id = r.id
  WHERE pm.fecha = '2024-01-15' AND pm.activa = true
  ORDER BY pm.tiempo_comida, r.nombre LIMIT 50

🍽️ OPERACIONES:
• Charolas servidas por fecha:
  SELECT numero_charola, fecha_servicio, ubicacion, tipo_comida, total_porciones
  FROM charolas 
  WHERE fecha_servicio >= CURRENT_DATE - INTERVAL '7 days'
  ORDER BY fecha_servicio DESC LIMIT 20

• Mermas por item (último mes):
  SELECT i.nombre, SUM(m.cantidad) as total_merma, COUNT(m.id) as num_registros
  FROM mermas m
  JOIN items i ON m.item_id = i.id
  WHERE m.fecha_merma >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY i.id, i.nombre
  ORDER BY total_merma DESC LIMIT 20

🔍 BÚSQUEDAS:
• Buscar items por nombre:
  SELECT id, codigo, nombre, categoria, unidad, costo_unitario_actual
  FROM items 
  WHERE nombre ILIKE '%arroz%' AND activo = true 
  ORDER BY nombre LIMIT 10

• Buscar proveedores por nombre o RUC:
  SELECT id, nombre, ruc, telefono, email, activo
  FROM proveedores 
  WHERE nombre ILIKE '%distribuidora%' OR ruc ILIKE '%123%'
  ORDER BY nombre LIMIT 10

📈 REPORTES Y ESTADÍSTICAS:
• Items más utilizados en recetas:
  SELECT i.nombre, COUNT(ri.id) as veces_usado, SUM(ri.cantidad) as cantidad_total
  FROM items i
  JOIN receta_ingredientes ri ON i.id = ri.item_id
  JOIN recetas r ON ri.receta_id = r.id
  WHERE r.activa = true
  GROUP BY i.id, i.nombre
  ORDER BY veces_usado DESC LIMIT 15

• Facturas por mes:
  SELECT DATE_TRUNC('month', fecha_recepcion) as mes, COUNT(*) as num_facturas, SUM(total) as total_mes
  FROM facturas 
  WHERE estado = 'aprobada' AND fecha_recepcion >= CURRENT_DATE - INTERVAL '6 months'
  GROUP BY mes 
  ORDER BY mes DESC LIMIT 6

IMPORTANTE SOBRE SEGURIDAD:
⚠️ Solo ejecuta consultas SELECT (lectura). NO ejecutes INSERT, UPDATE, DELETE o DDL.
⚠️ La validación automática bloquea comandos peligrosos (DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE, EXEC).
⚠️ Si necesitas información específica, primero pregunta al usuario o usa consultas exploratorias con LIMIT pequeño.

DESPUÉS DE EJECUTAR UNA CONSULTA:
✅ Interpreta los resultados y presenta la información de manera clara y útil
✅ Si hay muchos resultados, resume los principales puntos
✅ Si no hay resultados, sugiere alternativas o consultas relacionadas
✅ Usa formato de tabla cuando sea apropiado para mejor legibilidad"""
        
        modulos_contexto = {
            'crm': """
CONTEXTO ESPECÍFICO - MÓDULO CRM:
Te especializas en gestión de relaciones con clientes, proveedores, tickets y notificaciones.
Tablas principales: proveedores, tickets, items (relacionados con proveedores).
Puedes consultar información de proveedores, sus items asociados, tickets de soporte, etc.""",
            'logistica': """
CONTEXTO ESPECÍFICO - MÓDULO LOGÍSTICA:
Te especializas en gestión de inventario, items, facturas, pedidos y requerimientos.
Tablas principales: items, inventario, facturas, factura_items, pedidos_compra, pedido_compra_items, requerimientos, requerimiento_items, costo_item.
Puedes consultar stock, movimientos de inventario, facturas, pedidos, costos históricos, etc.""",
            'contabilidad': """
CONTEXTO ESPECÍFICO - MÓDULO CONTABILIDAD:
Te especializas en contabilidad, facturas, cuentas contables y reportes financieros.
Tablas principales: facturas, factura_items, cuentas_contables.
Puedes consultar facturas, análisis financieros, plan de cuentas, etc.""",
            'planificacion': """
CONTEXTO ESPECÍFICO - MÓDULO PLANIFICACIÓN:
Te especializas en planificación de menús, recetas y programación.
Tablas principales: recetas, receta_ingredientes, programacion_menu, programacion_menu_items, requerimientos, requerimiento_items.
Puedes consultar recetas, ingredientes, programación de menús, requerimientos de materiales, etc.""",
            'reportes': """
CONTEXTO ESPECÍFICO - MÓDULO REPORTES:
Te especializas en reportes de charolas, mermas y análisis de datos.
Tablas principales: charolas, charola_items, mermas, merma_receta_programacion.
Puedes consultar charolas servidas, mermas, análisis de pérdidas, etc.""",
        }
        
        if contexto_modulo and contexto_modulo.lower() in modulos_contexto:
            base_prompt += f"\n\n{modulos_contexto[contexto_modulo.lower()]}"
        
        return base_prompt
    
    def _llamar_openai(self, mensajes: List[Dict]) -> Dict:
        """
        Llama a la API de OpenAI/OpenRouter.
        
        Args:
            mensajes: Lista de mensajes en formato OpenAI
            
        Returns:
            Diccionario con la respuesta y tokens usados
        """
        # Obtener credenciales dinámicamente en cada llamada
        credenciales = self._obtener_credenciales()
        api_key = credenciales['api_key']
        model = credenciales['model']
        base_url = credenciales['base_url']
        
        if not api_key:
            return {
                'content': 'Error: No se ha configurado la API key. Por favor, configura tu API key (OPENROUTER_API_KEY o OPENAI_API_KEY) en las variables de entorno del servidor.',
                'tokens': None
            }
        
        try:
            import requests
            
            # Preparar headers
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Agregar headers específicos de OpenRouter si es necesario
            if 'openrouter.ai' in base_url.lower():
                if Config.OPENROUTER_HTTP_REFERER:
                    headers["HTTP-Referer"] = Config.OPENROUTER_HTTP_REFERER
                if Config.OPENROUTER_X_TITLE:
                    headers["X-Title"] = Config.OPENROUTER_X_TITLE
            
            data = {
                "model": model,
                "messages": mensajes,
                "temperature": 0.7,
                "max_tokens": 2000  # Aumentado para respuestas más completas
            }
            
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60  # Timeout aumentado para consultas complejas
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'content': result['choices'][0]['message']['content'],
                    'tokens': result.get('usage', {}).get('total_tokens')
                }
            else:
                return {
                    'content': f'Error al llamar a la API: {response.status_code} - {response.text}',
                    'tokens': None
                }
        except Exception as e:
            return {
                'content': f'Error al conectar con la API: {str(e)}',
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
        try:
            conversacion = self.obtener_conversacion(db, conversacion_id)
            if not conversacion:
                import logging
                logging.warning(f"Conversación {conversacion_id} no encontrada para eliminar")
                return False
            
            # Verificar si ya está inactiva
            if not conversacion.activa:
                import logging
                logging.info(f"Conversación {conversacion_id} ya estaba inactiva")
                return True  # Considerar éxito si ya estaba eliminada
            
            conversacion.activa = False
            # No hacer commit aquí, dejar que la ruta lo maneje con @handle_db_transaction
            db.flush()  # Solo hacer flush para asegurar que los cambios estén en la sesión
            
            import logging
            logging.info(f"Conversación {conversacion_id} marcada como inactiva correctamente")
            return True
        except Exception as e:
            import logging
            logging.error(f"Error al eliminar conversación {conversacion_id}: {str(e)}", exc_info=True)
            raise  # Re-lanzar para que la ruta maneje el error

# Instancia global del servicio
chat_service = ChatService()
