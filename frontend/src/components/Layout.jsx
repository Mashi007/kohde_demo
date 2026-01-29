import { Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import { 
  LayoutDashboard, 
  MessageSquare, 
  FileText, 
  Package, 
  ShoppingCart,
  ChefHat,
  Calendar,
  Truck,
  ClipboardList,
  BarChart3,
  AlertTriangle,
  MessageCircle,
  Settings,
  ChevronDown,
  ChevronRight,
  Users
} from 'lucide-react'

// Estructura de menú con secciones agrupadas
const menuStructure = [
  // Dashboard (sin agrupación)
  {
    section: null,
    items: [
      { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    ]
  },
  // CRM - Gestión de relaciones con clientes y proveedores
  {
    section: 'CRM',
    icon: Users,
    items: [
      { path: '/tickets', label: 'Tickets', icon: MessageSquare },
      { path: '/proveedores', label: 'Proveedores', icon: Truck },
    ]
  },
  // Logística - Gestión de inventario, compras y facturas
  {
    section: 'Logística',
    icon: Package,
    items: [
      { path: '/items', label: 'Items', icon: ShoppingCart },
      { path: '/inventario', label: 'Inventario', icon: Package },
      { path: '/pedidos', label: 'Pedidos', icon: ClipboardList },
      { path: '/facturas', label: 'Facturas', icon: FileText },
    ]
  },
  // Planificación - Recetas y programación de producción
  {
    section: 'Planificación',
    icon: Calendar,
    items: [
      { path: '/recetas', label: 'Recetas', icon: ChefHat },
      { path: '/programacion', label: 'Programación', icon: Calendar },
    ]
  },
  // Reportes - Análisis y reportes operativos
  {
    section: 'Reportes',
    icon: BarChart3,
    items: [
      { path: '/charolas', label: 'Charolas', icon: BarChart3 },
      { path: '/mermas', label: 'Mermas', icon: AlertTriangle },
    ]
  },
  // Herramientas - Utilidades del sistema
  {
    section: null,
    items: [
      { path: '/chat', label: 'Chat AI', icon: MessageCircle },
      { path: '/configuracion', label: 'Configuración', icon: Settings },
    ]
  },
]

export default function Layout({ children }) {
  const location = useLocation()
  const [expandedSections, setExpandedSections] = useState({
    CRM: true,
    Logística: true,
    Planificación: true,
    Reportes: true,
  })

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const isPathInSection = (sectionItems) => {
    return sectionItems.some(item => location.pathname === item.path)
  }

  return (
    <div className="flex h-screen bg-slate-900">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-800 border-r border-slate-700 flex flex-col">
        <div className="p-6 border-b border-slate-700">
          <h1 className="text-2xl font-bold text-white">ERP Restaurantes</h1>
        </div>
        <nav className="px-4 py-4 flex-1 overflow-y-auto">
          {menuStructure.map((group, groupIndex) => {
            // Si no tiene sección, renderizar items directamente
            if (!group.section) {
              return (
                <div key={`group-${groupIndex}`}>
                  {group.items.map((item) => {
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
                  {groupIndex < menuStructure.length - 1 && (
                    <div className="my-4 border-t border-slate-700"></div>
                  )}
                </div>
              )
            }

            // Si tiene sección, renderizar con colapso
            const SectionIcon = group.icon
            const isExpanded = expandedSections[group.section]
            const hasActiveItem = isPathInSection(group.items)

            return (
              <div key={group.section} className="mb-2">
                <button
                  onClick={() => toggleSection(group.section)}
                  className={`w-full flex items-center justify-between px-4 py-3 mb-1 rounded-lg transition-colors ${
                    hasActiveItem
                      ? 'bg-purple-600/20 text-purple-300'
                      : 'text-slate-400 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <SectionIcon size={18} />
                    <span className="font-semibold text-sm">{group.section}</span>
                  </div>
                  {isExpanded ? (
                    <ChevronDown size={16} />
                  ) : (
                    <ChevronRight size={16} />
                  )}
                </button>
                
                {isExpanded && (
                  <div className="ml-4 pl-4 border-l-2 border-slate-700">
                    {group.items.map((item) => {
                      const Icon = item.icon
                      const isActive = location.pathname === item.path
                      return (
                        <Link
                          key={item.path}
                          to={item.path}
                          className={`flex items-center gap-3 px-4 py-2 mb-1 rounded-lg transition-colors text-sm ${
                            isActive
                              ? 'bg-purple-600 text-white'
                              : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                          }`}
                        >
                          <Icon size={18} />
                          <span>{item.label}</span>
                        </Link>
                      )
                    })}
                  </div>
                )}
              </div>
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
