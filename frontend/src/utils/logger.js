/**
 * Sistema de logging para el frontend.
 * En producción, los logs se deshabilitan automáticamente.
 */

const isDevelopment = import.meta.env.DEV || import.meta.env.MODE === 'development'

class Logger {
  constructor() {
    this.isEnabled = isDevelopment
  }

  log(...args) {
    if (this.isEnabled) {
      console.log('[LOG]', ...args)
    }
  }

  info(...args) {
    if (this.isEnabled) {
      console.info('[INFO]', ...args)
    }
  }

  warn(...args) {
    // Los warnings siempre se muestran
    console.warn('[WARN]', ...args)
  }

  error(...args) {
    // Los errores siempre se muestran
    console.error('[ERROR]', ...args)
    
    // En producción, podrías enviar errores a un servicio de tracking
    // Ejemplo: Sentry.captureException(new Error(args.join(' ')))
  }

  debug(...args) {
    if (this.isEnabled) {
      console.debug('[DEBUG]', ...args)
    }
  }
}

export const logger = new Logger()
export default logger
