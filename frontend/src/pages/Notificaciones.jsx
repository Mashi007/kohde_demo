import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'
import { Bell, MessageSquare, Mail, Send, Plus } from 'lucide-react'
import toast from 'react-hot-toast'
import Modal from '../components/Modal'

export default function Notificaciones() {
  const [showModal, setShowModal] = useState(false)
  const [tipoNotificacion, setTipoNotificacion] = useState('whatsapp')
  const [destinatario, setDestinatario] = useState('')
  const [asunto, setAsunto] = useState('')
  const [mensaje, setMensaje] = useState('')

  const queryClient = useQueryClient()

  const { data: notificaciones } = useQuery({
    queryKey: ['notificaciones'],
    queryFn: () => api.get('/crm/notificaciones').then(res => res.data),
  })

  const enviarMutation = useMutation({
    mutationFn: (data) => api.post('/crm/notificaciones/enviar', data),
    onSuccess: (data) => {
      toast.success('Notificación enviada correctamente')
      queryClient.invalidateQueries(['notificaciones'])
      setShowModal(false)
      setDestinatario('')
      setAsunto('')
      setMensaje('')
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al enviar notificación')
    },
  })

  const handleEnviar = () => {
    if (!destinatario.trim() || !mensaje.trim()) {
      toast.error('Destinatario y mensaje son requeridos')
      return
    }

    if (tipoNotificacion === 'email' && !asunto.trim()) {
      toast.error('El asunto es requerido para emails')
      return
    }

    enviarMutation.mutate({
      tipo: tipoNotificacion,
      destinatario: destinatario.trim(),
      mensaje: mensaje.trim(),
      asunto: asunto.trim(),
    })
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <Bell size={32} className="text-purple-500" />
          <h1 className="text-3xl font-bold">Notificaciones</h1>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Plus size={20} />
          Nueva Notificación
        </button>
      </div>

      {/* Modal para enviar notificación */}
      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false)
          setDestinatario('')
          setAsunto('')
          setMensaje('')
        }}
        title="Enviar Notificación"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Tipo de Notificación *</label>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setTipoNotificacion('whatsapp')}
                className={`flex-1 px-4 py-2 rounded-lg border-2 transition-colors ${
                  tipoNotificacion === 'whatsapp'
                    ? 'border-green-500 bg-green-500/20 text-green-400'
                    : 'border-slate-600 bg-slate-700 text-slate-300 hover:border-slate-500'
                }`}
              >
                <MessageSquare size={20} className="mx-auto mb-1" />
                WhatsApp
              </button>
              <button
                type="button"
                onClick={() => setTipoNotificacion('email')}
                className={`flex-1 px-4 py-2 rounded-lg border-2 transition-colors ${
                  tipoNotificacion === 'email'
                    ? 'border-blue-500 bg-blue-500/20 text-blue-400'
                    : 'border-slate-600 bg-slate-700 text-slate-300 hover:border-slate-500'
                }`}
              >
                <Mail size={20} className="mx-auto mb-1" />
                Email
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              {tipoNotificacion === 'whatsapp' ? 'Número de Teléfono' : 'Email'} *
            </label>
            <input
              type={tipoNotificacion === 'whatsapp' ? 'tel' : 'email'}
              value={destinatario}
              onChange={(e) => setDestinatario(e.target.value)}
              placeholder={tipoNotificacion === 'whatsapp' ? '521234567890' : 'ejemplo@email.com'}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
            />
          </div>

          {tipoNotificacion === 'email' && (
            <div>
              <label className="block text-sm font-medium mb-2">Asunto *</label>
              <input
                type="text"
                value={asunto}
                onChange={(e) => setAsunto(e.target.value)}
                placeholder="Asunto del email"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">Mensaje *</label>
            <textarea
              value={mensaje}
              onChange={(e) => setMensaje(e.target.value)}
              rows={6}
              placeholder="Escribe tu mensaje aquí..."
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
            />
          </div>

          <div className="flex gap-4 pt-4">
            <button
              onClick={handleEnviar}
              disabled={enviarMutation.isPending}
              className="flex-1 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <Send size={18} />
              {enviarMutation.isPending ? 'Enviando...' : 'Enviar Notificación'}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowModal(false)
                setDestinatario('')
                setAsunto('')
                setMensaje('')
              }}
              className="flex-1 bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg"
            >
              Cancelar
            </button>
          </div>
        </div>
      </Modal>

      {/* Lista de notificaciones */}
      <div className="space-y-4">
        {notificaciones?.notificaciones?.length === 0 ? (
          <div className="bg-slate-800 p-8 rounded-lg border border-slate-700 text-center">
            <Bell size={48} className="mx-auto text-slate-500 mb-4" />
            <p className="text-slate-400">No hay notificaciones registradas</p>
            <p className="text-sm text-slate-500 mt-2">
              Envía tu primera notificación usando el botón "Nueva Notificación"
            </p>
          </div>
        ) : (
          notificaciones?.notificaciones?.map((notif, index) => (
            <div key={index} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <div className="flex items-start gap-4">
                {notif.tipo === 'whatsapp' ? (
                  <MessageSquare className="text-green-500" size={24} />
                ) : (
                  <Mail className="text-blue-500" size={24} />
                )}
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-bold">
                      {notif.tipo === 'whatsapp' ? 'WhatsApp' : 'Email'}
                    </h3>
                    <span className="text-xs text-slate-400">
                      {new Date(notif.fecha).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-slate-300 mb-1">
                    <strong>Para:</strong> {notif.destinatario}
                  </p>
                  {notif.asunto && (
                    <p className="text-slate-300 mb-2">
                      <strong>Asunto:</strong> {notif.asunto}
                    </p>
                  )}
                  <p className="text-slate-400">{notif.mensaje}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
