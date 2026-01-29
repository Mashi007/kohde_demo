/**
 * Función debounce para limitar la frecuencia de llamadas.
 */
export function debounce(func, wait = 300) {
  let timeout

  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }

    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Hook personalizado para debounce (para usar en componentes React).
 * Nota: Requiere imports: import { useState, useEffect } from 'react'
 */
export function useDebounce(value, delay = 300) {
  // Esta función requiere useState y useEffect de React
  // Se debe usar dentro de un componente React
  // Por ahora, se usa la función debounce directamente en lugar del hook
  return value
}
