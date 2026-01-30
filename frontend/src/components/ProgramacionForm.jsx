import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api, { extractData } from '../config/api'
import toast from 'react-hot-toast'
import { X, Plus, Trash2, Calculator } from 'lucide-react'
import { TIEMPO_COMIDA_VALUES, TIEMPO_COMIDA_OPTIONS, TIEMPO_COMIDA_DEFAULT } from '../constants/tiempoComida'

export default function ProgramacionForm({ programacion, fecha, tiempoComida, onClose, onSuccess }) {
  const queryClient = useQueryClient()
  
  const [formData, setFormData] = useState({
    fecha_desde: programacion?.fecha_desde || programacion?.fecha || fecha || new Date().toISOString().split('T')[0],
    fecha_hasta: programacion?.fecha_hasta || programacion?.fecha || fecha || new Date().toISOString().split('T')[0],
    tiempo_comida: tiempoComida || TIEMPO_COMIDA_VALUES.ALMUERZO, // Cambiar a ALMUERZO porque es el tipo más común
    ubicacion: programacion?.ubicacion || 'restaurante_A',
    charolas_planificadas: programacion?.charolas_planificadas || 0,
    // Al cargar una programación existente, solo guardamos el receta_id
    // La cantidad se tomará de charolas_planificadas automáticamente
    recetas: programacion?.items?.map(item => ({
      receta_id: item.receta_id,
    })) || [],
  })
  
  // Cargar recetas disponibles según el tipo de servicio
  // Cargar TODAS las recetas activas, no solo las del tipo específico
  const { data: recetasDisponiblesResponse, isLoading: cargandoRecetas, error: errorRecetas } = useQuery({
    queryKey: ['recetas', 'todas', formData.tiempo_comida],
    queryFn: async () => {
      try {
        // Cargar todas las recetas activas, sin filtrar por tipo
        // Esto permite usar cualquier receta en cualquier servicio
        const response = await api.get(`/planificacion/recetas?activa=true`)
        const todasLasRecetas = extractData(response)
        
        // Si no hay recetas, retornar array vacío
        if (!Array.isArray(todasLasRecetas) || todasLasRecetas.length === 0) {
          return []
        }
        
        return todasLasRecetas
      } catch (error) {
        console.error('Error al cargar recetas:', error)
        toast.error(`Error al cargar recetas: ${error.response?.data?.error || error.message}`)
        return [] // Retornar array vacío en caso de error
      }
    },
    retry: 2, // Reintentar 2 veces en caso de error
  })

  // Asegurar que recetasDisponibles sea un array
  const recetasDisponibles = Array.isArray(recetasDisponiblesResponse) ? recetasDisponiblesResponse : []
  
  // Debug: Log para verificar que las recetas se cargan
  useEffect(() => {
    if (import.meta.env.DEV) {
      console.log('Recetas disponibles:', recetasDisponibles)
      console.log('Tiempo comida seleccionado:', formData.tiempo_comida)
      console.log('Cargando recetas:', cargandoRecetas)
      console.log('Error recetas:', errorRecetas)
    }
  }, [recetasDisponibles, formData.tiempo_comida, cargandoRecetas, errorRecetas])
  
  // Calcular totales del servicio usando charolas_planificadas para todas las recetas
  const calcularTotales = () => {
    let caloriasTotales = 0
    let costoTotal = 0
    let caloriasPorCharola = 0
    let costoPorCharola = 0
    let totalRecetas = formData.recetas.length
    const cantidadPorReceta = formData.charolas_planificadas || 0
    let totalPorciones = cantidadPorReceta * totalRecetas
    
    formData.recetas.forEach(recetaProg => {
      const receta = recetasDisponibles?.find(r => r.id === recetaProg.receta_id)
      if (receta) {
        // Calcular para el total de charolas
        if (receta.calorias_por_porcion) {
          caloriasTotales += receta.calorias_por_porcion * cantidadPorReceta
          caloriasPorCharola += receta.calorias_por_porcion
        }
        if (receta.costo_por_porcion) {
          costoTotal += receta.costo_por_porcion * cantidadPorReceta
          costoPorCharola += receta.costo_por_porcion
        }
      }
    })
    
    return {
      caloriasTotales: Math.round(caloriasTotales * 100) / 100,
      costoTotal: Math.round(costoTotal * 100) / 100,
      caloriasPorCharola: Math.round(caloriasPorCharola * 100) / 100,
      costoPorCharola: Math.round(costoPorCharola * 100) / 100,
      totalRecetas,
      totalPorciones,
      porcionesPorCharola: totalRecetas, // Cada charola tiene una porción de cada receta
    }
  }
  
  const totales = calcularTotales()
  
  const agregarReceta = () => {
    if (cargandoRecetas) {
      toast.info('Cargando recetas, por favor espera...')
      return
    }
    
    if (errorRecetas) {
      toast.error('Error al cargar recetas. Por favor, intenta nuevamente.')
      return
    }
    
    if (!recetasDisponibles || recetasDisponibles.length === 0) {
      toast.error('No hay recetas disponibles para este tipo de servicio')
      return
    }
    
    const primeraReceta = recetasDisponibles[0]
    // Verificar que no esté ya agregada
    if (formData.recetas.some(r => r.receta_id === primeraReceta.id)) {
      toast.info(`La receta "${primeraReceta.nombre}" ya está agregada`)
      return
    }
    
    setFormData({
      ...formData,
      recetas: [
        ...formData.recetas,
        {
          receta_id: primeraReceta.id,
          // cantidad_porciones se calculará automáticamente desde charolas_planificadas
        },
      ],
    })
    toast.success(`Receta "${primeraReceta.nombre}" agregada`)
  }
  
  const eliminarReceta = (index) => {
    setFormData({
      ...formData,
      recetas: formData.recetas.filter((_, i) => i !== index),
    })
  }
  
  const actualizarReceta = (index, campo, valor) => {
    const nuevasRecetas = [...formData.recetas]
    // Si se cambia la receta, verificar que no esté duplicada
    if (campo === 'receta_id') {
      const recetaId = parseInt(valor)
      if (formData.recetas.some((r, i) => i !== index && r.receta_id === recetaId)) {
        toast.error('Esta receta ya está agregada al menú')
        return
      }
    }
    nuevasRecetas[index] = {
      ...nuevasRecetas[index],
      [campo]: valor,
    }
    setFormData({
      ...formData,
      recetas: nuevasRecetas,
    })
  }
  
  const createMutation = useMutation({
    mutationFn: (data) => api.post('/planificacion/programacion', data),
    onSuccess: () => {
      toast.success('Programación creada correctamente')
      queryClient.invalidateQueries(['programaciones'])
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al crear programación')
    },
  })
  
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => api.put(`/planificacion/programacion/${id}`, data),
    onSuccess: () => {
      toast.success('Programación actualizada correctamente')
      queryClient.invalidateQueries(['programaciones'])
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al actualizar programación')
    },
  })
  
  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (formData.recetas.length === 0) {
      toast.error('Debes agregar al menos una receta')
      return
    }
    
    // Validar que todas las recetas tengan receta_id seleccionado
    const recetasInvalidas = formData.recetas.filter(r => !r.receta_id)
    if (recetasInvalidas.length > 0) {
      toast.error('Todas las recetas deben estar seleccionadas')
      return
    }
    
    // Validar que haya charolas programadas
    if (!formData.charolas_planificadas || formData.charolas_planificadas <= 0) {
      toast.error('Debes especificar la cantidad de charolas programadas')
      return
    }
    
    const datos = {
      ...formData,
      recetas: formData.recetas.map(r => ({
        receta_id: r.receta_id,
        // Usar charolas_planificadas como cantidad_porciones para todas las recetas
        cantidad_porciones: parseInt(formData.charolas_planificadas) || 0,
      })),
    }
    
    if (programacion?.id) {
      updateMutation.mutate({ id: programacion.id, data: datos })
    } else {
      createMutation.mutate(datos)
    }
  }
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-lg border border-slate-700 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h2 className="text-2xl font-bold">
            {programacion?.id ? 'Editar Programación' : 'Nueva Programación'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-700 rounded transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Formulario */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Fechas y Servicio */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Fecha Desde *</label>
              <input
                type="date"
                required
                value={formData.fecha_desde}
                onChange={(e) => {
                  const nuevaFechaDesde = e.target.value
                  setFormData({
                    ...formData,
                    fecha_desde: nuevaFechaDesde,
                    // Si fecha_hasta es menor que fecha_desde, actualizarla también
                    fecha_hasta: formData.fecha_hasta < nuevaFechaDesde ? nuevaFechaDesde : formData.fecha_hasta
                  })
                }}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Fecha Hasta *</label>
              <input
                type="date"
                required
                min={formData.fecha_desde}
                value={formData.fecha_hasta}
                onChange={(e) => setFormData({ ...formData, fecha_hasta: e.target.value })}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Servicio *</label>
              <select
                required
                value={formData.tiempo_comida}
                onChange={(e) => setFormData({ ...formData, tiempo_comida: e.target.value })}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              >
                {TIEMPO_COMIDA_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Ubicación y Personas */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Ubicación *</label>
              <input
                type="text"
                required
                value={formData.ubicacion}
                onChange={(e) => setFormData({ ...formData, ubicacion: e.target.value })}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
                placeholder="Ej: restaurante_A"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Charolas Programadas</label>
              <input
                type="number"
                min="0"
                value={formData.charolas_planificadas}
                onChange={(e) => {
                  const nuevasCharolas = parseInt(e.target.value) || 0
                  setFormData({ ...formData, charolas_planificadas: nuevasCharolas })
                }}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
                placeholder="Cantidad de porciones por receta"
              />
              <p className="text-xs text-slate-400 mt-1">
                Esta cantidad se aplicará a todas las recetas del menú
              </p>
            </div>
          </div>
          
          {/* Recetas */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <label className="block text-sm font-medium">Recetas del Menú *</label>
              <button
                type="button"
                onClick={agregarReceta}
                disabled={cargandoRecetas || !recetasDisponibles || recetasDisponibles.length === 0}
                className="flex items-center gap-2 px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title={cargandoRecetas ? 'Cargando recetas...' : (!recetasDisponibles || recetasDisponibles.length === 0) ? 'No hay recetas disponibles' : 'Agregar receta al menú'}
              >
                <Plus className="w-4 h-4" />
                Agregar Receta
              </button>
            </div>
            
            {cargandoRecetas ? (
              <div className="text-center py-8 text-slate-400">Cargando recetas...</div>
            ) : errorRecetas ? (
              <div className="text-center py-8 text-red-400 border border-red-500/50 rounded-lg bg-red-500/10">
                <p className="mb-2">Error al cargar recetas</p>
                <p className="text-sm text-slate-400">{errorRecetas.response?.data?.error || errorRecetas.message}</p>
                <button
                  type="button"
                  onClick={() => queryClient.invalidateQueries(['recetas', formData.tiempo_comida])}
                  className="mt-3 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm"
                >
                  Reintentar
                </button>
              </div>
            ) : recetasDisponibles.length === 0 ? (
              <div className="text-center py-8 text-yellow-400 border border-yellow-500/50 rounded-lg bg-yellow-500/10">
                <p>No hay recetas activas disponibles</p>
                <p className="text-sm text-slate-400 mt-2">Crea recetas activas en la sección de Recetas para poder agregarlas al menú</p>
              </div>
            ) : formData.recetas.length === 0 ? (
              <div className="text-center py-8 text-slate-400 border border-slate-700 rounded-lg">
                No hay recetas agregadas. Haz clic en "Agregar Receta" para comenzar.
              </div>
            ) : (
              <div className="space-y-3">
                {formData.recetas.map((recetaProg, index) => {
                  const receta = recetasDisponibles?.find(r => r.id === recetaProg.receta_id)
                  return (
                    <div
                      key={index}
                      className="flex items-center gap-4 p-4 bg-slate-700/50 rounded-lg border border-slate-600"
                    >
                      <div className="flex-1">
                        <select
                          value={recetaProg.receta_id || ''}
                          onChange={(e) => actualizarReceta(index, 'receta_id', parseInt(e.target.value))}
                          className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded focus:outline-none focus:border-purple-500"
                        >
                          <option value="">Selecciona una receta</option>
                          {recetasDisponibles?.map(r => (
                            <option key={r.id} value={r.id}>
                              {r.nombre} {r.calorias_por_porcion && `(${Math.round(r.calorias_por_porcion)} kcal/porción)`}
                            </option>
                          ))}
                        </select>
                      </div>
                      
                      {receta && (
                        <div className="text-xs text-slate-400 min-w-[200px] text-right">
                          <div className="mb-2 pb-2 border-b border-slate-600">
                            <div className="text-slate-500 text-[10px] mb-1">Total ({formData.charolas_planificadas || 0} charolas)</div>
                            <div className="mb-1">
                              <span className="text-slate-500">Calorías: </span>
                              <span className="font-semibold text-purple-300">{Math.round((receta.calorias_por_porcion || 0) * (formData.charolas_planificadas || 0)).toLocaleString()} kcal</span>
                            </div>
                            <div>
                              <span className="text-slate-500">Costo: </span>
                              <span className="font-semibold text-purple-300">${((receta.costo_por_porcion || 0) * (formData.charolas_planificadas || 0)).toFixed(2)}</span>
                            </div>
                          </div>
                          <div>
                            <div className="text-slate-500 text-[10px] mb-1">Por charola (1)</div>
                            <div className="mb-1">
                              <span className="text-slate-500">Calorías: </span>
                              <span className="font-semibold text-green-300">{Math.round(receta.calorias_por_porcion || 0)} kcal</span>
                            </div>
                            <div>
                              <span className="text-slate-500">Costo: </span>
                              <span className="font-semibold text-green-300">${(receta.costo_por_porcion || 0).toFixed(2)}</span>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      <button
                        type="button"
                        onClick={() => eliminarReceta(index)}
                        className="p-2 text-red-400 hover:bg-red-500/20 rounded transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
          
          {/* Resumen del Servicio */}
          {totales.totalRecetas > 0 && (
            <div className="p-4 bg-purple-600/10 border border-purple-500/50 rounded-lg">
              <div className="flex items-center gap-2 mb-4">
                <Calculator className="w-5 h-5 text-purple-400" />
                <h3 className="font-semibold text-purple-300">Resumen del Servicio</h3>
              </div>
              
              {/* Total para todas las charolas */}
              <div className="mb-4 pb-4 border-b border-purple-500/30">
                <div className="text-xs text-purple-300/70 mb-2 font-medium">
                  Total para {formData.charolas_planificadas || 0} charolas programadas
                </div>
                <div className="grid grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-slate-400 text-xs">Total Recetas</div>
                    <div className="text-lg font-semibold">{totales.totalRecetas}</div>
                  </div>
                  <div>
                    <div className="text-slate-400 text-xs">Total Porciones</div>
                    <div className="text-lg font-semibold">{totales.totalPorciones.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-slate-400 text-xs">Calorías Totales</div>
                    <div className="text-lg font-semibold text-purple-300">{totales.caloriasTotales.toLocaleString()} kcal</div>
                  </div>
                  <div>
                    <div className="text-slate-400 text-xs">Costo Total</div>
                    <div className="text-lg font-semibold text-purple-300">${totales.costoTotal.toFixed(2)}</div>
                  </div>
                </div>
              </div>
              
              {/* Por charola individual */}
              <div>
                <div className="text-xs text-purple-300/70 mb-2 font-medium">
                  Por charola individual (1 charola)
                </div>
                <div className="grid grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-slate-400 text-xs">Porciones</div>
                    <div className="text-lg font-semibold">{totales.porcionesPorCharola}</div>
                  </div>
                  <div>
                    <div className="text-slate-400 text-xs">Calorías</div>
                    <div className="text-lg font-semibold text-green-300">{totales.caloriasPorCharola.toLocaleString()} kcal</div>
                  </div>
                  <div>
                    <div className="text-slate-400 text-xs">Costo</div>
                    <div className="text-lg font-semibold text-green-300">${totales.costoPorCharola.toFixed(2)}</div>
                  </div>
                  <div>
                    <div className="text-slate-400 text-xs">Costo por porción</div>
                    <div className="text-lg font-semibold text-slate-300">
                      ${totales.porcionesPorCharola > 0 ? (totales.costoPorCharola / totales.porcionesPorCharola).toFixed(2) : '0.00'}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Botones */}
          <div className="flex justify-end gap-3 pt-4 border-t border-slate-700">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending || formData.recetas.length === 0}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createMutation.isPending || updateMutation.isPending
                ? 'Guardando...'
                : programacion?.id
                ? 'Actualizar'
                : 'Crear Programación'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
