import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'
import { X, CheckCircle, XCircle, RotateCcw } from 'lucide-react'
import toast from 'react-hot-toast'
import ConfirmDialog from './ConfirmDialog'
import { useAuth } from '../contexts/AuthContext'

export default function FacturaOCRModal({ factura, isOpen, onClose }) {
  const [itemsConfirmados, setItemsConfirmados] = useState({})
  const [observaciones, setObservaciones] = useState('')
  const [confirmarRechazo, setConfirmarRechazo] = useState(false)
  const queryClient = useQueryClient()
  const { user } = useAuth()

  if (!isOpen || !factura) return null

  // Inicializar items confirmados con cantidad facturada
  const inicializarItems = () => {
    const items = {}
    factura.items?.forEach(item => {
      items[item.id] = {
        cantidad_aprobada: item.cantidad_facturada || 0,
        unidad: item.unidad || item.item?.unidad || 'unidad',
        confirmado: false
      }
    })
    setItemsConfirmados(items)
  }

  useState(() => {
    if (factura.items) {
      inicializarItems()
    }
  }, [factura])

  const handleConfirmarItem = (itemId) => {
    setItemsConfirmados(prev => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        confirmado: true
      }
    }))
  }

  const handleCambiarCantidad = (itemId, nuevaCantidad) => {
    setItemsConfirmados(prev => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        cantidad_aprobada: parseFloat(nuevaCantidad) || 0,
        confirmado: false
      }
    }))
  }

  const aprobarMutation = useMutation({
    mutationFn: (datos) => api.post(`/logistica/facturas/${factura.id}/aprobar`, datos),
    onSuccess: () => {
      toast.success('Factura aprobada correctamente')
      queryClient.invalidateQueries(['facturas'])
      queryClient.invalidateQueries(['factura-ultima'])
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al aprobar factura')
    },
  })

  const rechazarMutation = useMutation({
    mutationFn: (datos) => api.post(`/logistica/facturas/${factura.id}/rechazar`, datos),
    onSuccess: () => {
      toast.success('Factura rechazada')
      queryClient.invalidateQueries(['facturas'])
      queryClient.invalidateQueries(['factura-ultima'])
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al rechazar factura')
    },
  })

  const revisionMutation = useMutation({
    mutationFn: (datos) => api.post(`/logistica/facturas/${factura.id}/revision`, datos),
    onSuccess: () => {
      toast.success('Factura enviada a revisión')
      queryClient.invalidateQueries(['facturas'])
      queryClient.invalidateQueries(['factura-ultima'])
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al enviar a revisión')
    },
  })

  const handleAprobar = () => {
    const items_aprobados = Object.entries(itemsConfirmados).map(([itemId, data]) => ({
      factura_item_id: parseInt(itemId),
      cantidad_aprobada: data.cantidad_aprobada,
      unidad: data.unidad || factura.items?.find(i => i.id === parseInt(itemId))?.unidad || factura.items?.find(i => i.id === parseInt(itemId))?.item?.unidad
    }))

    const totalAprobado = items_aprobados.reduce((sum, item) => sum + item.cantidad_aprobada, 0)
    const totalFacturado = factura.items?.reduce((sum, item) => sum + (item.cantidad_facturada || 0), 0) || 0
    const porcentajeAprobado = totalFacturado > 0 ? (totalAprobado / totalFacturado * 100) : 0

    aprobarMutation.mutate({
      usuario_id: user?.id || 1, // Obtener del contexto de autenticación
      items_aprobados,
      aprobar_parcial: porcentajeAprobado < 100,
      observaciones
    })
  }

  const handleRechazar = () => {
    setConfirmarRechazo(true)
  }

  const confirmarRechazoAction = () => {
    rechazarMutation.mutate({
      usuario_id: user?.id || 1, // Obtener del contexto de autenticación
      motivo: observaciones || 'Factura rechazada - requiere refacturación'
    })
    setConfirmarRechazo(false)
  }

  const handleEnviarRevision = () => {
    revisionMutation.mutate({
      usuario_id: user?.id || 1, // Obtener del contexto de autenticación
      observaciones: observaciones || 'Enviada a revisión'
    })
  }

  const totalAprobado = Object.values(itemsConfirmados).reduce((sum, item) => sum + (item.cantidad_aprobada || 0), 0)
  const totalFacturado = factura.items?.reduce((sum, item) => sum + (item.cantidad_facturada || 0), 0) || 0
  const porcentajeAprobado = totalFacturado > 0 ? (totalAprobado / totalFacturado * 100) : 0

  return (
    <>
      <ConfirmDialog
        isOpen={confirmarRechazo}
        onClose={() => setConfirmarRechazo(false)}
        onConfirm={confirmarRechazoAction}
        title="Rechazar factura"
        message="¿Estás seguro de rechazar esta factura? El proveedor deberá refacturar solo por lo recibido."
        confirmText="Rechazar"
        cancelText="Cancelar"
        variant="danger"
        isLoading={rechazarMutation.isPending}
      />
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-lg border border-slate-700 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-slate-800 border-b border-slate-700 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Confirmar Factura OCR</h2>
            <p className="text-sm text-slate-400 mt-1">
              Factura #{factura.numero_factura} • {factura.proveedor?.nombre || 'Proveedor no identificado'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white"
          >
            <X size={24} />
          </button>
        </div>

        {/* Información de la factura */}
        <div className="p-6 border-b border-slate-700">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-slate-400">Proveedor</p>
              <p className="font-semibold">{factura.proveedor?.nombre || 'No identificado'}</p>
            </div>
            <div>
              <p className="text-sm text-slate-400">Fecha</p>
              <p className="font-semibold">
                {new Date(factura.fecha_emision).toLocaleDateString('es-ES')}
              </p>
            </div>
            <div>
              <p className="text-sm text-slate-400">Total Facturado</p>
              <p className="font-semibold">${parseFloat(factura.total || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</p>
            </div>
            <div>
              <p className="text-sm text-slate-400">Remitente</p>
              <p className="font-semibold">{factura.remitente_nombre || 'N/A'}</p>
              <p className="text-xs text-slate-500">{factura.remitente_telefono || ''}</p>
            </div>
          </div>
        </div>

        {/* Imagen de la factura */}
        {factura.imagen_url && (
          <div className="p-6 border-b border-slate-700">
            <p className="text-sm font-semibold mb-2">Imagen de la Factura</p>
            <img
              src={factura.imagen_url}
              alt="Factura"
              className="max-w-full h-auto rounded-lg border border-slate-700"
            />
          </div>
        )}

        {/* Items con confirmación */}
        <div className="p-6">
          <h3 className="text-lg font-bold mb-4">Items de la Factura</h3>
          <p className="text-sm text-slate-400 mb-4">
            Confirma la cantidad recibida para cada item. Si hay diferencias, ingresa la cantidad real recibida.
          </p>
          
          <div className="space-y-4">
            {factura.items?.map((item) => {
              const itemData = itemsConfirmados[item.id] || { cantidad_aprobada: item.cantidad_facturada || 0, confirmado: false }
              const diferencia = itemData.cantidad_aprobada - (item.cantidad_facturada || 0)
              
              return (
                <div
                  key={item.id}
                  className={`bg-slate-700/50 p-4 rounded-lg border ${
                    itemData.confirmado
                      ? 'border-green-500/50'
                      : diferencia !== 0
                      ? 'border-yellow-500/50'
                      : 'border-slate-600'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="font-semibold mb-1">
                        {item.item?.nombre || item.descripcion || 'Item sin identificar'}
                      </h4>
                      <p className="text-sm text-slate-400">
                        {item.item?.codigo || 'Sin código'} • {item.unidad || item.item?.unidad || 'unidad'}
                      </p>
                    </div>
                    {itemData.confirmado && (
                      <CheckCircle className="text-green-500" size={20} />
                    )}
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Cantidad Facturada</label>
                      <p className="font-semibold">
                        {item.cantidad_facturada || 0} {item.unidad || item.item?.unidad || 'unidad'}
                      </p>
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Cantidad Recibida</label>
                      <div className="flex gap-2">
                        <input
                          type="number"
                          step="0.01"
                          value={itemData.cantidad_aprobada}
                          onChange={(e) => handleCambiarCantidad(item.id, e.target.value)}
                          className="flex-1 px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
                          disabled={itemData.confirmado}
                        />
                        <select
                          value={itemData.unidad || item.unidad || item.item?.unidad || 'unidad'}
                          onChange={(e) => setItemsConfirmados(prev => ({
                            ...prev,
                            [item.id]: { ...prev[item.id], unidad: e.target.value }
                          }))}
                          className="px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500 text-sm"
                          disabled={itemData.confirmado}
                        >
                          <option value="kg">kg</option>
                          <option value="g">g</option>
                          <option value="qq">qq</option>
                          <option value="quintal">quintal</option>
                          <option value="l">l</option>
                          <option value="ml">ml</option>
                          <option value="unidad">unidad</option>
                          <option value="caja">caja</option>
                          <option value="paquete">paquete</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Precio Unitario</label>
                      <p className="font-semibold">
                        ${parseFloat(item.precio_unitario || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                        <span className="text-xs text-slate-500 ml-1">/{item.unidad || item.item?.unidad || 'unidad'}</span>
                      </p>
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Subtotal</label>
                      <p className="font-semibold">
                        ${(itemData.cantidad_aprobada * parseFloat(item.precio_unitario || 0)).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                      </p>
                    </div>
                  </div>

                  {diferencia !== 0 && (
                    <div className="mt-2 p-2 bg-yellow-500/20 border border-yellow-500/50 rounded text-sm text-yellow-300">
                      ⚠️ Diferencia: {diferencia > 0 ? '+' : ''}{diferencia.toFixed(2)} unidades
                    </div>
                  )}

                  {!itemData.confirmado && (
                    <button
                      onClick={() => handleConfirmarItem(item.id)}
                      className="mt-3 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm flex items-center gap-2"
                    >
                      <CheckCircle size={16} />
                      Confirmar {itemData.cantidad_aprobada} recibidos
                    </button>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Resumen */}
        <div className="p-6 bg-slate-700/30 border-t border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm text-slate-400">Total Facturado</p>
              <p className="text-xl font-bold">${parseFloat(factura.total || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-slate-400">Total Aprobado</p>
              <p className={`text-xl font-bold ${porcentajeAprobado === 100 ? 'text-green-400' : porcentajeAprobado > 0 ? 'text-yellow-400' : 'text-red-400'}`}>
                ${(totalAprobado * parseFloat(factura.items?.[0]?.precio_unitario || 0)).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
              </p>
              <p className="text-xs text-slate-400">
                {porcentajeAprobado.toFixed(1)}% aprobado
              </p>
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Observaciones</label>
            <textarea
              value={observaciones}
              onChange={(e) => setObservaciones(e.target.value)}
              rows={3}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Agregar observaciones sobre la factura..."
            />
          </div>

          {/* Acciones */}
          <div className="flex gap-3">
            <button
              onClick={handleAprobar}
              disabled={aprobarMutation.isPending || porcentajeAprobado === 0}
              className={`flex-1 px-4 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 ${
                porcentajeAprobado === 100
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-yellow-600 hover:bg-yellow-700'
              } disabled:opacity-50`}
            >
              <CheckCircle size={20} />
              {porcentajeAprobado === 100 ? 'Aprobar 100%' : `Aprobar ${porcentajeAprobado.toFixed(1)}%`}
            </button>
            <button
              onClick={handleEnviarRevision}
              disabled={revisionMutation.isPending}
              className="px-4 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold flex items-center gap-2 disabled:opacity-50"
            >
              <RotateCcw size={20} />
              Enviar a Revisión
            </button>
            <button
              onClick={handleRechazar}
              disabled={rechazarMutation.isPending}
              className="px-4 py-3 bg-red-600 hover:bg-red-700 rounded-lg font-semibold flex items-center gap-2 disabled:opacity-50"
            >
              <XCircle size={20} />
              Rechazar
            </button>
          </div>
        </div>
      </div>
    </>
  )
}
