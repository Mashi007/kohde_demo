import { useState, useEffect } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'
import { X, Search, CheckCircle2 } from 'lucide-react'

export default function ItemForm({ item, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    codigo: item?.codigo || '',
    nombre: item?.nombre || '',
    categoria: item?.categoria || 'materia_prima',
    unidad: item?.unidad || 'kg',
    calorias_por_unidad: item?.calorias_por_unidad || null,
    activo: item?.activo !== undefined ? item.activo : true,
    label_ids: item?.labels?.map(l => l.id) || [],
  })
  
  const [codigoAutoGenerado, setCodigoAutoGenerado] = useState(!item?.codigo)
  const [busquedaLabels, setBusquedaLabels] = useState('')
  const [categoriaExpandida, setCategoriaExpandida] = useState(null)

  const queryClient = useQueryClient()

  // Cargar item con costo promedio si es edición
  const { data: itemConCosto } = useQuery({
    queryKey: ['item', item?.id, 'costo'],
    queryFn: () => api.get(`/logistica/items/${item.id}`).then(res => res.data),
    enabled: !!item?.id,
  })

  // Cargar labels disponibles
  const { data: labels, isLoading: loadingLabels, error: errorLabels } = useQuery({
    queryKey: ['labels'],
    queryFn: () => api.get('/logistica/labels?activo=true').then(res => res.data),
    retry: 2,
  })

  // Filtrar labels por búsqueda
  const labelsFiltradas = labels?.filter(label => {
    if (!busquedaLabels) return true
    const busqueda = busquedaLabels.toLowerCase()
    return (
      label.nombre_es?.toLowerCase().includes(busqueda) ||
      label.nombre_en?.toLowerCase().includes(busqueda) ||
      label.categoria_principal?.toLowerCase().includes(busqueda)
    )
  }) || []

  // Agrupar labels por categoría
  const labelsPorCategoria = labelsFiltradas.reduce((acc, label) => {
    const cat = label.categoria_principal || 'Sin categoría'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(label)
    return acc
  }, {})

  // Ordenar categorías
  const categoriasOrdenadas = Object.keys(labelsPorCategoria).sort()

  const createMutation = useMutation({
    mutationFn: (data) => api.post('/logistica/items', data),
    onSuccess: () => {
      toast.success('Item creado correctamente')
      queryClient.invalidateQueries(['items'])
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al crear item')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    // Si el código debe generarse automáticamente, enviar sin código o vacío
    const datosEnvio = { ...formData }
    if (codigoAutoGenerado) {
      datosEnvio.codigo = '' // El backend generará el código automáticamente
    }
    createMutation.mutate(datosEnvio)
  }

  const toggleLabel = (labelId) => {
    setFormData(prev => {
      const currentIds = prev.label_ids || []
      if (currentIds.includes(labelId)) {
        return { ...prev, label_ids: currentIds.filter(id => id !== labelId) }
      } else {
        return { ...prev, label_ids: [...currentIds, labelId] }
      }
    })
  }

  const removeLabel = (labelId) => {
    setFormData(prev => ({
      ...prev,
      label_ids: (prev.label_ids || []).filter(id => id !== labelId)
    }))
  }

  const getSelectedLabels = () => {
    if (!labels || !formData.label_ids) return []
    return labels.filter(l => formData.label_ids.includes(l.id))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium">Código</label>
            <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
              <input
                type="checkbox"
                checked={codigoAutoGenerado}
                onChange={(e) => {
                  setCodigoAutoGenerado(e.target.checked)
                  if (e.target.checked) {
                    setFormData({ ...formData, codigo: '' })
                  }
                }}
                className="rounded"
              />
              Generar automáticamente
            </label>
          </div>
          <input
            type="text"
            required={!codigoAutoGenerado}
            disabled={codigoAutoGenerado}
            value={codigoAutoGenerado ? '(Se generará automáticamente)' : formData.codigo}
            onChange={(e) => {
              if (!codigoAutoGenerado) {
                setFormData({ ...formData, codigo: e.target.value })
              }
            }}
            className={`w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500 ${
              codigoAutoGenerado ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            placeholder={codigoAutoGenerado ? '' : 'Ej: MP-20240101-0001'}
          />
          {codigoAutoGenerado && (
            <p className="text-xs text-slate-400 mt-1">
              El código se generará automáticamente al guardar
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Unidad Estándar *</label>
          <select
            required
            value={formData.unidad}
            onChange={(e) => setFormData({ ...formData, unidad: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          >
            <option value="kg">Kilogramos (kg)</option>
            <option value="g">Gramos (g)</option>
            <option value="qq">Quintales (qq)</option>
            <option value="l">Litros (l)</option>
            <option value="ml">Mililitros (ml)</option>
            <option value="unidad">Unidad</option>
            <option value="caja">Caja</option>
            <option value="paquete">Paquete</option>
          </select>
          <p className="text-xs text-slate-400 mt-1">
            Esta es la unidad estándar del item. Todas las facturas se convertirán automáticamente a esta unidad.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Nombre *</label>
          <input
            type="text"
            required
            value={formData.nombre}
            onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Calorías por {formData.unidad}</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={formData.calorias_por_unidad || ''}
            onChange={(e) => setFormData({ 
              ...formData, 
              calorias_por_unidad: e.target.value === '' ? null : parseFloat(e.target.value) 
            })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
            placeholder="Ej: 250"
          />
          <p className="text-xs text-slate-400 mt-1">
            Calorías por {formData.unidad} de este item (opcional)
          </p>
        </div>
      </div>

      {/* Costo Unitario Promedio (solo lectura, calculado) */}
      {item?.id && itemConCosto?.costo_unitario_promedio !== undefined && (
        <div>
          <label className="block text-sm font-medium mb-2">Costo Unitario Promedio</label>
          <div className="px-4 py-2 bg-slate-700/50 border border-slate-600 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-slate-300">
                {itemConCosto.costo_unitario_promedio ? (
                  <>
                    <span className="text-2xl font-bold text-purple-400">
                      ${itemConCosto.costo_unitario_promedio.toFixed(2)}
                    </span>
                    <span className="text-sm text-slate-400 ml-2">por {formData.unidad}</span>
                  </>
                ) : (
                  <span className="text-slate-500">No hay facturas aprobadas</span>
                )}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Promedio calculado de las últimas 3 facturas aprobadas
            </p>
          </div>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium mb-2">Categoría General *</label>
        <select
          required
          value={formData.categoria}
          onChange={(e) => setFormData({ ...formData, categoria: e.target.value })}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        >
          <option value="materia_prima">Materia Prima</option>
          <option value="producto_terminado">Producto Terminado</option>
          <option value="insumo">Insumo</option>
          <option value="bebida">Bebida</option>
          <option value="limpieza">Limpieza</option>
          <option value="otros">Otros</option>
        </select>
        <p className="text-xs text-slate-400 mt-1">
          Categoría general del item. La clasificación detallada se selecciona abajo.
        </p>
      </div>

      {/* Labels seleccionadas */}
      {getSelectedLabels().length > 0 && (
        <div>
          <label className="block text-sm font-medium mb-2">Labels Seleccionadas</label>
          <div className="flex flex-wrap gap-2">
            {getSelectedLabels().map(label => (
              <span
                key={label.id}
                className="inline-flex items-center gap-1 px-3 py-1 bg-purple-600/20 text-purple-300 rounded-full text-sm border border-purple-500/50"
              >
                {label.nombre_es}
                <button
                  type="button"
                  onClick={() => removeLabel(label.id)}
                  className="hover:text-red-400"
                >
                  <X size={14} />
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Selector de Labels */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Clasificación de Alimentos
        </label>
        <p className="text-xs text-slate-400 mb-3">
          Selecciona las clasificaciones que aplican a este item. Esto facilita la búsqueda y la generación de recetas/menús.
        </p>

        {/* Buscador de labels */}
        <div className="mb-3 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            value={busquedaLabels}
            onChange={(e) => setBusquedaLabels(e.target.value)}
            placeholder="Buscar clasificación (ej: cebolla, carne, lácteo...)"
            className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500 text-sm"
          />
        </div>

        {/* Contador de seleccionadas */}
        {formData.label_ids && formData.label_ids.length > 0 && (
          <div className="mb-3 p-2 bg-purple-600/20 border border-purple-500/50 rounded-lg">
            <p className="text-sm text-purple-300">
              <CheckCircle2 className="inline mr-2" size={16} />
              {formData.label_ids.length} clasificación{formData.label_ids.length !== 1 ? 'es' : ''} seleccionada{formData.label_ids.length !== 1 ? 's' : ''}
            </p>
          </div>
        )}

        {/* Lista de labels */}
        {loadingLabels ? (
          <div className="p-8 text-center border border-slate-600 rounded-lg bg-slate-800">
            <div className="animate-pulse">
              <p className="text-slate-400 mb-2">Cargando clasificaciones...</p>
              <p className="text-xs text-slate-500">Por favor espera</p>
            </div>
          </div>
        ) : errorLabels ? (
          <div className="p-8 text-center border border-red-500/50 rounded-lg bg-red-500/10">
            <p className="text-red-400 mb-2">Error al cargar clasificaciones</p>
            <p className="text-xs text-red-300">
              {errorLabels.message || 'No se pudieron cargar las clasificaciones'}
            </p>
          </div>
        ) : categoriasOrdenadas.length === 0 ? (
          <div className="p-8 text-center border border-slate-600 rounded-lg bg-slate-800">
            <p className="text-slate-400 mb-2">
              {busquedaLabels ? 'No se encontraron resultados' : 'No hay clasificaciones disponibles'}
            </p>
            <p className="text-xs text-slate-500">
              {busquedaLabels ? (
                <>
                  No hay clasificaciones que coincidan con "{busquedaLabels}". 
                  <button 
                    type="button"
                    onClick={() => setBusquedaLabels('')}
                    className="text-purple-400 hover:text-purple-300 underline ml-1"
                  >
                    Limpiar búsqueda
                  </button>
                </>
              ) : (
                'Ejecuta el script de inicialización para cargar las clasificaciones: python scripts/init_food_labels.py'
              )}
            </p>
          </div>
        ) : (
          <div className="max-h-96 overflow-y-auto bg-slate-800 border border-slate-600 rounded-lg p-4 space-y-4">
            {categoriasOrdenadas.map((categoria) => {
              const labelsCat = labelsPorCategoria[categoria]
              const seleccionadasEnCategoria = labelsCat.filter(label => formData.label_ids?.includes(label.id)).length
              
              return (
                <div key={categoria} className="border-b border-slate-700 pb-3 last:border-b-0">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-semibold text-purple-400 uppercase tracking-wide">
                      {categoria}
                    </h4>
                    <span className="text-xs text-slate-500">
                      {seleccionadasEnCategoria > 0 && (
                        <span className="text-purple-400 font-medium mr-1">
                          {seleccionadasEnCategoria}/{labelsCat.length}
                        </span>
                      )}
                      {labelsCat.length} opciones
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {labelsCat
                      .sort((a, b) => a.nombre_es.localeCompare(b.nombre_es))
                      .map(label => {
                      const isSelected = formData.label_ids?.includes(label.id)
                      return (
                        <button
                          key={label.id}
                          type="button"
                          onClick={() => toggleLabel(label.id)}
                          className={`px-3 py-1.5 rounded-lg text-sm transition-all flex items-center gap-1.5 ${
                            isSelected
                              ? 'bg-purple-600 text-white border-2 border-purple-400 shadow-lg shadow-purple-500/20 font-medium'
                              : 'bg-slate-700 text-slate-300 border border-slate-600 hover:bg-slate-600 hover:border-slate-500 hover:text-white'
                          }`}
                          title={label.descripcion || label.nombre_es}
                        >
                          {isSelected && <CheckCircle2 size={14} className="flex-shrink-0" />}
                          <span>{label.nombre_es}</span>
                        </button>
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Mensaje de ayuda */}
        {formData.label_ids && formData.label_ids.length === 0 && !loadingLabels && (
          <p className="text-xs text-yellow-400 mt-2 flex items-center gap-1">
            <span>💡</span>
            <span>Selecciona al menos una clasificación para facilitar la búsqueda y organización</span>
          </p>
        )}
      </div>

      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={createMutation.isPending}
          className="flex-1 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {createMutation.isPending ? 'Guardando...' : 'Crear Item'}
        </button>
        <button
          type="button"
          onClick={onClose}
          className="flex-1 bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg"
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}
