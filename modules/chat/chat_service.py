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
        
        # NO hacer commit aquí - el decorador @handle_db_transaction en la ruta lo maneja
        # Solo hacer flush para asegurar que los cambios estén en la sesión
        db.flush()
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
            from sqlalchemy.exc import SQLAlchemyError
            import uuid
            
            # Crear un savepoint para aislar la consulta SQL
            # Si la consulta falla, solo se revierte el savepoint, no toda la transacción
            savepoint_name = f"sp_query_{uuid.uuid4().hex[:8]}"
            savepoint = db.begin_nested()  # Crea un savepoint automáticamente
            
            try:
                # Ejecutar consulta con timeout (30 segundos por defecto)
                # El timeout está configurado en SQLALCHEMY_ENGINE_OPTIONS pero también lo aplicamos aquí
                from sqlalchemy import event
                import time
                
                # Optimización: Validar consulta antes de ejecutar
                query_upper = query.upper().strip()
                
                # Detectar consultas potencialmente costosas sin LIMIT
                if 'SELECT' in query_upper and 'LIMIT' not in query_upper:
                    # Agregar LIMIT automático si no existe (máximo 100 filas por defecto)
                    if not any(keyword in query_upper for keyword in ['COUNT(', 'SUM(', 'AVG(', 'MAX(', 'MIN(', 'GROUP BY']):
                        # Solo agregar LIMIT si no es una agregación
                        query = query.rstrip(';').strip() + ' LIMIT 100'
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"Se agregó LIMIT 100 automáticamente a la consulta")
                
                inicio = time.time()
                resultado = db.execute(text(query))
                filas = resultado.fetchall()
                tiempo_ejecucion = time.time() - inicio
                
                # Log de consultas lentas (> 3 segundos ahora, más estricto)
                if tiempo_ejecucion > 3:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"⚠️ Consulta lenta detectada: {tiempo_ejecucion:.2f}s - Query: {query[:150]}...")
                    
                    # Sugerir optimización si no usa índices conocidos
                    sugerencias_optimizacion = []
                    if 'WHERE' in query_upper:
                        # Verificar si usa campos indexados
                        campos_indexados = ['id', 'activo', 'estado', 'fecha_', 'proveedor_id', 'item_id', 'codigo', 'nombre']
                        usa_indices = any(campo in query_upper for campo in campos_indexados)
                        if not usa_indices:
                            sugerencias_optimizacion.append("Considera usar campos indexados en WHERE (id, activo, estado, fecha_*, proveedor_id, item_id)")
                    
                    if 'JOIN' in query_upper and 'ON' not in query_upper:
                        sugerencias_optimizacion.append("Asegúrate de usar JOINs con foreign keys indexadas")
                    
                    if sugerencias_optimizacion:
                        logger.info(f"💡 Sugerencias de optimización: {'; '.join(sugerencias_optimizacion)}")
                
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
                
                # Confirmar el savepoint (commit de la subtransacción)
                savepoint.commit()
                
                # Información adicional para optimización
                info_optimizacion = {
                    'tiempo_ejecucion_ms': round(tiempo_ejecucion * 1000, 2),
                    'total_filas': len(resultados),
                    'usa_indices': any(campo in query_upper for campo in ['id', 'activo', 'estado', 'fecha_', 'proveedor_id', 'item_id'])
                }
                
                return {
                    'error': None,
                    'resultados': resultados,
                    'total_filas': len(resultados),
                    'info_optimizacion': info_optimizacion
                }
            except SQLAlchemyError as e:
                # Si hay un error SQL, hacer rollback solo del savepoint
                # La transacción principal sigue intacta
                savepoint.rollback()
                
                # Mejorar mensajes de error para valores de enum incorrectos
                error_msg = str(e)
                sugerencia = ""
                
                # Detectar errores comunes de valores inválidos
                if 'check constraint' in error_msg.lower() or 'invalid' in error_msg.lower():
                    if 'pedidos_compra' in error_msg.lower() or 'estado' in error_msg.lower():
                        sugerencia = "\n\n💡 Sugerencia: Los valores válidos para pedidos_compra.estado son: 'borrador', 'enviado', 'recibido', 'cancelado' (en minúsculas). NO existe 'pendiente'. Para pedidos activos usa: estado IN ('borrador', 'enviado')"
                    elif 'facturas' in error_msg.lower():
                        sugerencia = "\n\n💡 Sugerencia: Los valores válidos para facturas.estado son: 'pendiente', 'aprobada', 'rechazada' (en minúsculas)"
                    else:
                        sugerencia = "\n\n💡 Sugerencia: Verifica que los valores de estado sean válidos. Consulta: SELECT DISTINCT estado FROM tabla LIMIT 10"
                
                return {
                    'error': f'Error al ejecutar consulta SQL: {error_msg}{sugerencia}',
                    'resultados': None
                }
        except Exception as e:
            # Para otros errores, intentar hacer rollback del savepoint si existe
            try:
                if 'savepoint' in locals():
                    savepoint.rollback()
            except:
                pass  # Si ya está abortada o no existe, no importa
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
            # Buscar [QUERY_DB] en cualquier parte del contenido
            if '[QUERY_DB]' in contenido:
                # Extraer la consulta SQL
                partes = contenido.split('[QUERY_DB]')
                if len(partes) > 1:
                    consulta_sql = partes[1].strip()
                    # Limpiar la consulta - puede estar en múltiples líneas
                    # Tomar hasta el primer punto y coma o nueva línea significativa
                    lineas = consulta_sql.split('\n')
                    consulta_sql = ''
                    for linea in lineas:
                        linea = linea.strip()
                        if linea and not linea.startswith('--'):  # Ignorar comentarios
                            consulta_sql += linea + ' '
                            # Detener si encontramos punto y coma o si la línea parece ser texto explicativo
                            if ';' in linea or (len(consulta_sql) > 200 and not consulta_sql.upper().startswith('SELECT')):
                                break
                    consulta_sql = consulta_sql.strip()
                    # Limpiar punto y coma final si existe
                    if consulta_sql.endswith(';'):
                        consulta_sql = consulta_sql[:-1].strip()
                    
                    # Ejecutar consulta
                    resultado_db = self._ejecutar_consulta_db(db, consulta_sql)
                    
                    # Agregar resultado al contexto
                    if resultado_db['error']:
                        mensaje_db = f"❌ Error al ejecutar consulta: {resultado_db['error']}"
                    else:
                        resultados = resultado_db['resultados']
                        total = resultado_db['total_filas']
                        info_opt = resultado_db.get('info_optimizacion', {})
                        tiempo_ms = info_opt.get('tiempo_ejecucion_ms', 0)
                        consulta_upper = consulta_sql.upper()
                        
                        # Formatear resultados de manera más legible
                        if resultados:
                            columnas = list(resultados[0].keys())
                            
                            # Crear mensaje estructurado con información de rendimiento
                            mensaje_db = f"✅ Consulta ejecutada exitosamente. Total de filas: {total}"
                            if tiempo_ms > 0:
                                if tiempo_ms < 100:
                                    mensaje_db += f" ⚡ ({tiempo_ms}ms - rápida)"
                                elif tiempo_ms < 1000:
                                    mensaje_db += f" ⏱️ ({tiempo_ms}ms)"
                                else:
                                    mensaje_db += f" 🐌 ({tiempo_ms}ms - lenta, considera optimizar)"
                            mensaje_db += "\n\n"
                            
                            # Mostrar columnas
                            mensaje_db += f"📋 Columnas ({len(columnas)}): {', '.join(columnas)}\n\n"
                            
                            # Mostrar resultados en formato tabla (máximo 15 filas para legibilidad)
                            # Optimización: ajustar según el tipo de consulta
                            if total <= 20:
                                max_filas_mostrar = total  # Mostrar todas si son pocas
                            elif any(keyword in consulta_upper for keyword in ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN']):
                                max_filas_mostrar = min(30, total)  # Más filas para agregaciones
                            else:
                                max_filas_mostrar = min(15, total)  # Menos para listas
                            
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

🚨🚨🚨 REGLA CRÍTICA - LEE ESTO PRIMERO 🚨🚨🚨
═══════════════════════════════════════════════════════════════════════════════
TIENES ACCESO DIRECTO A LA BASE DE DATOS. PUEDES EJECUTAR CONSULTAS SQL EN TIEMPO REAL.

🎯 TU OBJETIVO: Ser un asistente experto que ayuda a los usuarios a encontrar información en la base de datos del ERP.

CUANDO EL USUARIO PREGUNTE SOBRE DATOS ESPECÍFICOS (cantidades, números, listas, información de tablas):
1. NO digas "no tengo capacidad" o "necesitarías consultar"
2. USA EL MAPA DE NAVEGACIÓN arriba para saber dónde buscar
3. EJECUTA la consulta INMEDIATAMENTE usando el formato [QUERY_DB]
4. Si no encuentras resultados, intenta consultas alternativas o más amplias
5. Interpreta los resultados y responde de forma útil y completa
6. Ofrece información relacionada cuando sea relevante

EJEMPLO CORRECTO:
Usuario: "¿Cuántas porciones servimos hoy?"
TÚ DEBES RESPONDER:
[QUERY_DB]
SELECT SUM(total_porciones) AS total_porciones_servidas FROM charolas WHERE fecha_servicio = CURRENT_DATE

Y luego interpretar los resultados cuando los recibas.

EJEMPLO INCORRECTO (NO HACER ESTO):
"No tengo la capacidad de ejecutar consultas en tiempo real. Aquí tienes la consulta SQL que podrías ejecutar..."

═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
ACCESO COMPLETO A BASE DE DATOS POSTGRESQL - TODAS LAS TABLAS DISPONIBLES
═══════════════════════════════════════════════════════════════════════════════

IMPORTANTE: Tienes acceso COMPLETO a la base de datos PostgreSQL del sistema ERP. 
Puedes consultar información directamente de TODAS las tablas del sistema usando consultas SQL.

🗺️ MAPA DE NAVEGACIÓN - DÓNDE ENCONTRAR INFORMACIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Para responder preguntas del usuario, usa este mapa para saber dónde buscar:

📊 INFORMACIÓN SOBRE PRODUCTOS/ITEMS:
  → Tabla principal: items
  → Stock actual: inventario (JOIN con items)
  → Historial de costos: costo_items (JOIN con items)
  → Clasificaciones: item_labels (JOIN con items)
  → Proveedor autorizado: items.proveedor_autorizado_id → proveedores.id

💰 INFORMACIÓN SOBRE COMPRAS Y FACTURACIÓN:
  → Facturas: facturas (JOIN con proveedores)
  → Items de facturas: factura_items (JOIN facturas + items)
  → Pedidos a proveedores: pedidos_compra (JOIN con proveedores)
  → Items de pedidos: pedido_compra_items (JOIN pedidos_compra + items)
  → Costos históricos: costo_items (por item_id)

👥 INFORMACIÓN SOBRE PROVEEDORES:
  → Datos del proveedor: proveedores
  → Items que suministra: items WHERE proveedor_autorizado_id = X
  → Facturas del proveedor: facturas WHERE proveedor_id = X
  → Pedidos al proveedor: pedidos_compra WHERE proveedor_id = X
  → Tickets de soporte: tickets WHERE proveedor_id = X

🍽️ INFORMACIÓN SOBRE SERVICIO Y OPERACIONES:
  → Charolas servidas: charolas
  → Items/recetas servidos: charola_items (JOIN charolas + items/recetas)
  → Mermas: mermas (JOIN con items)
  → Mermas relacionadas: mermas_receta_programacion (JOIN mermas + recetas + programacion_menu)

📋 INFORMACIÓN SOBRE PLANIFICACIÓN:
  → Recetas: recetas
  → Ingredientes de recetas: receta_ingredientes (JOIN recetas + items)
  → Programación de menús: programacion_menu
  → Items del menú: programacion_menu_items (JOIN programacion_menu + recetas)
  → Requerimientos: requerimientos
  → Items requeridos: requerimiento_items (JOIN requerimientos + items)

🔍 ESTRATEGIAS DE BÚSQUEDA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SI EL USUARIO PREGUNTA SOBRE CANTIDADES/NÚMEROS:
   → Busca en: inventario (stock), charolas (porciones servidas), facturas (totales)
   → Usa SUM(), COUNT(), AVG() según corresponda

2. SI EL USUARIO PREGUNTA SOBRE FECHAS:
   → Busca en: charolas.fecha_servicio, facturas.fecha_recepcion, pedidos_compra.fecha_pedido
   → Usa DATE() para comparar solo la fecha: DATE(fecha_servicio) = '2026-01-29'

3. SI EL USUARIO PREGUNTA SOBRE UN PRODUCTO ESPECÍFICO:
   → Empieza en: items (busca por nombre con ILIKE)
   → Luego consulta: inventario (stock), costo_items (costos), factura_items (compras)

4. SI EL USUARIO PREGUNTA SOBRE UN PROVEEDOR:
   → Empieza en: proveedores (busca por nombre)
   → Luego consulta: items (qué suministra), facturas (facturas recibidas)

5. SI EL USUARIO PREGUNTA SOBRE CHAROLAS/SERVICIO:
   → Tabla principal: charolas
   → Detalles: charola_items (qué se sirvió)
   → Filtra por: fecha_servicio, ubicacion, tipo_comida

6. SI NO ENCUENTRAS DATOS:
   → Verifica el formato de fecha (YYYY-MM-DD)
   → Verifica que uses DATE() para comparar fechas
   → Prueba consultas más amplias primero: SELECT COUNT(*) FROM tabla WHERE fecha >= '2026-01-01'
   → Sugiere alternativas al usuario: "No encontré datos para esa fecha, ¿quieres ver datos de otra fecha?"

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
  - id (PK), numero_factura, tipo (string: 'compra', 'venta' - minúsculas), proveedor_id (FK → proveedores.id)
  - fecha_emision, fecha_recepcion, subtotal, iva, total, estado (string: 'pendiente', 'aprobada', 'rechazada' - minúsculas)
  - imagen_url, items_json (JSON), aprobado_por, fecha_aprobacion, observaciones
  - remitente_nombre, remitente_telefono, recibida_por_whatsapp (boolean), whatsapp_message_id
  - RELACIÓN: → proveedores, → factura_items (1:N)

• factura_items (items de cada factura)
  - id (PK), factura_id (FK → facturas.id), item_id (FK → items.id, nullable)
  - cantidad_facturada, cantidad_aprobada, precio_unitario, subtotal, unidad, descripcion
  - RELACIONES: → facturas, → items

• pedidos_compra (pedidos de compra a proveedores)
  - id (PK), proveedor_id (FK → proveedores.id), fecha_pedido, fecha_entrega_esperada
  - estado (string: 'borrador', 'enviado', 'recibido', 'cancelado' - TODOS EN MINÚSCULAS), total, observaciones
  - RELACIONES: → proveedores, → pedido_compra_items (1:N)
  - ⚠️ IMPORTANTE: NO existe 'pendiente'. Para pedidos activos usa: estado IN ('borrador', 'enviado')

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
⚠️ VALORES DE ESTADO - STRINGS SIMPLES (MÁS PRÁCTICO) ⚠️
═══════════════════════════════════════════════════════════════════════════════

🚨 IMPORTANTE: Los campos de estado ahora usan STRINGS SIMPLES en minúsculas.
Es más práctico y evita errores de conversión de enum.

VALORES VÁLIDOS POR TABLA (TODOS EN MINÚSCULAS):

📦 pedidos_compra.estado:
  - 'borrador' (pedidos en creación)
  - 'enviado' (pedidos enviados al proveedor)
  - 'recibido' (pedidos recibidos)
  - 'cancelado' (pedidos cancelados)
  ⚠️ NO existe 'pendiente'. Para pedidos activos usa: estado IN ('borrador', 'enviado')

💰 facturas.estado:
  - 'pendiente' (facturas pendientes de aprobación)
  - 'aprobada' (facturas aprobadas)
  - 'rechazada' (facturas rechazadas)

📋 requerimientos.estado:
  - 'pendiente'
  - 'completado'
  - 'cancelado'

📦 pedidos_internos.estado:
  - 'pendiente'
  - 'enviado'
  - 'recibido'
  - 'cancelado'

🎫 tickets.estado:
  - 'abierto'
  - 'en_proceso'
  - 'resuelto'
  - 'cerrado'

🎫 tickets.prioridad:
  - 'baja'
  - 'media'
  - 'alta'
  - 'urgente'

📋 items.categoria:
  - 'materia_prima'
  - 'insumo'
  - 'producto_terminado'
  - 'bebida'
  - 'limpieza'
  - 'otros'

📋 recetas.tipo, programacion_menu.tiempo_comida, charolas.tipo_comida:
  - 'desayuno'
  - 'almuerzo'
  - 'cena'

📊 mermas.tipo:
  - 'perdida'
  - 'danio'
  - 'vencimiento'
  - 'otros'

REGLAS DE ORO (STRINGS SIMPLES):
✅ TODOS los valores de estado son STRINGS en MINÚSCULAS
✅ NO uses mayúsculas en los valores de estado
✅ NO uses valores inventados como 'pendiente' para pedidos_compra
✅ Si no estás seguro, consulta primero: SELECT DISTINCT estado FROM tabla LIMIT 10
✅ Para pedidos activos, usa: estado IN ('borrador', 'enviado')
✅ Para facturas pendientes, usa: estado = 'pendiente'

EJEMPLOS CORRECTOS:
✅ WHERE pc.estado = 'borrador'
✅ WHERE pc.estado IN ('borrador', 'enviado')
✅ WHERE f.estado = 'pendiente'
❌ WHERE pc.estado = 'pendiente' (no existe)
❌ WHERE pc.estado = 'BORRADOR' (debe ser minúsculas)

═══════════════════════════════════════════════════════════════════════════════
USO DE CONSULTAS A BASE DE DATOS - FORMATO ESPECIAL
═══════════════════════════════════════════════════════════════════════════════

⚠️ IMPORTANTE: Cuando el usuario pregunte sobre DATOS ESPECÍFICOS del sistema (inventario, facturas, proveedores, recetas, mermas, etc.), DEBES ejecutar una consulta INMEDIATAMENTE usando [QUERY_DB]. NO digas "necesitaríamos consultar", simplemente EJECUTA la consulta.

EJEMPLOS DE CUANDO DEBES USAR [QUERY_DB]:
- "¿Cuántas libras de pollo tenemos?" → EJECUTA consulta INMEDIATAMENTE
- "Muéstrame las facturas recientes" → EJECUTA consulta INMEDIATAMENTE
- "¿Cuál fue la merma en sandía?" → EJECUTA consulta INMEDIATAMENTE
- "Items con inventario bajo" → EJECUTA consulta INMEDIATAMENTE
- Cualquier pregunta sobre datos numéricos, cantidades, listas, etc. → EJECUTA consulta INMEDIATAMENTE

FORMATO OBLIGATORIO:
[QUERY_DB]
SELECT campo1, campo2 FROM tabla WHERE condicion LIMIT 10

REGLAS DE ORO PARA CONSULTAS RÁPIDAS Y OPTIMIZADAS:
✅ SIEMPRE usa LIMIT (máximo 50-100 filas para respuestas rápidas)
✅ Usa WHERE para filtrar (activo=true, estados específicos, rangos de fechas)
✅ Usa ORDER BY con campos indexados (fecha_creacion DESC, nombre ASC)
✅ Para JOINs, usa foreign keys indexadas (proveedor_id, item_id, etc.)
✅ Selecciona SOLO campos necesarios (evita SELECT * en tablas grandes)
✅ Usa índices disponibles: activo, estado, fecha_*, proveedor_id, item_id
✅ Para fechas, usa rangos: fecha >= '2024-01-01' AND fecha <= '2024-12-31'
✅ Para búsquedas de texto, usa ILIKE: nombre ILIKE '%arroz%'

🚀 OPTIMIZACIONES AVANZADAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CONSULTAS AGRUPADAS (GROUP BY):
   → Usa GROUP BY con campos indexados cuando sea posible
   → Ejemplo: GROUP BY estado, fecha (ambos indexados)
   → Evita GROUP BY en campos calculados o no indexados

2. SUBCONSULTAS VS JOINs:
   → Prefiere JOINs sobre subconsultas cuando sea posible (más eficiente)
   → Usa EXISTS() en lugar de IN() para subconsultas grandes
   → Ejemplo: WHERE EXISTS (SELECT 1 FROM tabla WHERE condicion)

3. ÍNDICES COMPUESTOS:
   → Usa múltiples campos indexados en WHERE cuando sea posible
   → Ejemplo: WHERE estado = 'pendiente' AND fecha >= '2026-01-01' (ambos indexados)

4. CONSULTAS DE AGRUPACIÓN:
   → Para COUNT, SUM, AVG: usa índices en campos de agrupación
   → Ejemplo: SELECT estado, COUNT(*) FROM facturas WHERE fecha >= X GROUP BY estado

5. EVITAR OPERACIONES COSTOSAS:
   → Evita funciones en WHERE: WHERE DATE(fecha) = X → WHERE fecha >= X AND fecha < X+1
   → Usa índices: WHERE fecha_servicio >= '2026-01-29' AND fecha_servicio < '2026-01-30'
   → Para comparar solo fecha: DATE(fecha_servicio) = '2026-01-29' (aceptable si hay índice en fecha)

6. LÍMITES INTELIGENTES:
   → Para listas: LIMIT 20-50
   → Para agregaciones: sin LIMIT (ya agrupa)
   → Para búsquedas: LIMIT 10-20 (resultados más relevantes primero)

7. ORDENAMIENTO EFICIENTE:
   → Usa ORDER BY con campos indexados
   → Evita ORDER BY en campos calculados
   → Para fechas recientes: ORDER BY fecha DESC (usa índice)

🚨 MANEJO DE FECHAS ESPECÍFICAS - MUY IMPORTANTE:
Cuando el usuario pregunte sobre una fecha específica (ej: "29 de enero", "29 de enero de 2026", "el 29"):
1. CONVIERTE la fecha al formato PostgreSQL: 'YYYY-MM-DD'
2. Si no se menciona el año, usa el año ACTUAL (2026)
3. Para comparaciones de fecha, usa el operador correcto:
   - Fecha exacta: fecha_servicio = '2026-01-29'
   - Rango de fechas: fecha_servicio >= '2026-01-29' AND fecha_servicio < '2026-01-30'
   - Día específico: DATE(fecha_servicio) = '2026-01-29'

EJEMPLOS CORRECTOS DE CONSULTAS CON FECHAS ESPECÍFICAS:
• Usuario: "¿Cuántas charolas se sirvieron el 29 de enero?"
  [QUERY_DB]
  SELECT COUNT(*) as total_charolas, SUM(total_porciones) as total_personas
  FROM charolas 
  WHERE DATE(fecha_servicio) = '2026-01-29'
  
• Usuario: "charolas del 29 de enero"
  [QUERY_DB]
  SELECT numero_charola, fecha_servicio, ubicacion, tipo_comida, total_porciones
  FROM charolas 
  WHERE DATE(fecha_servicio) = '2026-01-29'
  ORDER BY fecha_servicio DESC

• Usuario: "facturas del mes de enero"
  [QUERY_DB]
  SELECT numero_factura, fecha_recepcion, proveedor_id, total, estado
  FROM facturas
  WHERE fecha_recepcion >= '2026-01-01' AND fecha_recepcion < '2026-02-01'
  ORDER BY fecha_recepcion DESC LIMIT 50

⚠️ IMPORTANTE: 
- SIEMPRE usa DATE() para comparar solo la fecha sin hora
- El formato debe ser 'YYYY-MM-DD' (ej: '2026-01-29')
- Si el usuario dice "hoy", usa CURRENT_DATE
- Si el usuario dice "ayer", usa CURRENT_DATE - INTERVAL '1 day'

💡 CONSULTAS EXPLORATORIAS - CUANDO NO ESTÁS SEGURO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Si no estás seguro de qué tabla usar o cómo estructurar la consulta:

1. EXPLORA LAS TABLAS DISPONIBLES:
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public' 
   ORDER BY table_name

2. VER ESTRUCTURA DE UNA TABLA:
   SELECT column_name, data_type FROM information_schema.columns 
   WHERE table_name = 'nombre_tabla' 
   ORDER BY ordinal_position

3. VER VALORES ÚNICOS DE UN CAMPO:
   SELECT DISTINCT campo FROM tabla LIMIT 20

4. VER RANGO DE FECHAS DISPONIBLES:
   SELECT MIN(fecha_campo) as fecha_min, MAX(fecha_campo) as fecha_max 
   FROM tabla

5. CONTAR REGISTROS POR CRITERIO:
   SELECT COUNT(*) FROM tabla WHERE condicion

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

📦 PEDIDOS DE COMPRA:
• Pedidos pendientes (borradores o enviados):
  SELECT pc.id, p.nombre as proveedor, pc.fecha_pedido, pc.fecha_entrega_esperada, pc.estado, pc.total
  FROM pedidos_compra pc
  JOIN proveedores p ON pc.proveedor_id = p.id
  WHERE pc.estado IN ('borrador', 'enviado')
  ORDER BY pc.fecha_entrega_esperada ASC LIMIT 20

• Pedidos que requieren acción (compras pendientes):
  SELECT pc.id, p.nombre as proveedor, pc.estado, pc.total, COUNT(pci.id) as num_items
  FROM pedidos_compra pc
  JOIN proveedores p ON pc.proveedor_id = p.id
  LEFT JOIN pedido_compra_items pci ON pc.id = pci.pedido_id
  WHERE pc.estado IN ('borrador', 'enviado')
  GROUP BY pc.id, p.nombre, pc.estado, pc.total
  ORDER BY pc.fecha_pedido DESC LIMIT 20

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
• Charolas servidas por fecha específica (ej: 29 de enero de 2026):
  SELECT numero_charola, fecha_servicio, ubicacion, tipo_comida, total_porciones
  FROM charolas 
  WHERE DATE(fecha_servicio) = '2026-01-29'
  ORDER BY fecha_servicio DESC LIMIT 20

• Charolas servidas en un rango de fechas:
  SELECT numero_charola, fecha_servicio, ubicacion, tipo_comida, total_porciones
  FROM charolas 
  WHERE fecha_servicio >= CURRENT_DATE - INTERVAL '7 days'
  ORDER BY fecha_servicio DESC LIMIT 20

• Total de personas servidas en una fecha específica:
  SELECT COUNT(*) as total_charolas, SUM(total_porciones) as total_personas
  FROM charolas 
  WHERE DATE(fecha_servicio) = '2026-01-29'

• Mermas por item (último mes):
  SELECT i.nombre, SUM(m.cantidad) as total_merma, COUNT(m.id) as num_registros
  FROM mermas m
  JOIN items i ON m.item_id = i.id
  WHERE m.fecha_merma >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY i.id, i.nombre
  ORDER BY total_merma DESC LIMIT 20

• Buscar merma de un item específico (ej: sandía):
  SELECT i.nombre, m.cantidad, m.tipo, m.fecha_merma, m.motivo, m.ubicacion
  FROM mermas m
  JOIN items i ON m.item_id = i.id
  WHERE i.nombre ILIKE '%sandia%' OR i.nombre ILIKE '%sandía%'
  ORDER BY m.fecha_merma DESC LIMIT 20

• Inventario de un item específico (ej: pollo):
  SELECT i.nombre, i.unidad, inv.cantidad_actual, inv.cantidad_minima, inv.ubicacion
  FROM inventario inv
  JOIN items i ON inv.item_id = i.id
  WHERE i.nombre ILIKE '%pollo%' AND i.activo = true
  LIMIT 10

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
✅ Usa formato de tabla cuando sea apropiado para mejor legibilidad

═══════════════════════════════════════════════════════════════════════════════
INSTRUCCIONES CRÍTICAS PARA CONSULTAS
═══════════════════════════════════════════════════════════════════════════════

🚨🚨🚨 REGLA DE ORO ABSOLUTA 🚨🚨🚨

SI EL USUARIO PREGUNTA SOBRE DATOS ESPECÍFICOS, EJECUTA LA CONSULTA DIRECTAMENTE.

❌❌❌ NUNCA DIGAS ESTO (INCORRECTO):
- "Lo siento, pero como asistente virtual, no tengo la capacidad de ejecutar consultas en tiempo real"
- "Sin embargo, puedo proporcionarte la consulta SQL que podrías ejecutar"
- "Te recomiendo que ejecutes esta consulta directamente en la base de datos"
- "No tengo acceso directo a la base de datos"

✅✅✅ SIEMPRE HAZ ESTO (CORRECTO):
EJECUTA la consulta usando [QUERY_DB] y luego interpreta los resultados.

EJEMPLO REAL:
Usuario: "¿Cuántas porciones servimos hoy?"
TÚ DEBES RESPONDER:
[QUERY_DB]
SELECT SUM(total_porciones) AS total_porciones_servidas FROM charolas WHERE fecha_servicio = CURRENT_DATE

Y cuando recibas los resultados, interpreta y responde: "Hoy se sirvieron X porciones en total."

OTRO EJEMPLO:
Usuario: "cuantas porciones servimos hoy EJECUTA consulta INMEDIATAMENTE"
TÚ DEBES RESPONDER:
[QUERY_DB]
SELECT SUM(total_porciones) AS total FROM charolas WHERE DATE(fecha_servicio) = CURRENT_DATE

EJEMPLO CON FECHA ESPECÍFICA:
Usuario: "el 29 de enero cuantas charolas se sirvieron"
TÚ DEBES RESPONDER:
[QUERY_DB]
SELECT COUNT(*) as total_charolas, SUM(total_porciones) as total_personas
FROM charolas 
WHERE DATE(fecha_servicio) = '2026-01-29'

⚠️ CRUCIAL: Si la consulta devuelve 0 filas, verifica:
1. ¿La fecha está en el formato correcto? (YYYY-MM-DD)
2. ¿Estás usando DATE() para comparar solo la fecha?
3. ¿El año es correcto? (si no se menciona, usa 2026)
4. ¿Hay datos en la tabla? Prueba: SELECT COUNT(*) FROM charolas WHERE fecha_servicio >= '2026-01-01'

RECUERDA: Tienes acceso COMPLETO y DIRECTO a la base de datos PostgreSQL. EJECUTA las consultas automáticamente cuando el usuario pregunte sobre datos específicos."""
        
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
            # HTTP-Referer es REQUERIDO por OpenRouter para evitar errores 401
            if 'openrouter.ai' in base_url.lower():
                # HTTP-Referer es obligatorio para OpenRouter
                referer = Config.OPENROUTER_HTTP_REFERER or "https://github.com/Mashi007/kohde_demo"
                headers["HTTP-Referer"] = referer
                
                # X-Title es opcional pero recomendado
                if Config.OPENROUTER_X_TITLE:
                    headers["X-Title"] = Config.OPENROUTER_X_TITLE
                else:
                    headers["X-Title"] = "Kohde ERP Restaurantes"
            
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
                # Mejorar mensajes de error según el código de estado
                error_message = f'Error al llamar a la API: {response.status_code}'
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_detail = error_data['error']
                        if isinstance(error_detail, dict):
                            error_message = f'Error {response.status_code}: {error_detail.get("message", str(error_detail))}'
                        else:
                            error_message = f'Error {response.status_code}: {error_detail}'
                    else:
                        error_message = f'Error {response.status_code}: {response.text[:200]}'
                except:
                    error_message = f'Error {response.status_code}: {response.text[:200]}'
                
                # Mensajes específicos para errores comunes
                if response.status_code == 401:
                    error_message += '\n\nSugerencia: Verifica que la API key de OpenRouter sea válida y que el header HTTP-Referer esté configurado correctamente.'
                elif response.status_code == 429:
                    error_message += '\n\nSugerencia: Has excedido el límite de solicitudes. Por favor, espera un momento antes de intentar nuevamente.'
                
                return {
                    'content': error_message,
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
