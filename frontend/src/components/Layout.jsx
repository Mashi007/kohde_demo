import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Users, 
  MessageSquare, 
  FileText, 
  Package, 
  ShoppingCart,
  ChefHat,
  Calendar,
  Truck,
  ClipboardList,
  BarChart3,
  AlertTriangle
} from 'lucide-react'

const menuItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/tickets', label: 'Tickets', icon: MessageSquare },
  { path: '/facturas', label: 'Facturas', icon: FileText },
  { path: '/inventario', label: 'Inventario', icon: Package },
  { path: '/items', label: 'Items', icon: ShoppingCart },
  { path: '/recetas', label: 'Recetas', icon: ChefHat },
  { path: '/programacion', label: 'Programación', icon: Calendar },
  { path: '/proveedores', label: 'Proveedores', icon: Truck },
  { path: '/pedidos', label: 'Pedidos', icon: ClipboardList },
  { path: '/charolas', label: 'Charolas', icon: BarChart3 },
  { path: '/mermas', label: 'Mermas', icon: AlertTriangle },
]

export default function Layout({ children }) {
  const location = useLocation()

  return (
    <div className="flex h-screen bg-slate-900">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-800 border-r border-slate-700">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-white">ERP Restaurantes</h1>
        </div>
        <nav className="px-4">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 mb-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-purple-600 text-white'
                    : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                }`}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  )
}
