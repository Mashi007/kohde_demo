import toast from 'react-hot-toast'
import logger from './logger'

/**
 * Maneja errores de manera consistente y muestra mensajes descriptivos.
 */
export function handleApiError(error, defaultMessage = 'Ocurrió un error') {
  // Log del error para debugging
  logger.error('API Error:', error)

  // Determinar el mensaje de error apropiado
  let message = defaultMessage
  let type = 'error'

  if (error.response) {
    // Error con respuesta del servidor
    const status = error.response.status
    const data = error.response.data

    switch (status) {
      case 400:
        message = data.error || data.message || 'Datos inválidos. Por favor, verifica la información ingresada.'
        type = 'error'
        break
      case 401:
        message = 'Sesión expirada. Por favor, inicia sesión nuevamente.'
        type = 'error'
        break
      case 403:
        message = 'No tienes permisos para realizar esta acción.'
        type = 'error'
        break
      case 404:
        message = data.error || 'Recurso no encontrado.'
        type = 'warning'
        break
      case 409:
        message = data.error || 'Conflicto: El recurso ya existe o está en uso.'
        type = 'warning'
        break
      case 422:
        message = data.error || data.message || 'Error de validación. Verifica los datos ingresados.'
        type = 'error'
        break
      case 429:
        message = 'Demasiadas peticiones. Por favor, espera un momento antes de intentar nuevamente.'
        type = 'warning'
        break
      case 500:
        message = 'Error del servidor. Por favor, intenta nuevamente más tarde.'
        type = 'error'
        break
      case 503:
        message = 'Servicio temporalmente no disponible. Por favor, intenta más tarde.'
        type = 'warning'
        break
      default:
        message = data.error || data.message || `Error ${status}: ${defaultMessage}`
        type = 'error'
    }
  } else if (error.request) {
    // Error de red (sin respuesta del servidor)
    if (error.isTimeout) {
      message = 'La petición tardó demasiado. Por favor, intenta nuevamente.'
    } else if (error.isNetworkError) {
      message = 'Sin conexión a internet. Verifica tu conexión.'
    } else {
      message = 'Error de conexión. Verifica tu conexión a internet.'
    }
    type = 'error'
  } else {
    // Error al configurar la petición
    message = error.message || defaultMessage
    type = 'error'
  }

  // Mostrar toast según el tipo
  if (type === 'warning') {
    toast.error(message, { duration: 5000 })
  } else {
    toast.error(message, { duration: 6000 })
  }

  return { message, type }
}

/**
 * Maneja errores de validación de formularios.
 */
export function handleValidationError(errors) {
  if (typeof errors === 'string') {
    toast.error(errors)
    return
  }

  if (Array.isArray(errors)) {
    errors.forEach(error => {
      toast.error(error)
    })
    return
  }

  if (typeof errors === 'object') {
    Object.values(errors).forEach(error => {
      if (typeof error === 'string') {
        toast.error(error)
      } else if (Array.isArray(error)) {
        error.forEach(err => toast.error(err))
      }
    })
  }
}
