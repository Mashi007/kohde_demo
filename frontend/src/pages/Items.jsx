import { useQuery } from '@tanstack/react-query'
import api from '../config/api'
import { ShoppingCart } from 'lucide-react'

export default function Items() {
  const { data: items } = useQuery({
    queryKey: ['items'],
    queryFn: () => api.get('/logistica/items').then(res => res.data),
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Items</h1>
      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-700">
            <tr>
              <th className="px-6 py-3 text-left">Código</th>
              <th className="px-6 py-3 text-left">Nombre</th>
              <th className="px-6 py-3 text-left">Categoría</th>
              <th className="px-6 py-3 text-left">Unidad</th>
              <th className="px-6 py-3 text-left">Costo Unitario</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {items?.map((item) => (
              <tr key={item.id} className="hover:bg-slate-700/50">
                <td className="px-6 py-4">{item.codigo}</td>
                <td className="px-6 py-4">{item.nombre}</td>
                <td className="px-6 py-4 capitalize">{item.categoria?.replace('_', ' ')}</td>
                <td className="px-6 py-4">{item.unidad}</td>
                <td className="px-6 py-4">
                  ${item.costo_unitario_actual?.toFixed(2) || '0.00'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
