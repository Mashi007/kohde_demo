import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api, { extractData } from '../config/api'
import { DollarSign, RefreshCw, Search, Filter, Package, ChefHat } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Costos() {
  const [seccionActiva, setSeccionActiva] = useState('items') // 'items' o 'recetas'
  
  // Estados para filtros de items
  const [busquedaItems, setBusquedaItems] = useState('')
  const [filtroLabel, setFiltroLabel] = useState('')
  const [filtroCategoria, setFiltroCategoria] = useState('')
  
  // Estados para filtros de recetas
  const [busquedaRecetas, setBusquedaRecetas] = useState('')
  const [filtroTipoReceta, setFiltroTipoReceta] = useState('')
  
  const queryClient = useQueryClient()

  // Cargar costos de items
  const { data: costosItems, isLoading: isLoadingItems } = useQuery({
    queryKey: ['costos', filtroLabel, filtroCategoria],
    queryFn: () => {
      const params = {}
      if (filtroLabel) params.label_id = filtroLabel
      if (filtroCategoria) params.categoria = filtroCategoria
      return api.get('/logistica/costos', { params }).then(res => res.data)
    },
  })

  // Cargar costos de recetas
  const { data: costosRecetasResponse, isLoading: isLoadingRecetas } = useQuery({
    queryKey: ['costos-recetas', filtroTipoReceta],
    queryFn: () => {
      const params = {}
      if (filtroTipoReceta) params.tipo = filtroTipoReceta
      return api.get('/logistica/costos/recetas', { params }).then(extractData)
    },
  })

  // Asegurar que costosRecetas sea un array
  const costosRecetas = Array.isArray(costosRecetasResponse) ? costosRecetasResponse : []

  // Cargar labels para filtro
  const { data: labels } = useQuery({
    queryKey: ['labels'],
    queryFn: () => api.get('/logistica/labels').then(res => res.data),
  })

  // Mutación para recalcular todos
  const recalcularTodosMutation = useMutation({
    mutationFn: () => api.post('/logistica/costos/recalcular-todos'),
    onSuccess: (data) => {
      const stats = data.data.estadisticas
      const mensaje = `Recálculo completado: ${stats.items?.calculados || 0} items y ${stats.recetas?.calculadas || 0} recetas actualizadas`
      toast.success(mensaje)
      queryClient.invalidateQueries(['costos'])
      queryClient.invalidateQueries(['costos-recetas'])
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al recalcular costos')
    },
  })

  // Filtrar costos de items por búsqueda
  const costosItemsFiltrados = costosItems?.filter(costo => {
    if (!busquedaItems) return true
    const busquedaLower = busquedaItems.toLowerCase()
    return (
      costo.item?.nombre?.toLowerCase().includes(busquedaLower) ||
      costo.item?.codigo?.toLowerCase().includes(busquedaLower)
    )
  }) || []

  // Filtrar costos de recetas por búsqueda
  const costosRecetasFiltrados = costosRecetas?.filter(receta => {
    if (!busquedaRecetas) return true
    const busquedaLower = busquedaRecetas.toLowerCase()
    return receta.nombre?.toLowerCase().includes(busquedaLower)
  }) || []

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <DollarSign size={32} />
          Costos Estandarizados
        </h1>
        <button
          onClick={() => recalcularTodosMutation.mutate()}
          disabled={recalcularTodosMutation.isPending}
          className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50"
        >
          <RefreshCw size={20} className={recalcularTodosMutation.isPending ? 'animate-spin' : ''} />
          Recalcular Todos
        </button>
      </div>

      {/* Tabs para cambiar entre Items y Recetas */}
      <div className="mb-6 flex gap-2 border-b border-slate-700">
        <button
          onClick={() => setSeccionActiva('items')}
          className={`px-6 py-3 font-medium flex items-center gap-2 border-b-2 transition-colors ${
            seccionActiva === 'items'
              ? 'border-purple-500 text-purple-400'
              : 'border-transparent text-slate-400 hover:text-slate-300'
          }`}
        >
          <Package size={20} />
          Costos de Items
        </button>
        <button
          onClick={() => setSeccionActiva('recetas')}
          className={`px-6 py-3 font-medium flex items-center gap-2 border-b-2 transition-colors ${
            seccionActiva === 'recetas'
              ? 'border-purple-500 text-purple-400'
              : 'border-transparent text-slate-400 hover:text-slate-300'
          }`}
        >
          <ChefHat size={20} />
          Costos de Recetas
        </button>
      </div>

      {/* SECCIÓN DE ITEMS */}
      {seccionActiva === 'items' && (
        <>
          {/* Filtros y búsqueda para items */}
          <div className="mb-6 space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
              <input
                type="text"
                value={busquedaItems}
                onChange={(e) => setBusquedaItems(e.target.value)}
                placeholder="Buscar por nombre o código de item..."
                className="w-full pl-10 pr-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                  <Filter size={16} />
                  Filtrar por Clasificación
                </label>
                <select
                  value={filtroLabel}
                  onChange={(e) => setFiltroLabel(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
                >
                  <option value="">Todas las clasificaciones</option>
                  {labels?.map(label => (
                    <option key={label.id} value={label.id}>
                      {label.nombre_es}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                  <Filter size={16} />
                  Filtrar por Categoría
                </label>
                <select
                  value={filtroCategoria}
                  onChange={(e) => setFiltroCategoria(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
                >
                  <option value="">Todas las categorías</option>
                  <option value="materia_prima">Materia Prima</option>
                  <option value="insumo">Insumo</option>
                  <option value="producto_terminado">Producto Terminado</option>
                  <option value="bebida">Bebida</option>
                  <option value="limpieza">Limpieza</option>
                  <option value="otros">Otros</option>
                </select>
              </div>
            </div>
          </div>

          {/* Tabla de costos de items */}
          <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
            {isLoadingItems ? (
              <div className="p-8 text-center text-slate-400">
                <p>Cargando costos de items...</p>
              </div>
            ) : costosItemsFiltrados.length === 0 ? (
              <div className="p-8 text-center">
                <p className="text-slate-400 mb-2">
                  {busquedaItems || filtroLabel || filtroCategoria
                    ? 'No se encontraron costos con los filtros aplicados'
                    : 'No hay costos estandarizados calculados'}
                </p>
                <p className="text-xs text-slate-500">
                  {!busquedaItems && !filtroLabel && !filtroCategoria && (
                    'Haz clic en "Recalcular Todos" para calcular los costos basados en las últimas 3 facturas aprobadas'
                  )}
                </p>
              </div>
            ) : (
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="px-6 py-3 text-left">Item</th>
                    <th className="px-6 py-3 text-left">Código</th>
                    <th className="px-6 py-3 text-left">Unidad Estandarizada</th>
                    <th className="px-6 py-3 text-left">Costo Promedio</th>
                    <th className="px-6 py-3 text-left">Variación</th>
                    <th className="px-6 py-3 text-left">Facturas</th>
                    <th className="px-6 py-3 text-left">Última Actualización</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {costosItemsFiltrados.map((costo) => (
                    <tr key={costo.id} className="hover:bg-slate-700/50">
                      <td className="px-6 py-4">
                        <span className="font-medium">{costo.item?.nombre || 'N/A'}</span>
                        {costo.item?.labels && costo.item.labels.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-1">
                            {costo.item.labels.slice(0, 2).map(label => (
                              <span
                                key={label.id}
                                className="px-2 py-0.5 bg-purple-600/20 text-purple-300 rounded text-xs border border-purple-500/50"
                              >
                                {label.nombre_es}
                              </span>
                            ))}
                            {costo.item.labels.length > 2 && (
                              <span className="px-2 py-0.5 text-slate-400 text-xs">
                                +{costo.item.labels.length - 2}
                              </span>
                            )}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-slate-400">{costo.item?.codigo || 'N/A'}</td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 bg-slate-700 rounded text-sm">
                          {costo.unidad_estandar}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-2xl font-bold text-purple-400">
                          ${costo.costo_unitario_promedio.toFixed(2)}
                        </span>
                        <span className="text-sm text-slate-400 ml-1">
                          /{costo.unidad_estandar}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {costo.variacion_porcentaje !== null && costo.variacion_porcentaje !== undefined ? (
                          <div>
                            <span className={`font-semibold ${
                              costo.variacion_porcentaje < 5 ? 'text-green-400' :
                              costo.variacion_porcentaje < 15 ? 'text-yellow-400' :
                              'text-red-400'
                            }`}>
                              {costo.variacion_porcentaje.toFixed(1)}%
                            </span>
                            {costo.variacion_absoluta !== null && (
                              <div className="text-xs text-slate-400 mt-1">
                                ±${costo.variacion_absoluta.toFixed(2)}
                              </div>
                            )}
                          </div>
                        ) : (
                          <span className="text-slate-500 text-sm">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-slate-300">{costo.cantidad_facturas_usadas}</span>
                        <span className="text-xs text-slate-500 ml-1">facturas</span>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-400">
                        {costo.fecha_actualizacion
                          ? new Date(costo.fecha_actualizacion).toLocaleDateString('es-ES')
                          : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Resumen de items */}
          {costosItemsFiltrados.length > 0 && (
            <div className="mt-4 p-4 bg-slate-800 rounded-lg border border-slate-700">
              <p className="text-sm text-slate-400">
                Mostrando <span className="text-purple-400 font-medium">{costosItemsFiltrados.length}</span> de{' '}
                <span className="text-purple-400 font-medium">{costosItems?.length || 0}</span> costos de items
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Los costos se calculan basándose en el promedio de las últimas 3 facturas aprobadas
              </p>
            </div>
          )}
        </>
      )}

      {/* SECCIÓN DE RECETAS */}
      {seccionActiva === 'recetas' && (
        <>
          {/* Filtros y búsqueda para recetas */}
          <div className="mb-6 space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
              <input
                type="text"
                value={busquedaRecetas}
                onChange={(e) => setBusquedaRecetas(e.target.value)}
                placeholder="Buscar por nombre de receta..."
                className="w-full pl-10 pr-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 flex items-center gap-2">
                <Filter size={16} />
                Filtrar por Tipo
              </label>
              <select
                value={filtroTipoReceta}
                onChange={(e) => setFiltroTipoReceta(e.target.value)}
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              >
                <option value="">Todos los tipos</option>
                {TIEMPO_COMIDA_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Tabla de costos de recetas */}
          <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
            {isLoadingRecetas ? (
              <div className="p-8 text-center text-slate-400">
                <p>Cargando costos de recetas...</p>
              </div>
            ) : costosRecetasFiltrados.length === 0 ? (
              <div className="p-8 text-center">
                <p className="text-slate-400 mb-2">
                  {busquedaRecetas || filtroTipoReceta
                    ? 'No se encontraron recetas con los filtros aplicados'
                    : 'No hay recetas con costos calculados'}
                </p>
                <p className="text-xs text-slate-500">
                  {!busquedaRecetas && !filtroTipoReceta && (
                    'Los costos de recetas se actualizan automáticamente cuando cambian los costos de los items'
                  )}
                </p>
              </div>
            ) : (
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="px-6 py-3 text-left">Receta</th>
                    <th className="px-6 py-3 text-left">Tipo</th>
                    <th className="px-6 py-3 text-left">Porciones</th>
                    <th className="px-6 py-3 text-left">Costo Total</th>
                    <th className="px-6 py-3 text-left">Costo por Porción</th>
                    <th className="px-6 py-3 text-left">Ingredientes</th>
                    <th className="px-6 py-3 text-left">Peso Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {costosRecetasFiltrados.map((receta) => {
                    const costoInfo = receta.costo_info || {}
                    const tipoLabels = {
                      [TIEMPO_COMIDA_VALUES.DESAYUNO]: { label: getTiempoComidaLabel(TIEMPO_COMIDA_VALUES.DESAYUNO), color: getTiempoComidaColor(TIEMPO_COMIDA_VALUES.DESAYUNO) },
                      [TIEMPO_COMIDA_VALUES.ALMUERZO]: { label: getTiempoComidaLabel(TIEMPO_COMIDA_VALUES.ALMUERZO), color: getTiempoComidaColor(TIEMPO_COMIDA_VALUES.ALMUERZO) },
                      [TIEMPO_COMIDA_VALUES.CENA]: { label: getTiempoComidaLabel(TIEMPO_COMIDA_VALUES.CENA), color: getTiempoComidaColor(TIEMPO_COMIDA_VALUES.CENA) }
                    }
                    const tipoInfo = tipoLabels[receta.tipo?.toLowerCase()] || { label: getTiempoComidaLabel(receta.tipo) || 'N/A', color: 'bg-slate-600/20 text-slate-300 border-slate-500/50' }
                    
                    return (
                      <tr key={receta.id} className="hover:bg-slate-700/50">
                        <td className="px-6 py-4">
                          <span className="font-medium">{receta.nombre || 'N/A'}</span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded text-xs border ${tipoInfo.color}`}>
                            {tipoInfo.label}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-slate-300">
                          {receta.porciones || 0}
                        </td>
                        <td className="px-6 py-4">
                          {costoInfo.costo_total !== null && costoInfo.costo_total !== undefined ? (
                            <>
                              <span className="text-2xl font-bold text-purple-400">
                                ${costoInfo.costo_total.toFixed(2)}
                              </span>
                              <span className="text-xs text-slate-400 ml-1">total</span>
                            </>
                          ) : (
                            <span className="text-slate-500 text-sm">Sin costo</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {costoInfo.costo_por_porcion !== null && costoInfo.costo_por_porcion !== undefined ? (
                            <>
                              <span className="text-xl font-semibold text-green-400">
                                ${costoInfo.costo_por_porcion.toFixed(2)}
                              </span>
                              <span className="text-xs text-slate-400 ml-1">/porción</span>
                            </>
                          ) : (
                            <span className="text-slate-500 text-sm">-</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-slate-300">
                            {costoInfo.ingredientes_con_costo || 0}
                          </span>
                          <span className="text-xs text-slate-500 ml-1">
                            / {costoInfo.total_ingredientes || 0} con costo
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-400">
                          {costoInfo.porcion_gramos ? (
                            <>
                              {costoInfo.porcion_gramos.toFixed(0)}g
                              <span className="text-xs text-slate-500 ml-1">total</span>
                            </>
                          ) : (
                            '-'
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            )}
          </div>

          {/* Resumen de recetas */}
          {costosRecetasFiltrados.length > 0 && (
            <div className="mt-4 p-4 bg-slate-800 rounded-lg border border-slate-700">
              <p className="text-sm text-slate-400">
                Mostrando <span className="text-purple-400 font-medium">{costosRecetasFiltrados.length}</span> de{' '}
                <span className="text-purple-400 font-medium">{costosRecetas?.length || 0}</span> recetas
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Los costos de recetas se actualizan automáticamente cuando cambian los costos de los items (promedio de últimas 3 facturas)
              </p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
