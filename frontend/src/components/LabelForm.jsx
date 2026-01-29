import { useState, useMemo } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'
import logger from '../utils/logger'
import { X, Plus } from 'lucide-react'

export default function LabelForm({ onClose, onSuccess }) {
  const queryClient = useQueryClient()
  const [modoNuevaCategoria, setModoNuevaCategoria] = useState(true) // Por defecto en modo nueva categoría
  const [formData, setFormData] = useState({
    nombre_es: '',
    categoria_principal: '',
    descripcion: '',
    codigo: '', // Opcional, se generará automáticamente si está vacío
  })

  // Cargar labels existentes para obtener las categorías disponibles
  const { data: labels } = useQuery({
    queryKey: ['labels'],
    queryFn: async () => {
      try {
        const res = await api.get('/logistica/labels?activo=true')
        return res.data || []
      } catch (error) {
        logger.error('Error cargando labels:', error.response?.data || error.message)
        return []
      }
    },
    staleTime: 5 * 60 * 1000,
  })

  // Obtener categorías únicas de las labels existentes
  const categoriasExistentes = useMemo(() => {
    if (!labels || !Array.isArray(labels)) return []
    const categorias = new Set(labels.map(l => l.categoria_principal).filter(Boolean))
    return Array.from(categorias).sort()
  }, [labels])

  const createMutation = useMutation({
    mutationFn: (data) => api.post('/logistica/labels', data),
    onSuccess: async (response) => {
      toast.success('Clasificación creada correctamente')
      // Invalidar queries para refrescar la lista
      await queryClient.invalidateQueries(['labels'])
      // Llamar al callback de éxito con la nueva label ANTES de cerrar
      const nuevaLabel = response.data
      if (nuevaLabel && onSuccess) {
        // Esperar a que el callback termine antes de cerrar
        await onSuccess(nuevaLabel)
      }
      // Cerrar el modal después de que todo se haya actualizado
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al crear clasificación')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!formData.categoria_principal) {
      toast.error('La categoría principal es requerida')
      return
    }

    // Si está en modo nueva categoría, solo necesita la categoría
    // Si no, necesita nombre y categoría
    if (!modoNuevaCategoria && !formData.nombre_es) {
      toast.error('El nombre es requerido')
      return
    }

    const datosEnvio = {
      categoria_principal: formData.categoria_principal.trim(),
      // Si está en modo nueva categoría, usar la categoría como nombre también
      nombre_es: modoNuevaCategoria ? formData.categoria_principal.trim() : formData.nombre_es.trim(),
      descripcion: formData.descripcion.trim() || undefined,
      // Si el código está vacío, no enviarlo para que el backend lo genere
      codigo: formData.codigo.trim() || undefined,
    }

    createMutation.mutate(datosEnvio)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-lg border border-slate-700 w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <div className="flex items-center gap-2">
            <Plus className="w-5 h-5 text-purple-400" />
            <h2 className="text-xl font-bold">
              {modoNuevaCategoria ? 'Nueva Categoría Principal' : 'Nueva Clasificación'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-700 rounded transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Toggle entre nueva categoría o nueva clasificación */}
          <div className="flex gap-2 mb-4">
            <button
              type="button"
              onClick={() => {
                setModoNuevaCategoria(true)
                setFormData({ ...formData, nombre_es: '', categoria_principal: '' })
              }}
              className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                modoNuevaCategoria
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Nueva Categoría Principal
            </button>
            <button
              type="button"
              onClick={() => {
                setModoNuevaCategoria(false)
                setFormData({ ...formData, nombre_es: '', categoria_principal: '' })
              }}
              className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                !modoNuevaCategoria
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Nueva Clasificación
            </button>
          </div>

          {/* Campo de Categoría Principal */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Categoría Principal *
            </label>
            {modoNuevaCategoria ? (
              <input
                type="text"
                required
                value={formData.categoria_principal}
                onChange={(e) => setFormData({ ...formData, categoria_principal: e.target.value })}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
                placeholder="Ej: Verduras y hortalizas"
              />
            ) : (
              <div className="space-y-2">
                <select
                  value={formData.categoria_principal}
                  onChange={(e) => {
                    const valor = e.target.value
                    if (valor === '__NUEVA__') {
                      setModoNuevaCategoria(true)
                      setFormData({ ...formData, categoria_principal: '' })
                    } else {
                      setFormData({ ...formData, categoria_principal: valor })
                    }
                  }}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
                >
                  <option value="">Selecciona una categoría existente</option>
                  {categoriasExistentes.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                  <option value="__NUEVA__">➕ Crear nueva categoría</option>
                </select>
                {formData.categoria_principal && categoriasExistentes.includes(formData.categoria_principal) && (
                  <input
                    type="text"
                    required
                    value={formData.nombre_es}
                    onChange={(e) => setFormData({ ...formData, nombre_es: e.target.value })}
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
                    placeholder="Ej: Cebolla"
                  />
                )}
              </div>
            )}
            <p className="text-xs text-slate-400 mt-1">
              {modoNuevaCategoria 
                ? 'Ingresa el nombre de la nueva categoría principal'
                : 'Selecciona una categoría existente o crea una nueva'}
            </p>
          </div>

          {/* Campo de Nombre (solo si NO es nueva categoría) */}
          {!modoNuevaCategoria && formData.categoria_principal && categoriasExistentes.includes(formData.categoria_principal) && (
            <div>
              <label className="block text-sm font-medium mb-2">
                Nombre de la Clasificación *
              </label>
              <input
                type="text"
                required
                value={formData.nombre_es}
                onChange={(e) => setFormData({ ...formData, nombre_es: e.target.value })}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
                placeholder="Ej: Cebolla"
              />
              <p className="text-xs text-slate-400 mt-1">
                Nombre específico de la clasificación dentro de la categoría seleccionada
              </p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">
              Descripción
            </label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              rows="3"
              placeholder="Descripción opcional de la clasificación"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Código (Opcional)
            </label>
            <input
              type="text"
              value={formData.codigo}
              onChange={(e) => setFormData({ ...formData, codigo: e.target.value.toUpperCase() })}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Ej: VEG_CEBOLLA (se generará automáticamente si está vacío)"
            />
            <p className="text-xs text-slate-400 mt-1">
              Si se deja vacío, se generará automáticamente basado en la categoría y nombre
            </p>
          </div>

          {/* Botones */}
          <div className="flex justify-end gap-3 pt-4 border-t border-slate-700">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createMutation.isPending 
                ? 'Creando...' 
                : modoNuevaCategoria 
                  ? 'Crear Categoría Principal' 
                  : 'Crear Clasificación'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
