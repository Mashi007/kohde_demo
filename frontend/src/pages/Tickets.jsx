import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../config/api'
import { MessageSquare, AlertCircle, Plus } from 'lucide-react'
import Modal from '../components/Modal'
import TicketForm from '../components/TicketForm'

export default function Tickets() {
  const [showModal, setShowModal] = useState(false)
  
  const { data: tickets } = useQuery({
    queryKey: ['tickets'],
    queryFn: () => api.get('/crm/tickets').then(res => res.data),
  })

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Tickets</h1>
        <button 
          onClick={() => setShowModal(true)}
          className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Plus size={20} />
          Nuevo Ticket
        </button>
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Nuevo Ticket"
      >
        <TicketForm
          onClose={() => setShowModal(false)}
        />
      </Modal>
      <div className="space-y-4">
        {tickets?.map((ticket) => (
          <div key={ticket.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="flex items-start gap-4">
              <MessageSquare className="text-purple-500" size={24} />
              <div className="flex-1">
                <h3 className="text-lg font-bold">{ticket.asunto}</h3>
                <p className="text-slate-400 mt-1">{ticket.descripcion}</p>
                <div className="mt-4 flex gap-4 text-sm text-slate-400">
                  <span>Estado: {ticket.estado}</span>
                  <span>Prioridad: {ticket.prioridad}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
