import { useQuery } from '@tanstack/react-query'
import api from '../config/api'
import { Package, FileText, MessageSquare, AlertTriangle } from 'lucide-react'

export default function Dashboard() {
  const { data: stockBajo } = useQuery({
    queryKey: ['stock-bajo'],
    queryFn: () => api.get('/logistica/inventario/stock-bajo').then(res => res.data),
  })

  const { data: facturasPendientes } = useQuery({
    queryKey: ['facturas-pendientes'],
    queryFn: () => api.get('/contabilidad/facturas?estado=pendiente').then(res => res.data),
  })

  const { data: ticketsAbiertos } = useQuery({
    queryKey: ['tickets-abiertos'],
    queryFn: () => api.get('/crm/tickets?estado=abierto').then(res => res.data),
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      {/* Cards de Resumen */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Stock Bajo</p>
              <p className="text-3xl font-bold mt-2">
                {stockBajo?.length || 0}
              </p>
            </div>
            <AlertTriangle className="text-yellow-500" size={32} />
          </div>
        </div>

        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Facturas Pendientes</p>
              <p className="text-3xl font-bold mt-2">
                {facturasPendientes?.length || 0}
              </p>
            </div>
            <FileText className="text-blue-500" size={32} />
          </div>
        </div>

        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Tickets Abiertos</p>
              <p className="text-3xl font-bold mt-2">
                {ticketsAbiertos?.length || 0}
              </p>
            </div>
            <MessageSquare className="text-purple-500" size={32} />
          </div>
        </div>
      </div>

      {/* Alertas de Stock Bajo */}
      {stockBajo && stockBajo.length > 0 && (
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Package size={24} />
            Items con Stock Bajo
          </h2>
          <div className="space-y-2">
            {stockBajo.slice(0, 5).map((item) => (
              <div key={item.item_id} className="flex justify-between items-center p-3 bg-slate-700 rounded">
                <span className="font-medium">{item.nombre}</span>
                <span className="text-yellow-500">
                  {item.cantidad_actual} {item.unidad} (Mínimo: {item.cantidad_minima})
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
