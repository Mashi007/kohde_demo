import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'

export default function ItemForm({ item, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    codigo: item?.codigo || '',
    nombre: item?.nombre || '',
    categoria: item?.categoria || 'materia_prima',
    unidad: item?.unidad || 'kg',
    costo_unitario_actual: item?.costo_unitario_actual || 0,
    activo: item?.activo !== undefined ? item.activo : true,
  })

  const queryClient = useQueryClient()

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
