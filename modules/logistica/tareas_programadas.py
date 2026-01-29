"""
Tareas programadas para el módulo de logística.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import atexit
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(daemon=True)

def configurar_tareas_programadas(app):
    """
    Configura las tareas programadas de la aplicación.
    
    Args:
        app: Instancia de Flask
    """
    with app.app_context():
        from models import db
        from modules.logistica.costos import CostoService
        
        def recalcular_costos_semanales():
            """
            Tarea programada: Recalcula costos unitarios y desviaciones cada sábado.
            Ejecuta el recálculo para todos los items activos.
            """
            try:
                logger.info(f"[{datetime.now()}] Iniciando recálculo semanal de costos...")
                
                # Crear sesión de base de datos
                session = db.session
                
                # Recalcular todos los costos
                resultado = CostoService.recalcular_todos_los_costos(session)
                
                logger.info(
                    f"[{datetime.now()}] Recálculo completado: "
                    f"{resultado['calculados']} calculados, "
                    f"{resultado['sin_datos']} sin datos, "
                    f"{resultado['errores']} errores de {resultado['total']} items totales"
                )
                
                # Commit de los cambios
                session.commit()
                
            except Exception as e:
                logger.error(f"[{datetime.now()}] Error en recálculo semanal de costos: {e}")
                import traceback
                traceback.print_exc()
                if 'session' in locals():
                    session.rollback()
        
        # Programar tarea: Cada sábado a las 2:00 AM (hora del servidor)
        # CronTrigger: day_of_week='sat' (0=lunes, 6=domingo, pero 'sat' es sábado)
        scheduler.add_job(
            func=recalcular_costos_semanales,
            trigger=CronTrigger(day_of_week='sat', hour=2, minute=0),
            id='recalcular_costos_semanales',
            name='Recálculo semanal de costos unitarios y desviaciones',
            replace_existing=True
        )
        
        logger.info("Tareas programadas configuradas:")
        logger.info("  - Recálculo de costos: Cada sábado a las 2:00 AM")
        
        # Iniciar el scheduler
        scheduler.start()
        
        # Registrar shutdown al cerrar la aplicación
        atexit.register(lambda: scheduler.shutdown())
