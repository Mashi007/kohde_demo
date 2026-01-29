import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../config/api'
import { Package, Plus, Check, X, Search, Filter, User, Calendar } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import toast from 'react-hot-toast'
import Modal from '../components/Modal'
import PedidoInternoForm from '../components/PedidoInternoForm'

export default function PedidosInternos() {
  const [showModal, setShowModal] = useState(false)
  const [pedidoSeleccionado, setPedidoSeleccionado] = useState(null)
  const [filtroEstado, setFiltroEstado] = useState('')
  const [busqueda, setBusqueda] = useState('')
  
  const queryClient = useQueryClient()

  const { data: pedidos, isLoading } = useQuery({
    queryKey: ['pedidos-internos', filtroEstado],
    queryFn: () => {
      const params = {}
      if (filtroEstado) params.estado = filtroEstado
      return api.get('/logistica/pedidos-internos', { params }).then(res => res.data)
    },
  })

  const confirmarEntregaMutation = useMutation({
    mutationFn: ({ pedidoId, recibidoPorId, recibidoPorNombre }) =>
      api.post(`/logistica/pedidos-internos/${pedidoId}/confirmar`, {
        recibido_por_id: recibidoPorId,
        recibido_por_nombre: recibidoPorNombre
      }),
    onSuccess: () => {
      toast.success('Pedido confirmado y inventario actualizado')
      queryClient.invalidateQueries(['pedidos-internos'])
      queryClient.invalidateQueries(['inventario'])
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al confirmar pedido')
    },
  })

  const cancelarPedidoMutation = useMutation({
    mutationFn: (pedidoId) =>
      api.post(`/logistica/pedidos-internos/${pedidoId}/cancelar`),
    onSuccess: () => {
      toast.success('Pedido cancelado')
      queryClient.invalidateQueries(['pedidos-internos'])
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al cancelar pedido')
    },
  })

  const getEstadoBadge = (estado) => {
    const badges = {
      pendiente: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
      entregado: 'bg-green-500/20 text-green-400 border-green-500/50',
      cancelado: 'bg-red-500/20 text-red-400 border-red-500/50',
    }
    return badges[estado] || badges.pendiente
  }

  const getEstadoLabel = (estado) => {
    const labels = {
      pendiente: 'Pendiente',
      entregado: 'Entregado',
      cancelado: 'Cancelado',
    }
    return labels[estado] || estado
  }

  const handleConfirmarEntrega = (pedido) => {
    const recibidoPorNombre = prompt('Ingrese el nombre de quien recibe (responsable de cocina):')
    if (!recibidoPorNombre) return
    
    const recibidoPorId = prompt('Ingrese el ID del usuario que recibe:')
    if (!recibidoPorId) return
    
    confirmarEntregaMutation.mutate({
      pedidoId: pedido.id,
      recibidoPorId: parseInt(recibidoPorId),
      recibidoPorNombre: recibidoPorNombre
    })
  }

  const pedidosFiltrados = pedidos?.filter(pedido => {
    if (busqueda) {
      const busquedaLower = busqueda.toLowerCase()
      return (
        pedido.entregado_por_nombre?.toLowerCase().includes(busquedaLower) ||
        pedido.recibido_por_nombre?.toLowerCase().includes(busquedaLower) ||
        pedido.items?.some(item => item.item?.nombre?.toLowerCase().includes(busquedaLower))
      )
    }
    return true
  }) || []

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Package size={32} />
          Pedidos Internos (Bodega → Cocina)
        </h1>
        <button
          onClick={() => {
            setPedidoSeleccionado(null)
            setShowModal(true)
          }}
          className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Plus size={20} />
          Nuevo Pedido
        </button>
      </div>

      {/* Filtros */}
      <div className="mb-6 flex gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
          <input
            type="text"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="Buscar por responsable o item..."
            className="w-full pl-10 pr-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter size={20} className="text-slate-400" />
          <select
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
            className="px-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          >
            <option value="">Todos los estados</option>
            <option value="pendiente">Pendiente</option>
            <option value="entregado">Entregado</option>
            <option value="cancelado">Cancelado</option>
          </select>
        </div>
      </div>

      {/* Lista de pedidos */}
      {isLoading ? (
        <div className="text-center py-12 text-slate-400">
          <p>Cargando pedidos...</p>
        </div>
      ) : pedidosFiltrados.length === 0 ? (
        <div className="text-center py-12 text-slate-400">
          <p>No hay pedidos internos registrados</p>
        </div>
      ) : (
        <div className="space-y-4">
          {pedidosFiltrados.map((pedido) => (
            <div key={pedido.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-lg font-semibold">Pedido #{pedido.id}</span>
                    <span className={`px-2 py-1 rounded text-xs border ${getEstadoBadge(pedido.estado)}`}>
                      {getEstadoLabel(pedido.estado)}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm text-slate-400">
                    <div className="flex items-center gap-2">
                      <Calendar size={16} />
                      <span>
                        {pedido.fecha_pedido
                          ? format(new Date(pedido.fecha_pedido), 'dd/MM/yyyy HH:mm', { locale: es })
                          : 'N/A'}
                      </span>
                    </div>
                    {pedido.fecha_entrega && (
                      <div className="flex items-center gap-2">
                        <Check size={16} />
                        <span>
                          Entregado: {format(new Date(pedido.fecha_entrega), 'dd/MM/yyyy HH:mm', { locale: es })}
                        </span>
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <User size={16} />
                      <span>
                        Entrega: <span className="text-slate-300">{pedido.entregado_por_nombre || 'N/A'}</span>
                      </span>
                    </div>
                    {pedido.recibido_por_nombre && (
                      <div className="flex items-center gap-2">
                        <User size={16} />
                        <span>
                          Recibe: <span className="text-slate-300">{pedido.recibido_por_nombre}</span>
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                {pedido.estado === 'pendiente' && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleConfirmarEntrega(pedido)}
                      disabled={confirmarEntregaMutation.isPending}
                      className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50"
                    >
                      <Check size={18} />
                      Confirmar Entrega
                    </button>
                    <button
                      onClick={() => cancelarPedidoMutation.mutate(pedido.id)}
                      disabled={cancelarPedidoMutation.isPending}
                      className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50"
                    >
                      <X size={18} />
                      Cancelar
                    </button>
                  </div>
                )}
              </div>

              {/* Items del pedido */}
              <div className="mt-4">
                <h3 className="text-sm font-semibold text-slate-300 mb-2">Items ({pedido.total_items || 0}):</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {pedido.items?.map((item) => (
                    <div key={item.id} className="bg-slate-700/50 p-3 rounded border border-slate-600">
                      <div className="flex justify-between items-start">
                        <div>
                          <span className="font-medium text-slate-200">{item.item?.nombre || 'N/A'}</span>
                          <div className="text-sm text-slate-400 mt-1">
                            {item.cantidad} {item.unidad || item.item?.unidad || ''}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {pedido.observaciones && (
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <p className="text-sm text-slate-400">
                    <span className="font-semibold">Observaciones:</span> {pedido.observaciones}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Modal para crear/editar pedido */}
      {showModal && (
        <Modal onClose={() => setShowModal(false)}>
          <PedidoInternoForm
            pedido={pedidoSeleccionado}
            onClose={() => setShowModal(false)}
            onSuccess={() => {
              setShowModal(false)
              queryClient.invalidateQueries(['pedidos-internos'])
            }}
          />
        </Modal>
      )}
    </div>
  )
}
