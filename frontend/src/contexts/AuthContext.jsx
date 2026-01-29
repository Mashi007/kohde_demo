import { createContext, useContext, useState, useEffect } from 'react'
import api from '../config/api'
import logger from '../utils/logger'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Intentar obtener usuario del token almacenado
    const token = localStorage.getItem('token')
    if (token) {
      // Decodificar token JWT básico (sin verificación de firma)
      try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        setUser({
          id: payload.user_id || payload.sub || 1,
          email: payload.email || null,
          name: payload.name || null,
        })
      } catch (error) {
        logger.error('Error decodificando token:', error)
        localStorage.removeItem('token')
      }
    }
    setIsLoading(false)
  }, [])

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password })
      const { token, user: userData } = response.data
      
      localStorage.setItem('token', token)
      
      // Decodificar token para obtener datos del usuario
      const payload = JSON.parse(atob(token.split('.')[1]))
      const userInfo = {
        id: userData?.id || payload.user_id || payload.sub || 1,
        email: userData?.email || payload.email || email,
        name: userData?.name || payload.name || null,
      }
      
      setUser(userInfo)
      return { success: true, user: userInfo }
    } catch (error) {
      logger.error('Error en login:', error.response?.data || error.message)
      return { 
        success: false, 
        error: error.response?.data?.error || 'Error al iniciar sesión' 
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  const value = {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    // Si no hay contexto, retornar valores por defecto para desarrollo
    return {
      user: { id: 1 }, // Fallback para desarrollo
      isLoading: false,
      login: () => Promise.resolve({ success: false }),
      logout: () => {},
      isAuthenticated: false,
    }
  }
  return context
}
