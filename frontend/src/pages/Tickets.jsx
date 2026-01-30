import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api, { extractData } from '../config/api'
import { 
  MessageSquare, 
  AlertCircle, 
  Plus, 
  Search,
  Filter,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Info,
  ChevronRight,
  Calendar,
  User,
  Tag
} from 'lucide-react'
import Modal from '../components/Modal'
import TicketForm from '../components/TicketForm'
import toast from 'react-hot-toast'

export default function Tickets() {
  const [showModal, setShowModal] = useState(false)
  const [ticketSeleccionado, setTicketSeleccionado] = useState(null)
  const [busqueda, setBusqueda] = useState('')
  const [filtroEstado, setFiltroEstado] = useState(null) // 'abierto', 'resuelto', 'cerrado'
  const [filtroPrioridad, setFiltroPrioridad] = useState(null) // 'baja', 'media', 'alta', 'urgente'
  const [filtroTipo, setFiltroTipo] = useState(null) // 'consulta', 'queja', etc.
  const [mostrarModalResolver, setMostrarModalResolver] = useState(false)
  const [respuestaTicket, setRespuestaTicket] = useState('')
  
  const queryClient = useQueryClient()

  // Cargar tickets con filtros
  const { data: ticketsResponse } = useQuery({
    queryKey: ['tickets', busqueda, filtroEstado, filtroPrioridad, filtroTipo],
    queryFn: () => {
      const params = new URLSearchParams()
      if (busqueda) params.append('busqueda', busqueda)
      if (filtroEstado) params.append('estado', filtroEstado)
      if (filtroPrioridad) params.append('prioridad', filtroPrioridad)
      if (filtroTipo) params.append('tipo', filtroTipo)
      return api.get(`/crm/tickets?${params}`).then(extractData)
    },
  })

  // Cargar estadísticas
  const { data: estadisticas } = useQuery({
    queryKey: ['tickets-estadisticas'],
    queryFn: () => {
      // Calcular estadísticas desde los tickets
      const tickets = Array.isArray(ticketsResponse) ? ticketsResponse : []
      return {
        total: tickets.length,
        abiertos: tickets.filter(t => t.estado === 'abierto').length,
        resueltos: tickets.filter(t => t.estado === 'resuelto').length,
        cerrados: tickets.filter(t => t.estado === 'cerrado').length,
        urgentes: tickets.filter(t => t.prioridad === 'urgente').length,
        altas: tickets.filter(t => t.prioridad === 'alta').length,
      }
    },
    enabled: !!ticketsResponse,
  })

  const tickets = Array.isArray(ticketsResponse) ? ticketsResponse : []
  const ticketActual = tickets.find(t => t.id === ticketSeleccionado)

  // Mutación para resolver ticket
  const resolverMutation = useMutation({
    mutationFn: ({ ticketId, respuesta }) => api.post(`/crm/tickets/${ticketId}/resolver`, { respuesta }),
    onSuccess: () => {
      toast.success('Ticket resuelto correctamente')
      queryClient.invalidateQueries(['tickets'])
      queryClient.invalidateQueries(['tickets-estadisticas'])
      setMostrarModalResolver(false)
      setRespuestaTicket('')
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al resolver ticket')
    },
  })

  const handleResolverTicket = () => {
    if (!respuestaTicket.trim()) {
      toast.error('Debes escribir una respuesta para resolver el ticket')
      return
    }
    resolverMutation.mutate({ ticketId: ticketActual.id, respuesta: respuestaTicket })
  }

  const formatearFecha = (fecha) => {
    if (!fecha) return ''
    const date = new Date(fecha)
    const ahora = new Date()
    const diffMs = ahora - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Ahora'
    if (diffMins < 60) return `Hace ${diffMins} min`
    if (diffHours < 24) return `Hace ${diffHours} h`
    if (diffDays < 7) return `Hace ${diffDays} días`
    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
  }

  const getEstadoIcon = (estado) => {
    switch (estado) {
      case 'abierto':
        return <Clock size={14} className="text-yellow-400" />
      case 'resuelto':
        return <CheckCircle size={14} className="text-green-400" />
      case 'cerrado':
        return <XCircle size={14} className="text-slate-400" />
      default:
        return <Info size={14} className="text-slate-400" />
    }
  }

  const getPrioridadColor = (prioridad) => {
    switch (prioridad) {
      case 'urgente':
        return 'bg-red-500/20 text-red-300 border-red-500/50'
      case 'alta':
        return 'bg-orange-500/20 text-orange-300 border-orange-500/50'
      case 'media':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50'
      case 'baja':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/50'
      default:
        return 'bg-slate-500/20 text-slate-300 border-slate-500/50'
    }
  }

  const getTipoColor = (tipo) => {
    switch (tipo) {
      case 'consulta':
        return 'bg-blue-500/20 text-blue-300'
      case 'queja':
        return 'bg-red-500/20 text-red-300'
      case 'reclamo':
        return 'bg-orange-500/20 text-orange-300'
      case 'sugerencia':
        return 'bg-green-500/20 text-green-300'
      default:
        return 'bg-slate-500/20 text-slate-300'
    }
  }

  return (
    <div className="flex gap-6 h-[calc(100vh-4rem)]">
      {/* Panel izquierdo: Lista de Tickets */}
      <div className="w-80 bg-slate-800 rounded-lg border border-slate-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <MessageSquare size={24} className="text-purple-500" />
              <h1 className="text-xl font-bold">Tickets</h1>
            </div>
            <button
              onClick={() => setShowModal(true)}
              className="bg-purple-600 hover:bg-purple-700 p-2 rounded-lg"
              title="Nuevo Ticket"
            >
              <Plus size={18} />
            </button>
          </div>

          {/* Buscador */}
          <div className="relative mb-3">
            <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Buscar ticket..."
              className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm focus:outline-none focus:border-purple-500"
            />
          </div>

          {/* Filtros rápidos - Estado */}
          <div className="mb-2">
            <p className="text-xs text-slate-400 mb-2">Estado</p>
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => setFiltroEstado(null)}
                className={`px-2 py-1 rounded text-xs ${
                  filtroEstado === null
                    ? 'bg-purple-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                Todos
              </button>
              <button
                onClick={() => setFiltroEstado('abierto')}
                className={`px-2 py-1 rounded text-xs ${
                  filtroEstado === 'abierto'
                    ? 'bg-yellow-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                Abiertos
              </button>
              <button
                onClick={() => setFiltroEstado('resuelto')}
                className={`px-2 py-1 rounded text-xs ${
                  filtroEstado === 'resuelto'
                    ? 'bg-green-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                Resueltos
              </button>
            </div>
          </div>

          {/* Filtros rápidos - Prioridad */}
          <div>
            <p className="text-xs text-slate-400 mb-2">Prioridad</p>
            <div className="flex gap-2 flex-wrap">
              <button
                onClick={() => setFiltroPrioridad(null)}
                className={`px-2 py-1 rounded text-xs ${
                  filtroPrioridad === null
                    ? 'bg-purple-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                Todas
              </button>
              <button
                onClick={() => setFiltroPrioridad('urgente')}
                className={`px-2 py-1 rounded text-xs ${
                  filtroPrioridad === 'urgente'
                    ? 'bg-red-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                Urgente
              </button>
              <button
                onClick={() => setFiltroPrioridad('alta')}
                className={`px-2 py-1 rounded text-xs ${
                  filtroPrioridad === 'alta'
                    ? 'bg-orange-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                Alta
              </button>
            </div>
          </div>
        </div>

        {/* Estadísticas */}
        {estadisticas && (
          <div className="p-4 border-b border-slate-700 bg-slate-700/50">
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-slate-400">Total:</span>
                <p className="font-bold text-white">{estadisticas.total || 0}</p>
              </div>
              <div>
                <span className="text-slate-400">Abiertos:</span>
                <p className="font-bold text-yellow-400">{estadisticas.abiertos || 0}</p>
              </div>
              <div>
                <span className="text-slate-400">Resueltos:</span>
                <p className="font-bold text-green-400">{estadisticas.resueltos || 0}</p>
              </div>
              <div>
                <span className="text-slate-400">Urgentes:</span>
                <p className="font-bold text-red-400">{estadisticas.urgentes || 0}</p>
              </div>
            </div>
          </div>
        )}

        {/* Lista de tickets */}
        <div className="flex-1 overflow-y-auto">
          {tickets.length === 0 ? (
            <div className="p-8 text-center text-slate-400">
              <MessageSquare size={32} className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">No hay tickets disponibles</p>
              <button
                onClick={() => setShowModal(true)}
                className="mt-4 text-purple-400 hover:text-purple-300 text-sm"
              >
                Crear primer ticket
              </button>
            </div>
          ) : (
            <div className="divide-y divide-slate-700">
              {tickets.map((ticket) => (
                <button
                  key={ticket.id}
                  onClick={() => setTicketSeleccionado(ticket.id)}
                  className={`w-full text-left p-4 hover:bg-slate-700/50 transition-colors ${
                    ticketSeleccionado === ticket.id
                      ? 'bg-purple-600/20 border-l-4 border-purple-500'
                      : ''
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-white text-sm line-clamp-1">
                          {ticket.asunto}
                        </h3>
                        {getEstadoIcon(ticket.estado)}
                      </div>
                      <p className="text-xs text-slate-400 line-clamp-2 mb-2">
                        {ticket.descripcion}
                      </p>
                    </div>
                    <ChevronRight 
                      size={16} 
                      className={`text-slate-400 flex-shrink-0 ${
                        ticketSeleccionado === ticket.id ? 'text-purple-400' : ''
                      }`}
                    />
                  </div>

                  {/* Badges de tipo y prioridad */}
                  <div className="flex gap-2 flex-wrap mb-2">
                    <span className={`text-xs px-1.5 py-0.5 rounded ${getTipoColor(ticket.tipo)}`}>
                      {ticket.tipo}
                    </span>
                    <span className={`text-xs px-1.5 py-0.5 rounded border ${getPrioridadColor(ticket.prioridad)}`}>
                      {ticket.prioridad}
                    </span>
                  </div>

                  {/* Fecha */}
                  <div className="flex items-center gap-1 text-xs text-slate-500">
                    <Calendar size={12} />
                    <span>{formatearFecha(ticket.fecha_creacion)}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Panel derecho: Detalles del Ticket */}
      {ticketSeleccionado && ticketActual ? (
        <div className="flex-1 bg-slate-800 rounded-lg border border-slate-700 flex flex-col">
          {/* Header del ticket */}
          <div className="p-4 border-b border-slate-700">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-xl font-bold">{ticketActual.asunto}</h2>
                  {getEstadoIcon(ticketActual.estado)}
                </div>
                <div className="flex items-center gap-3 flex-wrap">
                  <span className={`text-sm px-2 py-1 rounded ${getTipoColor(ticketActual.tipo)}`}>
                    {ticketActual.tipo}
                  </span>
                  <span className={`text-sm px-2 py-1 rounded border ${getPrioridadColor(ticketActual.prioridad)}`}>
                    {ticketActual.prioridad}
                  </span>
                  <span className="text-sm text-slate-400 capitalize">
                    {ticketActual.estado}
                  </span>
                </div>
              </div>
              {ticketActual.estado === 'abierto' && (
                <button
                  onClick={() => setMostrarModalResolver(true)}
                  className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg text-sm flex items-center gap-2"
                >
                  <CheckCircle size={16} />
                  Resolver
                </button>
              )}
            </div>

            {/* Información adicional */}
            <div className="flex gap-4 text-sm text-slate-400 mt-3">
              <span className="flex items-center gap-1">
                <Calendar size={14} />
                Creado: {formatearFecha(ticketActual.fecha_creacion)}
              </span>
              {ticketActual.fecha_resolucion && (
                <span className="flex items-center gap-1">
                  <CheckCircle size={14} />
                  Resuelto: {formatearFecha(ticketActual.fecha_resolucion)}
                </span>
              )}
            </div>
          </div>

          {/* Contenido del ticket */}
          <div className="flex-1 overflow-y-auto p-6">
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
                  <Info size={16} />
                  Descripción
                </h3>
                <div className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
                  <p className="text-slate-300 whitespace-pre-wrap">{ticketActual.descripcion}</p>
                </div>
              </div>

              {ticketActual.respuesta && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
                    <MessageSquare size={16} />
                    Respuesta
                  </h3>
                  <div className="bg-green-600/10 rounded-lg p-4 border border-green-500/30">
                    <p className="text-slate-300 whitespace-pre-wrap">{ticketActual.respuesta}</p>
                  </div>
                </div>
              )}

              {ticketActual.cliente_id && (
                <div>
                  <h3 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
                    <User size={16} />
                    Cliente
                  </h3>
                  <div className="bg-slate-700/50 rounded-lg p-4 border border-slate-600">
                    <p className="text-slate-300">ID: {ticketActual.cliente_id}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Acciones */}
          {ticketActual.estado === 'abierto' && (
            <div className="p-4 border-t border-slate-700">
              <button
                onClick={() => setMostrarModalResolver(true)}
                className="w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2"
              >
                <CheckCircle size={18} />
                Resolver Ticket
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="flex-1 bg-slate-800 rounded-lg border border-slate-700 flex items-center justify-center">
          <div className="text-center text-slate-400">
            <MessageSquare size={48} className="mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-semibold mb-2">Selecciona un ticket</h3>
            <p className="text-sm">Elige un ticket de la lista para ver sus detalles</p>
            <button
              onClick={() => setShowModal(true)}
              className="mt-4 text-purple-400 hover:text-purple-300 text-sm flex items-center gap-2 mx-auto"
            >
              <Plus size={16} />
              Crear nuevo ticket
            </button>
          </div>
        </div>
      )}

      {/* Modal para crear ticket */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Nuevo Ticket"
      >
        <TicketForm
          onClose={() => {
            setShowModal(false)
            queryClient.invalidateQueries(['tickets'])
          }}
        />
      </Modal>

      {/* Modal para resolver ticket */}
      <Modal
        isOpen={mostrarModalResolver}
        onClose={() => {
          setMostrarModalResolver(false)
          setRespuestaTicket('')
        }}
        title="Resolver Ticket"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Respuesta *
            </label>
            <textarea
              value={respuestaTicket}
              onChange={(e) => setRespuestaTicket(e.target.value)}
              placeholder="Escribe la respuesta o solución para este ticket..."
              rows={6}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              required
            />
          </div>
          <div className="flex gap-4 pt-4">
            <button
              onClick={handleResolverTicket}
              disabled={resolverMutation.isPending || !respuestaTicket.trim()}
              className="flex-1 bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg disabled:opacity-50"
            >
              {resolverMutation.isPending ? 'Resolviendo...' : 'Resolver Ticket'}
            </button>
            <button
              onClick={() => {
                setMostrarModalResolver(false)
                setRespuestaTicket('')
              }}
              className="flex-1 bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg"
            >
              Cancelar
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
