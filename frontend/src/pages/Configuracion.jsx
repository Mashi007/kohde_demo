import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'
import { Settings, MessageSquare, Bot, CheckCircle, XCircle, Send, RefreshCw, Mail } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Configuracion() {
  const [whatsappNumero, setWhatsappNumero] = useState('')
  const [whatsappMensaje, setWhatsappMensaje] = useState('Mensaje de prueba desde ERP')
  const [aiMensaje, setAiMensaje] = useState('Hola, ¿puedes responder con OK?')
  const [aiToken, setAiToken] = useState('')
  const [aiModelo, setAiModelo] = useState('gpt-3.5-turbo')
  const [aiBaseUrl, setAiBaseUrl] = useState('https://api.openai.com/v1')
  const [emailNotificaciones, setEmailNotificaciones] = useState('')
  const [gmailUsuario, setGmailUsuario] = useState('')
  const [gmailPassword, setGmailPassword] = useState('')
  const [gmailServidor, setGmailServidor] = useState('smtp.gmail.com')
  const [gmailPuerto, setGmailPuerto] = useState('587')
  const [gmailUsarTLS, setGmailUsarTLS] = useState(true)

  const queryClient = useQueryClient()

  // WhatsApp
  const { data: whatsappConfig } = useQuery({
    queryKey: ['whatsapp-config'],
    queryFn: () => api.get('/configuracion/whatsapp').then(res => res.data),
  })

  const { data: whatsappVerificacion, refetch: refetchWhatsapp } = useQuery({
    queryKey: ['whatsapp-verificacion'],
    queryFn: () => api.get('/configuracion/whatsapp/verificar').then(res => res.data),
    enabled: false, // Solo se ejecuta manualmente
  })

  const { data: whatsappPoliticas } = useQuery({
    queryKey: ['whatsapp-politicas'],
    queryFn: () => api.get('/configuracion/whatsapp/politicas').then(res => res.data),
  })

  const probarWhatsappMutation = useMutation({
    mutationFn: (data) => api.post('/configuracion/whatsapp/probar', data),
    onSuccess: (data) => {
      toast.success('Mensaje de WhatsApp enviado correctamente')
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al enviar mensaje')
    },
  })

  // AI
  const { data: aiConfig } = useQuery({
    queryKey: ['ai-config'],
    queryFn: () => api.get('/configuracion/ai').then(res => res.data),
  })

  const { data: aiVerificacion, refetch: refetchAI } = useQuery({
    queryKey: ['ai-verificacion'],
    queryFn: () => api.get('/configuracion/ai/verificar').then(res => res.data),
    enabled: false, // Solo se ejecuta manualmente
  })

  const probarAIMutation = useMutation({
    mutationFn: (data) => api.post('/configuracion/ai/probar', data),
    onSuccess: (data) => {
      toast.success(`AI respondió: ${data.data.respuesta}`)
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al probar AI')
    },
  })

  const actualizarTokenAiMutation = useMutation({
    mutationFn: (data) => api.put('/configuracion/ai/token', data),
    onSuccess: (data) => {
      toast.success(data.data?.mensaje || 'Token actualizado correctamente')
      queryClient.invalidateQueries(['ai-config'])
      setAiToken('') // Limpiar el campo después de guardar
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al actualizar token')
    }
  })

  const verificarWhatsapp = () => {
    refetchWhatsapp()
  }

  const verificarAI = () => {
    refetchAI()
  }

  const probarWhatsapp = () => {
    if (!whatsappNumero.trim()) {
      toast.error('Ingresa un número de teléfono')
      return
    }
    
    // Validación básica del número según políticas (solo dígitos, 10-15 caracteres)
    const numeroLimpio = whatsappNumero.replace(/\D/g, '')
    if (numeroLimpio.length < 10 || numeroLimpio.length > 15) {
      toast.error('El número debe tener entre 10 y 15 dígitos')
      return
    }
    
    // Validación básica del mensaje según políticas
    if (!whatsappMensaje.trim()) {
      toast.error('Por favor ingresa un mensaje')
      return
    }
    
    if (whatsappMensaje.length > 4096) {
      toast.error('El mensaje no puede exceder 4096 caracteres')
      return
    }
    
    probarWhatsappMutation.mutate({
      numero: whatsappNumero,
      mensaje: whatsappMensaje
    })
  }

  const probarAI = () => {
    probarAIMutation.mutate({ mensaje: aiMensaje })
  }

  const guardarTokenAI = () => {
    if (!aiToken.trim()) {
      toast.error('Por favor ingresa un token de OpenAI')
      return
    }
    
    if (!aiToken.startsWith('sk-')) {
      toast.error('El token debe empezar con "sk-"')
      return
    }
    
    actualizarTokenAiMutation.mutate({
      api_key: aiToken,
      modelo: aiModelo || undefined,
      base_url: aiBaseUrl || undefined
    })
  }

  // Notificaciones por Email
  const { data: notificacionesConfig } = useQuery({
    queryKey: ['notificaciones-config'],
    queryFn: () => api.get('/configuracion/notificaciones').then(res => res.data),
  })

  const { data: notificacionesVerificacion, refetch: refetchNotificaciones } = useQuery({
    queryKey: ['notificaciones-verificacion'],
    queryFn: () => api.get('/configuracion/notificaciones/verificar').then(res => res.data),
    enabled: false, // Solo se ejecuta manualmente
  })

  const actualizarEmailMutation = useMutation({
    mutationFn: (data) => api.put('/configuracion/notificaciones', data),
    onSuccess: (data) => {
      toast.success('Email de notificaciones actualizado correctamente')
      queryClient.invalidateQueries(['notificaciones-config'])
      setEmailNotificaciones('')
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al actualizar email')
    },
  })

  const actualizarGmailMutation = useMutation({
    mutationFn: (data) => api.put('/configuracion/notificaciones/gmail', data),
    onSuccess: (data) => {
      toast.success(data.data?.mensaje || 'Configuración de Gmail actualizada correctamente')
      queryClient.invalidateQueries(['notificaciones-config'])
      setGmailUsuario('')
      setGmailPassword('')
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al actualizar configuración de Gmail')
    },
  })

  const probarNotificacionesMutation = useMutation({
    mutationFn: (data) => api.post('/configuracion/notificaciones/probar', data),
    onSuccess: () => {
      toast.success('Email de prueba enviado correctamente')
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al enviar email de prueba')
    },
  })

  const verificarNotificaciones = () => {
    refetchNotificaciones()
  }

  const actualizarEmail = () => {
    if (!emailNotificaciones.trim()) {
      toast.error('Ingresa un email válido')
      return
    }
    actualizarEmailMutation.mutate({ email: emailNotificaciones })
  }

  const probarNotificaciones = () => {
    probarNotificacionesMutation.mutate({ email: emailNotificaciones || notificacionesConfig?.email_notificaciones_pedidos })
  }

  const guardarGmail = () => {
    if (!gmailUsuario.trim()) {
      toast.error('Por favor ingresa el email de Gmail')
      return
    }
    
    if (!gmailPassword.trim()) {
      toast.error('Por favor ingresa la contraseña de aplicación')
      return
    }
    
    if (!gmailUsuario.includes('@gmail.com')) {
      toast.error('El email debe ser de Gmail (@gmail.com)')
      return
    }
    
    actualizarGmailMutation.mutate({
      usuario: gmailUsuario,
      contraseña: gmailPassword,
      password: gmailPassword, // Alias para compatibilidad
      servidor: gmailServidor || undefined,
      puerto: gmailPuerto ? parseInt(gmailPuerto) : undefined,
      usar_tls: gmailUsarTLS
    })
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <Settings size={32} className="text-purple-500" />
        <h1 className="text-3xl font-bold">Configuración</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {/* WhatsApp */}
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center gap-3 mb-4">
            <MessageSquare size={24} className="text-green-500" />
            <h2 className="text-xl font-bold">WhatsApp Business API</h2>
          </div>

          {/* Estado */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-400">Estado:</span>
              {whatsappConfig?.estado === 'configurado' ? (
                <span className="flex items-center gap-1 text-green-400">
                  <CheckCircle size={16} />
                  Configurado
                </span>
              ) : (
                <span className="flex items-center gap-1 text-red-400">
                  <XCircle size={16} />
                  No configurado
                </span>
              )}
            </div>

            {/* Información de configuración */}
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">API URL:</span>
                <span className="text-slate-300">{whatsappConfig?.whatsapp_api_url || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Phone Number ID:</span>
                <span className="text-slate-300">
                  {whatsappConfig?.whatsapp_phone_number_id || 'No configurado'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Access Token:</span>
                <span className="text-slate-300 font-mono text-xs">
                  {whatsappConfig?.whatsapp_access_token_preview || 'No configurado'}
                </span>
              </div>
            </div>
          </div>

          {/* Verificación */}
          {whatsappVerificacion && (
            <div className={`mb-4 p-3 rounded-lg ${
              whatsappVerificacion.valido 
                ? 'bg-green-500/10 border border-green-500/50' 
                : 'bg-red-500/10 border border-red-500/50'
            }`}>
              <p className={`text-sm font-medium ${
                whatsappVerificacion.valido ? 'text-green-400' : 'text-red-400'
              }`}>
                {whatsappVerificacion.mensaje}
              </p>
              {whatsappVerificacion.detalles && (
                <p className="text-xs text-slate-400 mt-1">{whatsappVerificacion.detalles}</p>
              )}
            </div>
          )}

          {/* Botones de acción */}
          <div className="space-y-3">
            <button
              onClick={verificarWhatsapp}
              className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2"
            >
              <RefreshCw size={18} />
              Verificar Configuración
            </button>

            <div className="border-t border-slate-700 pt-3">
              <h3 className="text-sm font-medium mb-2">Enviar Mensaje de Prueba</h3>
              <input
                type="text"
                value={whatsappNumero}
                onChange={(e) => setWhatsappNumero(e.target.value)}
                placeholder="Número (ej: 521234567890)"
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg mb-2 text-sm focus:outline-none focus:border-purple-500"
              />
              <textarea
                value={whatsappMensaje}
                onChange={(e) => setWhatsappMensaje(e.target.value)}
                placeholder="Mensaje de prueba"
                rows={2}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg mb-2 text-sm focus:outline-none focus:border-purple-500"
              />
              <button
                onClick={probarWhatsapp}
                disabled={probarWhatsappMutation.isPending}
                className="w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Send size={18} />
                {probarWhatsappMutation.isPending ? 'Enviando...' : 'Enviar Prueba'}
              </button>
            </div>
          </div>

          {/* Políticas de Configuración */}
          {whatsappPoliticas && (
            <div className="mt-4 p-3 bg-slate-700/50 rounded-lg">
              <h3 className="text-sm font-medium mb-2">Políticas de Configuración</h3>
              <div className="space-y-2 text-xs text-slate-400">
                <div>
                  <strong>Número de Teléfono:</strong> {whatsappPoliticas.numero_telefono.min_longitud}-{whatsappPoliticas.numero_telefono.max_longitud} dígitos
                  <br />
                  <span className="text-slate-500">Ejemplo: {whatsappPoliticas.numero_telefono.ejemplo}</span>
                </div>
                <div>
                  <strong>Mensaje:</strong> Máximo {whatsappPoliticas.mensaje.max_longitud} caracteres
                </div>
                <div>
                  <strong>Access Token:</strong> {whatsappPoliticas.access_token.min_longitud}-{whatsappPoliticas.access_token.max_longitud} caracteres
                  <br />
                  <span className="text-slate-500">{whatsappPoliticas.access_token.seguridad}</span>
                </div>
                <div>
                  <strong>API URL:</strong> {whatsappPoliticas.api_url.ejemplo}
                </div>
              </div>
            </div>
          )}

          {/* Políticas de Configuración */}
          {whatsappPoliticas && (
            <div className="mt-4 p-3 bg-slate-700/50 rounded-lg">
              <h3 className="text-sm font-medium mb-2">Políticas de Configuración</h3>
              <div className="space-y-2 text-xs text-slate-400">
                <div>
                  <strong>Número de Teléfono:</strong> {whatsappPoliticas.numero_telefono.min_longitud}-{whatsappPoliticas.numero_telefono.max_longitud} dígitos
                  <br />
                  <span className="text-slate-500">Ejemplo: {whatsappPoliticas.numero_telefono.ejemplo}</span>
                </div>
                <div>
                  <strong>Mensaje:</strong> Máximo {whatsappPoliticas.mensaje.max_longitud} caracteres
                </div>
                <div>
                  <strong>Access Token:</strong> {whatsappPoliticas.access_token.min_longitud}-{whatsappPoliticas.access_token.max_longitud} caracteres
                  <br />
                  <span className="text-slate-500">{whatsappPoliticas.access_token.seguridad}</span>
                </div>
                <div>
                  <strong>API URL:</strong> {whatsappPoliticas.api_url.ejemplo}
                </div>
              </div>
            </div>
          )}

          {/* Nota */}
          <div className="mt-4 p-3 bg-slate-700/50 rounded-lg">
            <p className="text-xs text-slate-400">
              <strong>Nota:</strong> Las variables de entorno deben configurarse en Render:
              <br />
              • WHATSAPP_ACCESS_TOKEN
              <br />
              • WHATSAPP_PHONE_NUMBER_ID
            </p>
          </div>
        </div>

        {/* AI (OpenAI) */}
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center gap-3 mb-4">
            <Bot size={24} className="text-purple-500" />
            <h2 className="text-xl font-bold">AI (OpenAI)</h2>
          </div>

          {/* Estado */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-400">Estado:</span>
              {aiConfig?.estado === 'configurado' ? (
                <span className="flex items-center gap-1 text-green-400">
                  <CheckCircle size={16} />
                  Configurado
                </span>
              ) : (
                <span className="flex items-center gap-1 text-red-400">
                  <XCircle size={16} />
                  No configurado
                </span>
              )}
            </div>

            {/* Información de configuración */}
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Modelo:</span>
                <span className="text-slate-300">{aiConfig?.openai_model || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Base URL:</span>
                <span className="text-slate-300 text-xs">{aiConfig?.openai_base_url || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">API Key:</span>
                <span className="text-slate-300 font-mono text-xs">
                  {aiConfig?.openai_api_key_preview || 'No configurado'}
                </span>
              </div>
            </div>
          </div>

          {/* Verificación */}
          {aiVerificacion && (
            <div className={`mb-4 p-3 rounded-lg ${
              aiVerificacion.valido 
                ? 'bg-green-500/10 border border-green-500/50' 
                : 'bg-red-500/10 border border-red-500/50'
            }`}>
              <p className={`text-sm font-medium ${
                aiVerificacion.valido ? 'text-green-400' : 'text-red-400'
              }`}>
                {aiVerificacion.mensaje}
              </p>
              {aiVerificacion.detalles && (
                <p className="text-xs text-slate-400 mt-1">{aiVerificacion.detalles}</p>
              )}
            </div>
          )}

          {/* Ingresar Token */}
          <div className="mb-4 p-3 bg-slate-700/50 rounded-lg">
            <h3 className="text-sm font-medium mb-2">Ingresar Token de OpenAI</h3>
            <input
              type="password"
              value={aiToken}
              onChange={(e) => setAiToken(e.target.value)}
              placeholder="sk-..."
              className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg mb-2 text-sm focus:outline-none focus:border-purple-500 font-mono"
            />
            <div className="grid grid-cols-2 gap-2 mb-2">
              <input
                type="text"
                value={aiModelo}
                onChange={(e) => setAiModelo(e.target.value)}
                placeholder="Modelo (ej: gpt-3.5-turbo)"
                className="px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-sm focus:outline-none focus:border-purple-500"
              />
              <input
                type="text"
                value={aiBaseUrl}
                onChange={(e) => setAiBaseUrl(e.target.value)}
                placeholder="Base URL"
                className="px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-sm focus:outline-none focus:border-purple-500"
              />
            </div>
            <button
              onClick={guardarTokenAI}
              disabled={actualizarTokenAiMutation.isPending}
              className="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <Settings size={18} />
              {actualizarTokenAiMutation.isPending ? 'Guardando...' : 'Guardar Token'}
            </button>
            {aiConfig?.token_en_memoria && (
              <p className="text-xs text-yellow-400 mt-2">
                ⚠️ Token guardado en memoria. Se perderá al reiniciar el servidor.
              </p>
            )}
          </div>

          {/* Botones de acción */}
          <div className="space-y-3">
            <button
              onClick={verificarAI}
              className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2"
            >
              <RefreshCw size={18} />
              Verificar Configuración
            </button>

            <div className="border-t border-slate-700 pt-3">
              <h3 className="text-sm font-medium mb-2">Enviar Mensaje de Prueba</h3>
              <textarea
                value={aiMensaje}
                onChange={(e) => setAiMensaje(e.target.value)}
                placeholder="Mensaje de prueba"
                rows={2}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg mb-2 text-sm focus:outline-none focus:border-purple-500"
              />
              <button
                onClick={probarAI}
                disabled={probarAIMutation.isPending}
                className="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Send size={18} />
                {probarAIMutation.isPending ? 'Enviando...' : 'Enviar Prueba'}
              </button>
            </div>
          </div>

          {/* Respuesta del AI */}
          {probarAIMutation.data?.data?.respuesta && (
            <div className="mt-3 p-3 bg-purple-500/10 border border-purple-500/50 rounded-lg">
              <p className="text-xs text-purple-400 font-medium mb-1">Respuesta del AI:</p>
              <p className="text-sm text-slate-300">{probarAIMutation.data.data.respuesta}</p>
              {probarAIMutation.data.data.tokens_usados && (
                <p className="text-xs text-slate-400 mt-1">
                  Tokens usados: {probarAIMutation.data.data.tokens_usados}
                </p>
              )}
            </div>
          )}

          {/* Nota */}
          <div className="mt-4 p-3 bg-slate-700/50 rounded-lg">
            <p className="text-xs text-slate-400">
              <strong>Nota:</strong> Las variables de entorno deben configurarse en Render:
              <br />
              • OPENAI_API_KEY (requerido)
              <br />
              • OPENAI_MODEL (opcional, por defecto: gpt-3.5-turbo)
              <br />
              • OPENAI_BASE_URL (opcional, por defecto: https://api.openai.com/v1)
            </p>
            <div className="mt-3 p-2 bg-blue-600/10 border border-blue-500/50 rounded">
              <p className="text-xs text-blue-300 font-medium mb-1">✨ Acceso a Base de Datos</p>
              <p className="text-xs text-slate-400">
                El AI tiene acceso a PostgreSQL y puede consultar datos directamente. 
                Usa el Chat AI y pregunta sobre inventario, facturas, pedidos, etc. 
                El AI ejecutará consultas SQL de forma segura (solo SELECT).
              </p>
            </div>
          </div>
        </div>

        {/* Notificaciones por Email */}
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="flex items-center gap-3 mb-4">
            <Mail size={24} className="text-blue-500" />
            <h2 className="text-xl font-bold">Notificaciones por Email</h2>
          </div>

          {/* Estado */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-400">Estado:</span>
              {notificacionesConfig?.estado === 'configurado' ? (
                <span className="flex items-center gap-1 text-green-400">
                  <CheckCircle size={16} />
                  Configurado
                </span>
              ) : (
                <span className="flex items-center gap-1 text-red-400">
                  <XCircle size={16} />
                  No configurado
                </span>
              )}
            </div>

            {/* Información de configuración */}
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Proveedor:</span>
                <span className="text-slate-300 capitalize">
                  {notificacionesConfig?.email_provider || 'sendgrid'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Email de notificaciones:</span>
                <span className="text-slate-300 break-all text-right">
                  {notificacionesConfig?.email_notificaciones_pedidos || 'No configurado'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Email remitente:</span>
                <span className="text-slate-300 text-xs">
                  {notificacionesConfig?.email_from || 'N/A'}
                </span>
              </div>
              {notificacionesConfig?.email_provider === 'sendgrid' && (
                <div className="flex justify-between">
                  <span className="text-slate-400">SendGrid API Key:</span>
                  <span className="text-slate-300 font-mono text-xs">
                    {notificacionesConfig?.sendgrid_api_key_preview || 'No configurado'}
                  </span>
                </div>
              )}
              {notificacionesConfig?.email_provider === 'gmail' && (
                <>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Gmail Usuario:</span>
                    <span className="text-slate-300 text-xs">
                      {notificacionesConfig?.gmail_user || 'No configurado'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">SMTP Server:</span>
                    <span className="text-slate-300 text-xs">
                      {notificacionesConfig?.gmail_smtp_server || 'smtp.gmail.com'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">SMTP Port:</span>
                    <span className="text-slate-300 text-xs">
                      {notificacionesConfig?.gmail_smtp_port || '587'}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Verificación */}
          {notificacionesVerificacion && (
            <div className={`mb-4 p-3 rounded-lg ${
              notificacionesVerificacion.valido 
                ? 'bg-green-500/10 border border-green-500/50' 
                : 'bg-red-500/10 border border-red-500/50'
            }`}>
              <p className={`text-sm font-medium ${
                notificacionesVerificacion.valido ? 'text-green-400' : 'text-red-400'
              }`}>
                {notificacionesVerificacion.mensaje}
              </p>
              {notificacionesVerificacion.detalles && (
                <p className="text-xs text-slate-400 mt-1">{notificacionesVerificacion.detalles}</p>
              )}
            </div>
          )}

          {/* Botones de acción */}
          <div className="space-y-3">
            <button
              onClick={verificarNotificaciones}
              className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2"
            >
              <RefreshCw size={18} />
              Verificar Configuración
            </button>

            {/* Configuración de Gmail IMAP */}
            {notificacionesConfig?.email_provider === 'gmail' && (
              <div className="border-t border-slate-700 pt-3 mb-3">
                <h3 className="text-sm font-medium mb-2">Configurar Gmail SMTP</h3>
                <input
                  type="email"
                  value={gmailUsuario}
                  onChange={(e) => setGmailUsuario(e.target.value)}
                  placeholder="usuario@gmail.com"
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg mb-2 text-sm focus:outline-none focus:border-purple-500"
                />
                <input
                  type="password"
                  value={gmailPassword}
                  onChange={(e) => setGmailPassword(e.target.value)}
                  placeholder="Contraseña de aplicación"
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg mb-2 text-sm focus:outline-none focus:border-purple-500"
                />
                <div className="grid grid-cols-2 gap-2 mb-2">
                  <input
                    type="text"
                    value={gmailServidor}
                    onChange={(e) => setGmailServidor(e.target.value)}
                    placeholder="Servidor SMTP"
                    className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm focus:outline-none focus:border-purple-500"
                  />
                  <input
                    type="text"
                    value={gmailPuerto}
                    onChange={(e) => setGmailPuerto(e.target.value)}
                    placeholder="Puerto"
                    className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm focus:outline-none focus:border-purple-500"
                  />
                </div>
                <label className="flex items-center gap-2 mb-2 text-sm text-slate-300">
                  <input
                    type="checkbox"
                    checked={gmailUsarTLS}
                    onChange={(e) => setGmailUsarTLS(e.target.checked)}
                    className="rounded"
                  />
                  Usar TLS
                </label>
                <button
                  onClick={guardarGmail}
                  disabled={actualizarGmailMutation.isPending || !gmailUsuario.trim() || !gmailPassword.trim()}
                  className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <Settings size={18} />
                  {actualizarGmailMutation.isPending ? 'Guardando...' : 'Guardar Configuración Gmail'}
                </button>
                <p className="text-xs text-slate-400 mt-2">
                  💡 Necesitas crear una <strong>contraseña de aplicación</strong> en tu cuenta de Google.
                  <br />
                  Ve a: Cuenta de Google → Seguridad → Contraseñas de aplicaciones
                </p>
              </div>
            )}

            <div className="border-t border-slate-700 pt-3">
              <h3 className="text-sm font-medium mb-2">Actualizar Email de Notificaciones</h3>
              <input
                type="email"
                value={emailNotificaciones}
                onChange={(e) => setEmailNotificaciones(e.target.value)}
                placeholder={notificacionesConfig?.email_notificaciones_pedidos || "Email para notificaciones"}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg mb-2 text-sm focus:outline-none focus:border-purple-500"
              />
              <button
                onClick={actualizarEmail}
                disabled={actualizarEmailMutation.isPending || !emailNotificaciones.trim()}
                className="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 mb-3"
              >
                {actualizarEmailMutation.isPending ? 'Actualizando...' : 'Actualizar Email'}
              </button>
            </div>

            <div className="border-t border-slate-700 pt-3">
              <h3 className="text-sm font-medium mb-2">Enviar Email de Prueba</h3>
              <button
                onClick={probarNotificaciones}
                disabled={probarNotificacionesMutation.isPending}
                className="w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Send size={18} />
                {probarNotificacionesMutation.isPending ? 'Enviando...' : 'Enviar Prueba'}
              </button>
            </div>
          </div>

          {/* Nota */}
          <div className="mt-4 p-3 bg-slate-700/50 rounded-lg">
            <p className="text-xs text-slate-400">
              <strong>Nota:</strong> Las variables de entorno deben configurarse en Render:
              <br />
              {notificacionesConfig?.email_provider === 'sendgrid' ? (
                <>
                  • EMAIL_PROVIDER=sendgrid (o no configurar)
                  <br />
                  • SENDGRID_API_KEY
                  <br />
                  • EMAIL_FROM
                  <br />
                  • EMAIL_NOTIFICACIONES_PEDIDOS (se puede actualizar desde aquí)
                </>
              ) : (
                <>
                  • EMAIL_PROVIDER=gmail
                  <br />
                  • GMAIL_SMTP_USER (email de Gmail)
                  <br />
                  • GMAIL_SMTP_PASSWORD (contraseña de aplicación)
                  <br />
                  • GMAIL_SMTP_SERVER (opcional, por defecto: smtp.gmail.com)
                  <br />
                  • GMAIL_SMTP_PORT (opcional, por defecto: 587)
                  <br />
                  • GMAIL_SMTP_USE_TLS (opcional, por defecto: true)
                  <br />
                  • EMAIL_NOTIFICACIONES_PEDIDOS (se puede actualizar desde aquí)
                </>
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
