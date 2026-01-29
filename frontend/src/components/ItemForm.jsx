import { useState, useMemo, useEffect } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'
import logger from '../utils/logger'
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
  
  // Estado separado para el valor del input de costo (como string para permitir escritura libre)
  const [costoInputValue, setCostoInputValue] = useState('')
  
  const [codigoAutoGenerado, setCodigoAutoGenerado] = useState(!item?.codigo)

  const queryClient = useQueryClient()

  // Inicializar costoInputValue cuando se carga un item existente o cambia el costo
  useEffect(() => {
    if (item?.costo_unitario_actual !== null && item?.costo_unitario_actual !== undefined) {
      // Formatear a 2 decimales automáticamente
      const valorFormateado = parseFloat(item.costo_unitario_actual).toFixed(2)
      setCostoInputValue(valorFormateado)
      setFormData(prev => ({
        ...prev,
        costo_unitario_manual: item.costo_unitario_actual
      }))
    } else {
      setCostoInputValue('')
    }
  }, [item?.costo_unitario_actual])

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
        logger.debug('Labels cargadas:', data.length)
        return data
      } catch (error) {
        logger.error('Error cargando labels:', error.response?.data || error.message)
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
    onSuccess: async () => {
      toast.success('Item creado correctamente')
      // Invalidar todas las queries relacionadas con items
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['items'] }),
        queryClient.invalidateQueries({ queryKey: ['items-con-costo'] }),
        queryClient.invalidateQueries({ queryKey: ['stock-bajo'] }),
      ])
      // Refetch inmediato para asegurar que los datos estén actualizados
      await queryClient.refetchQueries({ queryKey: ['items'] })
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al crear item')
    },
  })

  const updateMutation = useMutation({
    mutationFn: (data) => api.put(`/logistica/items/${item?.id}`, data),
    onSuccess: async () => {
      toast.success('Item actualizado correctamente')
      // Invalidar todas las queries relacionadas con items
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['items'] }),
        queryClient.invalidateQueries({ queryKey: ['item', item?.id] }),
        queryClient.invalidateQueries({ queryKey: ['items-con-costo'] }),
        queryClient.invalidateQueries({ queryKey: ['stock-bajo'] }),
      ])
      // Refetch inmediato para asegurar que los datos estén actualizados
      await queryClient.refetchQueries({ queryKey: ['items'] })
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al actualizar item')
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
    
    // Si hay costo manual, enviarlo como costo_unitario_actual (formateado a 2 decimales)
    if (datosEnvio.costo_unitario_manual !== null && datosEnvio.costo_unitario_manual !== undefined) {
      datosEnvio.costo_unitario_actual = parseFloat(datosEnvio.costo_unitario_manual.toFixed(2))
    }
    
    // Eliminar costo_unitario_manual del objeto antes de enviar
    delete datosEnvio.costo_unitario_manual
    
    // Si estamos editando, usar updateMutation, si no, createMutation
    if (item?.id) {
      updateMutation.mutate(datosEnvio)
    } else {
      createMutation.mutate(datosEnvio)
    }
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
            onBlur={(e) => {
              // Formatear a primera letra mayúscula y resto minúsculas
              const valor = e.target.value.trim()
              if (valor) {
                const formateado = valor.charAt(0).toUpperCase() + valor.slice(1).toLowerCase()
                setFormData({ ...formData, nombre: formateado })
              }
            }}
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
              type="text"
              inputMode="decimal"
              value={costoInputValue}
              onChange={(e) => {
                const valor = e.target.value.trim()
                
                // Permitir vacío
                if (valor === '') {
                  setCostoInputValue('')
                  setFormData({ 
                    ...formData, 
                    costo_unitario_manual: null 
                  })
                  return
                }
                
                // Permitir solo números y un punto decimal con hasta 2 decimales
                const regex = /^\d*\.?\d{0,2}$/
                if (regex.test(valor)) {
                  // Actualizar el valor del input (como string para permitir escritura libre)
                  setCostoInputValue(valor)
                  
                  // Convertir a número y guardar en formData
                  const numero = parseFloat(valor)
                  if (!isNaN(numero) && numero >= 0) {
                    setFormData({ 
                      ...formData, 
                      costo_unitario_manual: numero 
                    })
                  }
                }
              }}
              onBlur={(e) => {
                // Formatear a 2 decimales automáticamente cuando pierde el foco
                if (costoInputValue && costoInputValue !== '') {
                  const numero = parseFloat(costoInputValue)
                  if (!isNaN(numero) && numero >= 0) {
                    // Usar toFixed(2) directamente para mantener formato "XX.XX" siempre
                    const valorFormateadoString = numero.toFixed(2)
                    const valorFormateado = parseFloat(valorFormateadoString)
                    setCostoInputValue(valorFormateadoString) // Mantener formato "54.00" no "54"
                    setFormData({ 
                      ...formData, 
                      costo_unitario_manual: valorFormateado 
                    })
                  }
                } else {
                  // Si está vacío, asegurar que formData también esté en null
                  setFormData({ 
                    ...formData, 
                    costo_unitario_manual: null 
                  })
                }
              }}
              onFocus={(e) => {
                // Cuando obtiene el foco, asegurar formato de 2 decimales si hay valor
                if (costoInputValue && costoInputValue !== '') {
                  const numero = parseFloat(costoInputValue)
                  if (!isNaN(numero)) {
                    const valorFormateadoString = numero.toFixed(2)
                    // Solo actualizar si el formato es diferente (ej: "54" -> "54.00")
                    if (costoInputValue !== valorFormateadoString) {
                      setCostoInputValue(valorFormateadoString)
                    }
                  }
                }
              }}
              className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Ej: 25.50"
            />
            {item?.id && formData.costo_unitario_manual !== null && formData.costo_unitario_manual !== item?.costo_unitario_actual && (
              <button
                type="button"
                onClick={() => {
                  // Formatear a 2 decimales antes de enviar
                  const costoFormateado = parseFloat(formData.costo_unitario_manual.toFixed(2))
                  updateCostoMutation.mutate({
                    itemId: item.id,
                    costo: costoFormateado
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
            onSuccess={async (nuevaLabel) => {
              if (nuevaLabel && nuevaLabel.id) {
                try {
                  // Primero seleccionar la nueva label inmediatamente para evitar que se vacíe
                  setFormData(prev => ({
                    ...prev,
                    label_ids: [nuevaLabel.id]
                  }))
                  
                  // Luego invalidar y refetch las queries en segundo plano
                  queryClient.invalidateQueries(['labels'])
                  
                  // Refetch las labels para obtener la nueva (sin await para no bloquear)
                  queryClient.refetchQueries({ queryKey: ['labels'] }).then(() => {
                    // Asegurar que la selección se mantenga después del refetch
                    setFormData(prev => {
                      // Si ya está seleccionada, mantenerla
                      if (prev.label_ids && prev.label_ids.includes(nuevaLabel.id)) {
                        return prev
                      }
                      // Si no, seleccionarla
                      return {
                        ...prev,
                        label_ids: [nuevaLabel.id]
                      }
                    })
                  })
                  
                  // Cerrar el modal después de un pequeño delay
                  setTimeout(() => {
                    setMostrarFormLabel(false)
                  }, 200)
                } catch (error) {
                  logger.error('Error al actualizar labels:', error.response?.data || error.message)
                  // Aún así, mantener la selección
                  setFormData(prev => ({
                    ...prev,
                    label_ids: [nuevaLabel.id]
                  }))
                  setMostrarFormLabel(false)
                }
              }
            }}
          />
        )}
      </div>

      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={createMutation.isPending || updateMutation.isPending}
          className="flex-1 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {(createMutation.isPending || updateMutation.isPending) 
            ? 'Guardando...' 
            : item?.id ? 'Actualizar Item' : 'Crear Item'}
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
