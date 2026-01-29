import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'
import { ShoppingCart, Package, AlertTriangle, CheckCircle, X, Loader } from 'lucide-react'

export default function NecesidadesProgramacion({ programacionId, onClose }) {
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const [mostrarPedidosInteligentes, setMostrarPedidosInteligentes] = useState(false)
  
  // Cargar necesidades
  const { data: necesidades, isLoading, refetch } = useQuery({
    queryKey: ['necesidades', programacionId],
    queryFn: () => api.get(`/planificacion/programacion/${programacionId}/necesidades`).then(res => res.data),
    enabled: !!programacionId,
  })
  
  // Generar pedidos inteligentes
  const generarPedidosMutation = useMutation({
    mutationFn: () => api.post(`/planificacion/programacion/${programacionId}/generar-pedidos-inteligentes`, {
      usuario_id: user?.id || 1 // Obtener del contexto de autenticación
    }),
    onSuccess: (data) => {
      toast.success('Pedidos generados correctamente')
      queryClient.invalidateQueries(['pedidos'])
      queryClient.invalidateQueries(['programaciones'])
      refetch()
      setMostrarPedidosInteligentes(true)
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al generar pedidos')
    },
  })
  
  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-slate-800 rounded-lg p-8">
          <Loader className="w-8 h-8 animate-spin text-purple-400 mx-auto" />
          <p className="text-slate-400 mt-4">Cargando necesidades...</p>
        </div>
      </div>
    )
  }
  
  if (!necesidades) {
    return null
  }
  
  const itemsFaltantes = necesidades.items_faltantes || []
  const itemsSuficientes = necesidades.items_suficientes || []
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-slate-800 rounded-lg border border-slate-700 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700 sticky top-0 bg-slate-800 z-10">
          <div className="flex items-center gap-3">
            <Package className="w-6 h-6 text-purple-400" />
            <div>
              <h2 className="text-xl font-bold">Necesidades de Inventario</h2>
              <p className="text-sm text-slate-400">
                Fecha: {necesidades.fecha}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-700 rounded transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Contenido */}
        <div className="p-6 space-y-6">
          {/* Resumen */}
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 bg-green-600/10 border border-green-500/50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-sm font-medium text-green-300">Suficientes</span>
              </div>
              <p className="text-2xl font-bold text-green-400">{itemsSuficientes.length}</p>
            </div>
            <div className="p-4 bg-red-600/10 border border-red-500/50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                <span className="text-sm font-medium text-red-300">Faltantes</span>
              </div>
              <p className="text-2xl font-bold text-red-400">{itemsFaltantes.length}</p>
            </div>
            <div className="p-4 bg-purple-600/10 border border-purple-500/50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <ShoppingCart className="w-5 h-5 text-purple-400" />
                <span className="text-sm font-medium text-purple-300">Total Items</span>
              </div>
              <p className="text-2xl font-bold text-purple-400">
                {(necesidades.necesidades_totales && Object.keys(necesidades.necesidades_totales).length) || 0}
              </p>
            </div>
          </div>
          
          {/* Items Faltantes */}
          {itemsFaltantes.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3 text-red-300 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                Items Faltantes para la Programación
              </h3>
              <div className="space-y-2">
                {itemsFaltantes.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-4 bg-red-600/10 border border-red-500/50 rounded-lg"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold">{item.nombre}</h4>
                        <div className="grid grid-cols-3 gap-4 mt-2 text-sm">
                          <div>
                            <span className="text-slate-400">Necesario: </span>
                            <span className="font-semibold">{item.cantidad_necesaria.toFixed(2)} {item.unidad}</span>
                          </div>
                          <div>
                            <span className="text-slate-400">Disponible: </span>
                            <span className="font-semibold">{item.cantidad_disponible.toFixed(2)} {item.unidad}</span>
                          </div>
                          <div>
                            <span className="text-red-400">Faltante: </span>
                            <span className="font-semibold text-red-300">{item.cantidad_faltante.toFixed(2)} {item.unidad}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Items Suficientes */}
          {itemsSuficientes.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3 text-green-300 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Items con Stock Suficiente
              </h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {itemsSuficientes.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-green-600/10 border border-green-500/50 rounded-lg text-sm"
                  >
                    <span className="font-medium">{item.nombre}</span>
                    <span className="text-slate-400 ml-2">
                      ({item.cantidad_necesaria.toFixed(2)} {item.unidad} necesario, {item.cantidad_disponible.toFixed(2)} {item.unidad} disponible)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Botón para generar pedidos inteligentes */}
          {itemsFaltantes.length > 0 && (
            <div className="pt-4 border-t border-slate-700">
              <div className="bg-blue-600/10 border border-blue-500/50 rounded-lg p-4 mb-4">
                <h4 className="font-semibold text-blue-300 mb-2">Generar Pedidos Inteligentes</h4>
                <p className="text-sm text-slate-400">
                  El sistema generará pedidos en dos fases:
                </p>
                <ul className="text-sm text-slate-300 mt-2 space-y-1 ml-4 list-disc">
                  <li>Primero: Comprar lo necesario para la programación</li>
                  <li>Segundo: Asegurar el inventario de emergencia/base (stock mínimo)</li>
                </ul>
              </div>
              <button
                onClick={() => generarPedidosMutation.mutate()}
                disabled={generarPedidosMutation.isPending}
                className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {generarPedidosMutation.isPending ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    Generando pedidos...
                  </>
                ) : (
                  <>
                    <ShoppingCart className="w-5 h-5" />
                    Generar Pedidos Inteligentes
                  </>
                )}
              </button>
            </div>
          )}
          
          {/* Resultado de pedidos generados */}
          {mostrarPedidosInteligentes && generarPedidosMutation.data?.data && (
            <div className="pt-4 border-t border-slate-700">
              <h4 className="font-semibold mb-3 text-green-300">Pedidos Generados</h4>
              
              {/* Ticket creado */}
              {generarPedidosMutation.data.data.ticket_id && (
                <div className="mb-4 p-3 bg-blue-600/10 border border-blue-500/50 rounded-lg">
                  <p className="text-sm text-blue-300 font-medium">
                    ✓ Ticket creado en CRM: #{generarPedidosMutation.data.data.ticket_id}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    Los PDFs de los pedidos se han enviado por email automáticamente
                  </p>
                </div>
              )}
              
              <div className="space-y-3">
                {generarPedidosMutation.data.data.pedidos_programacion?.length > 0 && (
                  <div>
                    <p className="text-sm text-slate-400 mb-2">
                      Pedidos para Programación ({generarPedidosMutation.data.data.total_pedidos_programacion})
                    </p>
                    {generarPedidosMutation.data.data.pedidos_programacion.map((pedido, idx) => (
                      <div key={idx} className="p-3 bg-slate-700/50 rounded text-sm">
                        Pedido #{pedido.id} - Total: ${pedido.total?.toFixed(2)}
                      </div>
                    ))}
                  </div>
                )}
                {generarPedidosMutation.data.data.pedidos_stock_minimo?.length > 0 && (
                  <div>
                    <p className="text-sm text-slate-400 mb-2">
                      Pedidos para Stock Mínimo ({generarPedidosMutation.data.data.total_pedidos_stock_minimo})
                    </p>
                    {generarPedidosMutation.data.data.pedidos_stock_minimo.map((pedido, idx) => (
                      <div key={idx} className="p-3 bg-slate-700/50 rounded text-sm">
                        Pedido #{pedido.id} - Total: ${pedido.total?.toFixed(2)}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
