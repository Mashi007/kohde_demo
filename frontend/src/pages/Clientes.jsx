import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../config/api'
import { Plus, Search, Edit, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Clientes() {
  const [busqueda, setBusqueda] = useState('')
  const queryClient = useQueryClient()

  const { data: clientes, isLoading } = useQuery({
    queryKey: ['clientes', busqueda],
    queryFn: () => 
      api.get('/crm/clientes', { params: { busqueda } }).then(res => res.data),
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/crm/clientes/${id}`),
    onSuccess: () => {
      toast.success('Cliente eliminado')
      queryClient.invalidateQueries(['clientes'])
    },
    onError: () => toast.error('Error al eliminar cliente'),
  })

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Clientes</h1>
        <button className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2">
          <Plus size={20} />
          Nuevo Cliente
        </button>
      </div>

      {/* Búsqueda */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
          <input
            type="text"
            placeholder="Buscar por nombre, RUC o teléfono..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
      </div>

      {/* Tabla */}
      {isLoading ? (
        <div className="text-center py-8">Cargando...</div>
      ) : (
        <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-700">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium">Nombre</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Tipo</th>
                <th className="px-6 py-3 text-left text-sm font-medium">RUC/CI</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Teléfono</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Email</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {clientes?.map((cliente) => (
                <tr key={cliente.id} className="hover:bg-slate-700/50">
                  <td className="px-6 py-4">{cliente.nombre}</td>
                  <td className="px-6 py-4 capitalize">{cliente.tipo}</td>
                  <td className="px-6 py-4">{cliente.ruc_ci || '-'}</td>
                  <td className="px-6 py-4">{cliente.telefono || '-'}</td>
                  <td className="px-6 py-4">{cliente.email || '-'}</td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2">
                      <button className="text-blue-400 hover:text-blue-300">
                        <Edit size={18} />
                      </button>
                      <button 
                        onClick={() => deleteMutation.mutate(cliente.id)}
                        className="text-red-400 hover:text-red-300"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
