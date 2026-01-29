import { useState, useMemo } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'
import LabelForm from './LabelForm'
import { Plus } from 'lucide-react'

export default function ItemForm({ item, onClose, onSuccess }) {
  const [mostrarFormLabel, setMostrarFormLabel] = useState(false)
  
  const [formData, setFormData] = useState({
    codigo: item?.codigo || '',
    nombre: item?.nombre || '',
    categoria: item?.categoria || 'materia_prima',
    unidad: item?.unidad || 'kg',
    calorias_por_unidad: item?.calorias_por_unidad || null,
    activo: item?.activo !== undefined ? item.activo : true,
    label_ids: item?.labels?.map(l => l.id) || [],
    costo_unitario_manual: item?.costo_unitario_actual || null,
  })
  
  const [codigoAutoGenerado, setCodigoAutoGenerado] = useState(!item?.codigo)

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
    queryFn: async () => {
      try {
        const res = await api.get('/logistica/labels?activo=true')
        const data = res.data || []
        console.log('Labels cargadas:', data.length, data)
        return data
      } catch (error) {
        console.error('Error cargando labels:', error)
        console.error('Error completo:', error.response?.data || error.message)
        throw error
      }
    },
    retry: 2,
    staleTime: 5 * 60 * 1000, // Cache por 5 minutos
  })

  // Preparar labels para el selector (agrupadas por categoría)
  const labelsAgrupadas = useMemo(() => {
    if (!labels || !Array.isArray(labels) || labels.length === 0) {
      return {}
    }
    return labels.reduce((acc, label) => {
      const cat = label.categoria_principal || 'Sin categoría'
      if (!acc[cat]) acc[cat] = []
      acc[cat].push(label)
      return acc
    }, {})
  }, [labels])

  // Obtener todas las labels ordenadas por categoría y nombre
  const todasLasLabels = useMemo(() => {
    if (!labels || !Array.isArray(labels)) {
      return []
    }
    return [...labels].sort((a, b) => {
      const catA = a.categoria_principal || 'Sin categoría'
      const catB = b.categoria_principal || 'Sin categoría'
      if (catA !== catB) {
        return catA.localeCompare(catB)
      }
      return a.nombre_es.localeCompare(b.nombre_es)
    })
  }, [labels])

  // Obtener la categoría seleccionada basada en el label_id actual
  const categoriaSeleccionada = useMemo(() => {
    if (!formData.label_ids || formData.label_ids.length === 0 || !labels) {
      return ''
    }
    const labelSeleccionada = labels.find(l => l.id === formData.label_ids[0])
    return labelSeleccionada?.categoria_principal || ''
  }, [formData.label_ids, labels])

  // Obtener todas las categorías únicas ordenadas
  const categoriasDisponibles = useMemo(() => {
    if (!labels || !Array.isArray(labels)) {
      return []
    }
    const categorias = new Set(labels.map(l => l.categoria_principal).filter(Boolean))
    return Array.from(categorias).sort()
  }, [labels])

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

  // Mutación para actualizar costo unitario manual de un item existente
  const updateCostoMutation = useMutation({
    mutationFn: ({ itemId, costo }) => api.put(`/logistica/items/${itemId}/costo`, { costo }),
    onSuccess: () => {
      toast.success('Costo unitario actualizado correctamente')
      queryClient.invalidateQueries(['item', item?.id, 'costo'])
      queryClient.invalidateQueries(['items'])
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al actualizar costo unitario')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    // Si el código debe generarse automáticamente, enviar sin código o vacío
    const datosEnvio = { ...formData }
    if (codigoAutoGenerado) {
      datosEnvio.codigo = '' // El backend generará el código automáticamente
    }
    
    // Si hay costo manual, enviarlo como costo_unitario_actual
    if (datosEnvio.costo_unitario_manual !== null && datosEnvio.costo_unitario_manual !== undefined) {
      datosEnvio.costo_unitario_actual = datosEnvio.costo_unitario_manual
    }
    
    // Eliminar costo_unitario_manual del objeto antes de enviar
    delete datosEnvio.costo_unitario_manual
    
    createMutation.mutate(datosEnvio)
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

      {/* Costo Unitario Manual (solo si no se puede calcular automáticamente) */}
      {(!item?.id || (item?.id && itemConCosto && !itemConCosto.costo_unitario_promedio)) && (
        <div>
          <label className="block text-sm font-medium mb-2">
            Costo Unitario Manual {!item?.id && <span className="text-slate-400">(Opcional)</span>}
          </label>
          <div className="flex gap-2">
            <input
              type="number"
              step="0.01"
              min="0"
              value={formData.costo_unitario_manual || ''}
              onChange={(e) => setFormData({ 
                ...formData, 
                costo_unitario_manual: e.target.value === '' ? null : parseFloat(e.target.value) 
              })}
              className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Ej: 25.50"
            />
            {item?.id && formData.costo_unitario_manual !== null && formData.costo_unitario_manual !== item?.costo_unitario_actual && (
              <button
                type="button"
                onClick={() => {
                  updateCostoMutation.mutate({
                    itemId: item.id,
                    costo: formData.costo_unitario_manual
                  })
                }}
                disabled={updateCostoMutation.isPending}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg disabled:opacity-50 whitespace-nowrap"
              >
                {updateCostoMutation.isPending ? 'Guardando...' : 'Actualizar Costo'}
              </button>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {!item?.id 
              ? 'Ingresa el costo unitario manual si no hay facturas aprobadas aún. Este valor se usará hasta que el sistema pueda calcular el promedio automáticamente.'
              : 'Ingresa un costo unitario manual ya que el sistema no puede calcularlo automáticamente por falta de facturas aprobadas. Haz clic en "Actualizar Costo" para guardar el valor.'
            }
          </p>
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

      {/* Selector de Clasificación de Alimentos */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Clasificación de Alimentos
        </label>
        <p className="text-xs text-slate-400 mb-3">
          Selecciona la clasificación que aplica a este item. Esto facilita la búsqueda y la generación de recetas/menús.
        </p>

        {loadingLabels ? (
          <div className="p-4 text-center border border-slate-600 rounded-lg bg-slate-800">
            <div className="animate-pulse">
              <p className="text-slate-400 text-sm">Cargando clasificaciones...</p>
            </div>
          </div>
        ) : errorLabels ? (
          <div className="p-4 text-center border border-red-500/50 rounded-lg bg-red-500/10">
            <p className="text-red-400 text-sm mb-1">Error al cargar clasificaciones</p>
            <p className="text-xs text-red-300">
              {errorLabels.message || 'No se pudieron cargar las clasificaciones'}
            </p>
          </div>
        ) : todasLasLabels.length === 0 ? (
          <div className="p-4 text-center border border-yellow-500/50 rounded-lg bg-yellow-500/10">
            <p className="text-yellow-400 text-sm mb-2 font-medium">⚠️ No hay clasificaciones disponibles</p>
            <p className="text-xs text-yellow-300 mb-2">
              Las clasificaciones de alimentos no se han inicializado en la base de datos.
            </p>
            <div className="text-xs text-yellow-200 bg-yellow-500/20 p-2 rounded mt-2 font-mono">
              <p className="mb-1">Para inicializar, ejecuta en el servidor:</p>
              <code className="block bg-slate-900/50 p-2 rounded">
                python scripts/init_food_labels.py
              </code>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              O verifica que el endpoint <code className="bg-slate-800 px-1 rounded">/logistica/labels</code> esté funcionando correctamente.
            </p>
          </div>
        ) : (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <select
                value={categoriaSeleccionada}
                onChange={(e) => {
                  const categoriaSeleccionada = e.target.value
                  if (!categoriaSeleccionada) {
                    setFormData(prev => ({
                      ...prev,
                      label_ids: []
                    }))
                    return
                  }
                  
                  // Buscar el primer label de la categoría seleccionada
                  const labelsDeCategoria = labelsAgrupadas[categoriaSeleccionada] || []
                  if (labelsDeCategoria.length > 0) {
                    const primerLabel = labelsDeCategoria[0]
                    setFormData(prev => ({
                      ...prev,
                      label_ids: [primerLabel.id]
                    }))
                  }
                }}
                className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              >
                <option value="">Selecciona una categoría...</option>
                {categoriasDisponibles.map((categoria) => (
                  <option key={categoria} value={categoria}>
                    {categoria}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => setMostrarFormLabel(true)}
                className="px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors flex items-center gap-2 whitespace-nowrap"
                title="Crear nueva clasificación"
              >
                <Plus className="w-4 h-4" />
                <span className="hidden sm:inline">Nueva</span>
              </button>
            </div>
            {categoriaSeleccionada && (
              <p className="text-xs text-slate-400 mt-1">
                Categoría seleccionada: <span className="text-purple-400 font-medium">{categoriaSeleccionada}</span>
              </p>
            )}
            <p className="text-xs text-slate-400 mt-1">
              {categoriasDisponibles.length} categoría{categoriasDisponibles.length !== 1 ? 's' : ''} disponible{categoriasDisponibles.length !== 1 ? 's' : ''}
            </p>
          </div>
        )}
        
        {/* Modal para crear nueva clasificación */}
        {mostrarFormLabel && (
          <LabelForm
            onClose={() => setMostrarFormLabel(false)}
            onSuccess={(nuevaLabel) => {
              // Seleccionar automáticamente la nueva clasificación creada
              if (nuevaLabel && nuevaLabel.id) {
                setFormData(prev => ({
                  ...prev,
                  label_ids: [nuevaLabel.id]
                }))
              }
            }}
          />
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
