import { useQuery } from '@tanstack/react-query'
import api from '../config/api'
import { Package, AlertTriangle } from 'lucide-react'

export default function Inventario() {
  const { data: inventario } = useQuery({
    queryKey: ['inventario'],
    queryFn: () => api.get('/logistica/inventario').then(res => res.data),
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Inventario</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {inventario?.map((item) => {
          const stockBajo = parseFloat(item.cantidad_actual) < parseFloat(item.cantidad_minima)
          return (
            <div 
              key={item.id} 
              className={`bg-slate-800 p-6 rounded-lg border ${
                stockBajo ? 'border-yellow-500' : 'border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <Package size={24} className="text-purple-500" />
                {stockBajo && <AlertTriangle className="text-yellow-500" size={20} />}
              </div>
              <h3 className="text-lg font-bold mb-2">{item.item?.nombre || 'N/A'}</h3>
              <div className="space-y-1 text-sm">
                <p className="text-slate-400">
                  Stock: <span className="text-white font-medium">{item.cantidad_actual} {item.unidad}</span>
                </p>
                <p className="text-slate-400">
                  Mínimo: <span className="text-white">{item.cantidad_minima} {item.unidad}</span>
                </p>
                <p className="text-slate-400">
                  Ubicación: <span className="text-white">{item.ubicacion}</span>
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
