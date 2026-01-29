import { useState } from 'react'
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon } from 'lucide-react'

export default function CalendarioProgramacion({ fechaSeleccionada, onFechaSeleccionada }) {
  const [mesActual, setMesActual] = useState(fechaSeleccionada || new Date())
  
  const hoy = new Date()
  hoy.setHours(0, 0, 0, 0)
  
  const primerDiaMes = new Date(mesActual.getFullYear(), mesActual.getMonth(), 1)
  const ultimoDiaMes = new Date(mesActual.getFullYear(), mesActual.getMonth() + 1, 0)
  const primerDiaSemana = primerDiaMes.getDay()
  const diasEnMes = ultimoDiaMes.getDate()
  
  const nombresDias = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
  const nombresMeses = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ]
  
  const esHoy = (fecha) => {
    return fecha.getTime() === hoy.getTime()
  }
  
  const esSeleccionada = (fecha) => {
    if (!fechaSeleccionada) return false
    const fechaSel = new Date(fechaSeleccionada)
    fechaSel.setHours(0, 0, 0, 0)
    const fechaComp = new Date(fecha)
    fechaComp.setHours(0, 0, 0, 0)
    return fechaSel.getTime() === fechaComp.getTime()
  }
  
  const esPasada = (fecha) => {
    return fecha < hoy
  }
  
  const manejarClickDia = (dia) => {
    const fecha = new Date(mesActual.getFullYear(), mesActual.getMonth(), dia)
    if (!esPasada(fecha)) {
      onFechaSeleccionada(fecha)
    }
  }
  
  const cambiarMes = (direccion) => {
    setMesActual(prev => {
      const nuevoMes = new Date(prev)
      nuevoMes.setMonth(prev.getMonth() + direccion)
      return nuevoMes
    })
  }
  
  const irAHoy = () => {
    const hoy = new Date()
    setMesActual(hoy)
    onFechaSeleccionada(hoy)
  }
  
  const dias = []
  
  // Días vacíos al inicio
  for (let i = 0; i < primerDiaSemana; i++) {
    dias.push(null)
  }
  
  // Días del mes
  for (let dia = 1; dia <= diasEnMes; dia++) {
    const fecha = new Date(mesActual.getFullYear(), mesActual.getMonth(), dia)
    dias.push({
      dia,
      fecha,
      esHoy: esHoy(fecha),
      esSeleccionada: esSeleccionada(fecha),
      esPasada: esPasada(fecha),
    })
  }
  
  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 p-4">
      {/* Header del calendario */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <CalendarIcon className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-semibold">
            {nombresMeses[mesActual.getMonth()]} {mesActual.getFullYear()}
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => cambiarMes(-1)}
            className="p-1 hover:bg-slate-700 rounded transition-colors"
            title="Mes anterior"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <button
            onClick={irAHoy}
            className="px-3 py-1 text-sm bg-purple-600 hover:bg-purple-700 rounded transition-colors"
          >
            Hoy
          </button>
          <button
            onClick={() => cambiarMes(1)}
            className="p-1 hover:bg-slate-700 rounded transition-colors"
            title="Mes siguiente"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>
      
      {/* Nombres de días */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {nombresDias.map(dia => (
          <div key={dia} className="text-center text-xs font-medium text-slate-400 py-2">
            {dia}
          </div>
        ))}
      </div>
      
      {/* Días del calendario */}
      <div className="grid grid-cols-7 gap-1">
        {dias.map((diaInfo, index) => {
          if (diaInfo === null) {
            return <div key={`empty-${index}`} className="aspect-square" />
          }
          
          const { dia, fecha, esHoy, esSeleccionada, esPasada } = diaInfo
          
          return (
            <button
              key={dia}
              onClick={() => manejarClickDia(dia)}
              disabled={esPasada}
              className={`
                aspect-square rounded transition-all
                ${esSeleccionada 
                  ? 'bg-purple-600 text-white font-semibold ring-2 ring-purple-400' 
                  : esHoy
                  ? 'bg-purple-600/30 text-purple-300 font-semibold border-2 border-purple-500'
                  : esPasada
                  ? 'bg-slate-900/50 text-slate-600 cursor-not-allowed'
                  : 'bg-slate-700/50 hover:bg-slate-700 text-slate-200 hover:text-white'
                }
              `}
            >
              {dia}
            </button>
          )
        })}
      </div>
      
      {/* Leyenda */}
      <div className="flex items-center gap-4 mt-4 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-purple-600" />
          <span>Seleccionada</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-purple-600/30 border-2 border-purple-500" />
          <span>Hoy</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-slate-900/50" />
          <span>Pasada</span>
        </div>
      </div>
    </div>
  )
}
