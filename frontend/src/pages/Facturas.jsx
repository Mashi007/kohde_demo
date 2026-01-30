import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import api, { extractData } from '../config/api'
import { Upload, FileText, CheckCircle, XCircle, Eye, Image as ImageIcon } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Modal from '../components/Modal'
import FacturaUploadForm from '../components/FacturaUploadForm'
import FacturaOCRModal from '../components/FacturaOCRModal'
import { handleApiError } from '../utils/errorHandler'
import LoadingSpinner from '../components/LoadingSpinner'
import SkeletonLoader from '../components/SkeletonLoader'
import EmptyState from '../components/EmptyState'
import toast from 'react-hot-toast'

export default function Facturas() {
  const [tipoFiltro, setTipoFiltro] = useState('')
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [facturaOCRAbierta, setFacturaOCRAbierta] = useState(null)

  // Última factura ingresada (para dashboard)
  const { data: ultimaFactura } = useQuery({
    queryKey: ['factura-ultima'],
    queryFn: () => api.get('/logistica/facturas/ultima').then(res => res.data).catch(() => null),
  })

  // Facturas pendientes de confirmación
  const { data: facturasPendientesResponse, isLoading: isLoadingPendientes } = useQuery({
    queryKey: ['facturas-pendientes'],
    queryFn: () => api.get('/logistica/facturas?pendiente_confirmacion=true&estado=pendiente').then(extractData),
  })

  // Todas las facturas
  const { data: facturasResponse, isLoading } = useQuery({
    queryKey: ['facturas', tipoFiltro],
    queryFn: () => 
      api.get('/logistica/facturas', { params: tipoFiltro ? { estado: tipoFiltro } : {} })
        .then(extractData),
  })

  // Asegurar que sean arrays
  const facturasPendientes = Array.isArray(facturasPendientesResponse) ? facturasPendientesResponse : []
  const facturas = Array.isArray(facturasResponse) ? facturasResponse : []

  const getEstadoBadge = (estado) => {
    const badges = {
      pendiente: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
      parcial: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
      aprobada: 'bg-green-500/20 text-green-400 border-green-500/50',
      rechazada: 'bg-red-500/20 text-red-400 border-red-500/50',
    }
    return badges[estado] || badges.pendiente
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Facturas</h1>
        <button 
          onClick={() => setShowUploadModal(true)}
          className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Upload size={20} />
          Subir Factura
        </button>
      </div>

      {/* Última factura ingresada (Dashboard) */}
      {ultimaFactura && (
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-6">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <FileText size={20} />
            Última Factura Ingresada
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center">
            <div>
              <p className="text-xs text-slate-400 mb-1">Remitente</p>
              <p className="font-semibold">{ultimaFactura.remitente_nombre || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-slate-400 mb-1">Teléfono</p>
              <p className="font-semibold">{ultimaFactura.remitente_telefono || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-slate-400 mb-1">Imagen</p>
              {ultimaFactura.imagen_url ? (
                <div className="relative w-16 h-16 rounded-lg overflow-hidden border border-slate-600">
                  <img
                    src={ultimaFactura.imagen_url}
                    alt="Factura"
                    className="w-full h-full object-cover"
                  />
                </div>
              ) : (
                <div className="w-16 h-16 rounded-lg bg-slate-700 flex items-center justify-center">
                  <ImageIcon size={20} className="text-slate-400" />
                </div>
              )}
            </div>
            <div>
              <p className="text-xs text-slate-400 mb-1">Factura #{ultimaFactura.numero_factura}</p>
              <p className="font-semibold">${parseFloat(ultimaFactura.total || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</p>
            </div>
            <div>
              <button
                onClick={() => setFacturaOCRAbierta(ultimaFactura)}
                className="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2"
              >
                <Eye size={18} />
                Ver OCR
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Facturas pendientes de confirmación */}
      {facturasPendientes && facturasPendientes.length > 0 && (
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-6">
          <h2 className="text-lg font-bold mb-4">Facturas Pendientes de Confirmación</h2>
          <div className="space-y-3">
            {facturasPendientes.slice(0, 5).map((factura) => (
              <div key={factura.id} className="bg-slate-700/50 p-4 rounded-lg border border-slate-600">
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center">
                  <div>
                    <p className="text-xs text-slate-400 mb-1">Remitente</p>
                    <p className="font-semibold">{factura.remitente_nombre || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-1">Teléfono</p>
                    <p className="font-semibold">{factura.remitente_telefono || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-1">Imagen</p>
                    {factura.imagen_url ? (
                      <div className="relative w-16 h-16 rounded-lg overflow-hidden border border-slate-600 cursor-pointer hover:opacity-80"
                           onClick={() => window.open(factura.imagen_url, '_blank')}>
                        <img
                          src={factura.imagen_url}
                          alt="Factura"
                          className="w-full h-full object-cover"
                        />
                      </div>
                    ) : (
                      <div className="w-16 h-16 rounded-lg bg-slate-700 flex items-center justify-center">
                        <ImageIcon size={20} className="text-slate-400" />
                      </div>
                    )}
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-1">Factura #{factura.numero_factura}</p>
                    <p className="font-semibold">${parseFloat(factura.total || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</p>
                    <p className="text-xs text-slate-400">
                      {factura.items?.length || 0} items
                    </p>
                  </div>
                  <div>
                    <button
                      onClick={() => {
                        // Cargar factura completa con items
                        api.get(`/logistica/facturas/${factura.id}`)
                          .then(res => setFacturaOCRAbierta(res.data))
                          .catch(err => handleApiError(err, 'Error al cargar factura'))
                      }}
                      className="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2"
                    >
                      <Eye size={18} />
                      Confirmar OCR
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <Modal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        title="Subir Factura con OCR"
      >
        <FacturaUploadForm
          onClose={() => setShowUploadModal(false)}
        />
      </Modal>

      <FacturaOCRModal
        factura={facturaOCRAbierta}
        isOpen={!!facturaOCRAbierta}
        onClose={() => setFacturaOCRAbierta(null)}
      />

      {/* Filtros */}
      <div className="mb-6 flex gap-4">
        <select
          value={tipoFiltro}
          onChange={(e) => setTipoFiltro(e.target.value)}
          className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:border-purple-500"
        >
          <option value="">Todos los estados</option>
          <option value="pendiente">Pendiente</option>
          <option value="parcial">Parcial</option>
          <option value="aprobada">Aprobada</option>
          <option value="rechazada">Rechazada</option>
        </select>
      </div>

      {/* Lista de Facturas */}
      {isLoading ? (
        <div className="py-8">
          <SkeletonLoader type="card" lines={3} />
        </div>
      ) : !facturas || facturas.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No hay facturas"
          description={tipoFiltro ? 'No se encontraron facturas con el filtro seleccionado.' : 'Aún no hay facturas registradas en el sistema.'}
          action={() => setShowUploadModal(true)}
          actionLabel="Subir primera factura"
        />
      ) : (
        <div className="space-y-4">
          {facturas?.map((factura) => (
            <div key={factura.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <FileText size={24} className="text-purple-500" />
                    <h3 className="text-xl font-bold">{factura.numero_factura}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs border ${getEstadoBadge(factura.estado)}`}>
                      {factura.estado}
                    </span>
                  </div>
                  <p className="text-slate-400 mb-1">
                    {factura.proveedor?.nombre || factura.cliente?.nombre || 'N/A'}
                  </p>
                  <p className="text-slate-400 text-sm">
                    {format(new Date(factura.fecha_emision), 'dd MMM yyyy', { locale: es })}
                  </p>
                  {factura.remitente_nombre && (
                    <p className="text-slate-500 text-xs mt-1">
                      Enviada por: {factura.remitente_nombre} ({factura.remitente_telefono})
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold">${parseFloat(factura.total).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</p>
                  <p className="text-slate-400 text-sm">
                    Subtotal: ${parseFloat(factura.subtotal).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                  </p>
                </div>
              </div>
              {factura.estado === 'pendiente' && (
                <div className="mt-4 pt-4 border-t border-slate-700 flex gap-3">
                  <button 
                    onClick={() => {
                      api.get(`/logistica/facturas/${factura.id}`)
                        .then(res => setFacturaOCRAbierta(res.data))
                        .catch(err => handleApiError(err, 'Error al cargar factura'))
                    }}
                    className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-sm flex items-center gap-2"
                  >
                    <Eye size={16} />
                    Confirmar OCR
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
