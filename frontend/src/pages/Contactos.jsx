import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import api, { extractData } from '../config/api'
import ConfirmDialog from '../components/ConfirmDialog'
import { Users, Plus, Edit, Trash2, Mail, MessageCircle, Search, Filter, X } from 'lucide-react'
import Modal from '../components/Modal'
import ContactoForm from '../components/ContactoForm'
import toast from 'react-hot-toast'

export default function Contactos() {
  const [showModal, setShowModal] = useState(false)
  const [contactoSeleccionado, setContactoSeleccionado] = useState(null)
  const [busqueda, setBusqueda] = useState('')
  const [tipoFiltro, setTipoFiltro] = useState(null)
  const [proyectoFiltro, setProyectoFiltro] = useState(null)
  const [contactoEditando, setContactoEditando] = useState(null)
  const [showEmailModal, setShowEmailModal] = useState(false)
  const [showWhatsAppModal, setShowWhatsAppModal] = useState(false)
  const [emailData, setEmailData] = useState({ asunto: '', contenido: '' })
  const [whatsappMensaje, setWhatsappMensaje] = useState('')

  const queryClient = useQueryClient()

  // Cargar contactos con filtros
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

  // Obtener proyectos únicos para filtro
  const proyectos = [...new Set(
    (Array.isArray(contactosResponse) ? contactosResponse : [])
      .map(c => c.proyecto)
      .filter(Boolean)
  )]

  const contactos = Array.isArray(contactosResponse) ? contactosResponse : []

  // Mutaciones
  const eliminarMutation = useMutation({
    mutationFn: (id) => api.delete(`/crm/contactos/${id}`),
    onSuccess: () => {
      toast.success('Contacto eliminado correctamente')
      queryClient.invalidateQueries(['contactos'])
      setContactoSeleccionado(null)
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al eliminar contacto')
    },
  })

  const enviarEmailMutation = useMutation({
    mutationFn: ({ contactoId, asunto, contenido }) =>
      api.post(`/crm/contactos/${contactoId}/email`, { asunto, contenido }),
    onSuccess: () => {
      toast.success('Email enviado correctamente')
      setShowEmailModal(false)
      setEmailData({ asunto: '', contenido: '' })
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al enviar email')
    },
  })

  const enviarWhatsAppMutation = useMutation({
    mutationFn: ({ contactoId, mensaje }) =>
      api.post(`/crm/contactos/${contactoId}/whatsapp`, { mensaje }),
    onSuccess: () => {
      toast.success('Mensaje de WhatsApp enviado correctamente')
      setShowWhatsAppModal(false)
      setWhatsappMensaje('')
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al enviar WhatsApp')
    },
  })

  const [confirmarEliminar, setConfirmarEliminar] = useState(false)

  const handleEliminar = () => {
    setConfirmarEliminar(true)
  }

  const confirmarEliminacion = () => {
    if (contactoSeleccionado) {
      eliminarMutation.mutate(contactoSeleccionado)
      setConfirmarEliminar(false)
    }
  }

  const handleEditar = () => {
    const contacto = contactos?.find(c => c.id === contactoSeleccionado)
    setContactoEditando(contacto)
    setShowModal(true)
  }

  const handleSave = (formData) => {
    if (contactoEditando) {
      api.put(`/crm/contactos/${contactoEditando.id}`, formData)
        .then(() => {
          toast.success('Contacto actualizado correctamente')
          queryClient.invalidateQueries(['contactos'])
          setShowModal(false)
          setContactoEditando(null)
        })
        .catch((error) => {
          toast.error(error.response?.data?.error || 'Error al actualizar contacto')
        })
    } else {
      api.post('/crm/contactos', formData)
        .then(() => {
          toast.success('Contacto creado correctamente')
          queryClient.invalidateQueries(['contactos'])
          setShowModal(false)
        })
        .catch((error) => {
          toast.error(error.response?.data?.error || 'Error al crear contacto')
        })
    }
  }

  const contactoActual = contactos?.find(c => c.id === contactoSeleccionado)

  const handleEnviarEmail = () => {
    if (!emailData.asunto || !emailData.contenido) {
      toast.error('Completa todos los campos')
      return
    }
    enviarEmailMutation.mutate({
      contactoId: contactoSeleccionado,
      ...emailData
    })
  }

  const handleEnviarWhatsApp = () => {
    if (!whatsappMensaje.trim()) {
      toast.error('Ingresa un mensaje')
      return
    }
    enviarWhatsAppMutation.mutate({
      contactoId: contactoSeleccionado,
      mensaje: whatsappMensaje
    })
  }

  return (
    <>
      <ConfirmDialog
        isOpen={confirmarEliminar}
        onClose={() => setConfirmarEliminar(false)}
        onConfirm={confirmarEliminacion}
        title="Eliminar contacto"
        message="¿Estás seguro de eliminar este contacto? Esta acción no se puede deshacer."
        confirmText="Eliminar"
        cancelText="Cancelar"
        variant="danger"
        isLoading={eliminarMutation.isPending}
      />

      {/* Modal de Email */}
      <Modal
        isOpen={showEmailModal}
        onClose={() => setShowEmailModal(false)}
        title={`Enviar Email a ${contactoActual?.nombre}`}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Asunto *</label>
            <input
              type="text"
              value={emailData.asunto}
              onChange={(e) => setEmailData({ ...emailData, asunto: e.target.value })}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Asunto del email"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Contenido *</label>
            <textarea
              value={emailData.contenido}
              onChange={(e) => setEmailData({ ...emailData, contenido: e.target.value })}
              rows={6}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Escribe tu mensaje aquí..."
            />
          </div>
          <div className="flex justify-end gap-3">
            <button
              onClick={() => setShowEmailModal(false)}
              className="px-4 py-2 bg-slate-600 hover:bg-slate-700 rounded-lg"
            >
              Cancelar
            </button>
            <button
              onClick={handleEnviarEmail}
              disabled={enviarEmailMutation.isPending}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50"
            >
              {enviarEmailMutation.isPending ? 'Enviando...' : 'Enviar Email'}
            </button>
          </div>
        </div>
      </Modal>

      {/* Modal de WhatsApp */}
      <Modal
        isOpen={showWhatsAppModal}
        onClose={() => setShowWhatsAppModal(false)}
        title={`Enviar WhatsApp a ${contactoActual?.nombre}`}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Mensaje *</label>
            <textarea
              value={whatsappMensaje}
              onChange={(e) => setWhatsappMensaje(e.target.value)}
              rows={6}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
              placeholder="Escribe tu mensaje de WhatsApp aquí..."
            />
          </div>
          <div className="flex justify-end gap-3">
            <button
              onClick={() => setShowWhatsAppModal(false)}
              className="px-4 py-2 bg-slate-600 hover:bg-slate-700 rounded-lg"
            >
              Cancelar
            </button>
            <button
              onClick={handleEnviarWhatsApp}
              disabled={enviarWhatsAppMutation.isPending}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg disabled:opacity-50"
            >
              {enviarWhatsAppMutation.isPending ? 'Enviando...' : 'Enviar WhatsApp'}
            </button>
          </div>
        </div>
      </Modal>

      {/* Modal de Formulario */}
      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false)
          setContactoEditando(null)
        }}
        title={contactoEditando ? 'Editar Contacto' : 'Nuevo Contacto'}
      >
        <ContactoForm
          contacto={contactoEditando}
          onClose={() => {
            setShowModal(false)
            setContactoEditando(null)
          }}
          onSave={handleSave}
        />
      </Modal>

      <div className="flex gap-6 h-[calc(100vh-4rem)]">
        {/* Panel izquierdo: Filtros */}
        <div className="w-64 bg-slate-800 rounded-lg border border-slate-700 p-4 overflow-y-auto">
          <div className="flex items-center gap-2 mb-4">
            <Filter size={20} className="text-purple-500" />
            <h2 className="text-lg font-bold">Filtros</h2>
          </div>

          {/* Buscador */}
          <div className="mb-4">
            <div className="relative">
              <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                placeholder="Buscar contacto..."
                className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-sm focus:outline-none focus:border-purple-500"
              />
            </div>
          </div>

          {/* Filtro por Tipo */}
          <div className="mb-4">
            <h3 className="text-sm font-semibold mb-2 text-slate-300">Tipo</h3>
            <button
              onClick={() => setTipoFiltro(null)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm mb-2 transition-colors ${
                tipoFiltro === null
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Todos
            </button>
            <button
              onClick={() => setTipoFiltro('proveedor')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm mb-1 transition-colors ${
                tipoFiltro === 'proveedor'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Proveedores
            </button>
            <button
              onClick={() => setTipoFiltro('colaborador')}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                tipoFiltro === 'colaborador'
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Colaboradores
            </button>
          </div>

          {/* Filtro por Proyecto */}
          {proyectos.length > 0 && (
            <div className="mb-4">
              <h3 className="text-sm font-semibold mb-2 text-slate-300">Proyecto</h3>
              <button
                onClick={() => setProyectoFiltro(null)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm mb-2 transition-colors ${
                  proyectoFiltro === null
                    ? 'bg-purple-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                Todos los proyectos
              </button>
              {proyectos.map((proyecto) => (
                <button
                  key={proyecto}
                  onClick={() => setProyectoFiltro(proyecto)}
                  className={`w-full text-left px-3 py-1.5 rounded-lg text-xs mb-1 transition-colors ${
                    proyectoFiltro === proyecto
                      ? 'bg-purple-600 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  {proyecto}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Panel central: Lista de Contactos */}
        <div className="flex-1 bg-slate-800 rounded-lg border border-slate-700 p-6 overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold">Contactos</h1>
            <button
              onClick={() => {
                setContactoEditando(null)
                setShowModal(true)
              }}
              className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2"
            >
              <Plus size={20} />
              Nuevo Contacto
            </button>
          </div>

          {(tipoFiltro || proyectoFiltro) && (
            <div className="mb-4 p-3 bg-purple-600/20 border border-purple-500/50 rounded-lg flex items-center justify-between">
              <span className="text-sm text-purple-300">
                Filtros activos: {tipoFiltro && `Tipo: ${tipoFiltro}`} {proyectoFiltro && `| Proyecto: ${proyectoFiltro}`}
              </span>
              <button
                onClick={() => {
                  setTipoFiltro(null)
                  setProyectoFiltro(null)
                }}
                className="text-purple-300 hover:text-white"
              >
                <X size={18} />
              </button>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {contactos?.map((contacto) => (
              <div
                key={contacto.id}
                onClick={() => setContactoSeleccionado(contacto.id)}
                className={`bg-slate-700 p-4 rounded-lg border cursor-pointer transition-all ${
                  contactoSeleccionado === contacto.id
                    ? 'border-purple-500 bg-purple-600/20'
                    : 'border-slate-600 hover:border-slate-500'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Users className="text-purple-500" size={24} />
                    <div>
                      <h3 className="text-lg font-bold">{contacto.nombre}</h3>
                      <span className={`text-xs px-2 py-1 rounded ${
                        contacto.tipo === 'proveedor'
                          ? 'bg-blue-500/20 text-blue-300'
                          : 'bg-green-500/20 text-green-300'
                      }`}>
                        {contacto.tipo === 'proveedor' ? 'Proveedor' : 'Colaborador'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="space-y-1 text-sm text-slate-400">
                  {contacto.cargo && <p>Cargo: {contacto.cargo}</p>}
                  {contacto.proyecto && <p>Proyecto: {contacto.proyecto}</p>}
                  {contacto.email && <p>Email: {contacto.email}</p>}
                  {contacto.whatsapp && <p>WhatsApp: {contacto.whatsapp}</p>}
                  {contacto.proveedor && <p>Proveedor: {contacto.proveedor.nombre}</p>}
                </div>
              </div>
            ))}
          </div>

          {contactos.length === 0 && (
            <div className="text-center py-12 text-slate-400">
              <Users size={48} className="mx-auto mb-4 opacity-50" />
              <p>No hay contactos disponibles</p>
            </div>
          )}
        </div>

        {/* Panel derecho: Detalle del Contacto */}
        {contactoActual && (
          <div className="w-96 bg-slate-800 rounded-lg border border-slate-700 p-6 overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-bold">{contactoActual.nombre}</h2>
              <button
                onClick={() => setContactoSeleccionado(null)}
                className="text-slate-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <span className="text-sm text-slate-400">Tipo:</span>
                <p className="font-medium">{contactoActual.tipo === 'proveedor' ? 'Proveedor' : 'Colaborador'}</p>
              </div>

              {contactoActual.cargo && (
                <div>
                  <span className="text-sm text-slate-400">Cargo:</span>
                  <p className="font-medium">{contactoActual.cargo}</p>
                </div>
              )}

              {contactoActual.proyecto && (
                <div>
                  <span className="text-sm text-slate-400">Proyecto:</span>
                  <p className="font-medium">{contactoActual.proyecto}</p>
                </div>
              )}

              {contactoActual.email && (
                <div>
                  <span className="text-sm text-slate-400">Email:</span>
                  <p className="font-medium">{contactoActual.email}</p>
                </div>
              )}

              {contactoActual.whatsapp && (
                <div>
                  <span className="text-sm text-slate-400">WhatsApp:</span>
                  <p className="font-medium">{contactoActual.whatsapp}</p>
                </div>
              )}

              {contactoActual.telefono && (
                <div>
                  <span className="text-sm text-slate-400">Teléfono:</span>
                  <p className="font-medium">{contactoActual.telefono}</p>
                </div>
              )}

              {contactoActual.proveedor && (
                <div>
                  <span className="text-sm text-slate-400">Proveedor Asociado:</span>
                  <p className="font-medium">{contactoActual.proveedor.nombre}</p>
                </div>
              )}

              {contactoActual.notas && (
                <div>
                  <span className="text-sm text-slate-400">Notas:</span>
                  <p className="text-sm">{contactoActual.notas}</p>
                </div>
              )}

              <div className="pt-4 border-t border-slate-700 space-y-2">
                {contactoActual.email && (
                  <button
                    onClick={() => {
                      setEmailData({ asunto: '', contenido: '' })
                      setShowEmailModal(true)
                    }}
                    className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2"
                  >
                    <Mail size={18} />
                    Enviar Email
                  </button>
                )}

                {contactoActual.whatsapp && (
                  <button
                    onClick={() => {
                      setWhatsappMensaje('')
                      setShowWhatsAppModal(true)
                    }}
                    className="w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2"
                  >
                    <MessageCircle size={18} />
                    Enviar WhatsApp
                  </button>
                )}

                <button
                  onClick={handleEditar}
                  className="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2"
                >
                  <Edit size={18} />
                  Editar
                </button>

                <button
                  onClick={handleEliminar}
                  className="w-full bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2"
                >
                  <Trash2 size={18} />
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
