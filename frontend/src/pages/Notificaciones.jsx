import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api, { extractData } from '../config/api'
import { 
  Bell, 
  MessageSquare, 
  Mail, 
  Send, 
  Search, 
  Filter,
  Users,
  MessageCircle,
  ChevronRight,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function Notificaciones() {
  const [contactoSeleccionado, setContactoSeleccionado] = useState(null)
  const [tipoMensaje, setTipoMensaje] = useState('whatsapp') // 'whatsapp' o 'email'
  const [mensaje, setMensaje] = useState('')
  const [asunto, setAsunto] = useState('')
  const [busqueda, setBusqueda] = useState('')
  const [tipoFiltro, setTipoFiltro] = useState(null) // 'email' o 'whatsapp'
  const [proyectoFiltro, setProyectoFiltro] = useState(null)

  const queryClient = useQueryClient()

  // Cargar contactos
  const { data: contactosResponse } = useQuery({
    queryKey: ['contactos', busqueda, tipoFiltro, proyectoFiltro],
    queryFn: () => {
      const params = new URLSearchParams()
      if (busqueda) params.append('busqueda', busqueda)
      if (tipoFiltro) params.append('tipo', tipoFiltro)
      if (proyectoFiltro) params.append('proyecto', proyectoFiltro)
      params.append('activo', 'true')
      return api.get(`/crm/contactos?${params}`).then(extractData)
    },
  })

  // Cargar conversaciones del contacto seleccionado
  const { data: conversacionesResponse } = useQuery({
    queryKey: ['conversaciones', contactoSeleccionado],
    queryFn: () => {
      if (!contactoSeleccionado) return []
      return api.get(`/crm/notificaciones/conversaciones?contacto_id=${contactoSeleccionado}&limit=50`).then(extractData)
    },
    enabled: !!contactoSeleccionado,
  })

  // Cargar estadísticas
  const { data: estadisticas } = useQuery({
    queryKey: ['notificaciones-estadisticas'],
    queryFn: () => api.get('/crm/notificaciones/estadisticas').then(res => res.data),
  })

  const contactos = Array.isArray(contactosResponse) ? contactosResponse : []
  const conversaciones = Array.isArray(conversacionesResponse) ? conversacionesResponse : []

  // Obtener proyectos únicos para filtro
  const proyectos = [...new Set(contactos.map(c => c.proyecto).filter(Boolean))]

  // Obtener último mensaje por contacto
  const ultimosMensajes = {}
  contactos.forEach(contacto => {
    const conversacionesContacto = conversaciones.filter(c => c.contacto_id === contacto.id)
    if (conversacionesContacto.length > 0) {
      ultimosMensajes[contacto.id] = conversacionesContacto[0] // Ya están ordenadas por fecha DESC
    }
  })

  const contactoActual = contactos.find(c => c.id === contactoSeleccionado)

  // Mutación para enviar mensaje
  const enviarMutation = useMutation({
    mutationFn: (data) => api.post('/crm/notificaciones/enviar', data),
    onSuccess: () => {
      toast.success('Mensaje enviado correctamente')
      queryClient.invalidateQueries(['conversaciones'])
      queryClient.invalidateQueries(['notificaciones-estadisticas'])
      setMensaje('')
      setAsunto('')
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al enviar mensaje')
    },
  })

  const handleEnviar = () => {
    if (!contactoSeleccionado) {
      toast.error('Selecciona un contacto')
      return
    }

    if (!mensaje.trim()) {
      toast.error('Escribe un mensaje')
      return
    }

    if (tipoMensaje === 'email' && !asunto.trim()) {
      toast.error('El asunto es requerido para emails')
      return
    }

    // Validar que el contacto tenga el canal configurado
    if (tipoMensaje === 'email' && !contactoActual?.email) {
      toast.error('Este contacto no tiene email configurado')
      return
    }

    if (tipoMensaje === 'whatsapp' && !contactoActual?.whatsapp) {
      toast.error('Este contacto no tiene WhatsApp configurado')
      return
    }

    enviarMutation.mutate({
      contacto_id: contactoSeleccionado,
      tipo: tipoMensaje,
      mensaje: mensaje.trim(),
      asunto: asunto.trim(),
    })
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
    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
  }

  const getEstadoIcon = (estado) => {
    switch (estado) {
      case 'enviado':
        return <CheckCircle size={14} className="text-blue-400" />
      case 'entregado':
        return <CheckCircle size={14} className="text-green-400" />
      case 'leido':
        return <CheckCircle size={14} className="text-purple-400" />
      case 'error':
        return <XCircle size={14} className="text-red-400" />
      default:
        return <Clock size={14} className="text-slate-400" />
    }
  }

  return (
    <div className="flex gap-6 h-[calc(100vh-4rem)]">
      {/* Panel izquierdo: Lista de Contactos */}
      <div className="w-80 bg-slate-800 rounded-lg border border-slate-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-slate-700">
          <div className="flex items-center gap-2 mb-4">
            <Bell size={24} className="text-purple-500" />
            <h1 className="text-xl font-bold">Conversaciones</h1>
          </div>

          {/* Buscador */}
          <div className="relative mb-3">
            <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Buscar contacto..."
              className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm focus:outline-none focus:border-purple-500"
            />
          </div>

          {/* Filtros rápidos */}
          <div className="flex gap-2">
            <button
              onClick={() => setTipoFiltro(null)}
              className={`flex-1 px-2 py-1 rounded text-xs ${
                tipoFiltro === null
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Todos
            </button>
            <button
              onClick={() => setTipoFiltro('proveedor')}
              className={`flex-1 px-2 py-1 rounded text-xs ${
                tipoFiltro === 'proveedor'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Proveedores
            </button>
            <button
              onClick={() => setTipoFiltro('colaborador')}
              className={`flex-1 px-2 py-1 rounded text-xs ${
                tipoFiltro === 'colaborador'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Colaboradores
            </button>
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
                <span className="text-slate-400">Email:</span>
                <p className="font-bold text-blue-400">{estadisticas.total_email || 0}</p>
              </div>
              <div>
                <span className="text-slate-400">WhatsApp:</span>
                <p className="font-bold text-green-400">{estadisticas.total_whatsapp || 0}</p>
              </div>
              <div>
                <span className="text-slate-400">Exitosas:</span>
                <p className="font-bold text-green-400">{estadisticas.total_exitosas || 0}</p>
              </div>
            </div>
          </div>
        )}

        {/* Lista de contactos */}
        <div className="flex-1 overflow-y-auto">
          {contactos.length === 0 ? (
            <div className="p-8 text-center text-slate-400">
              <Users size={32} className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">No hay contactos disponibles</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-700">
              {contactos.map((contacto) => {
                const ultimoMensaje = ultimosMensajes[contacto.id]
                const tieneEmail = !!contacto.email
                const tieneWhatsApp = !!contacto.whatsapp

                return (
                  <button
                    key={contacto.id}
                    onClick={() => {
                      setContactoSeleccionado(contacto.id)
                      // Auto-seleccionar tipo según disponibilidad
                      if (contacto.email && contacto.whatsapp) {
                        setTipoMensaje('whatsapp') // Por defecto WhatsApp
                      } else if (contacto.email) {
                        setTipoMensaje('email')
                      } else if (contacto.whatsapp) {
                        setTipoMensaje('whatsapp')
                      }
                    }}
                    className={`w-full text-left p-4 hover:bg-slate-700/50 transition-colors ${
                      contactoSeleccionado === contacto.id
                        ? 'bg-purple-600/20 border-l-4 border-purple-500'
                        : ''
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-white">{contacto.nombre}</h3>
                          <span className={`text-xs px-1.5 py-0.5 rounded ${
                            contacto.tipo === 'proveedor'
                              ? 'bg-blue-500/20 text-blue-300'
                              : 'bg-green-500/20 text-green-300'
                          }`}>
                            {contacto.tipo === 'proveedor' ? 'P' : 'C'}
                          </span>
                        </div>
                        {contacto.cargo && (
                          <p className="text-xs text-slate-400 mb-1">{contacto.cargo}</p>
                        )}
                        {contacto.proyecto && (
                          <p className="text-xs text-purple-400">{contacto.proyecto}</p>
                        )}
                      </div>
                      <ChevronRight 
                        size={16} 
                        className={`text-slate-400 ${
                          contactoSeleccionado === contacto.id ? 'text-purple-400' : ''
                        }`}
                      />
                    </div>

                    {/* Último mensaje */}
                    {ultimoMensaje && (
                      <div className="mt-2 pt-2 border-t border-slate-700">
                        <div className="flex items-center gap-2 mb-1">
                          {ultimoMensaje.tipo_mensaje === 'email' ? (
                            <Mail size={12} className="text-blue-400" />
                          ) : (
                            <MessageCircle size={12} className="text-green-400" />
                          )}
                          <span className="text-xs text-slate-400 truncate flex-1">
                            {ultimoMensaje.contenido?.substring(0, 40)}...
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-500">
                            {formatearFecha(ultimoMensaje.fecha_envio)}
                          </span>
                          {getEstadoIcon(ultimoMensaje.estado)}
                        </div>
                      </div>
                    )}

                    {/* Indicadores de canales disponibles */}
                    <div className="flex gap-2 mt-2">
                      {tieneEmail && (
                        <span className="text-xs px-1.5 py-0.5 bg-blue-500/20 text-blue-300 rounded">
                          Email
                        </span>
                      )}
                      {tieneWhatsApp && (
                        <span className="text-xs px-1.5 py-0.5 bg-green-500/20 text-green-300 rounded">
                          WhatsApp
                        </span>
                      )}
                      {!tieneEmail && !tieneWhatsApp && (
                        <span className="text-xs px-1.5 py-0.5 bg-red-500/20 text-red-300 rounded">
                          Sin canales
                        </span>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* Panel central: Área de conversación */}
      {contactoSeleccionado && contactoActual ? (
        <div className="flex-1 bg-slate-800 rounded-lg border border-slate-700 flex flex-col">
          {/* Header del contacto */}
          <div className="p-4 border-b border-slate-700">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="text-xl font-bold">{contactoActual.nombre}</h2>
                <div className="flex items-center gap-3 mt-1">
                  {contactoActual.cargo && (
                    <span className="text-sm text-slate-400">{contactoActual.cargo}</span>
                  )}
                  {contactoActual.proyecto && (
                    <span className="text-sm text-purple-400">• {contactoActual.proyecto}</span>
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                {contactoActual.email && (
                  <button
                    onClick={() => setTipoMensaje('email')}
                    className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-2 ${
                      tipoMensaje === 'email'
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    <Mail size={16} />
                    Email
                  </button>
                )}
                {contactoActual.whatsapp && (
                  <button
                    onClick={() => setTipoMensaje('whatsapp')}
                    className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-2 ${
                      tipoMensaje === 'whatsapp'
                        ? 'bg-green-600 text-white'
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    <MessageCircle size={16} />
                    WhatsApp
                  </button>
                )}
              </div>
            </div>

            {/* Información de contacto */}
            <div className="flex gap-4 text-sm text-slate-400">
              {contactoActual.email && (
                <span className="flex items-center gap-1">
                  <Mail size={14} />
                  {contactoActual.email}
                </span>
              )}
              {contactoActual.whatsapp && (
                <span className="flex items-center gap-1">
                  <MessageCircle size={14} />
                  {contactoActual.whatsapp}
                </span>
              )}
            </div>
          </div>

          {/* Historial de conversaciones */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {conversaciones.length === 0 ? (
              <div className="text-center py-12 text-slate-400">
                <MessageSquare size={48} className="mx-auto mb-4 opacity-50" />
                <p>No hay conversaciones aún</p>
                <p className="text-sm mt-2">Envía tu primer mensaje usando el formulario de abajo</p>
              </div>
            ) : (
              conversaciones.map((conv) => (
                <div
                  key={conv.id}
                  className={`flex gap-3 ${
                    conv.direccion === 'enviado' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-[70%] rounded-lg p-3 ${
                      conv.direccion === 'enviado'
                        ? conv.tipo_mensaje === 'email'
                          ? 'bg-blue-600/20 border border-blue-500/50'
                          : 'bg-green-600/20 border border-green-500/50'
                        : 'bg-slate-700 border border-slate-600'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      {conv.tipo_mensaje === 'email' ? (
                        <Mail size={14} className="text-blue-400" />
                      ) : (
                        <MessageCircle size={14} className="text-green-400" />
                      )}
                      <span className="text-xs text-slate-400">
                        {formatearFecha(conv.fecha_envio)}
                      </span>
                      {getEstadoIcon(conv.estado)}
                    </div>
                    {conv.asunto && (
                      <p className="font-semibold text-sm mb-1">{conv.asunto}</p>
                    )}
                    <p className="text-sm whitespace-pre-wrap">{conv.contenido}</p>
                    {conv.error && (
                      <div className="mt-2 p-2 bg-red-500/20 border border-red-500/50 rounded text-xs text-red-300">
                        <AlertCircle size={12} className="inline mr-1" />
                        Error: {conv.error}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Formulario de envío */}
          <div className="p-4 border-t border-slate-700 bg-slate-700/30">
            {tipoMensaje === 'email' && !contactoActual.email ? (
              <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-sm text-red-300">
                Este contacto no tiene email configurado
              </div>
            ) : tipoMensaje === 'whatsapp' && !contactoActual.whatsapp ? (
              <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-sm text-red-300">
                Este contacto no tiene WhatsApp configurado
              </div>
            ) : (
              <div className="space-y-3">
                {tipoMensaje === 'email' && (
                  <input
                    type="text"
                    value={asunto}
                    onChange={(e) => setAsunto(e.target.value)}
                    placeholder="Asunto del email"
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
                  />
                )}
                <div className="flex gap-2">
                  <textarea
                    value={mensaje}
                    onChange={(e) => setMensaje(e.target.value)}
                    placeholder={`Escribe tu mensaje de ${tipoMensaje === 'email' ? 'email' : 'WhatsApp'} aquí...`}
                    rows={3}
                    className="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500 resize-none"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && e.ctrlKey) {
                        handleEnviar()
                      }
                    }}
                  />
                  <button
                    onClick={handleEnviar}
                    disabled={enviarMutation.isPending || !mensaje.trim() || (tipoMensaje === 'email' && !asunto.trim())}
                    className={`px-4 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50 ${
                      tipoMensaje === 'email'
                        ? 'bg-blue-600 hover:bg-blue-700'
                        : 'bg-green-600 hover:bg-green-700'
                    }`}
                  >
                    <Send size={18} />
                    {enviarMutation.isPending ? 'Enviando...' : 'Enviar'}
                  </button>
                </div>
                <p className="text-xs text-slate-500">
                  Presiona Ctrl+Enter para enviar
                </p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex-1 bg-slate-800 rounded-lg border border-slate-700 flex items-center justify-center">
          <div className="text-center text-slate-400">
            <MessageSquare size={64} className="mx-auto mb-4 opacity-50" />
            <p className="text-lg font-semibold mb-2">Selecciona un contacto</p>
            <p className="text-sm">Elige un contacto de la lista para comenzar una conversación</p>
          </div>
        </div>
      )}
    </div>
  )
}
