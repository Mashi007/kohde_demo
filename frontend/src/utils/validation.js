/**
 * Utilidades de validación y sanitización.
 */

/**
 * Valida tipos de archivo permitidos.
 */
export const ALLOWED_FILE_TYPES = {
  image: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
  pdf: ['application/pdf'],
  document: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  all: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'application/pdf']
}

/**
 * Valida el tipo de archivo.
 */
export function validateFileType(file, allowedTypes = ALLOWED_FILE_TYPES.all) {
  if (!file) {
    return { valid: false, error: 'No se seleccionó ningún archivo' }
  }

  if (!allowedTypes.includes(file.type)) {
    const types = allowedTypes.map(t => t.split('/')[1]).join(', ')
    return {
      valid: false,
      error: `Tipo de archivo no permitido. Tipos permitidos: ${types}`
    }
  }

  return { valid: true }
}

/**
 * Valida el tamaño del archivo.
 */
export function validateFileSize(file, maxSizeMB = 16) {
  if (!file) {
    return { valid: false, error: 'No se seleccionó ningún archivo' }
  }

  const maxSizeBytes = maxSizeMB * 1024 * 1024
  if (file.size > maxSizeBytes) {
    return {
      valid: false,
      error: `El archivo es demasiado grande. Tamaño máximo: ${maxSizeMB}MB`
    }
  }

  return { valid: true }
}

/**
 * Valida archivo completo (tipo y tamaño).
 */
export function validateFile(file, options = {}) {
  const {
    allowedTypes = ALLOWED_FILE_TYPES.all,
    maxSizeMB = 16
  } = options

  const typeValidation = validateFileType(file, allowedTypes)
  if (!typeValidation.valid) {
    return typeValidation
  }

  const sizeValidation = validateFileSize(file, maxSizeMB)
  if (!sizeValidation.valid) {
    return sizeValidation
  }

  return { valid: true }
}

/**
 * Sanitiza texto para prevenir XSS.
 * Nota: En producción, usar DOMPurify para sanitización completa.
 */
export function sanitizeText(text) {
  if (typeof text !== 'string') {
    return ''
  }

  // Escapar caracteres HTML básicos
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')
}

/**
 * Valida email.
 */
export function validateEmail(email) {
  if (!email) {
    return { valid: false, error: 'El email es requerido' }
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    return { valid: false, error: 'El email no es válido' }
  }

  return { valid: true }
}

/**
 * Valida número positivo.
 */
export function validatePositiveNumber(value, min = 0) {
  const num = parseFloat(value)
  
  if (isNaN(num)) {
    return { valid: false, error: 'Debe ser un número válido' }
  }

  if (num < min) {
    return { valid: false, error: `Debe ser mayor o igual a ${min}` }
  }

  return { valid: true, value: num }
}

/**
 * Valida que un campo requerido no esté vacío.
 */
export function validateRequired(value, fieldName = 'Este campo') {
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    return { valid: false, error: `${fieldName} es requerido` }
  }

  return { valid: true }
}

/**
 * Valida longitud de texto.
 */
export function validateLength(text, min = 0, max = Infinity, fieldName = 'Este campo') {
  if (!text) {
    return { valid: false, error: `${fieldName} es requerido` }
  }

  const length = text.trim().length

  if (length < min) {
    return { valid: false, error: `${fieldName} debe tener al menos ${min} caracteres` }
  }

  if (length > max) {
    return { valid: false, error: `${fieldName} no puede tener más de ${max} caracteres` }
  }

  return { valid: true }
}
