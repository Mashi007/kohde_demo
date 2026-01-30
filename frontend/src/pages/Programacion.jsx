import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api, { extractData } from '../config/api'
import { Calendar, Plus, Filter, UtensilsCrossed, Package } from 'lucide-react'
import CalendarioProgramacion from '../components/CalendarioProgramacion'
import ProgramacionForm from '../components/ProgramacionForm'
import NecesidadesProgramacion from '../components/NecesidadesProgramacion'
import { format, parseISO, isSameDay } from 'date-fns'
import { es } from 'date-fns/locale'
import { TIEMPO_COMIDA_OPTIONS, getTiempoComidaColor, getTiempoComidaLabel } from '../constants/tiempoComida'

export default function Programacion() {
  const [fechaSeleccionada, setFechaSeleccionada] = useState(new Date())
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [programacionEditando, setProgramacionEditando] = useState(null)
  const [programacionNecesidades, setProgramacionNecesidades] = useState(null)
  const [filtroServicio, setFiltroServicio] = useState('')
  
  // Cargar programaciones
  const { data: programaciones, isLoading } = useQuery({
    queryKey: ['programaciones', fechaSeleccionada, filtroServicio],
    queryFn: () => {
      const fechaStr = format(fechaSeleccionada, 'yyyy-MM-dd')
      const params = new URLSearchParams({
        fecha_desde: fechaStr,
        fecha_hasta: fechaStr,
      })
      if (filtroServicio) {
        params.append('tiempo_comida', filtroServicio)
      }
      return api.get(`/planificacion/programacion?${params}`).then(res => extractData(res))
    },
  })
  
  const servicios = [
    { value: '', label: 'Todos' },
    ...TIEMPO_COMIDA_OPTIONS,
  ]
  
  const getServicioBadge = (servicio) => {
    return getTiempoComidaColor(servicio)
  }
  
  const getServicioLabel = (servicio) => {
    return getTiempoComidaLabel(servicio)
  }
  
  const programacionesArray = Array.isArray(programaciones) ? programaciones : []
  // Filtrar programaciones que incluyan la fecha seleccionada en su rango
  const programacionesDelDia = programacionesArray.filter(p => {
    const fechaDesde = p.fecha_desde ? parseISO(p.fecha_desde) : (p.fecha ? parseISO(p.fecha) : null)
    const fechaHasta = p.fecha_hasta ? parseISO(p.fecha_hasta) : (p.fecha ? parseISO(p.fecha) : null)
    
    if (!fechaDesde || !fechaHasta) return false
    
    // La fecha seleccionada está en el rango si: fecha_desde <= fecha_seleccionada <= fecha_hasta
    return fechaSeleccionada >= fechaDesde && fechaSeleccionada <= fechaHasta
  })
  
  const programacionesPorServicio = programacionesDelDia.reduce((acc, prog) => {
    const servicio = prog.tiempo_comida
    if (!acc[servicio]) {
      acc[servicio] = []
    }
    acc[servicio].push(prog)
    return acc
  }, {})
  
  const handleNuevaProgramacion = () => {
    setProgramacionEditando(null)
    setMostrarFormulario(true)
  }
  
  const handleEditarProgramacion = (programacion) => {
    setProgramacionEditando(programacion)
    setMostrarFormulario(true)
  }
  
  const handleVerNecesidades = (programacion) => {
    setProgramacionNecesidades(programacion.id)
  }
  
  const handleFechaSeleccionada = (fecha) => {
    setFechaSeleccionada(fecha)
  }
  
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Calendar className="w-8 h-8 text-purple-400" />
          <h1 className="text-3xl font-bold">Programación de Menús</h1>
        </div>
        <button
          onClick={handleNuevaProgramacion}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          Nueva Programación
        </button>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendario */}
        <div className="lg:col-span-1">
          <CalendarioProgramacion
            fechaSeleccionada={fechaSeleccionada}
            onFechaSeleccionada={handleFechaSeleccionada}
          />
        </div>
        
        {/* Lista de Programaciones */}
        <div className="lg:col-span-2">
          {/* Filtros */}
          <div className="mb-4 flex items-center gap-3">
            <Filter className="w-5 h-5 text-slate-400" />
            <select
              value={filtroServicio}
              onChange={(e) => setFiltroServicio(e.target.value)}
              className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
            >
              {servicios.map(s => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
            <div className="text-sm text-slate-400">
              {format(fechaSeleccionada, "EEEE, d 'de' MMMM", { locale: es })}
            </div>
          </div>
          
          {/* Programaciones del día */}
          {isLoading ? (
            <div className="text-center py-12 text-slate-400">Cargando programaciones...</div>
          ) : programacionesDelDia.length === 0 ? (
            <div className="text-center py-12 border border-slate-700 rounded-lg bg-slate-800/50">
              <Calendar className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400 mb-2">No hay programaciones para esta fecha</p>
              <button
                onClick={handleNuevaProgramacion}
                className="text-purple-400 hover:text-purple-300"
              >
                Crear nueva programación
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Desayuno */}
              {programacionesPorServicio.desayuno && programacionesPorServicio.desayuno.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3 text-yellow-300">Desayuno</h3>
                  <div className="space-y-3">
                    {programacionesPorServicio.desayuno.map(prog => (
                      <ProgramacionCard
                        key={prog.id}
                        programacion={prog}
                        onEdit={handleEditarProgramacion}
                        onVerNecesidades={handleVerNecesidades}
                      />
                    ))}
                  </div>
                </div>
              )}
              
              {/* Almuerzo */}
              {programacionesPorServicio.almuerzo && programacionesPorServicio.almuerzo.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3 text-orange-300">Almuerzo</h3>
                  <div className="space-y-3">
                    {programacionesPorServicio.almuerzo.map(prog => (
                      <ProgramacionCard
                        key={prog.id}
                        programacion={prog}
                        onEdit={handleEditarProgramacion}
                        onVerNecesidades={handleVerNecesidades}
                      />
                    ))}
                  </div>
                </div>
              )}
              
              {/* Cena */}
              {programacionesPorServicio.cena && programacionesPorServicio.cena.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3 text-blue-300">Cena</h3>
                  <div className="space-y-3">
                    {programacionesPorServicio.cena.map(prog => (
                      <ProgramacionCard
                        key={prog.id}
                        programacion={prog}
                        onEdit={handleEditarProgramacion}
                        onVerNecesidades={handleVerNecesidades}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      
      {/* Modal de Formulario */}
      {mostrarFormulario && (
        <ProgramacionForm
          programacion={programacionEditando}
          fecha={fechaSeleccionada}
          tiempoComida={filtroServicio || undefined}
          onClose={() => {
            setMostrarFormulario(false)
            setProgramacionEditando(null)
          }}
          onSuccess={() => {
            setMostrarFormulario(false)
            setProgramacionEditando(null)
          }}
        />
      )}
      
      {/* Modal de Necesidades */}
      {programacionNecesidades && (
        <NecesidadesProgramacion
          programacionId={programacionNecesidades}
          onClose={() => setProgramacionNecesidades(null)}
        />
      )}
    </div>
  )
}

function ProgramacionCard({ programacion, onEdit, onVerNecesidades }) {
  const getServicioBadge = (servicio) => {
    const badges = {
      desayuno: 'bg-yellow-600/20 text-yellow-300 border-yellow-500/50',
      almuerzo: 'bg-orange-600/20 text-orange-300 border-orange-500/50',
      cena: 'bg-blue-600/20 text-blue-300 border-blue-500/50',
    }
    return badges[servicio] || 'bg-slate-600/20 text-slate-300 border-slate-500/50'
  }
  
  const getServicioLabel = (servicio) => {
    const labels = {
      desayuno: 'Desayuno',
      almuerzo: 'Almuerzo',
      cena: 'Cena',
    }
    return labels[servicio] || servicio
  }
  
  return (
    <div
      className="p-4 bg-slate-800 border border-slate-700 rounded-lg hover:border-purple-500/50 transition-colors cursor-pointer"
      onClick={() => onEdit(programacion)}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <UtensilsCrossed className="w-5 h-5 text-purple-400" />
          <div>
            <h4 className="font-semibold">{programacion.ubicacion}</h4>
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-xs px-2 py-1 rounded border ${getServicioBadge(programacion.tiempo_comida)}`}>
                {getServicioLabel(programacion.tiempo_comida)}
              </span>
              {(programacion.fecha_desde || programacion.fecha) && (
                <span className="text-xs text-slate-400">
                  {(() => {
                    const fechaDesde = programacion.fecha_desde || programacion.fecha
                    const fechaHasta = programacion.fecha_hasta || programacion.fecha
                    if (fechaDesde === fechaHasta) {
                      return format(parseISO(fechaDesde), "d 'de' MMM", { locale: es })
                    } else {
                      return `${format(parseISO(fechaDesde), "d MMM", { locale: es })} - ${format(parseISO(fechaHasta), "d MMM", { locale: es })}`
                    }
                  })()}
                </span>
              )}
            </div>
          </div>
        </div>
        {programacion.personas_estimadas > 0 && (
          <div className="text-sm text-slate-400">
            {programacion.personas_estimadas} personas
          </div>
        )}
      </div>
      
      {/* Recetas */}
      <div className="mb-3">
        <div className="text-xs text-slate-400 mb-1">
          {programacion.total_recetas} receta{programacion.total_recetas !== 1 ? 's' : ''} • {programacion.total_porciones} porciones
        </div>
        <div className="flex flex-wrap gap-2">
          {programacion.items?.slice(0, 3).map((item, idx) => (
            <span key={idx} className="text-xs px-2 py-1 bg-slate-700 rounded">
              {item.receta?.nombre} ({item.cantidad_porciones}x)
            </span>
          ))}
          {programacion.items?.length > 3 && (
            <span className="text-xs px-2 py-1 bg-slate-700 rounded text-slate-400">
              +{programacion.items.length - 3} más
            </span>
          )}
        </div>
      </div>
      
      {/* Resumen */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-700">
        <div className="flex items-center gap-4 text-sm">
          <div>
            <span className="text-slate-400">Calorías: </span>
            <span className="font-semibold">{Math.round(programacion.calorias_totales || 0).toLocaleString()} kcal</span>
          </div>
          <div>
            <span className="text-slate-400">Costo: </span>
            <span className="font-semibold">${(programacion.costo_total || 0).toFixed(2)}</span>
          </div>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onVerNecesidades(programacion)
          }}
          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm flex items-center gap-2 transition-colors"
          title="Ver necesidades de inventario"
        >
          <Package className="w-4 h-4" />
          Necesidades
        </button>
      </div>
    </div>
  )
}
