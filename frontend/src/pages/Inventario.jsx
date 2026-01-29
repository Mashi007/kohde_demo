import { useQuery } from '@tanstack/react-query'
import api from '../config/api'
import { Package, AlertTriangle, TrendingUp, TrendingDown, DollarSign, Box } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

export default function Inventario() {
  const { data: dashboard } = useQuery({
    queryKey: ['inventario-dashboard'],
    queryFn: () => api.get('/logistica/inventario/dashboard').then(res => res.data),
  })

  const { data: silos } = useQuery({
    queryKey: ['inventario-silos'],
    queryFn: () => api.get('/logistica/inventario/silos').then(res => res.data),
  })

  const { data: inventario, isLoading } = useQuery({
    queryKey: ['inventario-completo'],
    queryFn: () => api.get('/logistica/inventario/completo').then(res => res.data),
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Inventario</h1>

      {/* Dashboard tipo Silo - Top 10 Items Más Comprados */}
      {silos && silos.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Silos - Top 10 Productos Más Comprados</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {silos.map((silo) => {
              const nivelLlenado = Math.min(100, silo.nivel_llenado || 0)
              const porcentajeMinimo = Math.min(100, (silo.stock_minimo / Math.max(silo.stock_total, silo.stock_minimo)) * 100)
              
              return (
                <div 
                  key={silo.item_id}
                  className="bg-slate-800 p-4 rounded-lg border border-slate-700 flex flex-col items-center"
                >
                  {/* Nombre del Item */}
                  <h3 className="text-sm font-bold mb-2 text-center min-h-[2.5rem] line-clamp-2">
                    {silo.item_nombre}
                  </h3>
                  
                  {/* Silo Visual */}
                  <div className="relative w-20 h-32 bg-slate-700 rounded-b-lg border-2 border-slate-600 mb-2 overflow-hidden">
                    {/* Línea de stock mínimo */}
                    {silo.stock_minimo > 0 && (
                      <div 
                        className="absolute left-0 right-0 border-t-2 border-yellow-500 z-10"
                        style={{
                          bottom: `${100 - porcentajeMinimo}%`,
                        }}
                      >
                        <span className="absolute -top-4 left-0 text-xs text-yellow-400 font-bold">
                          Mín
                        </span>
                      </div>
                    )}
                    
                    {/* Relleno del silo */}
                    <div
                      className={`absolute bottom-0 left-0 right-0 transition-all duration-500 ${
                        silo.estado === 'critico' 
                          ? 'bg-red-600' 
                          : silo.estado === 'bajo' 
                          ? 'bg-yellow-600' 
                          : 'bg-green-600'
                      }`}
                      style={{
                        height: `${nivelLlenado}%`,
                      }}
                    />
                    
                    {/* Porcentaje de llenado */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-xs font-bold text-white drop-shadow-lg">
                        {nivelLlenado.toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  
                  {/* Información del Stock */}
                  <div className="text-xs text-center space-y-1 w-full">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Total:</span>
                      <span className="font-bold">{silo.stock_total.toFixed(2)} {silo.unidad}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-yellow-400">Mínimo:</span>
                      <span className="font-bold text-yellow-400">{silo.stock_minimo.toFixed(2)} {silo.unidad}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-green-400">Disponible:</span>
                      <span className="font-bold text-green-400">{silo.stock_disponible.toFixed(2)} {silo.unidad}</span>
                    </div>
                    {silo.frecuencia_compra > 0 && (
                      <div className="text-slate-500 text-[10px] mt-2 pt-2 border-t border-slate-700">
                        Compras: {silo.frecuencia_compra}
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Dashboard tipo Silo - Métricas Generales */}
      {dashboard && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between mb-2">
              <Box className="text-blue-500" size={24} />
              <span className="text-2xl font-bold">{dashboard.total_items}</span>
            </div>
            <p className="text-slate-400 text-sm">Total Items</p>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="text-green-500" size={24} />
              <span className="text-2xl font-bold text-green-500">{dashboard.items_stock_ok}</span>
            </div>
            <p className="text-slate-400 text-sm">Stock OK</p>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg border border-yellow-500/50">
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="text-yellow-500" size={24} />
              <span className="text-2xl font-bold text-yellow-500">{dashboard.items_stock_bajo}</span>
            </div>
            <p className="text-slate-400 text-sm">Stock Bajo</p>
            <p className="text-xs text-yellow-400 mt-1">{dashboard.porcentaje_stock_bajo}% del total</p>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg border border-red-500/50">
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="text-red-500" size={24} />
              <span className="text-2xl font-bold text-red-500">{dashboard.items_criticos}</span>
            </div>
            <p className="text-slate-400 text-sm">Críticos</p>
            <p className="text-xs text-red-400 mt-1">&lt; 50% del mínimo</p>
          </div>

          {dashboard.valor_total_inventario > 0 && (
            <div className="bg-slate-800 p-6 rounded-lg border border-purple-500/50 md:col-span-2 lg:col-span-4">
              <div className="flex items-center justify-between">
                <div>
                  <DollarSign className="text-purple-500 inline-block mr-2" size={24} />
                  <span className="text-slate-400 text-sm">Valor Total Inventario</span>
                </div>
                <span className="text-3xl font-bold text-purple-500">
                  ${dashboard.valor_total_inventario.toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Listado de Items */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <div className="p-4 border-b border-slate-700">
          <h2 className="text-xl font-bold">Listado de Items</h2>
        </div>
        
        {isLoading ? (
          <div className="p-8 text-center text-slate-400">Cargando inventario...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-700">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium">Item</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Último Ingreso</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Último Egreso</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Stock Seguridad</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Stock Disponible</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {inventario?.map((item) => {
                  const stockBajo = parseFloat(item.cantidad_actual || 0) < parseFloat(item.cantidad_minima || 0)
                  const stockCritico = parseFloat(item.cantidad_actual || 0) < (parseFloat(item.cantidad_minima || 0) * 0.5)
                  const stockDisponible = parseFloat(item.stock_disponible || 0)
                  
                  return (
                    <tr 
                      key={item.id} 
                      className={`hover:bg-slate-700/50 ${
                        stockCritico ? 'bg-red-900/20' : stockBajo ? 'bg-yellow-900/20' : ''
                      }`}
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <Package size={18} className="text-purple-500" />
                          <div>
                            <div className="font-medium">{item.item?.nombre || 'N/A'}</div>
                            <div className="text-xs text-slate-400">{item.ubicacion}</div>
                          </div>
                        </div>
                      </td>
                      
                      <td className="px-6 py-4">
                        {item.ultimo_ingreso ? (
                          <div>
                            <div className="text-sm">
                              {format(new Date(item.ultimo_ingreso.fecha), 'dd MMM yyyy', { locale: es })}
                            </div>
                            <div className="text-xs text-slate-400">
                              {item.ultimo_ingreso.cantidad} {item.unidad}
                            </div>
                            {item.ultimo_ingreso.factura_numero && (
                              <div className="text-xs text-slate-500">
                                Fact: {item.ultimo_ingreso.factura_numero}
                              </div>
                            )}
                          </div>
                        ) : (
                          <span className="text-slate-500 text-sm">Sin ingresos</span>
                        )}
                      </td>
                      
                      <td className="px-6 py-4">
                        {item.ultimo_egreso ? (
                          <div>
                            <div className="text-sm">
                              {format(new Date(item.ultimo_egreso.fecha), 'dd MMM yyyy', { locale: es })}
                            </div>
                            <div className="text-xs text-slate-400">
                              {item.ultimo_egreso.cantidad} {item.unidad}
                            </div>
                            {item.ultimo_egreso.requerimiento_id && (
                              <div className="text-xs text-slate-500">
                                Req: #{item.ultimo_egreso.requerimiento_id}
                              </div>
                            )}
                          </div>
                        ) : (
                          <span className="text-slate-500 text-sm">Sin egresos</span>
                        )}
                      </td>
                      
                      <td className="px-6 py-4">
                        <span className="text-sm">
                          {item.stock_seguridad} {item.unidad}
                        </span>
                      </td>
                      
                      <td className="px-6 py-4">
                        <span className={`text-sm font-medium ${
                          stockDisponible > 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {stockDisponible.toFixed(2)} {item.unidad}
                        </span>
                        <div className="text-xs text-slate-500">
                          Actual: {parseFloat(item.cantidad_actual || 0).toFixed(2)}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4">
                        {stockCritico ? (
                          <span className="px-2 py-1 rounded text-xs bg-red-500/20 text-red-400 border border-red-500/50">
                            Crítico
                          </span>
                        ) : stockBajo ? (
                          <span className="px-2 py-1 rounded text-xs bg-yellow-500/20 text-yellow-400 border border-yellow-500/50">
                            Bajo
                          </span>
                        ) : (
                          <span className="px-2 py-1 rounded text-xs bg-green-500/20 text-green-400 border border-green-500/50">
                            OK
                          </span>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
