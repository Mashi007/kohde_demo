import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Tickets from './pages/Tickets'
import Facturas from './pages/Facturas'
import Inventario from './pages/Inventario'
import Items from './pages/Items'
import Recetas from './pages/Recetas'
import Programacion from './pages/Programacion'
import Proveedores from './pages/Proveedores'
import Notificaciones from './pages/Notificaciones'
import Pedidos from './pages/Pedidos'
import PedidosInternos from './pages/PedidosInternos'
import Charolas from './pages/Charolas'
import Mermas from './pages/Mermas'
import Chat from './pages/Chat'
import Configuracion from './pages/Configuracion'
import ComprasDashboard from './pages/ComprasDashboard'
import Costos from './pages/Costos'

function App() {
  return (
    <>
      <Toaster position="top-right" />
      <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/tickets" element={<Tickets />} />
          <Route path="/facturas" element={<Facturas />} />
          <Route path="/inventario" element={<Inventario />} />
          <Route path="/items" element={<Items />} />
          <Route path="/recetas" element={<Recetas />} />
          <Route path="/programacion" element={<Programacion />} />
        <Route path="/proveedores" element={<Proveedores />} />
        <Route path="/notificaciones" element={<Notificaciones />} />
        <Route path="/pedidos" element={<Pedidos />} />
        <Route path="/pedidos-internos" element={<PedidosInternos />} />
        <Route path="/charolas" element={<Charolas />} />
        <Route path="/mermas" element={<Mermas />} />
        <Route path="/compras" element={<ComprasDashboard />} />
        <Route path="/costos" element={<Costos />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/configuracion" element={<Configuracion />} />
        </Routes>
      </Layout>
    </>
  )
}

export default App
