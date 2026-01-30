import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api, { extractData } from '../config/api'
import { Plus, AlertTriangle, TrendingDown } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import toast from 'react-hot-toast'
import Modal from '../components/Modal'
import MermaForm from '../components/MermaForm'

export default function Mermas() {
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [tipo, setTipo] = useState('')
  const [ubicacion, setUbicacion] = useState('')
  const [showModal, setShowModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: mermasResponse, isLoading } = useQuery({
    queryKey: ['mermas', fechaInicio, fechaFin, tipo, ubicacion],
    queryFn: () => {
      const params = {}
      if (fechaInicio) params.fecha_inicio = fechaInicio
      if (fechaFin) params.fecha_fin = fechaFin
      if (tipo) params.tipo = tipo
      if (ubicacion) params.ubicacion = ubicacion
      return api.get('/reportes/mermas', { params }).then(extractData)
    },
  })

  // Asegurar que mermas sea un array
  const mermas = Array.isArray(mermasResponse) ? mermasResponse : []

  const { data: resumen } = useQuery({
    queryKey: ['mermas-resumen', fechaInicio, fechaFin, ubicacion],
    queryFn: () => {
      if (!fechaInicio || !fechaFin) return null
      const params = { fecha_inicio: fechaInicio, fecha_fin: fechaFin }
      if (ubicacion) params.ubicacion = ubicacion
      return api.get('/reportes/mermas/resumen', { params }).then(res => res.data)
    },
    enabled: !!fechaInicio && !!fechaFin,
  })

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Reporte de Mermas</h1>
        <button 
          onClick={() => setShowModal(true)}
          className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Plus size={20} />
          Registrar Merma
        </button>
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Registrar Merma"
      >
        <MermaForm
          onClose={() => setShowModal(false)}
        />
      </Modal>

      {/* Filtros */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Fecha Inicio</label>
          <input
            type="date"
            value={fechaInicio}
            onChange={(e) => setFechaInicio(e.target.value)}
            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Fecha Fin</label>
          <input
            type="date"
            value={fechaFin}
            onChange={(e) => setFechaFin(e.target.value)}
            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Tipo</label>
          <select
            value={tipo}
            onChange={(e) => setTipo(e.target.value)}
            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:border-purple-500"
          >
            <option value="">Todos</option>
            <option value="vencimiento">Vencimiento</option>
            <option value="deterioro">Deterioro</option>
            <option value="preparacion">Preparación</option>
            <option value="servicio">Servicio</option>
            <option value="otro">Otro</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Ubicación</label>
          <input
            type="text"
            value={ubicacion}
            onChange={(e) => setUbicacion(e.target.value)}
            placeholder="Filtrar por ubicación"
            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
      </div>

      {/* Resumen */}
      {resumen && (
        <div className="mb-6">
          <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 mb-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Mermas</p>
                <p className="text-2xl font-bold">{resumen.total_mermas}</p>
              </div>
              <div className="text-right">
                <p className="text-slate-400 text-sm">Costo Total</p>
                <p className="text-2xl font-bold text-red-500">
                  ${resumen.total_costo?.toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                </p>
              </div>
            </div>
          </div>
          
          {resumen.por_tipo && Object.keys(resumen.por_tipo).length > 0 && (
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 mb-4">
              <h3 className="font-bold mb-3">Por Tipo</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {Object.entries(resumen.por_tipo).map(([tipo, datos]) => (
                  <div key={tipo}>
                    <p className="text-sm text-slate-400 capitalize">{tipo}</p>
                    <p className="font-bold">${datos.costo?.toLocaleString('es-ES', { minimumFractionDigits: 2 })}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Lista de Mermas */}
      {isLoading ? (
        <div className="text-center py-8">Cargando...</div>
      ) : (
        <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-700">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium">Fecha</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Item</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Tipo</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Cantidad</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Costo Total</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Ubicación</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {mermas?.map((merma) => (
                <tr key={merma.id} className="hover:bg-slate-700/50">
                  <td className="px-6 py-4">
                    {format(new Date(merma.fecha_merma), 'dd MMM yyyy', { locale: es })}
                  </td>
                  <td className="px-6 py-4">
                    {merma.item?.nombre || 'N/A'}
                  </td>
                  <td className="px-6 py-4 capitalize">{merma.tipo}</td>
                  <td className="px-6 py-4">
                    {parseFloat(merma.cantidad).toFixed(2)} {merma.unidad}
                  </td>
                  <td className="px-6 py-4 text-red-400">
                    ${parseFloat(merma.costo_total).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-6 py-4">{merma.ubicacion || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
