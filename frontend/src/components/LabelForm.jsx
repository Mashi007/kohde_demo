import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'
import { X, Plus } from 'lucide-react'

export default function LabelForm({ onClose, onSuccess }) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    categoria_principal: '',
    descripcion: '',
    codigo: '', // Opcional, se generará automáticamente si está vacío
  })

  const createMutation = useMutation({
    mutationFn: (data) => api.post('/logistica/labels', data),
    onSuccess: async (response) => {
      toast.success('Categoría principal creada correctamente')
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
      toast.error(error.response?.data?.error || 'Error al crear categoría principal')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!formData.categoria_principal) {
      toast.error('La categoría principal es requerida')
      return
    }

    const datosEnvio = {
      categoria_principal: formData.categoria_principal.trim(),
      // Usar la categoría como nombre también
      nombre_es: formData.categoria_principal.trim(),
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
              Nueva Categoría Principal
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
          {/* Campo de Categoría Principal */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Categoría Principal *
            </label>
            <input
              type="text"
              required
              value={formData.categoria_principal}
              onChange={(e) => setFormData({ ...formData, categoria_principal: e.target.value })}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Ej: Verduras y hortalizas"
            />
            <p className="text-xs text-slate-400 mt-1">
              Ingresa el nombre de la nueva categoría principal
            </p>
          </div>

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
                : 'Crear Categoría Principal'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
