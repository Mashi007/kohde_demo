import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'
import { X, Plus } from 'lucide-react'

const CATEGORIAS_DISPONIBLES = [
  'Verduras y hortalizas',
  'Frutas',
  'Carnes rojas',
  'Aves y pollo',
  'Pescados y mariscos',
  'Proteínas alternativas',
  'Lácteos y huevos',
  'Productos secos y granos',
  'Condimentos y especias',
  'Salsas y envasados',
  'Bebidas gaseosas',
  'Bebidas no alcohólicas',
  'Bebidas alcohólicas',
  'Panadería y repostería',
  'Congelados',
  'Artículos de limpieza y desechables',
  'Otros / suministros menores',
]

export default function LabelForm({ onClose, onSuccess }) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    nombre_es: '',
    nombre_en: '',
    categoria_principal: '',
    descripcion: '',
    codigo: '', // Opcional, se generará automáticamente si está vacío
  })

  const createMutation = useMutation({
    mutationFn: (data) => api.post('/logistica/labels', data),
    onSuccess: (data) => {
      toast.success('Clasificación creada correctamente')
      queryClient.invalidateQueries(['labels'])
      onSuccess?.(data.data)
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al crear clasificación')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!formData.nombre_es || !formData.categoria_principal) {
      toast.error('El nombre y la categoría son requeridos')
      return
    }

    const datosEnvio = {
      ...formData,
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
            <h2 className="text-xl font-bold">Nueva Clasificación</h2>
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
          <div>
            <label className="block text-sm font-medium mb-2">
              Nombre (Español) *
            </label>
            <input
              type="text"
              required
              value={formData.nombre_es}
              onChange={(e) => setFormData({ ...formData, nombre_es: e.target.value })}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Ej: Cebolla"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Nombre (Inglés)
            </label>
            <input
              type="text"
              value={formData.nombre_en}
              onChange={(e) => setFormData({ ...formData, nombre_en: e.target.value })}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Ej: Onion"
            />
            <p className="text-xs text-slate-400 mt-1">
              Si no se proporciona, se usará el nombre en español
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Categoría Principal *
            </label>
            <select
              required
              value={formData.categoria_principal}
              onChange={(e) => setFormData({ ...formData, categoria_principal: e.target.value })}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
            >
              <option value="">Selecciona una categoría</option>
              {CATEGORIAS_DISPONIBLES.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
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
              {createMutation.isPending ? 'Creando...' : 'Crear Clasificación'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
