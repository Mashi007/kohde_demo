import { useState } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import api, { extractData } from '../config/api'
import toast from 'react-hot-toast'

export default function MermaForm({ merma, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    item_id: merma?.item_id || null,
    fecha_merma: merma?.fecha_merma ? new Date(merma.fecha_merma).toISOString().slice(0, 16) : new Date().toISOString().slice(0, 16),
    tipo: merma?.tipo || 'otro',
    cantidad: merma?.cantidad || 0,
    unidad: merma?.unidad || '',
    costo_unitario: merma?.costo_unitario || 0,
    motivo: merma?.motivo || '',
    ubicacion: merma?.ubicacion || '',
  })

  const queryClient = useQueryClient()

  const { data: itemsResponse } = useQuery({
    queryKey: ['items'],
    queryFn: () => api.get('/logistica/items').then(res => {
      const items = extractData(res)
      return Array.isArray(items) ? items : []
    }),
  })
  
  const items = Array.isArray(itemsResponse) ? itemsResponse : []

  const createMutation = useMutation({
    mutationFn: (data) => api.post('/reportes/mermas', data),
    onSuccess: () => {
      toast.success('Merma registrada correctamente')
      queryClient.invalidateQueries(['mermas'])
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al registrar merma')
    },
  })

  const handleItemChange = (itemId) => {
    const item = items?.find(i => i.id === parseInt(itemId))
    if (item) {
      setFormData({
        ...formData,
        item_id: parseInt(itemId),
        unidad: item.unidad,
        costo_unitario: item.costo_unitario_actual || 0
      })
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">Item *</label>
        <select
          required
          value={formData.item_id || ''}
          onChange={(e) => handleItemChange(e.target.value)}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        >
          <option value="">Seleccionar item</option>
          {items?.map((item) => (
            <option key={item.id} value={item.id}>
              {item.nombre} ({item.codigo})
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Fecha de Merma *</label>
          <input
            type="datetime-local"
            required
            value={formData.fecha_merma}
            onChange={(e) => setFormData({ ...formData, fecha_merma: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Tipo *</label>
          <select
            required
            value={formData.tipo}
            onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          >
            <option value="vencimiento">Vencimiento</option>
            <option value="deterioro">Deterioro</option>
            <option value="preparacion">Preparación</option>
            <option value="servicio">Servicio</option>
            <option value="otro">Otro</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Cantidad *</label>
          <input
            type="number"
            step="0.01"
            min="0"
            required
            value={formData.cantidad}
            onChange={(e) => setFormData({ ...formData, cantidad: parseFloat(e.target.value) || 0 })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Unidad *</label>
          <input
            type="text"
            required
            value={formData.unidad}
            onChange={(e) => setFormData({ ...formData, unidad: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Costo Unitario</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={formData.costo_unitario}
            onChange={(e) => setFormData({ ...formData, costo_unitario: parseFloat(e.target.value) || 0 })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Ubicación</label>
        <input
          type="text"
          value={formData.ubicacion}
          onChange={(e) => setFormData({ ...formData, ubicacion: e.target.value })}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Motivo</label>
        <textarea
          value={formData.motivo}
          onChange={(e) => setFormData({ ...formData, motivo: e.target.value })}
          rows={3}
          placeholder="Describa el motivo de la merma..."
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        />
      </div>

      {formData.cantidad > 0 && formData.costo_unitario > 0 && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4">
          <p className="text-sm text-red-400">
            Costo Total de Merma: <span className="font-bold">
              ${(formData.cantidad * formData.costo_unitario).toFixed(2)}
            </span>
          </p>
        </div>
      )}

      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={createMutation.isPending}
          className="flex-1 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {createMutation.isPending ? 'Guardando...' : 'Registrar Merma'}
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
