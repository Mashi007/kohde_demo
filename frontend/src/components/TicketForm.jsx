import { useState } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'

export default function TicketForm({ ticket, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    cliente_id: ticket?.cliente_id || 1, // TODO: Obtener del contexto de usuario
    asunto: ticket?.asunto || '',
    descripcion: ticket?.descripcion || '',
    tipo: ticket?.tipo || 'consulta',
    prioridad: ticket?.prioridad || 'media',
  })

  const queryClient = useQueryClient()

  const createMutation = useMutation({
    mutationFn: (data) => api.post('/crm/tickets', data),
    onSuccess: () => {
      toast.success('Ticket creado correctamente')
      queryClient.invalidateQueries(['tickets'])
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al crear ticket')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">Cliente *</label>
        <select
          required
          value={formData.cliente_id || ''}
          onChange={(e) => setFormData({ ...formData, cliente_id: parseInt(e.target.value) })}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        >
          <option value="">Seleccionar cliente</option>
          {clientes?.map((cliente) => (
            <option key={cliente.id} value={cliente.id}>
              {cliente.nombre} {cliente.ruc_ci ? `(${cliente.ruc_ci})` : ''}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Asunto *</label>
        <input
          type="text"
          required
          value={formData.asunto}
          onChange={(e) => setFormData({ ...formData, asunto: e.target.value })}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Descripción *</label>
        <textarea
          required
          value={formData.descripcion}
          onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
          rows={4}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Tipo *</label>
          <select
            required
            value={formData.tipo}
            onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          >
            <option value="consulta">Consulta</option>
            <option value="queja">Queja</option>
            <option value="reclamo">Reclamo</option>
            <option value="sugerencia">Sugerencia</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Prioridad *</label>
          <select
            required
            value={formData.prioridad}
            onChange={(e) => setFormData({ ...formData, prioridad: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          >
            <option value="baja">Baja</option>
            <option value="media">Media</option>
            <option value="alta">Alta</option>
            <option value="urgente">Urgente</option>
          </select>
        </div>
      </div>

      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={createMutation.isPending}
          className="flex-1 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {createMutation.isPending ? 'Guardando...' : 'Crear Ticket'}
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
