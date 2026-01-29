import { useState } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'

export default function ItemForm({ item, onClose, onSuccess }) {
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
    queryFn: () => api.get('/logistica/labels?activo=true').then(res => res.data),
    retry: 2,
  })

  // Preparar labels para el selector (agrupadas por categoría)
  const labelsAgrupadas = labels?.reduce((acc, label) => {
    const cat = label.categoria_principal || 'Sin categoría'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(label)
    return acc
  }, {}) || {}

  // Obtener todas las labels ordenadas por categoría y nombre
  const todasLasLabels = labels?.sort((a, b) => {
    const catA = a.categoria_principal || 'Sin categoría'
    const catB = b.categoria_principal || 'Sin categoría'
    if (catA !== catB) {
      return catA.localeCompare(catB)
    }
    return a.nombre_es.localeCompare(b.nombre_es)
  }) || []

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

  // Obtener el ID de la label seleccionada (primera del array o null)
  const labelIdSeleccionada = formData.label_ids && formData.label_ids.length > 0 
    ? formData.label_ids[0] 
    : null

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
          <div className="p-4 text-center border border-slate-600 rounded-lg bg-slate-800">
            <p className="text-slate-400 text-sm mb-1">No hay clasificaciones disponibles</p>
            <p className="text-xs text-slate-500">
              Ejecuta el script de inicialización para cargar las clasificaciones: python scripts/init_food_labels.py
            </p>
          </div>
        ) : (
          <select
            value={labelIdSeleccionada || ''}
            onChange={(e) => {
              const selectedId = e.target.value ? parseInt(e.target.value) : null
              setFormData(prev => ({
                ...prev,
                label_ids: selectedId ? [selectedId] : []
              }))
            }}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          >
            <option value="">Selecciona una clasificación...</option>
            {Object.keys(labelsAgrupadas).sort().map((categoria) => {
              const labelsCat = labelsAgrupadas[categoria].sort((a, b) => 
                a.nombre_es.localeCompare(b.nombre_es)
              )
              return (
                <optgroup key={categoria} label={categoria}>
                  {labelsCat.map(label => (
                    <option key={label.id} value={label.id}>
                      {label.nombre_es}
                    </option>
                  ))}
                </optgroup>
              )
            })}
          </select>
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
