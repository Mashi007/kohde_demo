import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api, { extractData } from '../config/api'
import { Package, Plus, X, Save } from 'lucide-react'
import toast from 'react-hot-toast'

export default function PedidoInternoForm({ pedido, onClose, onSuccess }) {
  const queryClient = useQueryClient()
  const [entregadoPorId, setEntregadoPorId] = useState('')
  const [entregadoPorNombre, setEntregadoPorNombre] = useState('')
  const [recibidoPorId, setRecibidoPorId] = useState('')
  const [recibidoPorNombre, setRecibidoPorNombre] = useState('')
  const [observaciones, setObservaciones] = useState('')
  const [items, setItems] = useState([])

  // Cargar items disponibles
  const { data: itemsDisponibles } = useQuery({
    queryKey: ['items'],
    queryFn: () => api.get('/logistica/items?limit=1000').then(res => {
      const items = extractData(res)
      return Array.isArray(items) ? items : []
    }),
  })

  // Cargar inventario para verificar stock
  const { data: inventarioResponse } = useQuery({
    queryKey: ['inventario'],
    queryFn: () => api.get('/logistica/inventario/completo').then(extractData),
  })

  // Asegurar que inventario sea un array
  const inventario = Array.isArray(inventarioResponse) ? inventarioResponse : []

  const crearPedidoMutation = useMutation({
    mutationFn: (datos) => api.post('/logistica/pedidos-internos', datos),
    onSuccess: () => {
      toast.success('Pedido interno creado correctamente')
      onSuccess()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al crear pedido')
    },
  })

  const agregarItem = () => {
    setItems([...items, { item_id: '', cantidad: '', unidad: '' }])
  }

  const removerItem = (index) => {
    setItems(items.filter((_, i) => i !== index))
  }

  const actualizarItem = (index, campo, valor) => {
    const nuevosItems = [...items]
    nuevosItems[index] = { ...nuevosItems[index], [campo]: valor }
    
    // Si se selecciona un item, obtener su unidad por defecto
    if (campo === 'item_id' && valor) {
      const itemSeleccionado = itemsDisponibles?.find(i => i.id === parseInt(valor))
      if (itemSeleccionado) {
        nuevosItems[index].unidad = itemSeleccionado.unidad || ''
      }
    }
    
    setItems(nuevosItems)
  }

  const obtenerStockDisponible = (itemId) => {
    if (!inventario || !itemId) return null
    const inv = inventario.find(inv => inv.item_id === parseInt(itemId))
    return inv ? {
      cantidad: inv.cantidad_actual,
      unidad: inv.unidad
    } : null
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    if (!entregadoPorId || !entregadoPorNombre) {
      toast.error('Debe especificar quien entrega (responsable de bodega)')
      return
    }

    if (items.length === 0) {
      toast.error('Debe agregar al menos un item al pedido')
      return
    }

    // Validar que todos los items tengan item_id y cantidad
    const itemsInvalidos = items.filter(item => !item.item_id || !item.cantidad)
    if (itemsInvalidos.length > 0) {
      toast.error('Todos los items deben tener un producto y una cantidad')
      return
    }

    // Validar stock disponible
    for (const item of items) {
      const stock = obtenerStockDisponible(item.item_id)
      if (stock && parseFloat(item.cantidad) > parseFloat(stock.cantidad)) {
        const itemNombre = itemsDisponibles?.find(i => i.id === parseInt(item.item_id))?.nombre || 'Item'
        toast.error(`Stock insuficiente para ${itemNombre}. Disponible: ${stock.cantidad} ${stock.unidad}`)
        return
      }
    }

    const datos = {
      entregado_por_id: parseInt(entregadoPorId),
      entregado_por_nombre: entregadoPorNombre,
      recibido_por_id: recibidoPorId ? parseInt(recibidoPorId) : null,
      recibido_por_nombre: recibidoPorNombre || null,
      observaciones: observaciones || null,
      items: items.map(item => ({
        item_id: parseInt(item.item_id),
        cantidad: parseFloat(item.cantidad),
        unidad: item.unidad || null
      }))
    }

    crearPedidoMutation.mutate(datos)
  }

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
      <div className="p-6 border-b border-slate-700">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Package size={24} />
          {pedido ? 'Editar Pedido Interno' : 'Nuevo Pedido Interno'}
        </h2>
        <p className="text-sm text-slate-400 mt-1">Bodega → Cocina</p>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* Información de entrega */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              ID Responsable Bodega (quien entrega) *
            </label>
            <input
              type="number"
              value={entregadoPorId}
              onChange={(e) => setEntregadoPorId(e.target.value)}
              required
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Ej: 1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Nombre Responsable Bodega *
            </label>
            <input
              type="text"
              value={entregadoPorNombre}
              onChange={(e) => setEntregadoPorNombre(e.target.value)}
              required
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Ej: Juan Pérez"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              ID Responsable Cocina (quien recibe)
            </label>
            <input
              type="number"
              value={recibidoPorId}
              onChange={(e) => setRecibidoPorId(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Opcional"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Nombre Responsable Cocina
            </label>
            <input
              type="text"
              value={recibidoPorNombre}
              onChange={(e) => setRecibidoPorNombre(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Opcional"
            />
          </div>
        </div>

        {/* Items */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <label className="block text-sm font-medium">Items del Pedido *</label>
            <button
              type="button"
              onClick={agregarItem}
              className="bg-purple-600 hover:bg-purple-700 px-3 py-1.5 rounded-lg flex items-center gap-2 text-sm"
            >
              <Plus size={16} />
              Agregar Item
            </button>
          </div>

          <div className="space-y-3">
            {items.map((item, index) => {
              const stock = obtenerStockDisponible(item.item_id)
              return (
                <div key={index} className="bg-slate-700/50 p-4 rounded-lg border border-slate-600">
                  <div className="grid grid-cols-12 gap-3 items-end">
                    <div className="col-span-5">
                      <label className="block text-xs font-medium mb-1 text-slate-400">Item</label>
                      <select
                        value={item.item_id}
                        onChange={(e) => actualizarItem(index, 'item_id', e.target.value)}
                        required
                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500 text-sm"
                      >
                        <option value="">Seleccionar item...</option>
                        {itemsDisponibles?.map(i => (
                          <option key={i.id} value={i.id}>
                            {i.nombre} ({i.codigo})
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="col-span-3">
                      <label className="block text-xs font-medium mb-1 text-slate-400">Cantidad</label>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        value={item.cantidad}
                        onChange={(e) => actualizarItem(index, 'cantidad', e.target.value)}
                        required
                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500 text-sm"
                        placeholder="0.00"
                      />
                    </div>
                    <div className="col-span-3">
                      <label className="block text-xs font-medium mb-1 text-slate-400">Unidad</label>
                      <input
                        type="text"
                        value={item.unidad}
                        onChange={(e) => actualizarItem(index, 'unidad', e.target.value)}
                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500 text-sm"
                        placeholder="kg, g, l..."
                      />
                    </div>
                    <div className="col-span-1">
                      <button
                        type="button"
                        onClick={() => removerItem(index)}
                        className="w-full h-10 bg-red-600 hover:bg-red-700 rounded-lg flex items-center justify-center"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  </div>
                  {stock && (
                    <div className="mt-2 text-xs text-slate-400">
                      Stock disponible: <span className="text-green-400">{stock.cantidad} {stock.unidad}</span>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Observaciones */}
        <div>
          <label className="block text-sm font-medium mb-2">Observaciones</label>
          <textarea
            value={observaciones}
            onChange={(e) => setObservaciones(e.target.value)}
            rows={3}
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
            placeholder="Notas adicionales sobre el pedido..."
          />
        </div>

        {/* Botones */}
        <div className="flex justify-end gap-3 pt-4 border-t border-slate-700">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={crearPedidoMutation.isPending}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2 disabled:opacity-50"
          >
            <Save size={18} />
            {crearPedidoMutation.isPending ? 'Guardando...' : 'Crear Pedido'}
          </button>
        </div>
      </form>
    </div>
  )
}
