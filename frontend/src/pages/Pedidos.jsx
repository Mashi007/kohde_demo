import { useQuery } from '@tanstack/react-query'
import api from '../config/api'
import { ClipboardList, Send } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

export default function Pedidos() {
  const { data: pedidos } = useQuery({
    queryKey: ['pedidos'],
    queryFn: () => api.get('/logistica/pedidos').then(res => res.data),
  })

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
      <h1 className="text-3xl font-bold mb-6">Pedidos de Compra</h1>
      <div className="space-y-4">
        {pedidos?.map((pedido) => (
          <div key={pedido.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <ClipboardList className="text-purple-500" size={24} />
                <div>
                  <h3 className="text-lg font-bold mb-2">Pedido #{pedido.id}</h3>
                  <p className="text-slate-400 mb-1">{pedido.proveedor?.nombre}</p>
                  <p className="text-slate-400 text-sm">
                    {format(new Date(pedido.fecha_pedido), 'dd MMM yyyy', { locale: es })}
                  </p>
                  <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs border ${getEstadoBadge(pedido.estado)}`}>
                    {pedido.estado}
                  </span>
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold">
                  ${parseFloat(pedido.total).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                </p>
                {pedido.estado === 'borrador' && (
                  <button className="mt-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-sm flex items-center gap-2">
                    <Send size={16} />
                    Enviar
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
