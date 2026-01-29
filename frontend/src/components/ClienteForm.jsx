import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'

export default function ClienteForm({ cliente, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    nombre: cliente?.nombre || '',
    tipo: cliente?.tipo || 'persona',
    ruc_ci: cliente?.ruc_ci || '',
    telefono: cliente?.telefono || '',
    email: cliente?.email || '',
    direccion: cliente?.direccion || '',
    activo: cliente?.activo !== undefined ? cliente.activo : true,
  })

  const queryClient = useQueryClient()

  const createMutation = useMutation({
    mutationFn: (data) => api.post('/crm/clientes', data),
    onSuccess: () => {
      toast.success('Cliente creado correctamente')
      queryClient.invalidateQueries(['clientes'])
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al crear cliente')
    },
  })

  const updateMutation = useMutation({
    mutationFn: (data) => api.put(`/crm/clientes/${cliente.id}`, data),
    onSuccess: () => {
      toast.success('Cliente actualizado correctamente')
      queryClient.invalidateQueries(['clientes'])
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al actualizar cliente')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (cliente) {
      updateMutation.mutate(formData)
    } else {
      createMutation.mutate(formData)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
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
        <label className="block text-sm font-medium mb-2">Tipo *</label>
        <select
          required
          value={formData.tipo}
          onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        >
          <option value="persona">Persona</option>
          <option value="empresa">Empresa</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">RUC/CI</label>
        <input
          type="text"
          value={formData.ruc_ci}
          onChange={(e) => setFormData({ ...formData, ruc_ci: e.target.value })}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Teléfono</label>
          <input
            type="tel"
            value={formData.telefono}
            onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Email</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Dirección</label>
        <textarea
          value={formData.direccion}
          onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
          rows={3}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        />
      </div>

      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={createMutation.isPending || updateMutation.isPending}
          className="flex-1 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {createMutation.isPending || updateMutation.isPending
            ? 'Guardando...'
            : cliente
            ? 'Actualizar'
            : 'Crear'}
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
