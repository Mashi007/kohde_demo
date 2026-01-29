import { useState, useEffect } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'
import { X } from 'lucide-react'

export default function ItemForm({ item, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    codigo: item?.codigo || '',
    nombre: item?.nombre || '',
    categoria: item?.categoria || 'materia_prima',
    unidad: item?.unidad || 'kg',
    costo_unitario_actual: item?.costo_unitario_actual || 0,
    activo: item?.activo !== undefined ? item.activo : true,
    label_ids: item?.labels?.map(l => l.id) || [],
  })

  const queryClient = useQueryClient()

  // Cargar labels disponibles
  const { data: labels } = useQuery({
    queryKey: ['labels'],
    queryFn: () => api.get('/logistica/labels').then(res => res.data),
  })

  // Agrupar labels por categoría
  const labelsPorCategoria = labels?.reduce((acc, label) => {
    const cat = label.categoria_principal
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(label)
    return acc
  }, {}) || {}

  const createMutation = useMutation({
    mutationFn: (data) => api.post('/logistica/items', data),
    onSuccess: () => {
      toast.success('Item creado correctamente')
      queryClient.invalidateQueries(['items'])
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al crear item')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  const toggleLabel = (labelId) => {
    setFormData(prev => {
      const currentIds = prev.label_ids || []
      if (currentIds.includes(labelId)) {
        return { ...prev, label_ids: currentIds.filter(id => id !== labelId) }
      } else {
        return { ...prev, label_ids: [...currentIds, labelId] }
      }
    })
  }

  const removeLabel = (labelId) => {
    setFormData(prev => ({
      ...prev,
      label_ids: (prev.label_ids || []).filter(id => id !== labelId)
    }))
  }

  const getSelectedLabels = () => {
    if (!labels || !formData.label_ids) return []
    return labels.filter(l => formData.label_ids.includes(l.id))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Código *</label>
          <input
            type="text"
            required
            value={formData.codigo}
            onChange={(e) => setFormData({ ...formData, codigo: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Unidad *</label>
          <select
            required
            value={formData.unidad}
            onChange={(e) => setFormData({ ...formData, unidad: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          >
            <option value="kg">Kilogramos (kg)</option>
            <option value="g">Gramos (g)</option>
            <option value="l">Litros (l)</option>
            <option value="ml">Mililitros (ml)</option>
            <option value="unidad">Unidad</option>
            <option value="caja">Caja</option>
            <option value="paquete">Paquete</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Nombre *</label>
        <input
          type="text"
          required
          value={formData.nombre}
          onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Categoría *</label>
        <select
          required
          value={formData.categoria}
          onChange={(e) => setFormData({ ...formData, categoria: e.target.value })}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        >
          <option value="materia_prima">Materia Prima</option>
          <option value="producto_terminado">Producto Terminado</option>
          <option value="insumo">Insumo</option>
          <option value="bebida">Bebida</option>
          <option value="limpieza">Limpieza</option>
          <option value="otros">Otros</option>
        </select>
      </div>

      {/* Labels seleccionadas */}
      {getSelectedLabels().length > 0 && (
        <div>
          <label className="block text-sm font-medium mb-2">Labels Seleccionadas</label>
          <div className="flex flex-wrap gap-2">
            {getSelectedLabels().map(label => (
              <span
                key={label.id}
                className="inline-flex items-center gap-1 px-3 py-1 bg-purple-600/20 text-purple-300 rounded-full text-sm border border-purple-500/50"
              >
                {label.nombre_es}
                <button
                  type="button"
                  onClick={() => removeLabel(label.id)}
                  className="hover:text-red-400"
                >
                  <X size={14} />
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Selector de Labels */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Clasificación Internacional de Alimentos
        </label>
        <div className="max-h-64 overflow-y-auto bg-slate-800 border border-slate-600 rounded-lg p-4 space-y-4">
          {Object.entries(labelsPorCategoria).map(([categoria, labelsCat]) => (
            <div key={categoria}>
              <h4 className="text-sm font-semibold text-purple-400 mb-2">{categoria}</h4>
              <div className="flex flex-wrap gap-2">
                {labelsCat.map(label => {
                  const isSelected = formData.label_ids?.includes(label.id)
                  return (
                    <button
                      key={label.id}
                      type="button"
                      onClick={() => toggleLabel(label.id)}
                      className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                        isSelected
                          ? 'bg-purple-600 text-white border border-purple-500'
                          : 'bg-slate-700 text-slate-300 border border-slate-600 hover:bg-slate-600'
                      }`}
                    >
                      {label.nombre_es}
                    </button>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-400 mt-2">
          Selecciona las clasificaciones que aplican a este alimento para generar recetas/menús
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Costo Unitario</label>
        <input
          type="number"
          step="0.01"
          min="0"
          value={formData.costo_unitario_actual}
          onChange={(e) => setFormData({ ...formData, costo_unitario_actual: parseFloat(e.target.value) || 0 })}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        />
      </div>

      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={createMutation.isPending}
          className="flex-1 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {createMutation.isPending ? 'Guardando...' : 'Crear Item'}
        </button>
        <button
          type="button"
          onClick={onClose}
          className="flex-1 bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg"
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}
