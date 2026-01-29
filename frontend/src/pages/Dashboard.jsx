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
    queryFn: () => api.get('/logistica/facturas?estado=pendiente').then(res => res.data),
  })

  const { data: ticketsAbiertos } = useQuery({
    queryKey: ['tickets-abiertos'],
    queryFn: () => api.get('/crm/tickets?estado=abierto').then(res => res.data),
  })

  const { data: ultimaFactura } = useQuery({
    queryKey: ['factura-ultima'],
    queryFn: () => api.get('/logistica/facturas/ultima').then(res => res.data).catch(() => null),
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

      {/* Última Factura Ingresada */}
      {ultimaFactura && (
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <FileText size={24} />
            Última Factura Ingresada
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center">
            <div>
              <p className="text-xs text-slate-400 mb-1">Remitente</p>
              <p className="font-semibold">{ultimaFactura.remitente_nombre || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-slate-400 mb-1">Teléfono</p>
              <p className="font-semibold">{ultimaFactura.remitente_telefono || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-slate-400 mb-1">Imagen</p>
              {ultimaFactura.imagen_url ? (
                <div className="relative w-16 h-16 rounded-lg overflow-hidden border border-slate-600">
                  <img
                    src={ultimaFactura.imagen_url}
                    alt="Factura"
                    className="w-full h-full object-cover"
                  />
                </div>
              ) : (
                <div className="w-16 h-16 rounded-lg bg-slate-700 flex items-center justify-center">
                  <FileText size={20} className="text-slate-400" />
                </div>
              )}
            </div>
            <div>
              <p className="text-xs text-slate-400 mb-1">Factura #{ultimaFactura.numero_factura}</p>
              <p className="font-semibold">${parseFloat(ultimaFactura.total || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</p>
            </div>
            <div>
              <a
                href="/facturas"
                className="block w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-center text-sm"
              >
                Ver Detalles
              </a>
            </div>
          </div>
        </div>
      )}

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
