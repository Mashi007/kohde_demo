import { useQuery } from '@tanstack/react-query'
import api from '../config/api'
import { Calendar } from 'lucide-react'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

export default function Programacion() {
  const { data: programaciones } = useQuery({
    queryKey: ['programacion'],
    queryFn: () => api.get('/planificacion/programacion').then(res => res.data),
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Programación de Menús</h1>
      <div className="space-y-4">
        {programaciones?.map((programacion) => (
          <div key={programacion.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="flex items-start gap-4">
              <Calendar className="text-purple-500" size={24} />
              <div className="flex-1">
                <h3 className="text-lg font-bold mb-2">
                  {format(new Date(programacion.fecha), 'EEEE, dd MMMM yyyy', { locale: es })}
                </h3>
                <p className="text-slate-400 capitalize mb-2">
                  {programacion.tiempo_comida} - {programacion.ubicacion}
                </p>
                <p className="text-slate-400">
                  Personas estimadas: {programacion.personas_estimadas}
                </p>
                <div className="mt-4">
                  <button className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-sm">
                    Ver Necesidades
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
