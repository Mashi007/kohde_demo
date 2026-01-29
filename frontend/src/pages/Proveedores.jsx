import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../config/api'
import { Truck, Plus } from 'lucide-react'
import Modal from '../components/Modal'
import ProveedorForm from '../components/ProveedorForm'

export default function Proveedores() {
  const [showModal, setShowModal] = useState(false)
  
  const { data: proveedores } = useQuery({
    queryKey: ['proveedores'],
    queryFn: () => api.get('/crm/proveedores').then(res => res.data),
  })

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Proveedores</h1>
        <button 
          onClick={() => setShowModal(true)}
          className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Plus size={20} />
          Nuevo Proveedor
        </button>
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Nuevo Proveedor"
      >
        <ProveedorForm
          onClose={() => setShowModal(false)}
        />
      </Modal>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {proveedores?.map((proveedor) => (
          <div key={proveedor.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <Truck className="text-purple-500 mb-4" size={32} />
            <h3 className="text-xl font-bold mb-2">{proveedor.nombre}</h3>
            <div className="space-y-1 text-sm text-slate-400">
              <p>RUC: {proveedor.ruc || 'N/A'}</p>
              <p>Teléfono: {proveedor.telefono || 'N/A'}</p>
              <p>Email: {proveedor.email || 'N/A'}</p>
              <p>Días de crédito: {proveedor.dias_credito}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
