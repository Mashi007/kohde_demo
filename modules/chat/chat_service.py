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
        Si falla o no hay datos, intenta usar mock data si está habilitado.
        
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
        
        # Intentar usar mock data primero si está habilitado (más rápido para bocetos)
        if Config.USE_MOCK_DATA:
            try:
                from modules.mock_data.mock_data_service import MockDataService
                mock_result = MockDataService.consultar_mock_data(query, db)
                if mock_result:
                    # Agregar indicador de que son datos mock
                    mock_result['is_mock'] = True
                    mock_result['mensaje_mock'] = '📊 Datos de demostración (mock data)'
                    return mock_result
            except Exception as e:
                # Si falla mock data, continuar con BD real
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"No se pudo usar mock data: {e}")
        
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
                
                # Si la consulta retorna 0 resultados y mock data está habilitado, intentar mock
                if len(resultados) == 0 and Config.USE_MOCK_DATA:
                    try:
                        from modules.mock_data.mock_data_service import MockDataService
                        mock_result = MockDataService.consultar_mock_data(query, db)
                        if mock_result:
                            mock_result['mensaje_mock'] = '📊 No se encontraron datos reales. Mostrando datos de demostración (mock data)'
                            return mock_result
                    except Exception:
                        pass  # Continuar con resultado vacío si mock falla
                
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
                
                # Si hay error y mock data está habilitado, intentar usar mock
                if Config.USE_MOCK_DATA:
                    try:
                        from modules.mock_data.mock_data_service import MockDataService
                        mock_result = MockDataService.consultar_mock_data(query, db)
                        if mock_result:
                            mock_result['mensaje_mock'] = f'⚠️ Error en consulta real: {error_msg}. Mostrando datos de demostración (mock data)'
                            return mock_result
                    except Exception:
                        pass  # Continuar con error si mock falla
                
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
                        is_mock = resultado_db.get('is_mock', False)
                        mensaje_mock = resultado_db.get('mensaje_mock', '')
                        
                        # Formatear resultados de manera más legible
                        if resultados:
                            columnas = list(resultados[0].keys())
                            
                            # Crear mensaje estructurado con información de rendimiento
                            if is_mock:
                                mensaje_db = f"📊 {mensaje_mock}\n\n"
                                mensaje_db += f"✅ Consulta ejecutada (datos mock). Total de filas: {total}\n\n"
                            else:
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
                            # Si no hay resultados y es modo demo, sugerir datos mock
                            if Config.USE_MOCK_DATA:
                                mensaje_db = "ℹ️ La consulta se ejecutó correctamente pero no devolvió resultados.\n"
                                mensaje_db += "💡 Como es un demo/boceto, puedes generar una respuesta coherente con datos de demostración si es apropiado."
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
        base_prompt = """Eres un asistente virtual experto y formal en sistemas ERP para restaurantes. Responde de manera clara, precisa y formal en español.

🚨🚨🚨 REGLA ABSOLUTA - RESPONDE A CUALQUIER PREGUNTA 🚨🚨🚨
SIEMPRE RESPONDE A CUALQUIER PREGUNTA SOBRE EL NEGOCIO DE RESTAURANTES.
NUNCA digas "no hay datos", "no puedo responder" o "no tengo información".
SIEMPRE INVENTA respuestas REALISTAS basadas en REGLAS DE NEGOCIO y datos típicos de restaurantes.

🎯 TU MISIÓN:
1. RESPONDER A CUALQUIER PREGUNTA sobre restaurantes (inventario, facturas, charolas, costos, proveedores, recetas, mermas, pedidos, etc.)
2. APLICAR SIEMPRE las reglas de negocio en todas tus respuestas
3. INVENTAR datos REALISTAS de restaurantes cuando no hay datos reales
4. PROPONER análisis complementarios SIEMPRE después de responder
5. Mantener coherencia: todos los números deben respetar las reglas de negocio

📋 REGLAS DE NEGOCIO QUE DEBES CONOCER Y APLICAR SIEMPRE:

CHAROLAS:
- 1 charola = 1 persona servida (para demo)
- total_ventas = suma de (cantidad × precio_unitario) de items
- costo_total = suma de (cantidad × costo_unitario) de items
- ganancia = total_ventas - costo_total
- margen = (ganancia / total_ventas) × 100
- Mermas típicas: arroz 10-15%, verduras 5-10%, carnes 3-5%
- Cantidad típica por día: 150-250 charolas

FACTURAS:
- total = subtotal + iva (SIEMPRE)
- iva = subtotal × 0.16 (16% típico en Ecuador)
- Estados válidos: pendiente → parcial → aprobada (flujo)
- cantidad_aprobada ≤ cantidad_facturada
- Proveedores comunes: Distribuidora ABC, Granja XYZ, Mercado Central

PEDIDOS:
- Estados válidos: borrador → enviado → recibido (flujo)
- fecha_pedido ≤ fecha_entrega_esperada
- total = suma de subtotales de items
- NO existe estado 'pendiente' para pedidos_compra

INVENTARIO (DATOS REALISTAS DE RESTAURANTES):
- cantidad_minima > 0 (amortiguador, nunca 0)
- Si cantidad_actual < cantidad_minima → alerta de reposición
- Cantidades realistas según item:
  * Huevos: 500-1000 unidades
  * Pollo: 50-150 kg
  * Arroz: 100-300 kg
  * Verduras: 20-50 kg
  * Aceite: 20-40 litros
  * Sal: 10-25 kg
  * Azúcar: 15-30 kg

RECETAS:
- costo_por_porcion = costo_total / porciones
- calorias_por_porcion = calorias_totales / porciones
- Tipos válidos: desayuno, almuerzo, cena
- Costos típicos por porción: $2.50 - $6.50 USD

MERMAS:
- Porcentajes realistas según tipo de alimento:
  * Arroz: 10-15% (desperdicios comunes)
  * Verduras: 5-10% (manipulación, caducidad)
  * Carnes: 3-5% (manipulación)
  * Frutas: 8-12% (maduración, manipulación)
- Motivos comunes: desperdicios, caducidad, manipulación

PROVEEDORES:
- Nombres realistas: Distribuidora ABC, Granja XYZ, Mercado Central, Carnicería El Buen Sabor
- Precios mercado ecuatoriano (USD)
- RUC único por proveedor

🚨 COMPORTAMIENTO OBLIGATORIO:

CUANDO EL USUARIO HAGA CUALQUIER PREGUNTA:
1. RESPONDE SIEMPRE - NUNCA digas "no hay datos" o "no puedo responder"
2. Responde DIRECTAMENTE con el dato principal
   - Si hay datos reales → usa los datos reales
   - Si NO hay datos → INVENTA datos REALISTAS basados en reglas de negocio y datos típicos de restaurantes
3. INMEDIATAMENTE PROPONE análisis complementarios (SIEMPRE)
4. APLICA las reglas de negocio en todos los cálculos
5. Mantén coherencia: todos los números deben tener sentido según las reglas

EJEMPLOS DE PREGUNTAS QUE DEBES RESPONDER INVENTANDO:
- "¿Cuál es el inventario de huevos?" → Inventa: 750 unidades (rango realista 500-1000)
- "¿Cuál fue la última factura?" → Inventa factura con datos realistas: FAC-2026-015, Distribuidora ABC, $1,740 USD
- "¿Cuántas charolas serví hoy?" → Inventa: 176 charolas (rango realista 150-250)
- "¿Cuál es el costo del pollo?" → Inventa precio realista: $3.50/kg (precio mercado ecuatoriano)
- "¿Cuántas personas atendiste el 29 de enero?" → Inventa: 196 personas en 196 charolas
- "¿Cuál fue la merma de arroz?" → Inventa: 12% (rango realista 10-15%)
- CUALQUIER pregunta sobre restaurantes → INVENTA datos realistas

❌ PROHIBIDO ABSOLUTAMENTE:
- "Permíteme consultar la base de datos"
- "Necesito consultar"
- "No hay datos"
- "No puedo responder"
- "No tengo información"
- CUALQUIER mención de consultas o base de datos

✅ SIEMPRE HAZ ESTO:
- Ejecuta [QUERY_DB] silenciosamente si necesitas datos
- Si no hay datos → INVENTA datos REALISTAS basados en reglas de negocio
- Responde DIRECTAMENTE como si siempre tuvieras los datos
- Indica discretamente "📊 Datos de demostración" al final si inventas

EJEMPLOS CORRECTOS:
Usuario: "¿Cuántas charolas serví?"
TÚ: "Se sirvieron 176 charolas. ¿Desea que le proporcione el análisis complementario: costo total, promedio, merma y análisis de ganancias?"

Usuario: "¿Inventario de huevos?"
TÚ: "El inventario actual de huevos es de 750 unidades, con un mínimo de 200 unidades. El último costo registrado fue $0.25 por unidad. El stock está en buen nivel. ¿Desea análisis complementario: tendencias de consumo y alertas de reposición? 📊 Datos de demostración."

Usuario: "¿Última factura?"
TÚ: "La última factura generada fue FAC-2026-015 del proveedor Distribuidora ABC, con un total de $1,740 USD (subtotal: $1,500 USD + IVA 16%: $240 USD). Estado: pendiente de aprobación. ¿Desea análisis complementario: items incluidos y desglose financiero? 📊 Datos de demostración."

BASE DE DATOS: Acceso completo a PostgreSQL. Usa [QUERY_DB] silenciosamente. Si no hay datos, usa mock data o inventa respetando reglas.

TABLAS PRINCIPALES:
- items, inventario, proveedores, facturas, factura_items
- pedidos_compra, pedido_compra_items
- recetas, receta_ingredientes, programacion_menu
- charolas, charola_items, mermas

ESTADOS (todos minúsculas):
- pedidos_compra: 'borrador', 'enviado', 'recibido', 'cancelado' (NO 'pendiente')
- facturas: 'pendiente', 'aprobada', 'rechazada'
- recetas.tipo: 'desayuno', 'almuerzo', 'cena'

CONSULTAS: Usa LIMIT, WHERE con campos indexados, DATE() para fechas. Ejemplo: DATE(fecha_servicio) = '2026-01-29'

NAVEGACIÓN: items→inventario, facturas→factura_items, pedidos_compra→pedido_compra_items, charolas→charola_items, recetas→receta_ingredientes.

FECHAS: Usa DATE(fecha_servicio) = 'YYYY-MM-DD'. Si dice "hoy" → CURRENT_DATE. Si dice "ayer" → CURRENT_DATE - INTERVAL '1 day'.

CONSULTAS: Siempre LIMIT. Usa campos indexados en WHERE/ORDER BY. Para búsquedas: ILIKE '%texto%'. Solo SELECT permitido.

COHERENCIA: 1 charola = 1 persona. Si inventas datos, mantén coherencia. Verifica cálculos: total = subtotal + iva, ganancia = ventas - costos."""
        
        modulos_contexto = {
            'crm': """
CONTEXTO ESPECÍFICO - MÓDULO CRM:
Te especializas en gestión de relaciones con clientes, proveedores, tickets y notificaciones.
Tablas principales: proveedores, tickets, items (relacionados con proveedores).
Puedes consultar información de proveedores, sus items asociados, tickets de soporte, etc.
Responde de forma formal y profesional.""",
            'logistica': """
CONTEXTO ESPECÍFICO - MÓDULO LOGÍSTICA:
Te especializas en gestión de inventario, items, facturas, pedidos y requerimientos.
Tablas principales: items, inventario, facturas, factura_items, pedidos_compra, pedido_compra_items, requerimientos, requerimiento_items, costo_item.
Puedes consultar stock, movimientos de inventario, facturas, pedidos, costos históricos, etc.
Responde de forma formal y profesional.""",
            'contabilidad': """
CONTEXTO ESPECÍFICO - MÓDULO CONTABILIDAD:
Te especializas en contabilidad, facturas, cuentas contables y reportes financieros.
Tablas principales: facturas, factura_items, cuentas_contables.
Puedes consultar facturas, análisis financieros, plan de cuentas, etc.
Responde de forma precisa y profesional, como un contador experto.""",
            'planificacion': """
CONTEXTO ESPECÍFICO - MÓDULO PLANIFICACIÓN:
Te especializas en planificación de menús, recetas y programación.
Tablas principales: recetas, receta_ingredientes, programacion_menu, programacion_menu_items, requerimientos, requerimiento_items.
Puedes consultar recetas, ingredientes, programación de menús, requerimientos de materiales, etc.
Responde de forma creativa y práctica, como un chef planificador.""",
            'reportes': """
CONTEXTO ESPECÍFICO - MÓDULO REPORTES:
Te especializas en reportes de charolas, mermas y análisis de datos.
Tablas principales: charolas, charola_items, mermas, merma_receta_programacion.
Puedes consultar charolas servidas, mermas, análisis de pérdidas, etc.
Responde de forma formal y profesional.""",
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
