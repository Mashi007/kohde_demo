import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api, { extractData } from '../config/api'
import { ClipboardList, Send, ChevronDown, ChevronUp, Package, Plus, X } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import PedidoForm from '../components/PedidoForm'

export default function Pedidos() {
  const [pedidosExpandidos, setPedidosExpandidos] = useState({})
  const [mostrarFormulario, setMostrarFormulario] = useState(false)

  const { data: pedidosResponse } = useQuery({
    queryKey: ['pedidos'],
    queryFn: () => api.get('/logistica/pedidos').then(extractData),
  })

  // Asegurar que pedidos sea un array
  const pedidos = Array.isArray(pedidosResponse) ? pedidosResponse : []

  const toggleDetalle = (pedidoId) => {
    setPedidosExpandidos(prev => ({
      ...prev,
      [pedidoId]: !prev[pedidoId]
    }))
  }

  const getEstadoBadge = (estado) => {
    const badges = {
      borrador: 'bg-gray-500/20 text-gray-400 border-gray-500/50',
      enviado: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
      recibido: 'bg-green-500/20 text-green-400 border-green-500/50',
      cancelado: 'bg-red-500/20 text-red-400 border-red-500/50',
    }
    return badges[estado] || badges.borrador
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Pedidos de Compra</h1>
        <button
          onClick={() => setMostrarFormulario(true)}
          className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Plus size={20} />
          Nuevo Pedido
        </button>
      </div>

      {/* Modal/Overlay para el formulario */}
      {mostrarFormulario && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="relative w-full max-w-4xl">
            <button
              onClick={() => setMostrarFormulario(false)}
              className="absolute -top-2 -right-2 bg-red-600 hover:bg-red-700 rounded-full p-2 z-10"
            >
              <X size={20} />
            </button>
            <PedidoForm
              onClose={() => setMostrarFormulario(false)}
              onSuccess={() => {
                setMostrarFormulario(false)
              }}
            />
          </div>
        </div>
      )}

      <div className="space-y-4">
        {pedidos?.map((pedido) => {
          const estaExpandido = pedidosExpandidos[pedido.id]
          const tieneItems = pedido.items && pedido.items.length > 0

          return (
            <div key={pedido.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <ClipboardList className="text-purple-500" size={24} />
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="text-lg font-bold mb-2">Pedido #{pedido.id}</h3>
                        <p className="text-slate-400 mb-1">{pedido.proveedor?.nombre || 'Proveedor no especificado'}</p>
                        <p className="text-slate-400 text-sm">
                          {format(new Date(pedido.fecha_pedido), 'dd MMM yyyy', { locale: es })}
                        </p>
                        {pedido.fecha_entrega_esperada && (
                          <p className="text-slate-500 text-xs mt-1">
                            Entrega esperada: {format(new Date(pedido.fecha_entrega_esperada), 'dd MMM yyyy', { locale: es })}
                          </p>
                        )}
                      </div>
                      <div className="text-right ml-4">
                        <p className="text-2xl font-bold">
                          ${parseFloat(pedido.total || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                        </p>
                        {tieneItems && (
                          <button
                            onClick={() => toggleDetalle(pedido.id)}
                            className="mt-2 text-slate-400 hover:text-slate-300 text-sm flex items-center gap-1"
                          >
                            {estaExpandido ? (
                              <>
                                <ChevronUp size={16} />
                                Ocultar detalles
                              </>
                            ) : (
                              <>
                                <ChevronDown size={16} />
                                Ver detalles ({pedido.items.length} items)
                              </>
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                    <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs border ${getEstadoBadge(pedido.estado)}`}>
                      {pedido.estado}
                    </span>
                    {pedido.observaciones && (
                      <p className="text-slate-500 text-xs mt-2 italic">{pedido.observaciones}</p>
                    )}
                  </div>
                </div>
                {pedido.estado === 'borrador' && (
                  <button className="ml-4 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm flex items-center gap-2 whitespace-nowrap">
                    <Send size={16} />
                    Enviar
                  </button>
                )}
              </div>

              {/* Detalle de Items */}
              {estaExpandido && tieneItems && (
                <div className="mt-6 pt-6 border-t border-slate-700">
                  <h4 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                    <Package size={16} />
                    Items del Pedido ({pedido.items.length})
                  </h4>
                  <div className="space-y-3">
                    {pedido.items.map((item, index) => (
                      <div
                        key={item.id || index}
                        className="bg-slate-700/50 p-4 rounded-lg border border-slate-600"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs font-bold text-purple-400">#{index + 1}</span>
                              <h5 className="font-semibold text-slate-200">
                                {item.item?.nombre || 'Item no especificado'}
                              </h5>
                            </div>
                            <div className="text-xs text-slate-400 space-y-1">
                              <p>
                                Cantidad: <span className="font-semibold text-slate-300">{parseFloat(item.cantidad || 0).toFixed(2)}</span> {item.item?.unidad || 'unidad'}
                              </p>
                              <p>
                                Precio unitario: <span className="font-semibold text-slate-300">
                                  ${parseFloat(item.precio_unitario || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                                </span>
                              </p>
                            </div>
                          </div>
                          <div className="text-right ml-4">
                            <p className="text-lg font-bold text-green-400">
                              ${parseFloat(item.subtotal || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                            </p>
                            <p className="text-xs text-slate-500">Subtotal</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 pt-4 border-t border-slate-700 flex justify-between items-center">
                    <span className="text-sm text-slate-400">Total del pedido:</span>
                    <span className="text-2xl font-bold text-purple-400">
                      ${parseFloat(pedido.total || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )
        })}
        {pedidos.length === 0 && (
          <div className="bg-slate-800 p-8 rounded-lg border border-slate-700 text-center">
            <ClipboardList className="text-slate-500 mx-auto mb-4" size={48} />
            <p className="text-slate-400">No hay pedidos registrados</p>
          </div>
        )}
      </div>
    </div>
  )
}
