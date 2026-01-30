import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import api, { extractData } from '../config/api'
import { debounce } from '../utils/debounce'
import { ShoppingCart, Plus, Search, X, Edit, Trash2, Power, PowerOff, DollarSign } from 'lucide-react'
import Modal from '../components/Modal'
import ItemForm from '../components/ItemForm'
import LoadingSpinner from '../components/LoadingSpinner'
import SkeletonLoader from '../components/SkeletonLoader'
import EmptyState from '../components/EmptyState'
import toast from 'react-hot-toast'

export default function Items() {
  const [showModal, setShowModal] = useState(false)
  const [itemEditando, setItemEditando] = useState(null)
  const [itemEliminar, setItemEliminar] = useState(null)
  const [busqueda, setBusqueda] = useState('')
  const [busquedaDebounced, setBusquedaDebounced] = useState('')
  
  const queryClient = useQueryClient()
  
  // Debounce de búsqueda
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setBusquedaDebounced(busqueda)
    }, 300)
    
    return () => {
      clearTimeout(timeoutId)
    }
  }, [busqueda])
  
  const { data: itemsResponse, isLoading } = useQuery({
    queryKey: ['items', busquedaDebounced],
    queryFn: () => {
      const params = busquedaDebounced ? { busqueda: busquedaDebounced } : {}
      return api.get('/logistica/items', { params }).then(extractData)
    },
  })

  // Asegurar que items sea un array
  const items = Array.isArray(itemsResponse) ? itemsResponse : []

  // Mutación para eliminar item
  const deleteMutation = useMutation({
    mutationFn: (itemId) => api.delete(`/logistica/items/${itemId}`),
    onSuccess: () => {
      toast.success('Item eliminado correctamente')
      queryClient.invalidateQueries(['items'])
      setItemEliminar(null)
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al eliminar item')
    },
  })

  // Mutación para toggle activo/inactivo
  const toggleActivoMutation = useMutation({
    mutationFn: (itemId) => api.put(`/logistica/items/${itemId}/toggle-activo`),
    onSuccess: (response) => {
      const estado = response.data?.data?.activo ? 'activado' : 'desactivado'
      toast.success(`Item ${estado} correctamente`)
      queryClient.invalidateQueries(['items'])
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al cambiar estado del item')
    },
  })

  const handleEditar = (item) => {
    setItemEditando(item)
    setShowModal(true)
  }

  const handleEliminar = (item) => {
    setItemEliminar(item)
  }

  const confirmarEliminar = () => {
    if (itemEliminar) {
      deleteMutation.mutate(itemEliminar.id)
    }
  }

  const handleToggleActivo = (item) => {
    toggleActivoMutation.mutate(item.id)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setItemEditando(null)
  }

  const handleSuccess = () => {
    queryClient.invalidateQueries(['items'])
    handleCloseModal()
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Items</h1>
        <button 
          onClick={() => {
            setItemEditando(null)
            setShowModal(true)
          }}
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

      {/* Modal para crear/editar item */}
      <Modal
        isOpen={showModal}
        onClose={handleCloseModal}
        title={itemEditando ? 'Editar Item' : 'Nuevo Item'}
      >
        <ItemForm
          item={itemEditando}
          onClose={handleCloseModal}
          onSuccess={handleSuccess}
        />
      </Modal>

      {/* Modal de confirmación para eliminar */}
      {itemEliminar && (
        <Modal
          isOpen={!!itemEliminar}
          onClose={() => setItemEliminar(null)}
          title="Confirmar Eliminación"
        >
          <div className="p-6">
            <p className="text-slate-300 mb-4">
              ¿Estás seguro de que deseas eliminar el item <strong>{itemEliminar.nombre}</strong> (Código: {itemEliminar.codigo})?
            </p>
            <p className="text-sm text-slate-400 mb-6">
              Esta acción marcará el item como inactivo. No se eliminará físicamente de la base de datos.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setItemEliminar(null)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={confirmarEliminar}
                disabled={deleteMutation.isPending}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Trash2 size={16} />
                {deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}
              </button>
            </div>
          </div>
        </Modal>
      )}

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
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-700">
                <tr>
                  <th className="px-6 py-3 text-left">Código</th>
                  <th className="px-6 py-3 text-left">Nombre</th>
                  <th className="px-6 py-3 text-left">Categoría</th>
                  <th className="px-6 py-3 text-left">Unidad</th>
                  <th className="px-6 py-3 text-left">Calorías</th>
                  <th className="px-6 py-3 text-left">Costo/Unidad</th>
                  <th className="px-6 py-3 text-left">Estado</th>
                  <th className="px-6 py-3 text-left">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {items.map((item) => (
                <tr 
                  key={item.id} 
                  className={`hover:bg-slate-700/50 ${!item.activo ? 'opacity-60' : ''}`}
                >
                  <td className="px-6 py-4">{item.codigo}</td>
                  <td className="px-6 py-4">{item.nombre}</td>
                  <td className="px-6 py-4 capitalize">{item.categoria?.replace('_', ' ')}</td>
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
                  <td className="px-6 py-4">
                    {item.costo_unitario_actual || item.costo_unitario_promedio ? (
                      <span className="text-green-400 font-medium flex items-center gap-1">
                        <DollarSign size={14} />
                        ${((item.costo_unitario_actual || item.costo_unitario_promedio) || 0).toFixed(2)}/{item.unidad}
                      </span>
                    ) : (
                      <span className="text-slate-500 text-sm">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      item.activo 
                        ? 'bg-green-600/20 text-green-400 border border-green-500/50' 
                        : 'bg-red-600/20 text-red-400 border border-red-500/50'
                    }`}>
                      {item.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleEditar(item)}
                        className="p-2 hover:bg-slate-700 rounded transition-colors"
                        title="Editar item"
                      >
                        <Edit size={16} className="text-blue-400" />
                      </button>
                      <button
                        onClick={() => handleToggleActivo(item)}
                        disabled={toggleActivoMutation.isPending}
                        className="p-2 hover:bg-slate-700 rounded transition-colors disabled:opacity-50"
                        title={item.activo ? 'Desactivar item' : 'Activar item'}
                      >
                        {item.activo ? (
                          <PowerOff size={16} className="text-yellow-400" />
                        ) : (
                          <Power size={16} className="text-green-400" />
                        )}
                      </button>
                      <button
                        onClick={() => handleEliminar(item)}
                        className="p-2 hover:bg-slate-700 rounded transition-colors"
                        title="Eliminar item"
                      >
                        <Trash2 size={16} className="text-red-400" />
                      </button>
                    </div>
                  </td>
                </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
