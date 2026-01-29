import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../config/api'
import { Truck, Plus, Edit, Trash2, Power, X, Search, Filter } from 'lucide-react'
import Modal from '../components/Modal'
import ProveedorForm from '../components/ProveedorForm'
import toast from 'react-hot-toast'

export default function Proveedores() {
  const [showModal, setShowModal] = useState(false)
  const [proveedorSeleccionado, setProveedorSeleccionado] = useState(null)
  const [busqueda, setBusqueda] = useState('')
  const [labelFiltro, setLabelFiltro] = useState(null)
  const [proveedorEditando, setProveedorEditando] = useState(null)

  const queryClient = useQueryClient()

  // Cargar labels para filtros
  const { data: labels } = useQuery({
    queryKey: ['labels'],
    queryFn: () => api.get('/logistica/labels').then(res => res.data),
  })

  // Agrupar labels por categoría
  const labelsPorCategoria = labels?.reduce((acc, label) => {
    const cat = label.categoria_principal
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(label)
    return acc
  }, {}) || {}

  // Cargar proveedores con filtros
  const { data: proveedores } = useQuery({
    queryKey: ['proveedores', busqueda, labelFiltro],
    queryFn: () => {
      const params = new URLSearchParams()
      if (busqueda) params.append('busqueda', busqueda)
      if (labelFiltro) params.append('label_id', labelFiltro)
      return api.get(`/crm/proveedores?${params}`).then(res => res.data)
    },
  })

  // Cargar detalle del proveedor seleccionado
  const { data: detalleProveedor } = useQuery({
    queryKey: ['proveedor-detalle', proveedorSeleccionado],
    queryFn: () => api.get(`/crm/proveedores/${proveedorSeleccionado}`).then(res => res.data),
    enabled: !!proveedorSeleccionado,
  })

  // Mutaciones
  const eliminarMutation = useMutation({
    mutationFn: (id) => api.delete(`/crm/proveedores/${id}`),
    onSuccess: () => {
      toast.success('Proveedor eliminado correctamente')
      queryClient.invalidateQueries(['proveedores'])
      setProveedorSeleccionado(null)
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al eliminar proveedor')
    },
  })

  const toggleActivoMutation = useMutation({
    mutationFn: (id) => api.post(`/crm/proveedores/${id}/toggle-activo`),
    onSuccess: () => {
      toast.success('Estado actualizado correctamente')
      queryClient.invalidateQueries(['proveedores'])
      queryClient.invalidateQueries(['proveedor-detalle'])
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al actualizar estado')
    },
  })

  const handleEliminar = () => {
    if (window.confirm('¿Estás seguro de eliminar este proveedor?')) {
      eliminarMutation.mutate(proveedorSeleccionado)
    }
  }

  const handleToggleActivo = () => {
    toggleActivoMutation.mutate(proveedorSeleccionado)
  }

  const handleEditar = () => {
    const proveedor = proveedores?.find(p => p.id === proveedorSeleccionado)
    setProveedorEditando(proveedor)
    setShowModal(true)
  }

  const getLabelNombre = (labelId) => {
    if (!labels) return ''
    const label = labels.find(l => l.id === labelId)
    return label?.nombre_es || ''
  }

  return (
    <div className="flex gap-6 h-[calc(100vh-4rem)]">
      {/* Panel izquierdo: Filtros por Labels */}
      <div className="w-64 bg-slate-800 rounded-lg border border-slate-700 p-4 overflow-y-auto">
        <div className="flex items-center gap-2 mb-4">
          <Filter size={20} className="text-purple-500" />
          <h2 className="text-lg font-bold">Filtros</h2>
        </div>

        {/* Buscador */}
        <div className="mb-4">
          <div className="relative">
            <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Buscar proveedor..."
              className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm focus:outline-none focus:border-purple-500"
            />
          </div>
        </div>

        {/* Filtro por Label */}
        <div className="mb-4">
          <h3 className="text-sm font-semibold mb-2 text-slate-300">Clasificación de Alimentos</h3>
          <button
            onClick={() => setLabelFiltro(null)}
            className={`w-full text-left px-3 py-2 rounded-lg text-sm mb-2 transition-colors ${
              labelFiltro === null
                ? 'bg-purple-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Todas las clasificaciones
          </button>
          <div className="max-h-96 overflow-y-auto space-y-2">
            {Object.entries(labelsPorCategoria).map(([categoria, labelsCat]) => (
              <div key={categoria} className="mb-3">
                <h4 className="text-xs font-semibold text-purple-400 mb-1 px-2">{categoria}</h4>
                {labelsCat.map(label => (
                  <button
                    key={label.id}
                    onClick={() => setLabelFiltro(label.id)}
                    className={`w-full text-left px-3 py-1.5 rounded-lg text-xs mb-1 transition-colors ${
                      labelFiltro === label.id
                        ? 'bg-purple-600 text-white'
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    {label.nombre_es}
                  </button>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Panel central: Lista de Proveedores */}
      <div className="flex-1 bg-slate-800 rounded-lg border border-slate-700 p-6 overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Proveedores</h1>
          <button
            onClick={() => {
              setProveedorEditando(null)
              setShowModal(true)
            }}
            className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2"
          >
            <Plus size={20} />
            Nuevo Proveedor
          </button>
        </div>

        {labelFiltro && (
          <div className="mb-4 p-3 bg-purple-600/20 border border-purple-500/50 rounded-lg flex items-center justify-between">
            <span className="text-sm text-purple-300">
              Filtrando por: <strong>{getLabelNombre(labelFiltro)}</strong>
            </span>
            <button
              onClick={() => setLabelFiltro(null)}
              className="text-purple-300 hover:text-white"
            >
              <X size={18} />
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {proveedores?.map((proveedor) => (
            <div
              key={proveedor.id}
              onClick={() => setProveedorSeleccionado(proveedor.id)}
              className={`bg-slate-700 p-4 rounded-lg border cursor-pointer transition-all ${
                proveedorSeleccionado === proveedor.id
                  ? 'border-purple-500 bg-purple-600/20'
                  : 'border-slate-600 hover:border-slate-500'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Truck className="text-purple-500" size={24} />
                  <h3 className="text-lg font-bold">{proveedor.nombre}</h3>
                </div>
                {!proveedor.activo && (
                  <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs">
                    Inactivo
                  </span>
                )}
              </div>
              <div className="space-y-1 text-sm text-slate-400">
                <p>RUC: {proveedor.ruc || 'N/A'}</p>
                <p>Teléfono: {proveedor.telefono || 'N/A'}</p>
                {proveedor.total_items !== undefined && (
                  <p className="text-purple-400">
                    {proveedor.total_items} {proveedor.total_items === 1 ? 'item' : 'items'} • {proveedor.total_labels || 0} clasificaciones
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {proveedores?.length === 0 && (
          <div className="text-center py-12">
            <Truck size={48} className="mx-auto text-slate-500 mb-4" />
            <p className="text-slate-400">No se encontraron proveedores</p>
          </div>
        )}
      </div>

      {/* Panel derecho: Detalle y Acciones */}
      {proveedorSeleccionado && detalleProveedor && (
        <div className="w-96 bg-slate-800 rounded-lg border border-slate-700 p-6 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Detalle del Proveedor</h2>
            <button
              onClick={() => setProveedorSeleccionado(null)}
              className="text-slate-400 hover:text-white"
            >
              <X size={20} />
            </button>
          </div>

          <div className="space-y-4">
            {/* Información básica */}
            <div>
              <h3 className="text-sm font-semibold text-purple-400 mb-2">Información</h3>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-slate-400">Nombre:</span>
                  <p className="text-white font-medium">{detalleProveedor.proveedor.nombre}</p>
                </div>
                <div>
                  <span className="text-slate-400">RUC:</span>
                  <p className="text-white">{detalleProveedor.proveedor.ruc || 'N/A'}</p>
                </div>
                <div>
                  <span className="text-slate-400">Teléfono:</span>
                  <p className="text-white">{detalleProveedor.proveedor.telefono || 'N/A'}</p>
                </div>
                <div>
                  <span className="text-slate-400">Email:</span>
                  <p className="text-white">{detalleProveedor.proveedor.email || 'N/A'}</p>
                </div>
                {detalleProveedor.proveedor.nombre_contacto && (
                  <div>
                    <span className="text-slate-400">Contacto:</span>
                    <p className="text-white">{detalleProveedor.proveedor.nombre_contacto}</p>
                  </div>
                )}
                {detalleProveedor.proveedor.direccion && (
                  <div>
                    <span className="text-slate-400">Dirección:</span>
                    <p className="text-white">{detalleProveedor.proveedor.direccion}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Clasificaciones que provee */}
            {detalleProveedor.labels_por_categoria && Object.keys(detalleProveedor.labels_por_categoria).length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-purple-400 mb-2">
                  Clasificaciones que Provee ({detalleProveedor.total_labels})
                </h3>
                <div className="space-y-2">
                  {Object.entries(detalleProveedor.labels_por_categoria).map(([categoria, labelsCat]) => (
                    <div key={categoria}>
                      <p className="text-xs font-semibold text-slate-400 mb-1">{categoria}</p>
                      <div className="flex flex-wrap gap-1">
                        {labelsCat.map(label => (
                          <span
                            key={label.id}
                            className="px-2 py-1 bg-purple-600/20 text-purple-300 rounded text-xs border border-purple-500/50"
                          >
                            {label.nombre_es}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Items que provee */}
            {detalleProveedor.items && detalleProveedor.items.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-purple-400 mb-2">
                  Items que Provee ({detalleProveedor.total_items})
                </h3>
                <div className="space-y-1 max-h-40 overflow-y-auto">
                  {detalleProveedor.items.map(item => (
                    <div key={item.id} className="text-sm text-slate-300 bg-slate-700/50 p-2 rounded">
                      <p className="font-medium">{item.nombre}</p>
                      <p className="text-xs text-slate-400">{item.codigo} • {item.unidad}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Acciones */}
            <div className="pt-4 border-t border-slate-700">
              <h3 className="text-sm font-semibold text-purple-400 mb-3">Acciones</h3>
              <div className="space-y-2">
                <button
                  onClick={handleEditar}
                  className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2"
                >
                  <Edit size={18} />
                  Editar
                </button>
                <button
                  onClick={handleToggleActivo}
                  disabled={toggleActivoMutation.isPending}
                  className={`w-full px-4 py-2 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 ${
                    detalleProveedor.proveedor.activo
                      ? 'bg-yellow-600 hover:bg-yellow-700'
                      : 'bg-green-600 hover:bg-green-700'
                  }`}
                >
                  <Power size={18} />
                  {detalleProveedor.proveedor.activo ? 'Desactivar' : 'Activar'}
                </button>
                <button
                  onClick={handleEliminar}
                  disabled={eliminarMutation.isPending}
                  className="w-full bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <Trash2 size={18} />
                  {eliminarMutation.isPending ? 'Eliminando...' : 'Eliminar'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal para crear/editar */}
      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false)
          setProveedorEditando(null)
        }}
        title={proveedorEditando ? 'Editar Proveedor' : 'Nuevo Proveedor'}
      >
        <ProveedorForm
          proveedor={proveedorEditando}
          onClose={() => {
            setShowModal(false)
            setProveedorEditando(null)
          }}
          onSuccess={() => {
            queryClient.invalidateQueries(['proveedores'])
            if (proveedorSeleccionado) {
              queryClient.invalidateQueries(['proveedor-detalle'])
            }
          }}
        />
      </Modal>
    </div>
  )
}
