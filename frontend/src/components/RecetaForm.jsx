import { useState, useEffect } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import api, { extractData } from '../config/api'
import toast from 'react-hot-toast'
import { X, Plus, Calculator } from 'lucide-react'

export default function RecetaForm({ receta, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    nombre: receta?.nombre || '',
    descripcion: receta?.descripcion || '', // Mantener descripcion para el backend, pero mostrar como "Instrucciones"
    tipo: receta?.tipo || 'almuerzo',
    porciones: receta?.porciones || 1, // Por defecto 1 porción
    tiempo_preparacion: receta?.tiempo_preparacion || null,
    ingredientes: receta?.ingredientes?.map(ing => ({
      item_id: ing.item_id,
      cantidad: ing.cantidad,
      unidad: ing.unidad || ing.item?.unidad || 'kg',
      item: ing.item
    })) || [],
  })

  const queryClient = useQueryClient()

  // Cargar items disponibles (solo activos)
  const { data: itemsResponse, isLoading: loadingItems, error: itemsError } = useQuery({
    queryKey: ['items', 'activos'],
    queryFn: async () => {
      try {
        const res = await api.get('/logistica/items', { 
          params: { 
            activo: true, 
            limit: 1000 
          } 
        })
        const items = extractData(res)
        return Array.isArray(items) ? items : []
      } catch (error) {
        console.error('Error cargando items:', error)
        toast.error('Error al cargar items disponibles')
        return []
      }
    },
    staleTime: 30000, // Cache por 30 segundos
    refetchOnWindowFocus: false,
  })
  
  const items = Array.isArray(itemsResponse) ? itemsResponse : []
  
  // Mostrar estado de carga si es necesario
  useEffect(() => {
    if (itemsError) {
      console.error('Error cargando items para receta:', itemsError)
    }
  }, [itemsError])

  // Función para convertir a gramos
  const convertirAGramos = (cantidad, unidad) => {
    const unidadLower = unidad?.toLowerCase() || ''
    const cantidadNum = parseFloat(cantidad) || 0

    const conversiones = {
      'kg': cantidadNum * 1000,
      'g': cantidadNum,
      'gramo': cantidadNum,
      'gramos': cantidadNum,
      'qq': cantidadNum * 45359.2,
      'quintal': cantidadNum * 45359.2,
      'quintales': cantidadNum * 45359.2,
      'lb': cantidadNum * 453.592,
      'libras': cantidadNum * 453.592,
      'oz': cantidadNum * 28.3495,
      'onzas': cantidadNum * 28.3495,
      'l': cantidadNum * 1000,
      'litro': cantidadNum * 1000,
      'litros': cantidadNum * 1000,
      'ml': cantidadNum,
      'mililitro': cantidadNum,
      'mililitros': cantidadNum,
      'unidad': cantidadNum * 100,
      'unidades': cantidadNum * 100,
      'caja': cantidadNum * 500,
      'cajas': cantidadNum * 500,
      'paquete': cantidadNum * 300,
      'paquetes': cantidadNum * 300,
    }

    return conversiones[unidadLower] || cantidadNum
  }

  // Función para convertir cantidad de una unidad a otra
  const convertirUnidad = (cantidad, unidadOrigen, unidadDestino) => {
    const enGramos = convertirAGramos(cantidad, unidadOrigen)
    
    const unidadDestinoLower = unidadDestino?.toLowerCase() || ''
    const conversionesDesdeGramos = {
      'kg': enGramos / 1000,
      'g': enGramos,
      'gramo': enGramos,
      'gramos': enGramos,
      'qq': enGramos / 45359.2,
      'quintal': enGramos / 45359.2,
      'quintales': enGramos / 45359.2,
      'lb': enGramos / 453.592,
      'libras': enGramos / 453.592,
      'oz': enGramos / 28.3495,
      'onzas': enGramos / 28.3495,
      'l': enGramos / 1000,
      'litro': enGramos / 1000,
      'litros': enGramos / 1000,
      'ml': enGramos,
      'mililitro': enGramos,
      'mililitros': enGramos,
      'unidad': enGramos / 100,
      'unidades': enGramos / 100,
      'caja': enGramos / 500,
      'cajas': enGramos / 500,
      'paquete': enGramos / 300,
      'paquetes': enGramos / 300,
    }

    return conversionesDesdeGramos[unidadDestinoLower] || cantidad
  }

  // Calcular cálculos por ingrediente y totales
  const calcularIngrediente = (ing) => {
    if (!ing.item || !ing.cantidad) {
      return {
        pesoGramos: 0,
        calorias: 0,
        costo: 0,
      }
    }

    const cantidad = parseFloat(ing.cantidad) || 0
    const unidad = ing.unidad || ing.item.unidad || 'kg'
    const unidadItem = ing.item.unidad || 'kg'

    // Calcular peso en gramos
    const pesoGramos = convertirAGramos(cantidad, unidad)

    // Calcular calorías (convertir cantidad a unidad base del item)
    let calorias = 0
    if (ing.item.calorias_por_unidad) {
      const cantidadEnUnidadItem = convertirUnidad(cantidad, unidad, unidadItem)
      calorias = cantidadEnUnidadItem * (ing.item.calorias_por_unidad || 0)
    }

    // Calcular costo (convertir cantidad a unidad base del item)
    let costo = 0
    if (ing.item.costo_unitario_actual || ing.item.costo_unitario_promedio) {
      const cantidadEnUnidadItem = convertirUnidad(cantidad, unidad, unidadItem)
      const costoUnitario = ing.item.costo_unitario_actual || ing.item.costo_unitario_promedio || 0
      costo = cantidadEnUnidadItem * costoUnitario
    }

    return {
      pesoGramos,
      calorias,
      costo,
    }
  }

  // Calcular totales cuando cambian los ingredientes
  const [calculos, setCalculos] = useState({
    porcionGramos: 0,
    caloriasTotales: 0,
    costoTotal: 0,
    caloriasPorPorcion: 0,
    costoPorPorcion: 0,
    ingredientesCalculados: [],
  })

  useEffect(() => {
    let porcionGramos = 0
    let caloriasTotales = 0
    let costoTotal = 0
    const ingredientesCalculados = []

    formData.ingredientes.forEach(ing => {
      const calculo = calcularIngrediente(ing)
      porcionGramos += calculo.pesoGramos
      caloriasTotales += calculo.calorias
      costoTotal += calculo.costo

      ingredientesCalculados.push({
        ...ing,
        ...calculo,
      })
    })

    const porciones = formData.porciones || 1

    setCalculos({
      porcionGramos,
      caloriasTotales,
      costoTotal,
      caloriasPorPorcion: porciones > 0 ? caloriasTotales / porciones : 0,
      costoPorPorcion: porciones > 0 ? costoTotal / porciones : 0,
      ingredientesCalculados,
    })
  }, [formData.ingredientes, formData.porciones])

  const createMutation = useMutation({
    mutationFn: (data) => {
      if (receta?.id) {
        return api.put(`/planificacion/recetas/${receta.id}`, data)
      }
      return api.post('/planificacion/recetas', data)
    },
    onSuccess: () => {
      toast.success(receta?.id ? 'Receta actualizada correctamente' : 'Receta creada correctamente')
      queryClient.invalidateQueries(['recetas'])
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al guardar receta')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    
    const datosEnvio = {
      ...formData,
      ingredientes: formData.ingredientes.map(ing => ({
        item_id: ing.item_id,
        cantidad: parseFloat(ing.cantidad) || 0,
        unidad: ing.unidad || ing.item?.unidad || 'kg',
      })),
    }

    createMutation.mutate(datosEnvio)
  }

  const agregarIngrediente = () => {
    if (items.length === 0 && !loadingItems) {
      toast.error('No hay items disponibles. Crea items primero en el módulo de Logística.')
      return
    }
    
    setFormData(prev => ({
      ...prev,
      ingredientes: [...prev.ingredientes, {
        item_id: null,
        cantidad: 0,
        unidad: 'kg',
        item: null,
      }]
    }))
  }

  const eliminarIngrediente = (index) => {
    setFormData(prev => ({
      ...prev,
      ingredientes: prev.ingredientes.filter((_, i) => i !== index)
    }))
  }

  const actualizarIngrediente = (index, campo, valor) => {
    setFormData(prev => {
      const nuevosIngredientes = [...prev.ingredientes]
      
      if (campo === 'item_id') {
        const item = items?.find(i => i.id === parseInt(valor))
        nuevosIngredientes[index] = {
          ...nuevosIngredientes[index],
          item_id: item?.id || null,
          item: item || null,
          unidad: item?.unidad || nuevosIngredientes[index].unidad || 'kg',
        }
      } else {
        nuevosIngredientes[index] = {
          ...nuevosIngredientes[index],
          [campo]: valor,
        }
      }
      
      return {
        ...prev,
        ingredientes: nuevosIngredientes,
      }
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Información básica */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Nombre de la Receta *</label>
          <input
            type="text"
            required
            value={formData.nombre}
            onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
            placeholder="Ej: Arroz con Pollo"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Tipo *</label>
          <select
            required
            value={formData.tipo}
            onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          >
            <option value="desayuno">Desayuno</option>
            <option value="almuerzo">Almuerzo</option>
            <option value="cena">Cena</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Instrucciones para Cocina</label>
        <textarea
          value={formData.descripcion}
          onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          rows="4"
          placeholder="Instrucciones paso a paso para preparar la receta..."
        />
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Porciones *</label>
          <input
            type="number"
            required
            min="1"
            value={formData.porciones}
            onChange={(e) => setFormData({ ...formData, porciones: parseInt(e.target.value) || 1 })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Tiempo de Preparación (min)</label>
          <input
            type="number"
            min="0"
            value={formData.tiempo_preparacion || ''}
            onChange={(e) => setFormData({ ...formData, tiempo_preparacion: e.target.value ? parseInt(e.target.value) : null })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
            placeholder="Ej: 30"
          />
        </div>
      </div>

      {/* Ingredientes */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <label className="block text-sm font-medium">Ingredientes *</label>
          <div className="flex items-center gap-2">
            {loadingItems && (
              <span className="text-xs text-slate-400">Cargando items...</span>
            )}
            {!loadingItems && items.length > 0 && (
              <span className="text-xs text-slate-400">
                {items.length} item{items.length !== 1 ? 's' : ''} disponible{items.length !== 1 ? 's' : ''}
              </span>
            )}
            <button
              type="button"
              onClick={agregarIngrediente}
              disabled={loadingItems || items.length === 0}
              className="flex items-center gap-2 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Plus size={16} />
              Agregar Ingrediente
            </button>
          </div>
        </div>
        
        {!loadingItems && items.length === 0 && (
          <div className="mb-4 p-4 bg-yellow-600/20 border border-yellow-500/50 rounded-lg">
            <p className="text-sm text-yellow-400">
              ⚠️ No hay items activos disponibles. 
            </p>
            <p className="text-xs text-yellow-300 mt-1">
              Ve al módulo de <strong>Logística → Items</strong> para crear items antes de agregar ingredientes a la receta.
            </p>
          </div>
        )}

        {formData.ingredientes.length === 0 ? (
          <div className="p-8 text-center border border-slate-600 rounded-lg bg-slate-800">
            <p className="text-slate-400 mb-2">No hay ingredientes agregados</p>
            <p className="text-xs text-slate-500">Haz clic en "Agregar Ingrediente" para comenzar</p>
          </div>
        ) : (
          <div className="space-y-3">
            {formData.ingredientes.map((ingrediente, index) => {
              const item = ingrediente.item || items?.find(i => i.id === ingrediente.item_id)
              const calculoIngrediente = calcularIngrediente(ingrediente)
              
              return (
                <div key={index} className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                  <div className="grid grid-cols-12 gap-3 items-end">
                    <div className="col-span-5">
                      <label className="block text-xs text-slate-400 mb-1">Item</label>
                      {loadingItems ? (
                        <div className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm text-slate-400">
                          Cargando items...
                        </div>
                      ) : (
                        <select
                          required
                          value={ingrediente.item_id || ''}
                          onChange={(e) => actualizarIngrediente(index, 'item_id', e.target.value)}
                          className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500 text-sm"
                          disabled={loadingItems || items.length === 0}
                        >
                          <option value="">
                            {items.length === 0 ? 'No hay items disponibles' : 'Seleccionar item...'}
                          </option>
                          {items.map(item => (
                            <option key={item.id} value={item.id}>
                              {item.nombre} ({item.codigo})
                            </option>
                          ))}
                        </select>
                      )}
                    </div>

                    <div className="col-span-3">
                      <label className="block text-xs text-slate-400 mb-1">Cantidad</label>
                      <input
                        type="number"
                        required
                        step="0.01"
                        min="0"
                        value={ingrediente.cantidad || ''}
                        onChange={(e) => actualizarIngrediente(index, 'cantidad', e.target.value)}
                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500 text-sm"
                        placeholder="0"
                      />
                    </div>

                    <div className="col-span-3">
                      <label className="block text-xs text-slate-400 mb-1">Unidad</label>
                      <select
                        required
                        value={ingrediente.unidad || 'kg'}
                        onChange={(e) => actualizarIngrediente(index, 'unidad', e.target.value)}
                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500 text-sm"
                      >
                        <option value="kg">kg</option>
                        <option value="g">g</option>
                        <option value="qq">qq</option>
                        <option value="l">l</option>
                        <option value="ml">ml</option>
                        <option value="unidad">unidad</option>
                        <option value="caja">caja</option>
                        <option value="paquete">paquete</option>
                      </select>
                    </div>

                    <div className="col-span-1">
                      <button
                        type="button"
                        onClick={() => eliminarIngrediente(index)}
                        className="w-full p-2 bg-red-600/20 hover:bg-red-600/30 border border-red-600/50 rounded-lg text-red-400"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  </div>

                  {/* Información del item y cálculos */}
                  {item && (
                    <div className="mt-3 pt-3 border-t border-slate-700">
                      <div className="grid grid-cols-2 gap-4 text-xs">
                        <div>
                          <span className="text-slate-400">Información del Item:</span>
                          <div className="mt-1 space-y-1">
                            {item.calorias_por_unidad && (
                              <p className="text-slate-300">
                                Calorías: <span className="text-purple-300 font-medium">{item.calorias_por_unidad.toFixed(1)}</span> kcal/{item.unidad}
                              </p>
                            )}
                            {(item.costo_unitario_actual || item.costo_unitario_promedio) && (
                              <p className="text-slate-300">
                                Costo: <span className="text-green-300 font-medium">${((item.costo_unitario_actual || item.costo_unitario_promedio) || 0).toFixed(2)}</span>/{item.unidad}
                              </p>
                            )}
                          </div>
                        </div>
                        <div>
                          <span className="text-slate-400">Cálculos para esta cantidad:</span>
                          <div className="mt-1 space-y-1">
                            <p className="text-slate-300">
                              Peso: <span className="text-blue-300 font-medium">{calculoIngrediente.pesoGramos.toFixed(0)}</span> g
                            </p>
                            {calculoIngrediente.calorias > 0 && (
                              <p className="text-slate-300">
                                Calorías: <span className="text-purple-300 font-medium">{calculoIngrediente.calorias.toFixed(1)}</span> kcal
                              </p>
                            )}
                            {calculoIngrediente.costo > 0 && (
                              <p className="text-slate-300">
                                Costo: <span className="text-green-300 font-medium">${calculoIngrediente.costo.toFixed(2)}</span>
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Resumen de cálculos */}
      {formData.ingredientes.length > 0 && (
        <div className="bg-purple-600/20 border border-purple-500/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-4">
            <Calculator className="text-purple-400" size={20} />
            <h3 className="text-sm font-semibold text-purple-300">Resumen de la Receta</h3>
          </div>
          
          {/* Totales generales */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm mb-4 pb-4 border-b border-purple-500/30">
            <div>
              <p className="text-slate-400 text-xs">Peso Total</p>
              <p className="text-white font-bold text-lg">{calculos.porcionGramos.toFixed(0)} g</p>
            </div>
            <div>
              <p className="text-slate-400 text-xs">Calorías Totales</p>
              <p className="text-white font-bold text-lg">{calculos.caloriasTotales.toFixed(0)} kcal</p>
            </div>
            <div>
              <p className="text-slate-400 text-xs">Costo Total</p>
              <p className="text-white font-bold text-lg">${calculos.costoTotal.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-slate-400 text-xs">Calorías/Porción</p>
              <p className="text-purple-300 font-bold text-lg">{calculos.caloriasPorPorcion.toFixed(0)} kcal</p>
            </div>
            <div>
              <p className="text-slate-400 text-xs">Costo/Porción</p>
              <p className="text-purple-300 font-bold text-lg">${calculos.costoPorPorcion.toFixed(2)}</p>
            </div>
          </div>

          {/* Desglose por ingrediente */}
          <div>
            <h4 className="text-xs font-semibold text-purple-300 mb-2">Desglose por Ingrediente:</h4>
            <div className="space-y-2">
              {calculos.ingredientesCalculados.map((ing, index) => {
                const item = ing.item || items?.find(i => i.id === ing.item_id)
                if (!item) return null
                
                return (
                  <div key={index} className="bg-slate-800/50 p-2 rounded text-xs">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-300 font-medium">{item.nombre}</span>
                      <div className="flex gap-4 text-slate-400">
                        <span>{ing.cantidad || 0} {ing.unidad || 'kg'}</span>
                        {ing.calorias > 0 && (
                          <span className="text-purple-300">{ing.calorias.toFixed(1)} kcal</span>
                        )}
                        {ing.costo > 0 && (
                          <span className="text-green-300">${ing.costo.toFixed(2)}</span>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* Botones */}
      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={createMutation.isPending || formData.ingredientes.length === 0}
          className="flex-1 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {createMutation.isPending ? 'Guardando...' : (receta?.id ? 'Actualizar Receta' : 'Crear Receta')}
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
