import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../config/api'
import { ShoppingCart, Plus } from 'lucide-react'
import Modal from '../components/Modal'
import ItemForm from '../components/ItemForm'

export default function Items() {
  const [showModal, setShowModal] = useState(false)
  
  const { data: items } = useQuery({
    queryKey: ['items'],
    queryFn: () => api.get('/logistica/items').then(res => res.data),
  })

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Items</h1>
        <button 
          onClick={() => setShowModal(true)}
          className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Plus size={20} />
          Nuevo Item
        </button>
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Nuevo Item"
      >
        <ItemForm
          onClose={() => setShowModal(false)}
        />
      </Modal>
      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-700">
            <tr>
              <th className="px-6 py-3 text-left">Código</th>
              <th className="px-6 py-3 text-left">Nombre</th>
              <th className="px-6 py-3 text-left">Categoría</th>
              <th className="px-6 py-3 text-left">Labels</th>
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
                <td className="px-6 py-4">
                  {item.labels && item.labels.length > 0 ? (
                    <div className="flex flex-wrap gap-1">
                      {item.labels.slice(0, 3).map(label => (
                        <span
                          key={label.id}
                          className="px-2 py-0.5 bg-purple-600/20 text-purple-300 rounded text-xs border border-purple-500/50"
                        >
                          {label.nombre_es}
                        </span>
                      ))}
                      {item.labels.length > 3 && (
                        <span className="px-2 py-0.5 text-slate-400 text-xs">
                          +{item.labels.length - 3}
                        </span>
                      )}
                    </div>
                  ) : (
                    <span className="text-slate-500 text-sm">Sin labels</span>
                  )}
                </td>
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
