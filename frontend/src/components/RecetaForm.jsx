import { useState, useEffect } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import api, { extractData } from '../config/api'
import toast from 'react-hot-toast'
import { X, Plus, Calculator } from 'lucide-react'

export default function RecetaForm({ receta, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    nombre: receta?.nombre || '',
    descripcion: receta?.descripcion || '',
    tipo: receta?.tipo || 'almuerzo',
    porciones: receta?.porciones || 1,
    tiempo_preparacion: receta?.tiempo_preparacion || null,
    ingredientes: receta?.ingredientes?.map(ing => ({
      item_id: ing.item_id,
      cantidad: ing.cantidad,
      unidad: ing.unidad || ing.item?.unidad || 'kg',
      item: ing.item
    })) || [],
  })

  const queryClient = useQueryClient()

  // Cargar items disponibles
  const { data: itemsResponse, isLoading: loadingItems } = useQuery({
    queryKey: ['items'],
    queryFn: () => api.get('/logistica/items?activo=true&limit=1000').then(res => {
      const items = extractData(res)
      return Array.isArray(items) ? items : []
    }),
  })
  
  const items = Array.isArray(itemsResponse) ? itemsResponse : []

  // Cálculos automáticos
  const [calculos, setCalculos] = useState({
    porcionGramos: 0,
    caloriasTotales: 0,
    costoTotal: 0,
    caloriasPorPorcion: 0,
    costoPorPorcion: 0,
  })

  // Función para convertir a gramos (simplificada para el frontend)
  const convertirAGramos = (cantidad, unidad) => {
    const unidadLower = unidad?.toLowerCase() || ''
    const cantidadNum = parseFloat(cantidad) || 0

    // Conversiones básicas a gramos
    const conversiones = {
      // Peso
      'kg': cantidadNum * 1000,
      'g': cantidadNum,
      'gramo': cantidadNum,
      'gramos': cantidadNum,
      'qq': cantidadNum * 45359.2, // quintal a gramos (1 qq = 100 lb = 45.3592 kg)
      'quintal': cantidadNum * 45359.2,
      'quintales': cantidadNum * 45359.2,
      'lb': cantidadNum * 453.592, // libra a gramos
      'libras': cantidadNum * 453.592,
      'oz': cantidadNum * 28.3495, // onza a gramos
      'onzas': cantidadNum * 28.3495,
      // Volumen (asumiendo densidad ~1 g/ml para agua/líquidos)
      'l': cantidadNum * 1000, // litro a gramos (aproximado)
      'litro': cantidadNum * 1000,
      'litros': cantidadNum * 1000,
      'ml': cantidadNum, // mililitro a gramos (aproximado)
      'mililitro': cantidadNum,
      'mililitros': cantidadNum,
      // Unidades discretas (estimaciones)
      'unidad': cantidadNum * 100, // Asumiendo promedio de 100g por unidad
      'unidades': cantidadNum * 100,
      'caja': cantidadNum * 500, // Asumiendo promedio de 500g por caja
      'cajas': cantidadNum * 500,
      'paquete': cantidadNum * 300, // Asumiendo promedio de 300g por paquete
      'paquetes': cantidadNum * 300,
    }

    return conversiones[unidadLower] || cantidadNum
  }

  // Función para convertir cantidad de una unidad a otra (mismo grupo)
  const convertirUnidad = (cantidad, unidadOrigen, unidadDestino) => {
    // Primero convertir a gramos, luego a unidad destino
    const enGramos = convertirAGramos(cantidad, unidadOrigen)
    
    // Convertir de gramos a unidad destino
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

  // Calcular totales cuando cambian los ingredientes
  useEffect(() => {
    let porcionGramos = 0
    let caloriasTotales = 0
    let costoTotal = 0

    formData.ingredientes.forEach(ing => {
      if (!ing.item) return

      const cantidad = parseFloat(ing.cantidad) || 0
      const unidad = ing.unidad || ing.item.unidad || 'kg'

      // Calcular peso en gramos
      porcionGramos += convertirAGramos(cantidad, unidad)

      // Calcular calorías (convertir cantidad a unidad base del item)
      if (ing.item.calorias_por_unidad) {
        const unidadItem = ing.item.unidad || 'kg'
        // Convertir cantidad de la unidad ingresada a la unidad del item
        const cantidadEnUnidadItem = convertirUnidad(cantidad, unidad, unidadItem)
        caloriasTotales += cantidadEnUnidadItem * (ing.item.calorias_por_unidad || 0)
      }

      // Calcular costo (convertir cantidad a unidad base del item)
      if (ing.item.costo_unitario_actual) {
        const unidadItem = ing.item.unidad || 'kg'
        // Convertir cantidad de la unidad ingresada a la unidad del item
        const cantidadEnUnidadItem = convertirUnidad(cantidad, unidad, unidadItem)
        costoTotal += cantidadEnUnidadItem * (ing.item.costo_unitario_actual || 0)
      }
    })

    const porciones = formData.porciones || 1

    setCalculos({
      porcionGramos: porcionGramos,
      caloriasTotales: caloriasTotales,
      costoTotal: costoTotal,
      caloriasPorPorcion: porciones > 0 ? caloriasTotales / porciones : 0,
      costoPorPorcion: porciones > 0 ? costoTotal / porciones : 0,
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
            <option value="merienda">Merienda</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Descripción</label>
        <textarea
          value={formData.descripcion}
          onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          rows="3"
          placeholder="Descripción de la receta..."
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
          <button
            type="button"
            onClick={agregarIngrediente}
            className="flex items-center gap-2 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm"
          >
            <Plus size={16} />
            Agregar Ingrediente
          </button>
        </div>

        {formData.ingredientes.length === 0 ? (
          <div className="p-8 text-center border border-slate-600 rounded-lg bg-slate-800">
            <p className="text-slate-400 mb-2">No hay ingredientes agregados</p>
            <p className="text-xs text-slate-500">Haz clic en "Agregar Ingrediente" para comenzar</p>
          </div>
        ) : (
          <div className="space-y-3">
            {formData.ingredientes.map((ingrediente, index) => {
              const item = ingrediente.item || items?.find(i => i.id === ingrediente.item_id)
              return (
                <div key={index} className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                  <div className="grid grid-cols-12 gap-3 items-end">
                    <div className="col-span-5">
                      <label className="block text-xs text-slate-400 mb-1">Item</label>
                      <select
                        required
                        value={ingrediente.item_id || ''}
                        onChange={(e) => actualizarIngrediente(index, 'item_id', e.target.value)}
                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500 text-sm"
                      >
                        <option value="">Seleccionar item...</option>
                        {items?.map(item => (
                          <option key={item.id} value={item.id}>
                            {item.nombre} ({item.codigo})
                          </option>
                        ))}
                      </select>
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

                  {item && (
                    <div className="mt-2 text-xs text-slate-400">
                      {item.calorias_por_unidad && (
                        <span className="mr-3">
                          Calorías: {item.calorias_por_unidad} kcal/{item.unidad}
                        </span>
                      )}
                      {item.costo_unitario_actual && (
                        <span>
                          Costo: ${item.costo_unitario_actual.toFixed(2)}/{item.unidad}
                        </span>
                      )}
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
          <div className="flex items-center gap-2 mb-3">
            <Calculator className="text-purple-400" size={20} />
            <h3 className="text-sm font-semibold text-purple-300">Resumen de la Receta</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
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
