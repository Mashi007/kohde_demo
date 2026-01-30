import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api, { extractData } from '../config/api'
import { ChefHat, Plus, Filter, Edit, Trash2, Power, PowerOff } from 'lucide-react'
import RecetaForm from '../components/RecetaForm'
import Modal from '../components/Modal'
import toast from 'react-hot-toast'
import { TIEMPO_COMIDA_OPTIONS, getTiempoComidaColor, getTiempoComidaLabel } from '../constants/tiempoComida'

export default function Recetas() {
  const queryClient = useQueryClient()
  const [tipoFiltro, setTipoFiltro] = useState('')
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [recetaEditando, setRecetaEditando] = useState(null)

  const { data: recetasResponse, isLoading } = useQuery({
    queryKey: ['recetas', tipoFiltro],
    queryFn: () => {
      const params = tipoFiltro ? `?tipo=${tipoFiltro}` : ''
      return api.get(`/planificacion/recetas${params}`).then(extractData)
    },
  })

  // Asegurar que recetas sea un array
  const recetas = Array.isArray(recetasResponse) ? recetasResponse : []

  // Mutación para eliminar receta
  const deleteMutation = useMutation({
    mutationFn: (recetaId) => api.delete(`/planificacion/recetas/${recetaId}`),
    onSuccess: () => {
      toast.success('Receta eliminada correctamente')
      queryClient.invalidateQueries(['recetas'])
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al eliminar receta')
    },
  })

  // Mutación para activar/desactivar receta
  const toggleActivaMutation = useMutation({
    mutationFn: ({ recetaId, activa }) => 
      api.patch(`/planificacion/recetas/${recetaId}/activar`, { activa }),
    onSuccess: (_, variables) => {
      toast.success(`Receta ${variables.activa ? 'activada' : 'desactivada'} correctamente`)
      queryClient.invalidateQueries(['recetas'])
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al cambiar estado de la receta')
    },
  })

  const handleEliminar = (e, receta) => {
    e.stopPropagation()
    if (window.confirm(`¿Estás seguro de eliminar la receta "${receta.nombre}"?`)) {
      deleteMutation.mutate(receta.id)
    }
  }

  const handleEditar = (e, receta) => {
    e.stopPropagation()
    setRecetaEditando(receta)
    setMostrarFormulario(true)
  }

  const handleToggleActiva = (e, receta) => {
    e.stopPropagation()
    toggleActivaMutation.mutate({ 
      recetaId: receta.id, 
      activa: !receta.activa 
    })
  }

  const tiposReceta = [
    { value: '', label: 'Todas' },
    ...TIEMPO_COMIDA_OPTIONS,
  ]

  const getTipoBadge = (tipo) => {
    return getTiempoComidaColor(tipo)
  }

  const getTipoLabel = (tipo) => {
    return getTiempoComidaLabel(tipo)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Recetas</h1>
        <button
          onClick={() => {
            setRecetaEditando(null)
            setMostrarFormulario(true)
          }}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg"
        >
          <Plus size={20} />
          Nueva Receta
        </button>
      </div>

      {/* Filtros */}
      <div className="mb-6 flex items-center gap-4">
        <Filter className="text-slate-400" size={20} />
        <div className="flex gap-2">
          {tiposReceta.map(tipo => (
            <button
              key={tipo.value}
              onClick={() => setTipoFiltro(tipo.value)}
              className={`px-4 py-2 rounded-lg text-sm transition-all ${
                tipoFiltro === tipo.value
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {tipo.label}
            </button>
          ))}
        </div>
      </div>

      {/* Lista de recetas */}
      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-slate-400">Cargando recetas...</p>
        </div>
      ) : !recetas || recetas.length === 0 ? (
        <div className="text-center py-12 border border-slate-600 rounded-lg bg-slate-800">
          <ChefHat className="mx-auto text-slate-600 mb-4" size={48} />
          <p className="text-slate-400 mb-2">No hay recetas {tipoFiltro ? `de ${getTipoLabel(tipoFiltro)}` : ''}</p>
          <button
            onClick={() => {
              setRecetaEditando(null)
              setMostrarFormulario(true)
            }}
            className="text-purple-400 hover:text-purple-300 underline"
          >
            Crear la primera receta
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recetas.map((receta) => (
            <div
              key={receta.id}
              className="bg-slate-800 p-6 rounded-lg border border-slate-700 hover:border-purple-500/50 transition-all relative"
            >
              {/* Header con icono, etiquetas y botones de acción */}
              <div className="flex items-start justify-between mb-3">
                <ChefHat className="text-purple-500" size={28} />
                
                {/* Contenedor para etiquetas y botones - organizados verticalmente */}
                <div className="flex flex-col items-end gap-2">
                  {/* Etiquetas de tipo y estado */}
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium border ${getTipoBadge(receta.tipo)}`}>
                      {getTipoLabel(receta.tipo)}
                    </span>
                    {!receta.activa && (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-slate-700 text-slate-400 border border-slate-600">
                        Inactiva
                      </span>
                    )}
                  </div>
                  
                  {/* Botones de acción */}
                  <div className="flex gap-2">
                    <button
                      onClick={(e) => handleToggleActiva(e, receta)}
                      className={`p-2 rounded transition-colors ${
                        receta.activa
                          ? 'bg-green-600/20 text-green-400 hover:bg-green-600/30'
                          : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                      }`}
                      title={receta.activa ? 'Desactivar receta' : 'Activar receta'}
                    >
                      {receta.activa ? <Power size={16} /> : <PowerOff size={16} />}
                    </button>
                    <button
                      onClick={(e) => handleEditar(e, receta)}
                      className="p-2 rounded bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 transition-colors"
                      title="Editar receta"
                    >
                      <Edit size={16} />
                    </button>
                    <button
                      onClick={(e) => handleEliminar(e, receta)}
                      className="p-2 rounded bg-red-600/20 text-red-400 hover:bg-red-600/30 transition-colors"
                      title="Eliminar receta"
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </div>

              <div 
                className="cursor-pointer"
                onClick={() => {
                  setRecetaEditando(receta)
                  setMostrarFormulario(true)
                }}
              >
              
              <h3 className="text-xl font-bold mb-2">{receta.nombre}</h3>
              {receta.descripcion && (
                <p className="text-slate-400 text-sm mb-4 line-clamp-2">{receta.descripcion}</p>
              )}
              
              <div className="space-y-2 text-sm border-t border-slate-700 pt-3">
                <div className="flex justify-between">
                  <span className="text-slate-400">Porciones:</span>
                  <span className="text-white font-medium">{receta.porciones}</span>
                </div>
                {receta.porcion_gramos && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">Peso total:</span>
                    <span className="text-white font-medium">{receta.porcion_gramos.toFixed(0)} g</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-slate-400">Costo/porción:</span>
                  <span className="text-green-400 font-bold">
                    ${receta.costo_por_porcion?.toFixed(2) || '0.00'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Calorías/porción:</span>
                  <span className="text-orange-400 font-bold">
                    {receta.calorias_por_porcion?.toFixed(0) || '0'} kcal
                  </span>
                </div>
                {receta.tiempo_preparacion && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">Tiempo:</span>
                    <span className="text-white">{receta.tiempo_preparacion} min</span>
                  </div>
                )}
              </div>

              {receta.ingredientes && receta.ingredientes.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-700">
                  <p className="text-xs text-slate-500">
                    {receta.ingredientes.length} ingrediente{receta.ingredientes.length !== 1 ? 's' : ''}
                  </p>
                </div>
              )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal de formulario */}
      <Modal
        isOpen={mostrarFormulario}
        title={recetaEditando ? 'Editar Receta' : 'Nueva Receta'}
        onClose={() => {
          setMostrarFormulario(false)
          setRecetaEditando(null)
        }}
      >
        <RecetaForm
          receta={recetaEditando}
          onClose={() => {
            setMostrarFormulario(false)
            setRecetaEditando(null)
          }}
          onSuccess={() => {
            setMostrarFormulario(false)
            setRecetaEditando(null)
          }}
        />
      </Modal>
    </div>
  )
}
