import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'
import { Send, Bot, User, Plus, Trash2, MessageSquare } from 'lucide-react'
import toast from 'react-hot-toast'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import ConfirmDialog from '../components/ConfirmDialog'

export default function Chat() {
  const [conversacionActual, setConversacionActual] = useState(null)
  const [mensaje, setMensaje] = useState('')
  const [contextoModulo, setContextoModulo] = useState('')
  const [confirmarEliminar, setConfirmarEliminar] = useState(null)
  const messagesEndRef = useRef(null)
  const queryClient = useQueryClient()

  const { data: conversaciones } = useQuery({
    queryKey: ['conversaciones'],
    queryFn: () => api.get('/chat/conversaciones?activa=true').then(res => res.data),
  })

  const { data: mensajes, isLoading: cargandoMensajes } = useQuery({
    queryKey: ['mensajes', conversacionActual],
    queryFn: () => 
      api.get(`/chat/conversaciones/${conversacionActual}/mensajes`).then(res => res.data),
    enabled: !!conversacionActual,
  })

  const crearConversacionMutation = useMutation({
    mutationFn: (data) => api.post('/chat/conversaciones', data),
    onSuccess: (data) => {
      setConversacionActual(data.data.id)
      queryClient.invalidateQueries(['conversaciones'])
      toast.success('Nueva conversación creada')
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al crear conversación')
    },
  })

  const enviarMensajeMutation = useMutation({
    mutationFn: (contenido) => 
      api.post(`/chat/conversaciones/${conversacionActual}/mensajes`, { contenido }),
    onSuccess: () => {
      setMensaje('')
      queryClient.invalidateQueries(['mensajes', conversacionActual])
      queryClient.invalidateQueries(['conversaciones'])
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al enviar mensaje')
    },
  })

  const eliminarConversacionMutation = useMutation({
    mutationFn: (id) => api.delete(`/chat/conversaciones/${id}`),
    onSuccess: () => {
      if (conversacionActual === id) {
        setConversacionActual(null)
      }
      queryClient.invalidateQueries(['conversaciones'])
      toast.success('Conversación eliminada')
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al eliminar conversación')
    },
  })

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [mensajes])

  const crearNuevaConversacion = () => {
    crearConversacionMutation.mutate({
      titulo: 'Nueva conversación',
      contexto_modulo: contextoModulo || null
    })
  }

  const enviarMensaje = (e) => {
    e.preventDefault()
    if (!mensaje.trim() || !conversacionActual) return
    
    if (!conversacionActual) {
      // Crear conversación automáticamente si no existe
      crearConversacionMutation.mutate({
        contexto_modulo: contextoModulo || null
      }, {
        onSuccess: (data) => {
          setConversacionActual(data.data.id)
          // Enviar mensaje después de crear conversación
          setTimeout(() => {
            enviarMensajeMutation.mutate(mensaje)
          }, 500)
        }
      })
    } else {
      enviarMensajeMutation.mutate(mensaje)
    }
  }

  const seleccionarConversacion = (id) => {
    setConversacionActual(id)
  }

  const eliminarConversacion = (id, e) => {
    e.stopPropagation()
    setConfirmarEliminar(id)
  }

  const confirmarEliminacion = () => {
    if (confirmarEliminar) {
      eliminarConversacionMutation.mutate(confirmarEliminar)
      setConfirmarEliminar(null)
    }
  }

  return (
    <>
      <ConfirmDialog
        isOpen={!!confirmarEliminar}
        onClose={() => setConfirmarEliminar(null)}
        onConfirm={confirmarEliminacion}
        title="Eliminar conversación"
        message="¿Estás seguro de eliminar esta conversación? Esta acción no se puede deshacer."
        confirmText="Eliminar"
        cancelText="Cancelar"
        variant="danger"
        isLoading={eliminarConversacionMutation.isPending}
      />
      <div className="flex h-[calc(100vh-4rem)] bg-slate-900">
      {/* Sidebar de conversaciones */}
      <div className="w-80 bg-slate-800 border-r border-slate-700 flex flex-col">
        <div className="p-4 border-b border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <MessageSquare size={24} />
              Chat AI
            </h2>
            <button
              onClick={crearNuevaConversacion}
              className="bg-purple-600 hover:bg-purple-700 p-2 rounded-lg"
              title="Nueva conversación"
            >
              <Plus size={20} />
            </button>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Contexto del Módulo</label>
            <select
              value={contextoModulo}
              onChange={(e) => setContextoModulo(e.target.value)}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm focus:outline-none focus:border-purple-500"
            >
              <option value="">General</option>
              <option value="crm">CRM</option>
              <option value="logistica">Logística</option>
              <option value="contabilidad">Contabilidad</option>
              <option value="planificacion">Planificación</option>
              <option value="reportes">Reportes</option>
            </select>
          </div>
          
          <div className="mt-3 p-2 bg-blue-600/10 border border-blue-500/50 rounded">
            <p className="text-xs text-blue-300 font-medium mb-1">💡 Acceso a Base de Datos</p>
            <p className="text-xs text-slate-400">
              Puedes preguntar sobre datos del sistema. El AI consultará PostgreSQL automáticamente.
              <br />
              Ejemplos: "¿Cuántos items hay en inventario?", "Muéstrame las facturas recientes", etc.
            </p>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {conversaciones?.map((conv) => (
            <div
              key={conv.id}
              onClick={() => seleccionarConversacion(conv.id)}
              className={`p-3 mb-2 rounded-lg cursor-pointer transition-colors ${
                conversacionActual === conv.id
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 hover:bg-slate-600 text-slate-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{conv.titulo || 'Sin título'}</p>
                  <p className="text-xs opacity-75 mt-1">
                    {format(new Date(conv.fecha_actualizacion), 'dd MMM HH:mm', { locale: es })}
                  </p>
                </div>
                <button
                  onClick={(e) => eliminarConversacion(conv.id, e)}
                  className="ml-2 text-red-400 hover:text-red-300"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Área de chat */}
      <div className="flex-1 flex flex-col bg-slate-900">
        {conversacionActual ? (
          <div className="flex-1 flex flex-col">
            {/* Mensajes */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {cargandoMensajes ? (
                <div className="text-center py-8 text-slate-400">Cargando mensajes...</div>
              ) : mensajes?.length === 0 ? (
                <div className="text-center py-8 text-slate-400">
                  <Bot size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Inicia la conversación enviando un mensaje</p>
                </div>
              ) : (
                mensajes?.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex gap-3 ${
                      msg.tipo === 'usuario' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {msg.tipo === 'asistente' && (
                      <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0">
                        <Bot size={18} />
                      </div>
                    )}
                    <div
                      className={`max-w-[70%] rounded-lg p-4 ${
                        msg.tipo === 'usuario'
                          ? 'bg-purple-600 text-white'
                          : 'bg-slate-800 text-slate-200 border border-slate-700'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{msg.contenido}</p>
                      <p className="text-xs opacity-75 mt-2">
                        {format(new Date(msg.fecha_envio), 'HH:mm', { locale: es })}
                      </p>
                    </div>
                    {msg.tipo === 'usuario' && (
                      <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center flex-shrink-0">
                        <User size={18} />
                      </div>
                    )}
                  </div>
                ))
              )}
              {enviarMensajeMutation.isPending && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center">
                    <Bot size={18} />
                  </div>
                  <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input de mensaje */}
            <form onSubmit={enviarMensaje} className="p-4 border-t border-slate-700">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={mensaje}
                  onChange={(e) => setMensaje(e.target.value)}
                  placeholder="Escribe tu mensaje..."
                  className="flex-1 px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:border-purple-500 text-white"
                  disabled={enviarMensajeMutation.isPending}
                />
                <button
                  type="submit"
                  disabled={!mensaje.trim() || enviarMensajeMutation.isPending}
                  className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Send size={20} />
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <Bot size={64} className="mx-auto mb-4 text-purple-500 opacity-50" />
              <h3 className="text-xl font-bold mb-2">Selecciona una conversación</h3>
              <p className="text-slate-400 mb-4">o crea una nueva para comenzar</p>
              <button
                onClick={crearNuevaConversacion}
                className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-lg"
              >
                Nueva Conversación
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
