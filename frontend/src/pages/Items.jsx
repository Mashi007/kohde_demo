import { useQuery } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import api from '../config/api'
import { debounce } from '../utils/debounce'
import { ShoppingCart, Plus, Search, X } from 'lucide-react'
import Modal from '../components/Modal'
import ItemForm from '../components/ItemForm'
import LoadingSpinner from '../components/LoadingSpinner'
import SkeletonLoader from '../components/SkeletonLoader'
import EmptyState from '../components/EmptyState'

export default function Items() {
  const [showModal, setShowModal] = useState(false)
  const [busqueda, setBusqueda] = useState('')
  const [busquedaDebounced, setBusquedaDebounced] = useState('')
  
  // Debounce de búsqueda
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setBusquedaDebounced(busqueda)
    }, 300)
    
    return () => {
      clearTimeout(timeoutId)
    }
  }, [busqueda])
  
  const { data: items, isLoading } = useQuery({
    queryKey: ['items', busquedaDebounced],
    queryFn: () => {
      const params = busquedaDebounced ? { busqueda: busquedaDebounced } : {}
      return api.get('/logistica/items', { params }).then(res => res.data)
    },
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

      {/* Buscador */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
          <input
            type="text"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="Buscar por código o nombre (ej: leche, MP-20240129-0001)..."
            className="w-full pl-10 pr-10 py-2.5 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500 text-sm"
          />
          {busqueda && (
            <button
              onClick={() => setBusqueda('')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-300"
              title="Limpiar búsqueda"
            >
              <X size={18} />
            </button>
          )}
        </div>
        {busqueda && (
          <p className="text-xs text-slate-400 mt-2">
            Buscando: <span className="text-purple-400 font-medium">"{busqueda}"</span>
            {items && (
              <span className="ml-2">
                ({items.length} resultado{items.length !== 1 ? 's' : ''})
              </span>
            )}
          </p>
        )}
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
        {isLoading ? (
          <div className="p-8">
            <SkeletonLoader type="table" lines={5} />
          </div>
        ) : !items || items.length === 0 ? (
          <EmptyState
            icon={ShoppingCart}
            title={busqueda ? 'No se encontraron items' : 'No hay items registrados'}
            description={
              busqueda
                ? 'Intenta con otro término de búsqueda o limpia el filtro para ver todos los items.'
                : 'Comienza agregando tu primer item al sistema.'
            }
            action={busqueda ? () => setBusqueda('') : () => setShowModal(true)}
            actionLabel={busqueda ? 'Limpiar búsqueda' : 'Crear primer item'}
          />
        ) : (
          <table className="w-full">
            <thead className="bg-slate-700">
              <tr>
                <th className="px-6 py-3 text-left">Código</th>
                <th className="px-6 py-3 text-left">Nombre</th>
                <th className="px-6 py-3 text-left">Categoría</th>
                <th className="px-6 py-3 text-left">Labels</th>
                <th className="px-6 py-3 text-left">Unidad</th>
                <th className="px-6 py-3 text-left">Calorías</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {items.map((item) => (
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
                  {item.calorias_por_unidad ? (
                    <span className="text-slate-300">
                      {item.calorias_por_unidad.toFixed(1)} cal/{item.unidad}
                    </span>
                  ) : (
                    <span className="text-slate-500 text-sm">-</span>
                  )}
                </td>
              </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
