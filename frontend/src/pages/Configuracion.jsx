import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'
import { Settings, MessageSquare, Bot, CheckCircle, XCircle, Send, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Configuracion() {
  const [whatsappNumero, setWhatsappNumero] = useState('')
  const [whatsappMensaje, setWhatsappMensaje] = useState('Mensaje de prueba desde ERP')
  const [aiMensaje, setAiMensaje] = useState('Hola, ¿puedes responder con OK?')

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
    probarWhatsappMutation.mutate({
      numero: whatsappNumero,
      mensaje: whatsappMensaje
    })
  }

  const probarAI = () => {
    probarAIMutation.mutate({ mensaje: aiMensaje })
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <Settings size={32} className="text-purple-500" />
        <h1 className="text-3xl font-bold">Configuración</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
              • OPENAI_API_KEY
              <br />
              • OPENAI_MODEL (opcional, por defecto: gpt-3.5-turbo)
              <br />
              • OPENAI_BASE_URL (opcional, por defecto: https://api.openai.com/v1)
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
