import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api, { extractData } from '../config/api'
import {
  Package,
  FileText,
  MessageSquare,
  AlertTriangle,
  DollarSign,
  TrendingUp,
  ShoppingCart,
  BarChart3,
  Calendar,
  RefreshCw
} from 'lucide-react'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  ComposedChart,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush,
  ReferenceLine,
  ReferenceArea,
  LabelList
} from 'recharts'
import LoadingSpinner from '../components/LoadingSpinner'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

const COLORS = {
  primary: '#8b5cf6',
  secondary: '#3b82f6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#06b6d4',
  purple: '#a855f7',
  blue: '#3b82f6',
  green: '#10b981',
  yellow: '#f59e0b',
  red: '#ef4444',
  cyan: '#06b6d4'
}

const CHART_COLORS = [
  COLORS.purple,
  COLORS.blue,
  COLORS.green,
  COLORS.yellow,
  COLORS.red,
  COLORS.cyan
]

export default function Dashboard() {
  const [fechaInicio, setFechaInicio] = useState(() => {
    const date = new Date()
    date.setDate(date.getDate() - 30)
    return date.toISOString().split('T')[0]
  })
  const [fechaFin, setFechaFin] = useState(() => {
    return new Date().toISOString().split('T')[0]
  })

  // Obtener KPIs
  const { data: kpisData, isLoading: kpisLoading, refetch: refetchKpis } = useQuery({
    queryKey: ['kpis', fechaInicio, fechaFin],
    queryFn: () => api.get(`/reportes/kpis?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`).then(extractData),
    staleTime: 30000,
  })

  // Obtener datos de gráficos
  const { data: facturasChart, isLoading: facturasChartLoading } = useQuery({
    queryKey: ['graficos-facturas', fechaInicio, fechaFin],
    queryFn: () => api.get(`/reportes/kpis/graficos?tipo=facturas&fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`).then(extractData),
    staleTime: 30000,
  })

  const { data: pedidosChart, isLoading: pedidosChartLoading } = useQuery({
    queryKey: ['graficos-pedidos', fechaInicio, fechaFin],
    queryFn: () => api.get(`/reportes/kpis/graficos?tipo=pedidos&fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`).then(extractData),
    staleTime: 30000,
  })

  const { data: ticketsChart, isLoading: ticketsChartLoading } = useQuery({
    queryKey: ['graficos-tickets', fechaInicio, fechaFin],
    queryFn: () => api.get(`/reportes/kpis/graficos?tipo=tickets&fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`).then(extractData),
    staleTime: 30000,
  })

  const { data: mermasChart, isLoading: mermasChartLoading } = useQuery({
    queryKey: ['graficos-mermas', fechaInicio, fechaFin],
    queryFn: () => api.get(`/reportes/kpis/graficos?tipo=mermas&fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`).then(extractData),
    staleTime: 30000,
  })

  // Comparación de charolas programadas vs servidas
  const { data: charolasComparacion, isLoading: charolasComparacionLoading } = useQuery({
    queryKey: ['charolas-comparacion', fechaInicio, fechaFin],
    queryFn: () => api.get(`/reportes/kpis/charolas-comparacion?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`).then(extractData),
    staleTime: 30000,
  })

  // Datos detallados de mermas
  const { data: mermasDetalle, isLoading: mermasDetalleLoading } = useQuery({
    queryKey: ['mermas-detalle', fechaInicio, fechaFin],
    queryFn: () => api.get(`/reportes/kpis/mermas-detalle?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`).then(extractData),
    staleTime: 30000,
  })

  // Costo por charola por servicio
  const { data: costoCharolaServicio, isLoading: costoCharolaServicioLoading } = useQuery({
    queryKey: ['costo-charola-servicio', fechaInicio, fechaFin],
    queryFn: () => api.get(`/reportes/kpis/costo-charola-servicio?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`).then(extractData),
    staleTime: 30000,
  })

  // Mermas por día con línea tolerable
  const [porcentajeTolerable, setPorcentajeTolerable] = useState(5.0)
  const { data: mermasTolerable, isLoading: mermasTolerableLoading } = useQuery({
    queryKey: ['mermas-tolerable', fechaInicio, fechaFin, porcentajeTolerable],
    queryFn: () => api.get(`/reportes/kpis/mermas-por-dia-tolerable?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}&porcentaje_tolerable=${porcentajeTolerable}`).then(extractData),
    staleTime: 30000,
  })

  // Mermas tendencia por categoría
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState('MATERIA_PRIMA')
  const { data: mermasTendenciaCategoria, isLoading: mermasTendenciaCategoriaLoading } = useQuery({
    queryKey: ['mermas-tendencia-categoria', fechaInicio, fechaFin, categoriaSeleccionada],
    queryFn: () => api.get(`/reportes/kpis/mermas-tendencia-categoria?categoria=${categoriaSeleccionada}&fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`).then(extractData),
    staleTime: 30000,
  })

  // Datos legacy para compatibilidad
  const { data: stockBajoResponse } = useQuery({
    queryKey: ['stock-bajo'],
    queryFn: () => api.get('/logistica/inventario/stock-bajo').then(extractData),
  })

  const stockBajo = Array.isArray(stockBajoResponse) ? stockBajoResponse : []
  const kpis = kpisData || {}

  // Formatear datos para gráficos
  const facturasSeries = facturasChart?.series || []
  const pedidosSeries = pedidosChart?.series || []
  const ticketsSeries = ticketsChart?.series || []
  const mermasSeries = mermasChart?.series || []
  const charolasComparacionSeries = charolasComparacion?.series || []
  const charolasEstadisticas = charolasComparacion?.estadisticas || {}
  const mermasDetalleSeries = mermasDetalle?.series || []
  const mermasDetalleEstadisticas = mermasDetalle?.estadisticas || {}
  const mermasPorTipoDetalle = mermasDetalle?.por_tipo || []
  const costoCharolaSeries = costoCharolaServicio?.series || []
  const costoCharolaEstadisticas = costoCharolaServicio?.estadisticas || {}
  const mermasTolerableSeries = mermasTolerable?.series || []
  const mermasTolerableEstadisticas = mermasTolerable?.estadisticas || {}
  const mermasTendenciaCategoriaSeries = mermasTendenciaCategoria?.series || []
  const mermasTendenciaCategoriaEstadisticas = mermasTendenciaCategoria?.estadisticas || {}
  const categoriaActual = mermasTendenciaCategoria?.categoria || categoriaSeleccionada

  // Categorías disponibles
  const categoriasAlimentos = [
    { value: 'MATERIA_PRIMA', label: 'Materia Prima' },
    { value: 'INSUMO', label: 'Insumo' },
    { value: 'PRODUCTO_TERMINADO', label: 'Producto Terminado' },
    { value: 'BEBIDA', label: 'Bebida' },
    { value: 'LIMPIEZA', label: 'Limpieza' },
    { value: 'OTROS', label: 'Otros' }
  ]

  // Datos para gráficos de donut
  const facturasPorEstado = facturasChart?.por_estado || []
  const pedidosPorEstado = pedidosChart?.por_estado || []
  const ticketsPorEstado = ticketsChart?.por_estado || []
  const mermasPorTipo = mermasChart?.por_tipo || []

  const handleRefresh = () => {
    refetchKpis()
  }

  // Tooltip profesional mejorado
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-slate-600 rounded-xl p-4 shadow-2xl backdrop-blur-sm min-w-[200px]">
          <div className="border-b border-slate-600 pb-2 mb-3">
            <p className="text-slate-200 font-bold text-sm">
              {label ? format(new Date(label), 'EEEE, dd MMM yyyy', { locale: es }) : ''}
            </p>
          </div>
          <div className="space-y-2">
            {payload.map((entry, index) => (
              <div key={index} className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full shadow-sm" 
                    style={{ backgroundColor: entry.color }}
                  />
                  <span className="text-xs text-slate-400 uppercase tracking-wide">
                    {entry.name}
                  </span>
                </div>
                <span className="text-sm font-bold text-slate-200" style={{ color: entry.color }}>
                  {typeof entry.value === 'number' 
                    ? entry.value.toLocaleString('es-ES', { 
                        minimumFractionDigits: entry.value % 1 !== 0 ? 2 : 0,
                        maximumFractionDigits: 2
                      })
                    : entry.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      )
    }
    return null
  }

  // Tooltip avanzado para gráficos con múltiples métricas
  const AdvancedTooltip = ({ active, payload, label, formatters = {} }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gradient-to-br from-slate-800 via-slate-800 to-slate-900 border-2 border-slate-600 rounded-xl p-5 shadow-2xl backdrop-blur-md min-w-[240px] transform transition-all duration-200">
          <div className="border-b-2 border-slate-600 pb-3 mb-3">
            <p className="text-slate-100 font-bold text-base">
              {label ? format(new Date(label), 'EEEE, dd MMM yyyy', { locale: es }) : ''}
            </p>
            {label && (
              <p className="text-xs text-slate-400 mt-1">
                {format(new Date(label), 'HH:mm', { locale: es })}
              </p>
            )}
          </div>
          <div className="space-y-2.5">
            {payload.map((entry, index) => {
              const formatter = formatters[entry.dataKey] || ((val) => val)
              const displayValue = typeof entry.value === 'number' 
                ? formatter(entry.value)
                : entry.value
              
              return (
                <div 
                  key={index} 
                  className="flex items-center justify-between gap-4 p-2 rounded-lg bg-slate-700/30 hover:bg-slate-700/50 transition-colors"
                >
                  <div className="flex items-center gap-2.5">
                    <div 
                      className="w-3.5 h-3.5 rounded-full shadow-lg border-2 border-slate-600" 
                      style={{ backgroundColor: entry.color }}
                    />
                    <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                      {entry.name || entry.dataKey}
                    </span>
                  </div>
                  <span 
                    className="text-base font-bold" 
                    style={{ color: entry.color }}
                  >
                    {displayValue}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )
    }
    return null
  }

  if (kpisLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header con filtros */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-slate-400 mt-1">Vista general de KPIs y métricas del sistema</p>
        </div>
        <div className="flex gap-3 items-center">
          <div className="flex gap-2">
            <input
              type="date"
              value={fechaInicio}
              onChange={(e) => setFechaInicio(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <input
              type="date"
              value={fechaFin}
              onChange={(e) => setFechaFin(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <button
            onClick={handleRefresh}
            className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
          >
            <RefreshCw size={18} />
            <span className="hidden sm:inline">Actualizar</span>
          </button>
        </div>
      </div>

      {/* Cards de KPIs principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Facturas */}
        <div className="bg-gradient-to-br from-purple-600/20 to-purple-800/20 p-6 rounded-xl border border-purple-500/30 backdrop-blur-sm hover:border-purple-500/50 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-purple-600/20 p-3 rounded-lg">
              <FileText className="text-purple-400" size={24} />
            </div>
            <TrendingUp className="text-purple-400" size={20} />
          </div>
          <p className="text-slate-400 text-sm mb-1">Facturas Aprobadas</p>
          <p className="text-3xl font-bold mb-1">{kpis.facturas?.aprobadas || 0}</p>
          <p className="text-xs text-slate-500">
            Total: ${(kpis.facturas?.total_facturado || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
          </p>
        </div>

        {/* Pedidos */}
        <div className="bg-gradient-to-br from-blue-600/20 to-blue-800/20 p-6 rounded-xl border border-blue-500/30 backdrop-blur-sm hover:border-blue-500/50 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-blue-600/20 p-3 rounded-lg">
              <ShoppingCart className="text-blue-400" size={24} />
            </div>
            <TrendingUp className="text-blue-400" size={20} />
          </div>
          <p className="text-slate-400 text-sm mb-1">Pedidos Totales</p>
          <p className="text-3xl font-bold mb-1">{kpis.pedidos?.totales || 0}</p>
          <p className="text-xs text-slate-500">
            Pendientes: {kpis.pedidos?.pendientes || 0}
          </p>
        </div>

        {/* Tickets */}
        <div className="bg-gradient-to-br from-green-600/20 to-green-800/20 p-6 rounded-xl border border-green-500/30 backdrop-blur-sm hover:border-green-500/50 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-green-600/20 p-3 rounded-lg">
              <MessageSquare className="text-green-400" size={24} />
            </div>
            <BarChart3 className="text-green-400" size={20} />
          </div>
          <p className="text-slate-400 text-sm mb-1">Tickets Abiertos</p>
          <p className="text-3xl font-bold mb-1">{kpis.tickets?.abiertos || 0}</p>
          <p className="text-xs text-slate-500">
            Resueltos: {kpis.tickets?.resueltos || 0}
          </p>
        </div>

        {/* Inventario */}
        <div className="bg-gradient-to-br from-yellow-600/20 to-yellow-800/20 p-6 rounded-xl border border-yellow-500/30 backdrop-blur-sm hover:border-yellow-500/50 transition-all">
          <div className="flex items-center justify-between mb-4">
            <div className="bg-yellow-600/20 p-3 rounded-lg">
              <AlertTriangle className="text-yellow-400" size={24} />
            </div>
            <Package className="text-yellow-400" size={20} />
          </div>
          <p className="text-slate-400 text-sm mb-1">Stock Bajo</p>
          <p className="text-3xl font-bold mb-1">{kpis.inventario?.items_stock_bajo || 0}</p>
          <p className="text-xs text-slate-500">Items críticos</p>
        </div>
      </div>

      {/* Gráfico Comparativo de Charolas - PRIMERO Y DESTACADO */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 p-6 rounded-xl border border-slate-700 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-3 mb-2">
              <Calendar size={28} className="text-cyan-400" />
              Charolas Programadas vs Servidas
            </h2>
            {charolasEstadisticas.eficiencia_promedio && (
              <p className="text-slate-400 text-sm">
                Eficiencia promedio: <span className="font-bold text-cyan-400">{charolasEstadisticas.eficiencia_promedio}%</span>
                {' | '}
                Total Programadas: <span className="font-semibold">{charolasEstadisticas.total_programadas || 0}</span>
                {' | '}
                Total Servidas: <span className="font-semibold">{charolasEstadisticas.total_servidas || 0}</span>
              </p>
            )}
          </div>
        </div>
        {charolasComparacionLoading ? (
          <div className="h-96 flex items-center justify-center">
            <LoadingSpinner />
          </div>
        ) : charolasComparacionSeries.length > 0 ? (
          <ResponsiveContainer width="100%" height={450}>
            <ComposedChart 
              data={charolasComparacionSeries}
              margin={{ top: 20, right: 30, left: 20, bottom: 80 }}
            >
              <defs>
                <linearGradient id="colorProgramadas" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.blue} stopOpacity={0.9} />
                  <stop offset="50%" stopColor={COLORS.blue} stopOpacity={0.6} />
                  <stop offset="95%" stopColor={COLORS.blue} stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id="colorServidas" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.green} stopOpacity={0.9} />
                  <stop offset="50%" stopColor={COLORS.green} stopOpacity={0.6} />
                  <stop offset="95%" stopColor={COLORS.green} stopOpacity={0.1} />
                </linearGradient>
                <filter id="areaShadow">
                  <feDropShadow dx="0" dy="3" stdDeviation="4" floodOpacity="0.25"/>
                </filter>
              </defs>
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="#374151" 
                opacity={0.2}
                vertical={false}
              />
              <XAxis
                dataKey="fecha"
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                tickLine={{ stroke: '#4b5563' }}
                axisLine={{ stroke: '#4b5563' }}
              />
              <YAxis 
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                tickLine={{ stroke: '#4b5563' }}
                axisLine={{ stroke: '#4b5563' }}
              />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const programadas = payload.find(p => p.dataKey === 'programadas')?.value || 0
                    const servidas = payload.find(p => p.dataKey === 'servidas')?.value || 0
                    const diferencia = programadas - servidas
                    const eficiencia = programadas > 0 ? ((servidas / programadas) * 100).toFixed(1) : 0
                    
                    return (
                      <div className="bg-gradient-to-br from-slate-800 via-slate-800 to-slate-900 border-2 border-slate-600 rounded-xl p-5 shadow-2xl backdrop-blur-md min-w-[260px]">
                        <div className="border-b-2 border-slate-600 pb-3 mb-3">
                          <p className="text-slate-100 font-bold text-base">
                            {label ? format(new Date(label), 'EEEE, dd MMM yyyy', { locale: es }) : ''}
                          </p>
                        </div>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between gap-4 p-2 rounded-lg bg-blue-500/10">
                            <div className="flex items-center gap-2.5">
                              <div className="w-3.5 h-3.5 rounded-full bg-blue-500 shadow-lg" />
                              <span className="text-sm font-semibold text-slate-300">Programadas</span>
                            </div>
                            <span className="text-lg font-bold text-blue-400">{programadas}</span>
                          </div>
                          <div className="flex items-center justify-between gap-4 p-2 rounded-lg bg-green-500/10">
                            <div className="flex items-center gap-2.5">
                              <div className="w-3.5 h-3.5 rounded-full bg-green-500 shadow-lg" />
                              <span className="text-sm font-semibold text-slate-300">Servidas</span>
                            </div>
                            <span className="text-lg font-bold text-green-400">{servidas}</span>
                          </div>
                          <div className="border-t-2 border-slate-600 pt-3 mt-3 space-y-2">
                            <div className="flex items-center justify-between gap-4">
                              <span className="text-xs text-slate-400 font-medium">Diferencia:</span>
                              <span className={`font-bold text-sm ${diferencia >= 0 ? 'text-yellow-400' : 'text-red-400'}`}>
                                {diferencia >= 0 ? '+' : ''}{diferencia}
                              </span>
                            </div>
                            <div className="flex items-center justify-between gap-4">
                              <span className="text-xs text-slate-400 font-medium">Eficiencia:</span>
                              <span className={`font-bold text-sm ${eficiencia >= 90 ? 'text-green-400' : eficiencia >= 80 ? 'text-yellow-400' : 'text-red-400'}`}>
                                {eficiencia}%
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  }
                  return null
                }}
                cursor={{ stroke: COLORS.blue, strokeWidth: 2, strokeDasharray: '5 5' }}
                animationDuration={200}
              />
              <Legend
                wrapperStyle={{ paddingTop: '30px', paddingBottom: '10px' }}
                iconType="circle"
                iconSize={12}
                formatter={(value) => (
                  <span className="text-slate-300 text-sm font-semibold">
                    {value === 'programadas' ? 'Programadas' : 'Servidas'}
                  </span>
                )}
              />
              <Area
                type="monotone"
                dataKey="programadas"
                stroke={COLORS.blue}
                strokeWidth={4}
                fillOpacity={1}
                fill="url(#colorProgramadas)"
                name="programadas"
                dot={{ fill: COLORS.blue, r: 5, strokeWidth: 2, stroke: '#fff' }}
                activeDot={{ r: 8, strokeWidth: 3, stroke: '#fff', fill: COLORS.blue }}
                animationDuration={1200}
                animationEasing="ease-out"
                filter="url(#areaShadow)"
              />
              <Area
                type="monotone"
                dataKey="servidas"
                stroke={COLORS.green}
                strokeWidth={4}
                fillOpacity={1}
                fill="url(#colorServidas)"
                name="servidas"
                dot={{ fill: COLORS.green, r: 5, strokeWidth: 2, stroke: '#fff' }}
                activeDot={{ r: 8, strokeWidth: 3, stroke: '#fff', fill: COLORS.green }}
                animationDuration={1200}
                animationEasing="ease-out"
                animationBegin={200}
                filter="url(#areaShadow)"
              />
              <ReferenceLine 
                y={charolasEstadisticas.total_programadas ? Math.round(charolasEstadisticas.total_programadas / (charolasComparacionSeries.length || 1)) : 0} 
                stroke={COLORS.blue} 
                strokeDasharray="5 5" 
                strokeOpacity={0.5}
                label={{ value: "Promedio Programadas", position: "right", fill: COLORS.blue, fontSize: 10 }}
              />
              <Brush 
                dataKey="fecha"
                height={40}
                stroke={COLORS.blue}
                fill="#1e293b"
                tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
              />
            </ComposedChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-96 flex items-center justify-center text-slate-400">
            No hay datos disponibles
          </div>
        )}
      </div>

      {/* Gráficos principales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de Facturas - Área */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <FileText size={24} className="text-purple-400" />
              Facturas Aprobadas
            </h2>
          </div>
          {facturasChartLoading ? (
            <div className="h-64 flex items-center justify-center">
              <LoadingSpinner />
            </div>
          ) : facturasSeries.length > 0 ? (
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart 
                data={facturasSeries}
                margin={{ top: 10, right: 20, left: 10, bottom: 60 }}
              >
                <defs>
                  <linearGradient id="colorFacturas" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.purple} stopOpacity={0.9} />
                    <stop offset="50%" stopColor={COLORS.purple} stopOpacity={0.5} />
                    <stop offset="95%" stopColor={COLORS.purple} stopOpacity={0.1} />
                  </linearGradient>
                  <filter id="shadow">
                    <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.3"/>
                  </filter>
                </defs>
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke="#374151" 
                  opacity={0.3}
                  vertical={false}
                />
                <XAxis
                  dataKey="fecha"
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                  tickLine={{ stroke: '#4b5563' }}
                  axisLine={{ stroke: '#4b5563' }}
                />
                <YAxis 
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                  tickLine={{ stroke: '#4b5563' }}
                  axisLine={{ stroke: '#4b5563' }}
                  tickFormatter={(value) => `$${value.toLocaleString('es-ES')}`}
                />
                <Tooltip 
                  content={<AdvancedTooltip formatters={{ total: (val) => `$${val.toLocaleString('es-ES', { minimumFractionDigits: 2 })}` }} />}
                  cursor={{ stroke: COLORS.purple, strokeWidth: 2, strokeDasharray: '5 5' }}
                  animationDuration={200}
                />
                <Area
                  type="monotone"
                  dataKey="total"
                  stroke={COLORS.purple}
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#colorFacturas)"
                  name="Total Facturado"
                  dot={{ fill: COLORS.purple, r: 4, strokeWidth: 2, stroke: '#fff' }}
                  activeDot={{ r: 7, strokeWidth: 2, stroke: '#fff', fill: COLORS.purple }}
                  animationDuration={1000}
                  animationEasing="ease-out"
                  filter="url(#shadow)"
                />
                <Brush 
                  dataKey="fecha"
                  height={30}
                  stroke={COLORS.purple}
                  fill="#1e293b"
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-400">
              No hay datos disponibles
            </div>
          )}
        </div>

        {/* Gráfico de Pedidos - Barras */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <ShoppingCart size={24} className="text-blue-400" />
              Pedidos por Día
            </h2>
          </div>
          {pedidosChartLoading ? (
            <div className="h-64 flex items-center justify-center">
              <LoadingSpinner />
            </div>
          ) : pedidosSeries.length > 0 ? (
            <ResponsiveContainer width="100%" height={350}>
              <BarChart 
                data={pedidosSeries}
                margin={{ top: 10, right: 20, left: 10, bottom: 60 }}
                barCategoryGap="15%"
              >
                <defs>
                  <linearGradient id="colorPedidosCantidad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={COLORS.blue} stopOpacity={1} />
                    <stop offset="100%" stopColor={COLORS.blue} stopOpacity={0.7} />
                  </linearGradient>
                  <linearGradient id="colorPedidosTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={COLORS.cyan} stopOpacity={1} />
                    <stop offset="100%" stopColor={COLORS.cyan} stopOpacity={0.7} />
                  </linearGradient>
                  <filter id="barShadow">
                    <feDropShadow dx="0" dy="2" stdDeviation="2" floodOpacity="0.2"/>
                  </filter>
                </defs>
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke="#374151" 
                  opacity={0.3}
                  vertical={false}
                />
                <XAxis
                  dataKey="fecha"
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                  tickLine={{ stroke: '#4b5563' }}
                  axisLine={{ stroke: '#4b5563' }}
                />
                <YAxis 
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                  tickLine={{ stroke: '#4b5563' }}
                  axisLine={{ stroke: '#4b5563' }}
                />
                <Tooltip 
                  content={<AdvancedTooltip formatters={{ 
                    cantidad: (val) => val.toLocaleString('es-ES'),
                    total: (val) => `$${val.toLocaleString('es-ES', { minimumFractionDigits: 2 })}`
                  }} />}
                  cursor={{ fill: 'rgba(59, 130, 246, 0.1)' }}
                  animationDuration={200}
                />
                <Bar 
                  dataKey="cantidad" 
                  fill="url(#colorPedidosCantidad)" 
                  name="Cantidad" 
                  radius={[8, 8, 0, 0]}
                  filter="url(#barShadow)"
                  animationDuration={1200}
                  animationEasing="ease-out"
                >
                  <LabelList 
                    dataKey="cantidad" 
                    position="top" 
                    fill="#3b82f6"
                    fontSize={10}
                    fontWeight="bold"
                  />
                </Bar>
                <Bar 
                  dataKey="total" 
                  fill="url(#colorPedidosTotal)" 
                  name="Total" 
                  radius={[8, 8, 0, 0]}
                  filter="url(#barShadow)"
                  animationDuration={1200}
                  animationEasing="ease-out"
                  animationBegin={200}
                >
                  <LabelList 
                    dataKey="total" 
                    position="top" 
                    fill="#06b6d4"
                    fontSize={10}
                    fontWeight="bold"
                    formatter={(value) => `$${value.toFixed(0)}`}
                  />
                </Bar>
                <Brush 
                  dataKey="fecha"
                  height={30}
                  stroke={COLORS.blue}
                  fill="#1e293b"
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-400">
              No hay datos disponibles
            </div>
          )}
        </div>

        {/* Gráfico de Tickets - Líneas */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <MessageSquare size={24} className="text-green-400" />
              Tickets por Día
            </h2>
          </div>
          {ticketsChartLoading ? (
            <div className="h-64 flex items-center justify-center">
              <LoadingSpinner />
            </div>
          ) : ticketsSeries.length > 0 ? (
            <ResponsiveContainer width="100%" height={350}>
              <LineChart 
                data={ticketsSeries}
                margin={{ top: 10, right: 20, left: 10, bottom: 60 }}
              >
                <defs>
                  <linearGradient id="colorTickets" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor={COLORS.green} stopOpacity={1} />
                    <stop offset="100%" stopColor={COLORS.green} stopOpacity={0.6} />
                  </linearGradient>
                  <filter id="lineShadow">
                    <feDropShadow dx="0" dy="2" stdDeviation="2" floodOpacity="0.3"/>
                  </filter>
                </defs>
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke="#374151" 
                  opacity={0.3}
                  vertical={false}
                />
                <XAxis
                  dataKey="fecha"
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                  tickLine={{ stroke: '#4b5563' }}
                  axisLine={{ stroke: '#4b5563' }}
                />
                <YAxis 
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                  tickLine={{ stroke: '#4b5563' }}
                  axisLine={{ stroke: '#4b5563' }}
                />
                <Tooltip 
                  content={<AdvancedTooltip formatters={{ cantidad: (val) => val.toLocaleString('es-ES') }} />}
                  cursor={{ stroke: COLORS.green, strokeWidth: 2, strokeDasharray: '5 5' }}
                  animationDuration={200}
                />
                <Line
                  type="monotone"
                  dataKey="cantidad"
                  stroke="url(#colorTickets)"
                  strokeWidth={4}
                  dot={{ fill: COLORS.green, r: 5, strokeWidth: 2, stroke: '#fff' }}
                  activeDot={{ r: 8, strokeWidth: 3, stroke: '#fff', fill: COLORS.green }}
                  name="Tickets"
                  animationDuration={1000}
                  animationEasing="ease-out"
                  filter="url(#lineShadow)"
                />
                <Brush 
                  dataKey="fecha"
                  height={30}
                  stroke={COLORS.green}
                  fill="#1e293b"
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-400">
              No hay datos disponibles
            </div>
          )}
        </div>

        {/* Gráfico de Mermas - Área */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <AlertTriangle size={24} className="text-yellow-400" />
              Mermas por Día
            </h2>
          </div>
          {mermasChartLoading ? (
            <div className="h-64 flex items-center justify-center">
              <LoadingSpinner />
            </div>
          ) : mermasSeries.length > 0 ? (
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart 
                data={mermasSeries}
                margin={{ top: 10, right: 20, left: 10, bottom: 60 }}
              >
                <defs>
                  <linearGradient id="colorMermas" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.yellow} stopOpacity={0.9} />
                    <stop offset="50%" stopColor={COLORS.yellow} stopOpacity={0.5} />
                    <stop offset="95%" stopColor={COLORS.yellow} stopOpacity={0.1} />
                  </linearGradient>
                  <filter id="mermasShadowSimple">
                    <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.3"/>
                  </filter>
                </defs>
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke="#374151" 
                  opacity={0.3}
                  vertical={false}
                />
                <XAxis
                  dataKey="fecha"
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                  tickLine={{ stroke: '#4b5563' }}
                  axisLine={{ stroke: '#4b5563' }}
                />
                <YAxis 
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                  tickLine={{ stroke: '#4b5563' }}
                  axisLine={{ stroke: '#4b5563' }}
                  tickFormatter={(value) => `$${value.toFixed(0)}`}
                />
                <Tooltip 
                  content={<AdvancedTooltip formatters={{ total_costo: (val) => `$${val.toLocaleString('es-ES', { minimumFractionDigits: 2 })}` }} />}
                  cursor={{ stroke: COLORS.yellow, strokeWidth: 2, strokeDasharray: '5 5' }}
                  animationDuration={200}
                />
                <Area
                  type="monotone"
                  dataKey="total_costo"
                  stroke={COLORS.yellow}
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#colorMermas)"
                  name="Costo Total"
                  dot={{ fill: COLORS.yellow, r: 4, strokeWidth: 2, stroke: '#fff' }}
                  activeDot={{ r: 7, strokeWidth: 2, stroke: '#fff', fill: COLORS.yellow }}
                  animationDuration={1000}
                  animationEasing="ease-out"
                  filter="url(#mermasShadowSimple)"
                />
                <Brush 
                  dataKey="fecha"
                  height={30}
                  stroke={COLORS.yellow}
                  fill="#1e293b"
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-400">
              No hay datos disponibles
            </div>
          )}
        </div>
      </div>

      {/* Gráfico de Mermas - Destacado */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 p-6 rounded-xl border border-slate-700 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-3 mb-2">
              <AlertTriangle size={28} className="text-yellow-400" />
              Análisis de Mermas
            </h2>
            {mermasDetalleEstadisticas.total_cantidad !== undefined && (
              <p className="text-slate-400 text-sm">
                Total Mermas: <span className="font-bold text-yellow-400">{mermasDetalleEstadisticas.total_cantidad || 0}</span>
                {' | '}
                Costo Total: <span className="font-semibold">${(mermasDetalleEstadisticas.total_costo || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</span>
                {' | '}
                Promedio Diario: <span className="font-semibold">{mermasDetalleEstadisticas.promedio_diario?.toFixed(1) || 0}</span>
                {mermasDetalleEstadisticas.dia_max_mermas && (
                  <>
                    {' | '}
                    Día Máximo: <span className="font-semibold text-red-400">{mermasDetalleEstadisticas.cantidad_max}</span>
                  </>
                )}
              </p>
            )}
          </div>
        </div>
        {mermasDetalleLoading ? (
          <div className="h-96 flex items-center justify-center">
            <LoadingSpinner />
          </div>
        ) : mermasDetalleSeries.length > 0 ? (
          <div className="space-y-6">
            {/* Gráfico principal: Cantidad y Costo */}
            <ResponsiveContainer width="100%" height={450}>
              <ComposedChart 
                data={mermasDetalleSeries}
                margin={{ top: 20, right: 30, left: 20, bottom: 80 }}
              >
                <defs>
                  <linearGradient id="colorMermasCantidad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.yellow} stopOpacity={0.9} />
                    <stop offset="50%" stopColor={COLORS.yellow} stopOpacity={0.6} />
                    <stop offset="95%" stopColor={COLORS.yellow} stopOpacity={0.1} />
                  </linearGradient>
                  <linearGradient id="colorMermasCosto" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.red} stopOpacity={0.9} />
                    <stop offset="50%" stopColor={COLORS.red} stopOpacity={0.6} />
                    <stop offset="95%" stopColor={COLORS.red} stopOpacity={0.1} />
                  </linearGradient>
                  <filter id="mermasShadow">
                    <feDropShadow dx="0" dy="3" stdDeviation="4" floodOpacity="0.25"/>
                  </filter>
                </defs>
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke="#374151" 
                  opacity={0.2}
                  vertical={false}
                />
                <XAxis
                  dataKey="fecha"
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                  tickLine={{ stroke: '#4b5563' }}
                  axisLine={{ stroke: '#4b5563' }}
                />
                <YAxis 
                  yAxisId="left" 
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                  tickLine={{ stroke: '#4b5563' }}
                  axisLine={{ stroke: '#4b5563' }}
                />
                <YAxis 
                  yAxisId="right" 
                  orientation="right" 
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                  tickLine={{ stroke: '#4b5563' }}
                  axisLine={{ stroke: '#4b5563' }}
                  tickFormatter={(value) => `$${value.toFixed(0)}`}
                />
                <Tooltip
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      const cantidad = payload.find(p => p.dataKey === 'cantidad')?.value || 0
                      const costo = payload.find(p => p.dataKey === 'total_costo')?.value || 0
                      const costo_unitario = cantidad > 0 ? (costo / cantidad).toFixed(2) : 0
                      
                      return (
                        <div className="bg-gradient-to-br from-slate-800 via-slate-800 to-slate-900 border-2 border-slate-600 rounded-xl p-5 shadow-2xl backdrop-blur-md min-w-[260px]">
                          <div className="border-b-2 border-slate-600 pb-3 mb-3">
                            <p className="text-slate-100 font-bold text-base">
                              {label ? format(new Date(label), 'EEEE, dd MMM yyyy', { locale: es }) : ''}
                            </p>
                          </div>
                          <div className="space-y-3">
                            <div className="flex items-center justify-between gap-4 p-2 rounded-lg bg-yellow-500/10">
                              <div className="flex items-center gap-2.5">
                                <div className="w-3.5 h-3.5 rounded-full bg-yellow-500 shadow-lg" />
                                <span className="text-sm font-semibold text-slate-300">Cantidad</span>
                              </div>
                              <span className="text-lg font-bold text-yellow-400">{cantidad}</span>
                            </div>
                            <div className="flex items-center justify-between gap-4 p-2 rounded-lg bg-red-500/10">
                              <div className="flex items-center gap-2.5">
                                <div className="w-3.5 h-3.5 rounded-full bg-red-500 shadow-lg" />
                                <span className="text-sm font-semibold text-slate-300">Costo Total</span>
                              </div>
                              <span className="text-lg font-bold text-red-400">
                                ${typeof costo === 'number' ? costo.toLocaleString('es-ES', { minimumFractionDigits: 2 }) : costo}
                              </span>
                            </div>
                            <div className="border-t-2 border-slate-600 pt-3 mt-3">
                              <div className="flex items-center justify-between gap-4">
                                <span className="text-xs text-slate-400 font-medium">Costo Unitario:</span>
                                <span className="font-bold text-sm text-cyan-400">${costo_unitario}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )
                    }
                    return null
                  }}
                  cursor={{ stroke: COLORS.yellow, strokeWidth: 2, strokeDasharray: '5 5' }}
                  animationDuration={200}
                />
                <Legend
                  wrapperStyle={{ paddingTop: '30px', paddingBottom: '10px' }}
                  iconType="circle"
                  iconSize={12}
                  formatter={(value) => (
                    <span className="text-slate-300 text-sm font-semibold">
                      {value === 'cantidad' ? 'Cantidad de Mermas' : 'Costo Total ($)'}
                    </span>
                  )}
                />
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey="cantidad"
                  stroke={COLORS.yellow}
                  strokeWidth={4}
                  fillOpacity={1}
                  fill="url(#colorMermasCantidad)"
                  name="cantidad"
                  dot={{ fill: COLORS.yellow, r: 5, strokeWidth: 2, stroke: '#fff' }}
                  activeDot={{ r: 8, strokeWidth: 3, stroke: '#fff', fill: COLORS.yellow }}
                  animationDuration={1200}
                  animationEasing="ease-out"
                  filter="url(#mermasShadow)"
                />
                <Area
                  yAxisId="right"
                  type="monotone"
                  dataKey="total_costo"
                  stroke={COLORS.red}
                  strokeWidth={4}
                  fillOpacity={1}
                  fill="url(#colorMermasCosto)"
                  name="total_costo"
                  dot={{ fill: COLORS.red, r: 5, strokeWidth: 2, stroke: '#fff' }}
                  activeDot={{ r: 8, strokeWidth: 3, stroke: '#fff', fill: COLORS.red }}
                  animationDuration={1200}
                  animationEasing="ease-out"
                  animationBegin={200}
                  filter="url(#mermasShadow)"
                />
                <Brush 
                  dataKey="fecha"
                  height={40}
                  stroke={COLORS.yellow}
                  fill="#1e293b"
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                />
              </ComposedChart>
            </ResponsiveContainer>

            {/* Gráfico de distribución por tipo */}
            {mermasPorTipoDetalle.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                  <h3 className="text-lg font-bold mb-4 text-slate-300">Mermas por Tipo (Cantidad)</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={mermasPorTipoDetalle}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ tipo, cantidad }) => `${tipo}: ${cantidad}`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="cantidad"
                      >
                        {mermasPorTipoDetalle.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                  <h3 className="text-lg font-bold mb-4 text-slate-300">Mermas por Tipo (Costo)</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={mermasPorTipoDetalle}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ tipo, total_costo }) => `${tipo}: $${total_costo.toFixed(0)}`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="total_costo"
                      >
                        {mermasPorTipoDetalle.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => `$${Number(value).toLocaleString('es-ES', { minimumFractionDigits: 2 })}`} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="h-96 flex items-center justify-center text-slate-400">
            No hay datos disponibles
          </div>
        )}
      </div>

      {/* Gráfico de Costo por Charola por Servicio - Destacado */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 p-6 rounded-xl border border-slate-700 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-3 mb-2">
              <DollarSign size={28} className="text-green-400" />
              Costo por Charola por Servicio
            </h2>
            {costoCharolaEstadisticas.costo_total_real !== undefined && (
              <p className="text-slate-400 text-sm">
                Costo Total Real: <span className="font-bold text-red-400">${(costoCharolaEstadisticas.costo_total_real || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</span>
                {' | '}
                Costo Total Ideal: <span className="font-semibold text-green-400">${(costoCharolaEstadisticas.costo_total_ideal || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</span>
                {' | '}
                Ahorro Potencial: <span className="font-semibold text-yellow-400">${(costoCharolaEstadisticas.ahorro_potencial || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</span>
                {' | '}
                Eficiencia: <span className="font-semibold text-cyan-400">{costoCharolaEstadisticas.eficiencia_promedio?.toFixed(1) || 0}%</span>
              </p>
            )}
          </div>
        </div>
        {costoCharolaServicioLoading ? (
          <div className="h-96 flex items-center justify-center">
            <LoadingSpinner />
          </div>
        ) : costoCharolaSeries.length > 0 ? (
          <div className="space-y-6">
            {/* Gráfico principal: Comparación Real vs Ideal */}
            <ResponsiveContainer width="100%" height={450}>
              <BarChart 
                data={costoCharolaSeries}
                margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
                barCategoryGap="20%"
              >
                <defs>
                  <linearGradient id="colorCostoReal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={COLORS.red} stopOpacity={1} />
                    <stop offset="100%" stopColor={COLORS.red} stopOpacity={0.7} />
                  </linearGradient>
                  <linearGradient id="colorCostoIdeal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={COLORS.green} stopOpacity={1} />
                    <stop offset="100%" stopColor={COLORS.green} stopOpacity={0.7} />
                  </linearGradient>
                  <filter id="barShadowCostos">
                    <feDropShadow dx="0" dy="3" stdDeviation="3" floodOpacity="0.3"/>
                  </filter>
                </defs>
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke="#374151" 
                  opacity={0.2}
                  vertical={false}
                />
                <XAxis
                  dataKey="tiempo_comida"
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af', fontSize: 12, fontWeight: 'bold' }}
                  tickFormatter={(value) => {
                    const labels = {
                      'desayuno': 'Desayuno',
                      'almuerzo': 'Almuerzo',
                      'cena': 'Cena'
                    }
                    return labels[value] || value
                  }}
                  tickLine={{ stroke: '#4b5563' }}
                  axisLine={{ stroke: '#4b5563', strokeWidth: 2 }}
                />
                <YAxis 
                  stroke="#9ca3af"
                  tick={{ fill: '#9ca3af', fontSize: 11 }}
                  tickLine={{ stroke: '#4b5563' }}
                  axisLine={{ stroke: '#4b5563' }}
                  tickFormatter={(value) => `$${value.toFixed(0)}`}
                />
                <Tooltip
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      const real = payload.find(p => p.dataKey === 'costo_promedio')?.value || 0
                      const ideal = payload.find(p => p.dataKey === 'costo_ideal')?.value || 0
                      const diferencia = real - ideal
                      const porcentaje_diferencia = ideal > 0 ? ((diferencia / ideal) * 100).toFixed(1) : 0
                      const cantidad = payload[0]?.payload?.cantidad_charolas || 0
                      const costo_por_persona = payload[0]?.payload?.costo_por_persona || 0
                      
                      return (
                        <div className="bg-gradient-to-br from-slate-800 via-slate-800 to-slate-900 border-2 border-slate-600 rounded-xl p-5 shadow-2xl backdrop-blur-md min-w-[280px]">
                          <div className="border-b-2 border-slate-600 pb-3 mb-3">
                            <p className="text-slate-100 font-bold text-base capitalize">
                              {label}
                            </p>
                          </div>
                          <div className="space-y-3">
                            <div className="flex items-center justify-between gap-4 p-2 rounded-lg bg-red-500/10">
                              <div className="flex items-center gap-2.5">
                                <div className="w-3.5 h-3.5 rounded-full bg-red-500 shadow-lg" />
                                <span className="text-sm font-semibold text-slate-300">Costo Real</span>
                              </div>
                              <span className="text-lg font-bold text-red-400">
                                ${typeof real === 'number' ? real.toLocaleString('es-ES', { minimumFractionDigits: 2 }) : real}
                              </span>
                            </div>
                            <div className="flex items-center justify-between gap-4 p-2 rounded-lg bg-green-500/10">
                              <div className="flex items-center gap-2.5">
                                <div className="w-3.5 h-3.5 rounded-full bg-green-500 shadow-lg" />
                                <span className="text-sm font-semibold text-slate-300">Costo Ideal</span>
                              </div>
                              <span className="text-lg font-bold text-green-400">
                                ${typeof ideal === 'number' ? ideal.toLocaleString('es-ES', { minimumFractionDigits: 2 }) : ideal}
                              </span>
                            </div>
                            <div className="border-t-2 border-slate-600 pt-3 mt-3 space-y-2">
                              <div className="flex items-center justify-between gap-4">
                                <span className="text-xs text-slate-400 font-medium">Diferencia:</span>
                                <span className={`font-bold text-sm ${diferencia >= 0 ? 'text-yellow-400' : 'text-green-400'}`}>
                                  {diferencia >= 0 ? '+' : ''}${diferencia.toFixed(2)} ({porcentaje_diferencia}%)
                                </span>
                              </div>
                              <div className="flex items-center justify-between gap-4">
                                <span className="text-xs text-slate-400 font-medium">Charolas:</span>
                                <span className="font-semibold text-sm text-slate-300">{cantidad}</span>
                              </div>
                              <div className="flex items-center justify-between gap-4">
                                <span className="text-xs text-slate-400 font-medium">Costo por Persona:</span>
                                <span className="font-bold text-sm text-cyan-400">${costo_por_persona.toFixed(2)}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )
                    }
                    return null
                  }}
                  cursor={{ fill: 'rgba(239, 68, 68, 0.1)' }}
                  animationDuration={200}
                />
                <Legend
                  wrapperStyle={{ paddingTop: '30px', paddingBottom: '10px' }}
                  iconType="square"
                  iconSize={14}
                  formatter={(value) => (
                    <span className="text-slate-300 text-sm font-semibold">
                      {value === 'costo_promedio' ? 'Costo Real' : 'Costo Ideal'}
                    </span>
                  )}
                />
                <Bar
                  dataKey="costo_promedio"
                  fill="url(#colorCostoReal)"
                  name="costo_promedio"
                  radius={[10, 10, 0, 0]}
                  filter="url(#barShadowCostos)"
                  animationDuration={1200}
                  animationEasing="ease-out"
                >
                  <LabelList 
                    dataKey="costo_promedio" 
                    position="top" 
                    fill="#ef4444"
                    fontSize={12}
                    fontWeight="bold"
                    formatter={(value) => `$${value.toFixed(0)}`}
                  />
                </Bar>
                <Bar
                  dataKey="costo_ideal"
                  fill="url(#colorCostoIdeal)"
                  name="costo_ideal"
                  radius={[10, 10, 0, 0]}
                  filter="url(#barShadowCostos)"
                  animationDuration={1200}
                  animationEasing="ease-out"
                  animationBegin={200}
                >
                  <LabelList 
                    dataKey="costo_ideal" 
                    position="top" 
                    fill="#10b981"
                    fontSize={12}
                    fontWeight="bold"
                    formatter={(value) => `$${value.toFixed(0)}`}
                  />
                </Bar>
              </BarChart>
            </ResponsiveContainer>

            {/* Tabla de detalles */}
            <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
              <h3 className="text-lg font-bold mb-4 text-slate-300">Detalles por Servicio</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left p-2 text-slate-400">Servicio</th>
                      <th className="text-right p-2 text-slate-400">Charolas</th>
                      <th className="text-right p-2 text-slate-400">Costo Real</th>
                      <th className="text-right p-2 text-slate-400">Costo Ideal</th>
                      <th className="text-right p-2 text-slate-400">Diferencia</th>
                      <th className="text-right p-2 text-slate-400">Costo/Persona</th>
                      <th className="text-right p-2 text-slate-400">Eficiencia</th>
                    </tr>
                  </thead>
                  <tbody>
                    {costoCharolaSeries.map((item, index) => {
                      const diferencia = item.costo_promedio - item.costo_ideal
                      const eficiencia = item.costo_ideal > 0 ? ((item.costo_ideal / item.costo_promedio) * 100).toFixed(1) : 0
                      const labels = {
                        'desayuno': 'Desayuno',
                        'almuerzo': 'Almuerzo',
                        'cena': 'Cena'
                      }
                      return (
                        <tr key={index} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                          <td className="p-2 font-semibold capitalize">{labels[item.tiempo_comida] || item.tiempo_comida}</td>
                          <td className="p-2 text-right">{item.cantidad_charolas}</td>
                          <td className="p-2 text-right text-red-400 font-semibold">${item.costo_promedio.toFixed(2)}</td>
                          <td className="p-2 text-right text-green-400 font-semibold">${item.costo_ideal.toFixed(2)}</td>
                          <td className={`p-2 text-right font-semibold ${diferencia >= 0 ? 'text-yellow-400' : 'text-green-400'}`}>
                            {diferencia >= 0 ? '+' : ''}${diferencia.toFixed(2)}
                          </td>
                          <td className="p-2 text-right text-cyan-400">${item.costo_por_persona.toFixed(2)}</td>
                          <td className="p-2 text-right">
                            <span className={`font-semibold ${eficiencia >= 85 ? 'text-green-400' : eficiencia >= 75 ? 'text-yellow-400' : 'text-red-400'}`}>
                              {eficiencia}%
                            </span>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          <div className="h-96 flex items-center justify-center text-slate-400">
            No hay datos disponibles
          </div>
        )}
      </div>

      {/* Gráfico de Mermas por Día con Línea Tolerable - Destacado */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 p-6 rounded-xl border border-slate-700 shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 gap-4">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-3 mb-2">
              <AlertTriangle size={28} className="text-orange-400" />
              Mermas por Día - Control de Límite Tolerable
            </h2>
            {mermasTolerableEstadisticas.total_costo !== undefined && (
              <p className="text-slate-400 text-sm">
                Costo Total: <span className="font-bold text-orange-400">${(mermasTolerableEstadisticas.total_costo || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}</span>
                {' | '}
                Promedio Diario: <span className="font-semibold">${(mermasTolerableEstadisticas.promedio_diario || 0).toFixed(2)}</span>
                {' | '}
                Promedio %: <span className="font-semibold">{(mermasTolerableEstadisticas.promedio_porcentaje || 0).toFixed(2)}%</span>
                {' | '}
                Días Excedidos: <span className={`font-semibold ${mermasTolerableEstadisticas.dias_excedidos > 0 ? 'text-red-400' : 'text-green-400'}`}>
                  {mermasTolerableEstadisticas.dias_excedidos || 0} ({(mermasTolerableEstadisticas.porcentaje_dias_excedidos || 0).toFixed(1)}%)
                </span>
              </p>
            )}
          </div>
          <div className="flex items-center gap-3">
            <label className="text-slate-300 text-sm whitespace-nowrap">
              Límite Tolerable:
            </label>
            <input
              type="number"
              min="1"
              max="20"
              step="0.5"
              value={porcentajeTolerable}
              onChange={(e) => setPorcentajeTolerable(parseFloat(e.target.value) || 5.0)}
              className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm w-20 focus:outline-none focus:ring-2 focus:ring-orange-500 text-slate-200"
            />
            <span className="text-slate-400 text-sm">%</span>
          </div>
        </div>
        {mermasTolerableLoading ? (
          <div className="h-96 flex items-center justify-center">
            <LoadingSpinner />
          </div>
        ) : mermasTolerableSeries.length > 0 ? (
          <ResponsiveContainer width="100%" height={450}>
            <ComposedChart 
              data={mermasTolerableSeries}
              margin={{ top: 20, right: 30, left: 20, bottom: 80 }}
            >
              <defs>
                <linearGradient id="colorMermasTolerable" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.orange} stopOpacity={0.9} />
                  <stop offset="50%" stopColor={COLORS.orange} stopOpacity={0.6} />
                  <stop offset="95%" stopColor={COLORS.orange} stopOpacity={0.1} />
                </linearGradient>
                <filter id="mermasTolerableShadow">
                  <feDropShadow dx="0" dy="3" stdDeviation="4" floodOpacity="0.25"/>
                </filter>
                <pattern id="tolerablePattern" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse">
                  <path d="M 0 8 L 8 0" stroke={COLORS.cyan} strokeWidth="1.5" opacity="0.6"/>
                </pattern>
              </defs>
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="#374151" 
                opacity={0.2}
                vertical={false}
              />
              <XAxis
                dataKey="fecha"
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                tickLine={{ stroke: '#4b5563' }}
                axisLine={{ stroke: '#4b5563' }}
              />
              <YAxis 
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                tickLine={{ stroke: '#4b5563' }}
                axisLine={{ stroke: '#4b5563' }}
                tickFormatter={(value) => `$${value.toFixed(0)}`}
              />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const costo = payload.find(p => p.dataKey === 'total_costo')?.value || 0
                    const tolerable = payload.find(p => p.dataKey === 'costo_tolerable')?.value || 0
                    const porcentaje = payload[0]?.payload?.porcentaje || 0
                    const porcentajeTol = payload[0]?.payload?.porcentaje_tolerable || porcentajeTolerable
                    const cantidad = payload[0]?.payload?.cantidad || 0
                    const excede = costo > tolerable
                    const diferencia = costo - tolerable
                    
                    return (
                      <div className="bg-gradient-to-br from-slate-800 via-slate-800 to-slate-900 border-2 border-slate-600 rounded-xl p-5 shadow-2xl backdrop-blur-md min-w-[280px]">
                        <div className="border-b-2 border-slate-600 pb-3 mb-3">
                          <p className="text-slate-100 font-bold text-base">
                            {label ? format(new Date(label), 'EEEE, dd MMM yyyy', { locale: es }) : ''}
                          </p>
                        </div>
                        <div className="space-y-3">
                          <div className={`flex items-center justify-between gap-4 p-2 rounded-lg ${excede ? 'bg-red-500/10 border border-red-500/30' : 'bg-orange-500/10'}`}>
                            <div className="flex items-center gap-2.5">
                              <div className="w-3.5 h-3.5 rounded-full bg-orange-500 shadow-lg" />
                              <span className="text-sm font-semibold text-slate-300">Costo Mermas</span>
                            </div>
                            <span className={`text-lg font-bold ${excede ? 'text-red-400' : 'text-orange-400'}`}>
                              ${typeof costo === 'number' ? costo.toLocaleString('es-ES', { minimumFractionDigits: 2 }) : costo}
                            </span>
                          </div>
                          <div className="flex items-center justify-between gap-4 p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
                            <div className="flex items-center gap-2.5">
                              <div className="w-3.5 h-3.5 rounded-full bg-cyan-500 shadow-lg border-2 border-cyan-300" />
                              <span className="text-sm font-semibold text-slate-300">Límite Tolerable</span>
                            </div>
                            <span className="text-lg font-bold text-cyan-400">
                              ${typeof tolerable === 'number' ? tolerable.toLocaleString('es-ES', { minimumFractionDigits: 2 }) : tolerable}
                            </span>
                          </div>
                          <div className="border-t-2 border-slate-600 pt-3 mt-3 space-y-2">
                            <div className="flex items-center justify-between gap-4">
                              <span className="text-xs text-slate-400 font-medium">Porcentaje:</span>
                              <span className={`font-bold text-sm ${porcentaje > porcentajeTol ? 'text-red-400' : 'text-green-400'}`}>
                                {porcentaje.toFixed(2)}% (Límite: {porcentajeTol}%)
                              </span>
                            </div>
                            <div className="flex items-center justify-between gap-4">
                              <span className="text-xs text-slate-400 font-medium">Cantidad:</span>
                              <span className="font-semibold text-sm text-slate-300">{cantidad}</span>
                            </div>
                            {excede && (
                              <div className="mt-3 pt-3 border-t-2 border-red-500/50 bg-red-500/5 rounded-lg p-2">
                                <div className="flex items-center justify-between gap-4">
                                  <span className="text-xs text-red-400 font-semibold">⚠️ Exceso:</span>
                                  <span className="text-sm font-bold text-red-400">
                                    +${diferencia.toFixed(2)}
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  }
                  return null
                }}
                cursor={{ stroke: COLORS.orange, strokeWidth: 2, strokeDasharray: '5 5' }}
                animationDuration={200}
              />
              <Legend
                wrapperStyle={{ paddingTop: '30px', paddingBottom: '10px' }}
                iconType="line"
                iconSize={14}
                formatter={(value) => (
                  <span className="text-slate-300 text-sm font-semibold">
                    {value === 'total_costo' ? 'Costo Mermas' : 'Límite Tolerable'}
                  </span>
                )}
              />
              <Area
                type="monotone"
                dataKey="total_costo"
                stroke={COLORS.orange}
                strokeWidth={4}
                fillOpacity={1}
                fill="url(#colorMermasTolerable)"
                name="total_costo"
                dot={{ fill: COLORS.orange, r: 5, strokeWidth: 2, stroke: '#fff' }}
                activeDot={{ r: 8, strokeWidth: 3, stroke: '#fff', fill: COLORS.orange }}
                animationDuration={1200}
                animationEasing="ease-out"
                filter="url(#mermasTolerableShadow)"
              />
              <Line
                type="monotone"
                dataKey="costo_tolerable"
                stroke={COLORS.cyan}
                strokeWidth={3}
                strokeDasharray="8 4"
                name="costo_tolerable"
                dot={false}
                label={false}
                animationDuration={1200}
                animationEasing="ease-out"
              />
              <ReferenceArea 
                y1={0} 
                y2={mermasTolerableSeries.reduce((max, item) => Math.max(max, item.costo_tolerable || 0), 0)} 
                fill={COLORS.cyan} 
                fillOpacity={0.05}
                stroke="none"
              />
              <Brush 
                dataKey="fecha"
                height={40}
                stroke={COLORS.orange}
                fill="#1e293b"
                tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
              />
            </ComposedChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-96 flex items-center justify-center text-slate-400">
            No hay datos disponibles
          </div>
        )}
      </div>

      {/* Gráfico de Tendencia de Mermas por Categoría */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 p-6 rounded-xl border border-slate-700 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-3 mb-2">
              <TrendingUp size={28} className="text-orange-400" />
              Tendencia de Mermas por Categoría
            </h2>
            {mermasTendenciaCategoriaEstadisticas.promedio_merma_real !== undefined && (
              <p className="text-slate-400 text-sm">
                Promedio Real: <span className="font-bold text-red-400">{mermasTendenciaCategoriaEstadisticas.promedio_merma_real?.toFixed(2) || 0}</span>
                {' | '}
                Promedio Máximo: <span className="font-semibold text-cyan-400">{mermasTendenciaCategoriaEstadisticas.promedio_merma_maxima?.toFixed(2) || 0}</span>
                {' | '}
                Días Excedidos: <span className={`font-semibold ${mermasTendenciaCategoriaEstadisticas.dias_excedidos > 0 ? 'text-red-400' : 'text-green-400'}`}>
                  {mermasTendenciaCategoriaEstadisticas.dias_excedidos || 0} ({(mermasTendenciaCategoriaEstadisticas.porcentaje_dias_excedidos || 0).toFixed(1)}%)
                </span>
              </p>
            )}
          </div>
          <div className="flex items-center gap-3">
            <label className="text-sm text-slate-300 font-semibold">Categoría:</label>
            <select
              value={categoriaSeleccionada}
              onChange={(e) => setCategoriaSeleccionada(e.target.value)}
              className="bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-slate-200 font-medium focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
            >
              {categoriasAlimentos.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        {mermasTendenciaCategoriaLoading ? (
          <div className="h-96 flex items-center justify-center">
            <LoadingSpinner />
          </div>
        ) : mermasTendenciaCategoriaSeries.length > 0 ? (
          <ResponsiveContainer width="100%" height={450}>
            <LineChart 
              data={mermasTendenciaCategoriaSeries}
              margin={{ top: 20, right: 30, left: 20, bottom: 80 }}
            >
              <defs>
                <linearGradient id="colorMermaReal" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.red} stopOpacity={0.9} />
                  <stop offset="50%" stopColor={COLORS.red} stopOpacity={0.6} />
                  <stop offset="95%" stopColor={COLORS.red} stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id="colorMermaMaxima" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.cyan} stopOpacity={0.9} />
                  <stop offset="50%" stopColor={COLORS.cyan} stopOpacity={0.6} />
                  <stop offset="95%" stopColor={COLORS.cyan} stopOpacity={0.1} />
                </linearGradient>
                <filter id="lineShadow">
                  <feDropShadow dx="0" dy="3" stdDeviation="4" floodOpacity="0.25"/>
                </filter>
              </defs>
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="#374151" 
                opacity={0.2}
                vertical={false}
              />
              <XAxis
                dataKey="fecha"
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                tickLine={{ stroke: '#4b5563' }}
                axisLine={{ stroke: '#4b5563' }}
              />
              <YAxis 
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                tickLine={{ stroke: '#4b5563' }}
                axisLine={{ stroke: '#4b5563' }}
                label={{ value: 'Cantidad', angle: -90, position: 'insideLeft', fill: '#9ca3af', fontSize: 12 }}
              />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const mermaReal = payload.find(p => p.dataKey === 'merma_real')?.value || 0
                    const mermaMaxima = payload.find(p => p.dataKey === 'merma_maxima_aceptada')?.value || 0
                    const diferencia = mermaReal - mermaMaxima
                    const porcentajeUso = mermaMaxima > 0 ? ((mermaReal / mermaMaxima) * 100).toFixed(1) : 0
                    const excede = diferencia > 0
                    
                    return (
                      <div className="bg-gradient-to-br from-slate-800 via-slate-800 to-slate-900 border-2 border-slate-600 rounded-xl p-5 shadow-2xl backdrop-blur-md min-w-[280px]">
                        <div className="border-b-2 border-slate-600 pb-3 mb-3">
                          <p className="text-slate-100 font-bold text-base">
                            {label ? format(new Date(label), 'EEEE, dd MMM yyyy', { locale: es }) : ''}
                          </p>
                          <p className="text-xs text-slate-400 mt-1 capitalize">
                            Categoría: {categoriasAlimentos.find(c => c.value === categoriaActual)?.label || categoriaActual}
                          </p>
                        </div>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between gap-4 p-2 rounded-lg bg-red-500/10">
                            <div className="flex items-center gap-2.5">
                              <div className="w-3.5 h-3.5 rounded-full bg-red-500 shadow-lg" />
                              <span className="text-sm font-semibold text-slate-300">Merma Real</span>
                            </div>
                            <span className="text-lg font-bold text-red-400">{mermaReal.toFixed(2)}</span>
                          </div>
                          <div className="flex items-center justify-between gap-4 p-2 rounded-lg bg-cyan-500/10">
                            <div className="flex items-center gap-2.5">
                              <div className="w-3.5 h-3.5 rounded-full bg-cyan-500 shadow-lg" />
                              <span className="text-sm font-semibold text-slate-300">Máxima Aceptada</span>
                            </div>
                            <span className="text-lg font-bold text-cyan-400">{mermaMaxima.toFixed(2)}</span>
                          </div>
                          <div className="border-t-2 border-slate-600 pt-3 mt-3 space-y-2">
                            <div className="flex items-center justify-between gap-4">
                              <span className="text-xs text-slate-400 font-medium">Diferencia:</span>
                              <span className={`font-bold text-sm ${excede ? 'text-red-400' : 'text-green-400'}`}>
                                {excede ? '+' : ''}{diferencia.toFixed(2)}
                              </span>
                            </div>
                            <div className="flex items-center justify-between gap-4">
                              <span className="text-xs text-slate-400 font-medium">% Uso:</span>
                              <span className={`font-bold text-sm ${porcentajeUso >= 100 ? 'text-red-400' : porcentajeUso >= 90 ? 'text-yellow-400' : 'text-green-400'}`}>
                                {porcentajeUso}%
                              </span>
                            </div>
                            {excede && (
                              <div className="mt-2 p-2 bg-red-500/20 border border-red-500/50 rounded-lg">
                                <p className="text-xs text-red-400 font-semibold flex items-center gap-1">
                                  <AlertTriangle size={12} />
                                  Límite excedido
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  }
                  return null
                }}
                cursor={{ stroke: COLORS.red, strokeWidth: 2, strokeDasharray: '5 5' }}
                animationDuration={200}
              />
              <Legend
                wrapperStyle={{ paddingTop: '30px', paddingBottom: '10px' }}
                iconType="line"
                iconSize={16}
                formatter={(value) => (
                  <span className="text-slate-300 text-sm font-semibold">
                    {value === 'merma_real' ? 'Merma Real' : 'Merma Máxima Aceptada'}
                  </span>
                )}
              />
              <Line
                type="monotone"
                dataKey="merma_real"
                stroke={COLORS.red}
                strokeWidth={4}
                dot={{ fill: COLORS.red, r: 5, strokeWidth: 2, stroke: '#fff' }}
                activeDot={{ r: 8, strokeWidth: 3, stroke: '#fff', fill: COLORS.red }}
                name="merma_real"
                animationDuration={1200}
                animationEasing="ease-out"
                filter="url(#lineShadow)"
              />
              <Line
                type="monotone"
                dataKey="merma_maxima_aceptada"
                stroke={COLORS.cyan}
                strokeWidth={3}
                strokeDasharray="8 4"
                dot={{ fill: COLORS.cyan, r: 4, strokeWidth: 2, stroke: '#fff' }}
                activeDot={{ r: 7, strokeWidth: 3, stroke: '#fff', fill: COLORS.cyan }}
                name="merma_maxima_aceptada"
                animationDuration={1200}
                animationEasing="ease-out"
                animationBegin={200}
                filter="url(#lineShadow)"
              />
              <ReferenceArea
                y1={0}
                y2={mermasTendenciaCategoriaSeries.reduce((max, item) => Math.max(max, item.merma_maxima_aceptada || 0), 0)}
                fill={COLORS.cyan}
                fillOpacity={0.05}
                stroke={COLORS.cyan}
                strokeDasharray="3 3"
                strokeOpacity={0.3}
              />
              <Brush 
                dataKey="fecha"
                height={40}
                stroke={COLORS.red}
                fill="#1e293b"
                tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-96 flex items-center justify-center text-slate-400">
            No hay datos disponibles
          </div>
        )}
      </div>

      {/* Gráficos de distribución (Donut/Pie) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Facturas por Estado */}
        {facturasPorEstado.length > 0 && (
          <div className="bg-gradient-to-br from-slate-800 to-slate-800/50 p-6 rounded-xl border border-slate-700 hover:border-purple-500/50 transition-all shadow-lg">
            <h3 className="text-lg font-bold mb-4 text-slate-200">Facturas por Estado</h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <defs>
                  <filter id="pieShadow">
                    <feDropShadow dx="0" dy="2" stdDeviation="2" floodOpacity="0.2"/>
                  </filter>
                </defs>
                <Pie
                  data={facturasPorEstado}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ estado, cantidad, percent }) => `${estado}: ${cantidad} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={75}
                  innerRadius={25}
                  fill="#8884d8"
                  dataKey="cantidad"
                  animationDuration={800}
                  animationEasing="ease-out"
                >
                  {facturasPorEstado.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={CHART_COLORS[index % CHART_COLORS.length]}
                      stroke="#1e293b"
                      strokeWidth={2}
                      filter="url(#pieShadow)"
                    />
                  ))}
                </Pie>
                <Tooltip 
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0]
                      const total = facturasPorEstado.reduce((sum, item) => sum + item.cantidad, 0)
                      const percent = ((data.value / total) * 100).toFixed(1)
                      return (
                        <div className="bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-slate-600 rounded-lg p-3 shadow-xl">
                          <p className="text-slate-200 font-bold text-sm mb-2 capitalize">{data.name}</p>
                          <div className="flex items-center justify-between gap-4">
                            <span className="text-xs text-slate-400">Cantidad:</span>
                            <span className="text-sm font-bold text-slate-200">{data.value}</span>
                          </div>
                          <div className="flex items-center justify-between gap-4 mt-1">
                            <span className="text-xs text-slate-400">Porcentaje:</span>
                            <span className="text-sm font-bold" style={{ color: data.payload.fill }}>{percent}%</span>
                          </div>
                        </div>
                      )
                    }
                    return null
                  }}
                  animationDuration={200}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Pedidos por Estado */}
        {pedidosPorEstado.length > 0 && (
          <div className="bg-gradient-to-br from-slate-800 to-slate-800/50 p-6 rounded-xl border border-slate-700 hover:border-blue-500/50 transition-all shadow-lg">
            <h3 className="text-lg font-bold mb-4 text-slate-200">Pedidos por Estado</h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pedidosPorEstado}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ estado, cantidad, percent }) => `${estado}: ${cantidad} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={75}
                  innerRadius={25}
                  fill="#8884d8"
                  dataKey="cantidad"
                  animationDuration={800}
                  animationEasing="ease-out"
                >
                  {pedidosPorEstado.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={CHART_COLORS[index % CHART_COLORS.length]}
                      stroke="#1e293b"
                      strokeWidth={2}
                      filter="url(#pieShadow)"
                    />
                  ))}
                </Pie>
                <Tooltip 
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0]
                      const total = pedidosPorEstado.reduce((sum, item) => sum + item.cantidad, 0)
                      const percent = ((data.value / total) * 100).toFixed(1)
                      return (
                        <div className="bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-slate-600 rounded-lg p-3 shadow-xl">
                          <p className="text-slate-200 font-bold text-sm mb-2 capitalize">{data.name}</p>
                          <div className="flex items-center justify-between gap-4">
                            <span className="text-xs text-slate-400">Cantidad:</span>
                            <span className="text-sm font-bold text-slate-200">{data.value}</span>
                          </div>
                          <div className="flex items-center justify-between gap-4 mt-1">
                            <span className="text-xs text-slate-400">Porcentaje:</span>
                            <span className="text-sm font-bold" style={{ color: data.payload.fill }}>{percent}%</span>
                          </div>
                        </div>
                      )
                    }
                    return null
                  }}
                  animationDuration={200}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Tickets por Estado */}
        {ticketsPorEstado.length > 0 && (
          <div className="bg-gradient-to-br from-slate-800 to-slate-800/50 p-6 rounded-xl border border-slate-700 hover:border-green-500/50 transition-all shadow-lg">
            <h3 className="text-lg font-bold mb-4 text-slate-200">Tickets por Estado</h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={ticketsPorEstado}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ estado, cantidad, percent }) => `${estado}: ${cantidad} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={75}
                  innerRadius={25}
                  fill="#8884d8"
                  dataKey="cantidad"
                  animationDuration={800}
                  animationEasing="ease-out"
                >
                  {ticketsPorEstado.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={CHART_COLORS[index % CHART_COLORS.length]}
                      stroke="#1e293b"
                      strokeWidth={2}
                      filter="url(#pieShadow)"
                    />
                  ))}
                </Pie>
                <Tooltip 
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0]
                      const total = ticketsPorEstado.reduce((sum, item) => sum + item.cantidad, 0)
                      const percent = ((data.value / total) * 100).toFixed(1)
                      return (
                        <div className="bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-slate-600 rounded-lg p-3 shadow-xl">
                          <p className="text-slate-200 font-bold text-sm mb-2 capitalize">{data.name}</p>
                          <div className="flex items-center justify-between gap-4">
                            <span className="text-xs text-slate-400">Cantidad:</span>
                            <span className="text-sm font-bold text-slate-200">{data.value}</span>
                          </div>
                          <div className="flex items-center justify-between gap-4 mt-1">
                            <span className="text-xs text-slate-400">Porcentaje:</span>
                            <span className="text-sm font-bold" style={{ color: data.payload.fill }}>{percent}%</span>
                          </div>
                        </div>
                      )
                    }
                    return null
                  }}
                  animationDuration={200}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Mermas por Tipo */}
        {mermasPorTipo.length > 0 && (
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
            <h3 className="text-lg font-bold mb-4">Mermas por Tipo</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={mermasPorTipo}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ tipo, cantidad }) => `${tipo}: ${cantidad}`}
                  outerRadius={70}
                  fill="#8884d8"
                  dataKey="cantidad"
                >
                  {mermasPorTipo.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Resumen adicional */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Charolas */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-cyan-600/20 p-2 rounded-lg">
              <Calendar className="text-cyan-400" size={20} />
            </div>
            <div>
              <p className="text-slate-400 text-sm">Charolas</p>
              <p className="text-2xl font-bold">{kpis.charolas?.totales || 0}</p>
            </div>
          </div>
        </div>

        {/* Mermas */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-red-600/20 p-2 rounded-lg">
              <AlertTriangle className="text-red-400" size={20} />
            </div>
            <div>
              <p className="text-slate-400 text-sm">Mermas Totales</p>
              <p className="text-2xl font-bold">{kpis.mermas?.totales || 0}</p>
              <p className="text-xs text-slate-500">
                Costo: ${(kpis.mermas?.total_costo || 0).toLocaleString('es-ES', { minimumFractionDigits: 2 })}
              </p>
            </div>
          </div>
        </div>

        {/* Facturas Pendientes */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-orange-600/20 p-2 rounded-lg">
              <FileText className="text-orange-400" size={20} />
            </div>
            <div>
              <p className="text-slate-400 text-sm">Facturas Pendientes</p>
              <p className="text-2xl font-bold">{kpis.facturas?.pendientes || 0}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
