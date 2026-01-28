import { useQuery } from '@tanstack/react-query'
import api from '../config/api'
import { MessageSquare, AlertCircle } from 'lucide-react'

export default function Tickets() {
  const { data: tickets } = useQuery({
    queryKey: ['tickets'],
    queryFn: () => api.get('/crm/tickets').then(res => res.data),
  })

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Tickets</h1>
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
