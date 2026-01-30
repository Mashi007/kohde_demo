import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import api, { extractData } from '../config/api'
import { ShoppingCart, Package, Truck, TrendingUp, AlertTriangle, Calendar } from 'lucide-react'

export default function ComprasDashboard() {
  const [fechaDesde, setFechaDesde] = useState(() => {
    const date = new Date()
    date.setDate(date.getDate() - 30)
    return date.toISOString().split('T')[0]
  })
  const [fechaHasta, setFechaHasta] = useState(() => {
    return new Date().toISOString().split('T')[0]
  })

  // Resumen general
  const { data: resumen } = useQuery({
    queryKey: ['compras-resumen', fechaDesde, fechaHasta],
    queryFn: () => api.get(`/logistica/compras/resumen?fecha_desde=${fechaDesde}&fecha_hasta=${fechaHasta}`).then(res => res.data),
  })

  // Compras por item
  const { data: comprasPorItemResponse } = useQuery({
    queryKey: ['compras-por-item', fechaDesde, fechaHasta],
    queryFn: () => api.get(`/logistica/compras/por-item?fecha_desde=${fechaDesde}&fecha_hasta=${fechaHasta}&limite=10`).then(extractData),
  })

  // Compras por proveedor
  const { data: comprasPorProveedorResponse } = useQuery({
    queryKey: ['compras-por-proveedor', fechaDesde, fechaHasta],
    queryFn: () => api.get(`/logistica/compras/por-proveedor?fecha_desde=${fechaDesde}&fecha_hasta=${fechaHasta}&limite=10`).then(extractData),
  })

  // Asegurar que sean arrays
  const comprasPorItem = Array.isArray(comprasPorItemResponse) ? comprasPorItemResponse : []
  const comprasPorProveedor = Array.isArray(comprasPorProveedorResponse) ? comprasPorProveedorResponse : []

  // Compras por proceso
  const { data: comprasPorProceso } = useQuery({
    queryKey: ['compras-por-proceso', fechaDesde, fechaHasta],
    queryFn: () => api.get(`/logistica/compras/por-proceso?fecha_desde=${fechaDesde}&fecha_hasta=${fechaHasta}`).then(res => res.data),
  })

  const formatearMoneda = (valor) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'USD'
    }).format(valor)
  }

  const formatearFecha = (fecha) => {
    return new Date(fecha).toLocaleDateString('es-ES')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard de Compras</h1>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Calendar size={20} className="text-slate-400" />
            <input
              type="date"
              value={fechaDesde}
              onChange={(e) => setFechaDesde(e.target.value)}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm"
            />
            <span className="text-slate-400">a</span>
            <input
              type="date"
              value={fechaHasta}
              onChange={(e) => setFechaHasta(e.target.value)}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm"
            />
          </div>
        </div>
      </div>

      {/* Resumen General */}
      {resumen && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm text-slate-400">Total Gastado</h3>
              <ShoppingCart className="text-purple-500" size={24} />
            </div>
            <p className="text-2xl font-bold">{formatearMoneda(resumen.resumen.total_gastado)}</p>
            <p className="text-xs text-slate-500 mt-1">
              {formatearFecha(resumen.periodo.fecha_desde)} - {formatearFecha(resumen.periodo.fecha_hasta)}
            </p>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm text-slate-400">Total Pedidos</h3>
              <Package className="text-blue-500" size={24} />
            </div>
            <p className="text-2xl font-bold">{resumen.resumen.total_pedidos}</p>
            <p className="text-xs text-slate-500 mt-1">
              {resumen.resumen.pedidos_pendientes} pendientes
            </p>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm text-slate-400">Total Facturas</h3>
              <Truck className="text-green-500" size={24} />
            </div>
            <p className="text-2xl font-bold">{resumen.resumen.total_facturas}</p>
            <p className="text-xs text-slate-500 mt-1">
              {formatearMoneda(resumen.resumen.total_gastado_facturas)} en facturas
            </p>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm text-slate-400">Pedidos Pendientes</h3>
              <AlertTriangle className="text-yellow-500" size={24} />
            </div>
            <p className="text-2xl font-bold">{resumen.resumen.pedidos_pendientes}</p>
            <p className="text-xs text-slate-500 mt-1">Requieren aprobación</p>
          </div>
        </div>
      )}

      {/* Compras por Proceso */}
      {comprasPorProceso && (
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <TrendingUp size={24} />
            Compras por Proceso
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-700/50 p-4 rounded-lg">
              <h3 className="text-sm text-slate-400 mb-1">Pedidos Automáticos</h3>
              <p className="text-xl font-bold">{comprasPorProceso.pedidos_automaticos.cantidad}</p>
              <p className="text-xs text-slate-500 mt-1">
                {formatearMoneda(comprasPorProceso.pedidos_automaticos.total_gastado)}
              </p>
            </div>
            <div className="bg-slate-700/50 p-4 rounded-lg">
              <h3 className="text-sm text-slate-400 mb-1">Programaciones</h3>
              <p className="text-xl font-bold">{comprasPorProceso.programaciones.cantidad}</p>
              <p className="text-xs text-slate-500 mt-1">Menús programados</p>
            </div>
            <div className="bg-slate-700/50 p-4 rounded-lg">
              <h3 className="text-sm text-slate-400 mb-1">Items Bajo Stock</h3>
              <p className="text-xl font-bold">{comprasPorProceso.inventario.items_bajo_stock}</p>
              <p className="text-xs text-slate-500 mt-1">
                {comprasPorProceso.inventario.porcentaje_bajo_stock.toFixed(1)}% del inventario
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Compras por Item */}
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Package size={24} />
            Top Items Comprados
          </h2>
          <div className="space-y-3">
            {comprasPorItem?.map((item, index) => (
              <div key={item.item_id} className="bg-slate-700/50 p-4 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-purple-400">#{index + 1}</span>
                      <h3 className="font-semibold">{item.item.nombre}</h3>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      {item.cantidad_total_comprada.toFixed(2)} {item.unidad} • {item.veces_comprado} compras
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">{formatearMoneda(item.total_gastado)}</p>
                    <p className="text-xs text-slate-400">
                      {formatearMoneda(item.precio_promedio)}/unidad
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-500 mt-2">
                  <span>Stock: {item.inventario_actual.toFixed(2)}</span>
                  <span>Mínimo: {item.inventario_minimo.toFixed(2)}</span>
                  {item.inventario_actual < item.inventario_minimo && (
                    <span className="text-yellow-500 flex items-center gap-1">
                      <AlertTriangle size={12} />
                      Bajo stock
                    </span>
                  )}
                </div>
              </div>
            ))}
            {comprasPorItem?.length === 0 && (
              <p className="text-center text-slate-400 py-8">No hay datos de compras por item</p>
            )}
          </div>
        </div>

        {/* Compras por Proveedor */}
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Truck size={24} />
            Top Proveedores
          </h2>
          <div className="space-y-3">
            {comprasPorProveedor?.map((proveedor, index) => (
              <div key={proveedor.proveedor_id} className="bg-slate-700/50 p-4 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-purple-400">#{index + 1}</span>
                      <h3 className="font-semibold">{proveedor.proveedor.nombre}</h3>
                      {!proveedor.activo && (
                        <span className="text-xs px-2 py-1 bg-red-500/20 text-red-400 rounded">Inactivo</span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      {proveedor.total_pedidos} pedidos • {proveedor.total_facturas} facturas • {proveedor.items_que_provee} items
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">{formatearMoneda(proveedor.total_gastado)}</p>
                    <p className="text-xs text-slate-400">
                      Promedio: {formatearMoneda(proveedor.promedio_pedido)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-500 mt-2">
                  <span>Pedidos: {formatearMoneda(proveedor.total_gastado_pedidos)}</span>
                  <span>Facturas: {formatearMoneda(proveedor.total_gastado_facturas)}</span>
                </div>
              </div>
            ))}
            {comprasPorProveedor?.length === 0 && (
              <p className="text-center text-slate-400 py-8">No hay datos de compras por proveedor</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
