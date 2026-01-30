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
  ResponsiveContainer
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

  // Datos para gráficos de donut
  const facturasPorEstado = facturasChart?.por_estado || []
  const pedidosPorEstado = pedidosChart?.por_estado || []
  const ticketsPorEstado = ticketsChart?.por_estado || []
  const mermasPorTipo = mermasChart?.por_tipo || []

  const handleRefresh = () => {
    refetchKpis()
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
          <p className="text-slate-300 font-semibold mb-2">
            {label ? format(new Date(label), 'dd MMM yyyy', { locale: es }) : ''}
          </p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {`${entry.name}: ${typeof entry.value === 'number' ? entry.value.toLocaleString('es-ES') : entry.value}`}
            </p>
          ))}
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
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={facturasSeries}>
                <defs>
                  <linearGradient id="colorFacturas" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.purple} stopOpacity={0.8} />
                    <stop offset="95%" stopColor={COLORS.purple} stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="fecha"
                  stroke="#9ca3af"
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                />
                <YAxis stroke="#9ca3af" />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="total"
                  stroke={COLORS.purple}
                  fillOpacity={1}
                  fill="url(#colorFacturas)"
                  name="Total Facturado"
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
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={pedidosSeries}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="fecha"
                  stroke="#9ca3af"
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                />
                <YAxis stroke="#9ca3af" />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="cantidad" fill={COLORS.blue} name="Cantidad" radius={[8, 8, 0, 0]} />
                <Bar dataKey="total" fill={COLORS.cyan} name="Total" radius={[8, 8, 0, 0]} />
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
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={ticketsSeries}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="fecha"
                  stroke="#9ca3af"
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                />
                <YAxis stroke="#9ca3af" />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="cantidad"
                  stroke={COLORS.green}
                  strokeWidth={3}
                  dot={{ fill: COLORS.green, r: 5 }}
                  activeDot={{ r: 7 }}
                  name="Tickets"
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
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={mermasSeries}>
                <defs>
                  <linearGradient id="colorMermas" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.yellow} stopOpacity={0.8} />
                    <stop offset="95%" stopColor={COLORS.yellow} stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="fecha"
                  stroke="#9ca3af"
                  tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                />
                <YAxis stroke="#9ca3af" />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="total_costo"
                  stroke={COLORS.yellow}
                  fillOpacity={1}
                  fill="url(#colorMermas)"
                  name="Costo Total"
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

      {/* Gráfico Comparativo de Charolas - Destacado */}
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
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={charolasComparacionSeries}>
              <defs>
                <linearGradient id="colorProgramadas" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.blue} stopOpacity={0.8} />
                  <stop offset="95%" stopColor={COLORS.blue} stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id="colorServidas" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.green} stopOpacity={0.8} />
                  <stop offset="95%" stopColor={COLORS.green} stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis
                dataKey="fecha"
                stroke="#9ca3af"
                tickFormatter={(value) => format(new Date(value), 'dd/MM', { locale: es })}
                style={{ fontSize: '12px' }}
              />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const programadas = payload.find(p => p.dataKey === 'programadas')?.value || 0
                    const servidas = payload.find(p => p.dataKey === 'servidas')?.value || 0
                    const diferencia = programadas - servidas
                    const eficiencia = programadas > 0 ? ((servidas / programadas) * 100).toFixed(1) : 0
                    
                    return (
                      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 shadow-xl">
                        <p className="text-slate-300 font-semibold mb-3 text-sm">
                          {label ? format(new Date(label), 'EEEE, dd MMM yyyy', { locale: es }) : ''}
                        </p>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between gap-4">
                            <span className="text-sm" style={{ color: COLORS.blue }}>Programadas:</span>
                            <span className="font-bold">{programadas}</span>
                          </div>
                          <div className="flex items-center justify-between gap-4">
                            <span className="text-sm" style={{ color: COLORS.green }}>Servidas:</span>
                            <span className="font-bold">{servidas}</span>
                          </div>
                          <div className="border-t border-slate-700 pt-2 mt-2">
                            <div className="flex items-center justify-between gap-4">
                              <span className="text-xs text-slate-400">Diferencia:</span>
                              <span className={`font-semibold text-xs ${diferencia >= 0 ? 'text-yellow-400' : 'text-red-400'}`}>
                                {diferencia >= 0 ? '+' : ''}{diferencia}
                              </span>
                            </div>
                            <div className="flex items-center justify-between gap-4 mt-1">
                              <span className="text-xs text-slate-400">Eficiencia:</span>
                              <span className="font-semibold text-xs text-cyan-400">{eficiencia}%</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  }
                  return null
                }}
              />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="circle"
                formatter={(value) => (
                  <span className="text-slate-300 text-sm">
                    {value === 'programadas' ? 'Programadas' : 'Servidas'}
                  </span>
                )}
              />
              <Area
                type="monotone"
                dataKey="programadas"
                stroke={COLORS.blue}
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#colorProgramadas)"
                name="programadas"
                dot={{ fill: COLORS.blue, r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Area
                type="monotone"
                dataKey="servidas"
                stroke={COLORS.green}
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#colorServidas)"
                name="servidas"
                dot={{ fill: COLORS.green, r: 4 }}
                activeDot={{ r: 6 }}
              />
            </AreaChart>
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
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
            <h3 className="text-lg font-bold mb-4">Facturas por Estado</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={facturasPorEstado}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ estado, cantidad }) => `${estado}: ${cantidad}`}
                  outerRadius={70}
                  fill="#8884d8"
                  dataKey="cantidad"
                >
                  {facturasPorEstado.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Pedidos por Estado */}
        {pedidosPorEstado.length > 0 && (
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
            <h3 className="text-lg font-bold mb-4">Pedidos por Estado</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={pedidosPorEstado}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ estado, cantidad }) => `${estado}: ${cantidad}`}
                  outerRadius={70}
                  fill="#8884d8"
                  dataKey="cantidad"
                >
                  {pedidosPorEstado.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Tickets por Estado */}
        {ticketsPorEstado.length > 0 && (
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
            <h3 className="text-lg font-bold mb-4">Tickets por Estado</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={ticketsPorEstado}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ estado, cantidad }) => `${estado}: ${cantidad}`}
                  outerRadius={70}
                  fill="#8884d8"
                  dataKey="cantidad"
                >
                  {ticketsPorEstado.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
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
