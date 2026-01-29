import axios from 'axios'
import logger from '../utils/logger'

// URL del backend - se configura desde variable de entorno
// En producción: https://kohde-demo-ewhi.onrender.com/api
// En desarrollo: http://localhost:5000/api
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 segundos de timeout
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para agregar token si existe
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    logger.debug('Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    logger.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Interceptor para manejar errores y retry
let retryCount = 0
const MAX_RETRIES = 3
const RETRY_DELAY = 1000 // 1 segundo

const retryRequest = (config) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(api(config))
    }, RETRY_DELAY * Math.pow(2, retryCount))
  })
}

api.interceptors.response.use(
  (response) => {
    retryCount = 0 // Reset retry count on success
    logger.debug('Response:', response.status, response.config.url)
    return response
  },
  async (error) => {
    const config = error.config

    // Manejo de errores de red y timeouts
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        logger.error('Request timeout:', config.url)
        // No retry para timeouts, el usuario puede intentar manualmente
        return Promise.reject({
          ...error,
          message: 'La petición tardó demasiado. Por favor, intenta nuevamente.',
          isTimeout: true,
        })
      } else {
        logger.error('Network error:', error.message)
        // Retry para errores de red (sin conexión, etc.)
        if (retryCount < MAX_RETRIES && config && !config.__isRetry) {
          retryCount++
          config.__isRetry = true
          logger.info(`Retrying request (${retryCount}/${MAX_RETRIES}):`, config.url)
          return retryRequest(config)
        }
        return Promise.reject({
          ...error,
          message: 'Sin conexión a internet. Verifica tu conexión.',
          isNetworkError: true,
        })
      }
    }

    // Manejo de errores HTTP
    const status = error.response?.status

    if (status === 401) {
      // Token expirado o inválido
      logger.warn('Unauthorized - removing token')
      localStorage.removeItem('token')
      // Redirigir a login solo si no estamos ya en la página de login
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
      return Promise.reject({
        ...error,
        message: 'Sesión expirada. Por favor, inicia sesión nuevamente.',
        isUnauthorized: true,
      })
    }

    if (status === 429) {
      // Too Many Requests
      const retryAfter = error.response.headers['retry-after']
      logger.warn('Rate limited - retry after:', retryAfter)
      return Promise.reject({
        ...error,
        message: 'Demasiadas peticiones. Por favor, espera un momento antes de intentar nuevamente.',
        isRateLimited: true,
        retryAfter,
      })
    }

    // Retry para errores 5xx (errores del servidor)
    if (status >= 500 && status < 600 && retryCount < MAX_RETRIES && config && !config.__isRetry) {
      retryCount++
      config.__isRetry = true
      logger.info(`Retrying request (${retryCount}/${MAX_RETRIES}) due to server error:`, config.url)
      return retryRequest(config)
    }

    retryCount = 0 // Reset retry count
    logger.error('Response error:', status, error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default api
