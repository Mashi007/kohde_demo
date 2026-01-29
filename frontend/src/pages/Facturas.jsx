import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../config/api'
import { Upload, FileText, CheckCircle, XCircle } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import Modal from '../components/Modal'
import FacturaUploadForm from '../components/FacturaUploadForm'

export default function Facturas() {
  const [tipoFiltro, setTipoFiltro] = useState('')
  const [showUploadModal, setShowUploadModal] = useState(false)

  const { data: facturas, isLoading } = useQuery({
    queryKey: ['facturas', tipoFiltro],
    queryFn: () => 
      api.get('/contabilidad/facturas', { params: tipoFiltro ? { estado: tipoFiltro } : {} })
        .then(res => res.data),
  })

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

      <Modal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        title="Subir Factura con OCR"
      >
        <FacturaUploadForm
          onClose={() => setShowUploadModal(false)}
        />
      </Modal>

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
        <div className="text-center py-8">Cargando...</div>
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
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold">${parseFloat(factura.total).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</p>
                  <p className="text-slate-400 text-sm">
                    Subtotal: ${parseFloat(factura.subtotal).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                  </p>
                </div>
              </div>
              {factura.estado === 'pendiente' && (
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <button 
                    onClick={async () => {
                      try {
                        await api.post(`/contabilidad/facturas/${factura.id}/aprobar`, {
                          usuario_id: 1, // TODO: Obtener del contexto de usuario
                          items_aprobados: factura.items?.map(item => ({
                            factura_item_id: item.id,
                            cantidad_aprobada: item.cantidad_facturada
                          })) || [],
                          aprobar_parcial: false
                        })
                        window.location.reload()
                      } catch (error) {
                        alert(error.response?.data?.error || 'Error al aprobar factura')
                      }
                    }}
                    className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg text-sm"
                  >
                    Revisar y Aprobar
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
