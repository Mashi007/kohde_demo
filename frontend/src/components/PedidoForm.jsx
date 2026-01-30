import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api, { extractData } from '../config/api'
import { ClipboardList, Plus, X, Save, ShoppingCart } from 'lucide-react'
import toast from 'react-hot-toast'

export default function PedidoForm({ pedido, onClose, onSuccess }) {
  const queryClient = useQueryClient()
  const [proveedorId, setProveedorId] = useState(pedido?.proveedor_id || '')
  const [fechaEntregaEsperada, setFechaEntregaEsperada] = useState('')
  const [observaciones, setObservaciones] = useState(pedido?.observaciones || '')
  const [items, setItems] = useState([])

  // Cargar proveedores disponibles
  const { data: proveedoresResponse } = useQuery({
    queryKey: ['proveedores'],
    queryFn: () => api.get('/logistica/proveedores?activo=true').then(extractData),
  })

  const proveedores = Array.isArray(proveedoresResponse) ? proveedoresResponse : []

  // Cargar items disponibles
  const { data: itemsDisponibles } = useQuery({
    queryKey: ['items'],
    queryFn: () => api.get('/logistica/items?activo=true&limit=1000').then(res => {
      const items = extractData(res)
      return Array.isArray(items) ? items : []
    }),
  })

  const crearPedidoMutation = useMutation({
    mutationFn: (datos) => api.post('/logistica/pedidos', datos),
    onSuccess: () => {
      toast.success('Pedido creado correctamente')
      queryClient.invalidateQueries(['pedidos'])
      if (onSuccess) onSuccess()
      if (onClose) onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al crear pedido')
    },
  })

  const agregarItem = () => {
    setItems([...items, { item_id: '', cantidad: '', precio_unitario: '' }])
  }

  const removerItem = (index) => {
    setItems(items.filter((_, i) => i !== index))
  }

  const actualizarItem = (index, campo, valor) => {
    const nuevosItems = [...items]
    nuevosItems[index] = { ...nuevosItems[index], [campo]: valor }
    
    // Si se selecciona un item, obtener su precio unitario por defecto si no está establecido
    if (campo === 'item_id' && valor && !nuevosItems[index].precio_unitario) {
      const itemSeleccionado = itemsDisponibles?.find(i => i.id === parseInt(valor))
      if (itemSeleccionado && itemSeleccionado.costo_unitario_actual) {
        nuevosItems[index].precio_unitario = itemSeleccionado.costo_unitario_actual
      }
    }
    
    setItems(nuevosItems)
  }

  const calcularSubtotal = (item) => {
    const cantidad = parseFloat(item.cantidad || 0)
    const precio = parseFloat(item.precio_unitario || 0)
    return cantidad * precio
  }

  const calcularTotal = () => {
    return items.reduce((total, item) => total + calcularSubtotal(item), 0)
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    if (!proveedorId) {
      toast.error('Debe seleccionar un proveedor')
      return
    }

    if (items.length === 0) {
      toast.error('Debe agregar al menos un item al pedido')
      return
    }

    // Validar que todos los items tengan item_id, cantidad y precio_unitario
    const itemsInvalidos = items.filter(item => 
      !item.item_id || !item.cantidad || !item.precio_unitario
    )
    if (itemsInvalidos.length > 0) {
      toast.error('Todos los items deben tener un producto, cantidad y precio unitario')
      return
    }

    const datos = {
      proveedor_id: parseInt(proveedorId),
      fecha_entrega_esperada: fechaEntregaEsperada || null,
      observaciones: observaciones || null,
      creado_por: 1, // TODO: Obtener del contexto de usuario
      items: items.map(item => ({
        item_id: parseInt(item.item_id),
        cantidad: parseFloat(item.cantidad),
        precio_unitario: parseFloat(item.precio_unitario)
      }))
    }

    crearPedidoMutation.mutate(datos)
  }

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
      <div className="p-6 border-b border-slate-700">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <ShoppingCart size={24} />
          {pedido ? 'Editar Pedido de Compra' : 'Nuevo Pedido de Compra'}
        </h2>
        <p className="text-sm text-slate-400 mt-1">Crear pedido a proveedor</p>
      </div>

      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {/* Información del pedido */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Proveedor *
            </label>
            <select
              value={proveedorId}
              onChange={(e) => setProveedorId(e.target.value)}
              required
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
            >
              <option value="">Seleccionar proveedor...</option>
              {proveedores.map(proveedor => (
                <option key={proveedor.id} value={proveedor.id}>
                  {proveedor.nombre}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Fecha de Entrega Esperada
            </label>
            <input
              type="date"
              value={fechaEntregaEsperada}
              onChange={(e) => setFechaEntregaEsperada(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
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
              const subtotal = calcularSubtotal(item)
              const itemSeleccionado = itemsDisponibles?.find(i => i.id === parseInt(item.item_id))
              
              return (
                <div key={index} className="bg-slate-700/50 p-4 rounded-lg border border-slate-600">
                  <div className="grid grid-cols-12 gap-3 items-end">
                    <div className="col-span-4">
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
                            {i.nombre} ({i.codigo || i.id})
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="col-span-2">
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
                      {itemSeleccionado && (
                        <span className="text-xs text-slate-500 mt-1 block">{itemSeleccionado.unidad}</span>
                      )}
                    </div>
                    <div className="col-span-2">
                      <label className="block text-xs font-medium mb-1 text-slate-400">Precio Unitario</label>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        value={item.precio_unitario}
                        onChange={(e) => actualizarItem(index, 'precio_unitario', e.target.value)}
                        required
                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500 text-sm"
                        placeholder="0.00"
                      />
                    </div>
                    <div className="col-span-3">
                      <label className="block text-xs font-medium mb-1 text-slate-400">Subtotal</label>
                      <div className="px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-sm font-semibold text-green-400">
                        ${subtotal.toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                      </div>
                    </div>
                    <div className="col-span-1">
                      <button
                        type="button"
                        onClick={() => removerItem(index)}
                        className="w-full h-10 bg-red-600 hover:bg-red-700 rounded-lg flex items-center justify-center"
                        title="Eliminar item"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {items.length > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-700 flex justify-between items-center">
              <span className="text-lg font-semibold text-slate-300">Total del Pedido:</span>
              <span className="text-2xl font-bold text-purple-400">
                ${calcularTotal().toLocaleString('es-ES', { minimumFractionDigits: 2 })}
              </span>
            </div>
          )}
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
