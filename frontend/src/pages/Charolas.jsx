import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api, { extractData } from '../config/api'
import { Plus, FileText, TrendingUp, Users } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import toast from 'react-hot-toast'
import Modal from '../components/Modal'
import CharolaForm from '../components/CharolaForm'
import { TIEMPO_COMIDA_OPTIONS } from '../constants/tiempoComida'

export default function Charolas() {
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [ubicacion, setUbicacion] = useState('')
  const [tiempoComida, setTiempoComida] = useState('')
  const [showModal, setShowModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: charolasResponse, isLoading } = useQuery({
    queryKey: ['charolas', fechaInicio, fechaFin, ubicacion, tiempoComida],
    queryFn: () => {
      const params = {}
      if (fechaInicio) params.fecha_inicio = fechaInicio
      if (fechaFin) params.fecha_fin = fechaFin
      if (ubicacion) params.ubicacion = ubicacion
      if (tiempoComida) params.tiempo_comida = tiempoComida
      return api.get('/reportes/charolas', { params }).then(extractData)
    },
  })

  // Asegurar que charolas sea un array
  const charolas = Array.isArray(charolasResponse) ? charolasResponse : []

  const { data: resumen } = useQuery({
    queryKey: ['charolas-resumen', fechaInicio, fechaFin, ubicacion],
    queryFn: () => {
      if (!fechaInicio || !fechaFin) return null
      const params = { fecha_inicio: fechaInicio, fecha_fin: fechaFin }
      if (ubicacion) params.ubicacion = ubicacion
      return api.get('/reportes/charolas/resumen', { params }).then(res => res.data)
    },
    enabled: !!fechaInicio && !!fechaFin,
  })

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Reporte de Charolas</h1>
        <button 
          onClick={() => setShowModal(true)}
          className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Plus size={20} />
          Nueva Charola
        </button>
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Nueva Charola"
      >
        <CharolaForm
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
          <label className="block text-sm font-medium mb-2">Ubicación</label>
          <input
            type="text"
            value={ubicacion}
            onChange={(e) => setUbicacion(e.target.value)}
            placeholder="Filtrar por ubicación"
            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Tiempo de Comida</label>
          <select
            value={tiempoComida}
            onChange={(e) => setTiempoComida(e.target.value)}
            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:border-purple-500"
          >
            <option value="">Todos</option>
            {TIEMPO_COMIDA_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Resumen */}
      {resumen && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
            <p className="text-slate-400 text-sm">Total Charolas</p>
            <p className="text-2xl font-bold">{resumen.total_charolas}</p>
          </div>
          <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
            <p className="text-slate-400 text-sm">Total Ventas</p>
            <p className="text-2xl font-bold">${resumen.total_ventas?.toLocaleString('es-ES', { minimumFractionDigits: 2 })}</p>
          </div>
          <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
            <p className="text-slate-400 text-sm">Total Ganancia</p>
            <p className="text-2xl font-bold text-green-500">${resumen.total_ganancia?.toLocaleString('es-ES', { minimumFractionDigits: 2 })}</p>
          </div>
          <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
            <p className="text-slate-400 text-sm">Personas Servidas</p>
            <p className="text-2xl font-bold">{resumen.total_personas_servidas}</p>
          </div>
        </div>
      )}

      {/* Lista de Charolas */}
      {isLoading ? (
        <div className="text-center py-8">Cargando...</div>
      ) : (
        <div className="space-y-4">
          {charolas?.map((charola) => (
            <div key={charola.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <FileText size={24} className="text-purple-500" />
                    <h3 className="text-xl font-bold">{charola.numero_charola}</h3>
                  </div>
                  <p className="text-slate-400 mb-1">
                    {format(new Date(charola.fecha_servicio), 'dd MMM yyyy HH:mm', { locale: es })}
                  </p>
                  <p className="text-slate-400 text-sm capitalize">
                    {charola.ubicacion} - {charola.tiempo_comida}
                  </p>
                  <div className="flex items-center gap-4 mt-2">
                    <span className="text-sm text-slate-400 flex items-center gap-1">
                      <Users size={16} />
                      {charola.personas_servidas} personas
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold">${parseFloat(charola.total_ventas).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</p>
                  <p className="text-green-500 font-semibold">
                    Ganancia: ${parseFloat(charola.ganancia).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                  </p>
                  <p className="text-slate-400 text-sm">
                    Costo: ${parseFloat(charola.costo_total).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
                  </p>
                </div>
              </div>
              {charola.items && charola.items.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <p className="text-sm font-medium mb-2">Items incluidos:</p>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {charola.items.map((item) => (
                      <div key={item.id} className="text-sm text-slate-400">
                        {item.nombre_item} x{item.cantidad}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
