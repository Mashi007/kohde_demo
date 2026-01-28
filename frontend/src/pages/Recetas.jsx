import { useQuery } from '@tanstack/react-query'
import api from '../config/api'
import { ChefHat } from 'lucide-react'

export default function Recetas() {
  const { data: recetas } = useQuery({
    queryKey: ['recetas'],
    queryFn: () => api.get('/planificacion/recetas').then(res => res.data),
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Recetas</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {recetas?.map((receta) => (
          <div key={receta.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <ChefHat className="text-purple-500 mb-4" size={32} />
            <h3 className="text-xl font-bold mb-2">{receta.nombre}</h3>
            <p className="text-slate-400 text-sm mb-4">{receta.descripcion}</p>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Porciones:</span>
                <span className="text-white">{receta.porciones}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Costo por porción:</span>
                <span className="text-white">
                  ${receta.costo_por_porcion?.toFixed(2) || '0.00'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Calorías por porción:</span>
                <span className="text-white">
                  {receta.calorias_por_porcion?.toFixed(0) || '0'} kcal
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
