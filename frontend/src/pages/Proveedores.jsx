import { useQuery } from '@tanstack/react-query'
import api from '../config/api'
import { Truck } from 'lucide-react'

export default function Proveedores() {
  const { data: proveedores } = useQuery({
    queryKey: ['proveedores'],
    queryFn: () => api.get('/compras/proveedores').then(res => res.data),
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Proveedores</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {proveedores?.map((proveedor) => (
          <div key={proveedor.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <Truck className="text-purple-500 mb-4" size={32} />
            <h3 className="text-xl font-bold mb-2">{proveedor.nombre}</h3>
            <div className="space-y-1 text-sm text-slate-400">
              <p>RUC: {proveedor.ruc || 'N/A'}</p>
              <p>Teléfono: {proveedor.telefono || 'N/A'}</p>
              <p>Email: {proveedor.email || 'N/A'}</p>
              <p>Días de crédito: {proveedor.dias_credito}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
