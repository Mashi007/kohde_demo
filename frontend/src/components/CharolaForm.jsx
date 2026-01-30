import { useState } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import api, { extractData } from '../config/api'
import toast from 'react-hot-toast'
import { Plus, Trash2 } from 'lucide-react'
import { TIEMPO_COMIDA_VALUES, TIEMPO_COMIDA_OPTIONS, TIEMPO_COMIDA_DEFAULT } from '../constants/tiempoComida'

export default function CharolaForm({ charola, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    numero_charola: charola?.numero_charola || '',
    fecha_servicio: charola?.fecha_servicio ? new Date(charola.fecha_servicio).toISOString().slice(0, 16) : new Date().toISOString().slice(0, 16),
    ubicacion: charola?.ubicacion || '',
    tiempo_comida: charola?.tiempo_comida || TIEMPO_COMIDA_DEFAULT,
    personas_servidas: charola?.personas_servidas || 0,
    observaciones: charola?.observaciones || '',
    items: charola?.items || []
  })

  const queryClient = useQueryClient()

  const { data: itemsResponse } = useQuery({
    queryKey: ['items'],
    queryFn: () => api.get('/logistica/items').then(res => {
      const items = extractData(res)
      return Array.isArray(items) ? items : []
    }),
  })
  
  const items = Array.isArray(itemsResponse) ? itemsResponse : []

  const { data: recetasResponse } = useQuery({
    queryKey: ['recetas'],
    queryFn: () => api.get('/planificacion/recetas').then(extractData),
  })
  
  const recetas = Array.isArray(recetasResponse) ? recetasResponse : []

  const createMutation = useMutation({
    mutationFn: (data) => api.post('/reportes/charolas', data),
    onSuccess: () => {
      toast.success('Charola registrada correctamente')
      queryClient.invalidateQueries(['charolas'])
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al registrar charola')
    },
  })

  const agregarItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, {
        item_id: null,
        receta_id: null,
        nombre_item: '',
        cantidad: 0,
        precio_unitario: 0,
        costo_unitario: 0,
        subtotal: 0,
        costo_subtotal: 0
      }]
    })
  }

  const eliminarItem = (index) => {
    setFormData({
      ...formData,
      items: formData.items.filter((_, i) => i !== index)
    })
  }

  const actualizarItem = (index, campo, valor) => {
    const nuevosItems = [...formData.items]
    nuevosItems[index][campo] = valor

    // Si se selecciona un item o receta, obtener sus datos
    if (campo === 'item_id' && valor) {
      const item = items?.find(i => i.id === parseInt(valor))
      if (item) {
        nuevosItems[index].nombre_item = item.nombre
        nuevosItems[index].costo_unitario = item.costo_unitario_actual || 0
      }
    } else if (campo === 'receta_id' && valor) {
      const receta = recetas?.find(r => r.id === parseInt(valor))
      if (receta) {
        nuevosItems[index].nombre_item = receta.nombre
        nuevosItems[index].costo_unitario = receta.costo_por_porcion || 0
      }
    }

    // Calcular subtotales
    if (campo === 'cantidad' || campo === 'precio_unitario' || campo === 'costo_unitario') {
      const cantidad = parseFloat(nuevosItems[index].cantidad) || 0
      const precio = parseFloat(nuevosItems[index].precio_unitario) || 0
      const costo = parseFloat(nuevosItems[index].costo_unitario) || 0
      nuevosItems[index].subtotal = cantidad * precio
      nuevosItems[index].costo_subtotal = cantidad * costo
    }

    setFormData({ ...formData, items: nuevosItems })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Validar que haya al menos un item
    if (formData.items.length === 0) {
      toast.error('Debe agregar al menos un item')
      return
    }

    // Validar items completos
    const itemsIncompletos = formData.items.some(item => 
      !item.item_id && !item.receta_id || !item.nombre_item || item.cantidad <= 0
    )
    
    if (itemsIncompletos) {
      toast.error('Complete todos los items antes de guardar')
      return
    }

    createMutation.mutate(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Número de Charola</label>
          <input
            type="text"
            required
            value={formData.numero_charola}
            onChange={(e) => setFormData({ ...formData, numero_charola: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Fecha de Servicio</label>
          <input
            type="datetime-local"
            required
            value={formData.fecha_servicio}
            onChange={(e) => setFormData({ ...formData, fecha_servicio: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Ubicación *</label>
          <input
            type="text"
            required
            value={formData.ubicacion}
            onChange={(e) => setFormData({ ...formData, ubicacion: e.target.value })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Tiempo de Comida *</label>
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
        <div>
          <label className="block text-sm font-medium mb-2">Personas Servidas</label>
          <input
            type="number"
            min="0"
            value={formData.personas_servidas}
            onChange={(e) => setFormData({ ...formData, personas_servidas: parseInt(e.target.value) || 0 })}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Observaciones</label>
        <textarea
          value={formData.observaciones}
          onChange={(e) => setFormData({ ...formData, observaciones: e.target.value })}
          rows={3}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        />
      </div>

      {/* Items */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="block text-sm font-medium">Items de la Charola</label>
          <button
            type="button"
            onClick={agregarItem}
            className="text-purple-400 hover:text-purple-300 flex items-center gap-1 text-sm"
          >
            <Plus size={16} />
            Agregar Item
          </button>
        </div>
        
        <div className="space-y-3">
          {formData.items.map((item, index) => (
            <div key={index} className="bg-slate-700 p-4 rounded-lg grid grid-cols-12 gap-2">
              <div className="col-span-4">
                <select
                  value={item.item_id || item.receta_id || ''}
                  onChange={(e) => {
                    const valor = e.target.value
                    if (valor.startsWith('item-')) {
                      actualizarItem(index, 'item_id', valor.replace('item-', ''))
                      actualizarItem(index, 'receta_id', null)
                    } else if (valor.startsWith('receta-')) {
                      actualizarItem(index, 'receta_id', valor.replace('receta-', ''))
                      actualizarItem(index, 'item_id', null)
                    }
                  }}
                  className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-sm"
                >
                  <option value="">Seleccionar...</option>
                  <optgroup label="Items">
                    {items?.map(i => (
                      <option key={`item-${i.id}`} value={`item-${i.id}`}>{i.nombre}</option>
                    ))}
                  </optgroup>
                  <optgroup label="Recetas">
                    {recetas?.map(r => (
                      <option key={`receta-${r.id}`} value={`receta-${r.id}`}>{r.nombre}</option>
                    ))}
                  </optgroup>
                </select>
              </div>
              <div className="col-span-2">
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="Cantidad"
                  value={item.cantidad}
                  onChange={(e) => actualizarItem(index, 'cantidad', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-sm"
                />
              </div>
              <div className="col-span-2">
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="Precio Unit."
                  value={item.precio_unitario}
                  onChange={(e) => actualizarItem(index, 'precio_unitario', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-sm"
                />
              </div>
              <div className="col-span-2">
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="Costo Unit."
                  value={item.costo_unitario}
                  onChange={(e) => actualizarItem(index, 'costo_unitario', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-sm"
                />
              </div>
              <div className="col-span-1 text-sm text-slate-300">
                ${parseFloat(item.subtotal || 0).toFixed(2)}
              </div>
              <div className="col-span-1">
                <button
                  type="button"
                  onClick={() => eliminarItem(index)}
                  className="text-red-400 hover:text-red-300"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={createMutation.isPending}
          className="flex-1 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {createMutation.isPending ? 'Guardando...' : 'Registrar Charola'}
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
