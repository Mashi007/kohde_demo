import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import api, { extractData } from '../config/api'
import { X } from 'lucide-react'

export default function ContactoForm({ contacto, onClose, onSave }) {
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    whatsapp: '',
    telefono: '',
    proyecto: '',
    cargo: '',
    tipo: 'proveedor',
    proveedor_id: null,
    notas: '',
  })

  // Cargar proveedores para el select
  const { data: proveedoresResponse } = useQuery({
    queryKey: ['proveedores'],
    queryFn: () => api.get('/crm/proveedores?activo=true&limit=1000').then(extractData),
  })

  const proveedores = Array.isArray(proveedoresResponse) ? proveedoresResponse : []

  useEffect(() => {
    if (contacto) {
      setFormData({
        nombre: contacto.nombre || '',
        email: contacto.email || '',
        whatsapp: contacto.whatsapp || '',
        telefono: contacto.telefono || '',
        proyecto: contacto.proyecto || '',
        cargo: contacto.cargo || '',
        tipo: contacto.tipo || 'proveedor',
        proveedor_id: contacto.proveedor_id || null,
        notas: contacto.notas || '',
      })
    }
  }, [contacto])

  const handleSubmit = (e) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Nombre */}
        <div>
          <label className="block text-sm font-medium mb-1">Nombre *</label>
          <input
            type="text"
            value={formData.nombre}
            onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
            required
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>

        {/* Tipo */}
        <div>
          <label className="block text-sm font-medium mb-1">Tipo *</label>
          <select
            value={formData.tipo}
            onChange={(e) => setFormData({ ...formData, tipo: e.target.value, proveedor_id: e.target.value === 'colaborador' ? null : formData.proveedor_id })}
            required
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          >
            <option value="proveedor">Proveedor</option>
            <option value="colaborador">Colaborador</option>
          </select>
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>

        {/* WhatsApp */}
        <div>
          <label className="block text-sm font-medium mb-1">WhatsApp</label>
          <input
            type="text"
            value={formData.whatsapp}
            onChange={(e) => setFormData({ ...formData, whatsapp: e.target.value })}
            placeholder="+1234567890"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>

        {/* Teléfono */}
        <div>
          <label className="block text-sm font-medium mb-1">Teléfono</label>
          <input
            type="text"
            value={formData.telefono}
            onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>

        {/* Proyecto */}
        <div>
          <label className="block text-sm font-medium mb-1">Proyecto</label>
          <input
            type="text"
            value={formData.proyecto}
            onChange={(e) => setFormData({ ...formData, proyecto: e.target.value })}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>

        {/* Cargo */}
        <div>
          <label className="block text-sm font-medium mb-1">Cargo</label>
          <input
            type="text"
            value={formData.cargo}
            onChange={(e) => setFormData({ ...formData, cargo: e.target.value })}
            placeholder="Ej: Gerente de Compras, Chef Ejecutivo"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
          />
        </div>

        {/* Proveedor (solo si tipo es proveedor) */}
        {formData.tipo === 'proveedor' && (
          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-1">Proveedor Asociado</label>
            <select
              value={formData.proveedor_id || ''}
              onChange={(e) => setFormData({ ...formData, proveedor_id: e.target.value ? parseInt(e.target.value) : null })}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
            >
              <option value="">Seleccionar proveedor (opcional)</option>
              {proveedores.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nombre}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Notas */}
      <div>
        <label className="block text-sm font-medium mb-1">Notas</label>
        <textarea
          value={formData.notas}
          onChange={(e) => setFormData({ ...formData, notas: e.target.value })}
          rows={3}
          className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        />
      </div>

      {/* Botones */}
      <div className="flex justify-end gap-3 pt-4 border-t border-slate-700">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 bg-slate-600 hover:bg-slate-700 rounded-lg transition-colors"
        >
          Cancelar
        </button>
        <button
          type="submit"
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
        >
          {contacto ? 'Actualizar' : 'Crear'} Contacto
        </button>
      </div>
    </form>
  )
}
