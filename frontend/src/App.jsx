import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Clientes from './pages/Clientes'
import Tickets from './pages/Tickets'
import Facturas from './pages/Facturas'
import Inventario from './pages/Inventario'
import Items from './pages/Items'
import Recetas from './pages/Recetas'
import Programacion from './pages/Programacion'
import Proveedores from './pages/Proveedores'
import Pedidos from './pages/Pedidos'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/clientes" element={<Clientes />} />
        <Route path="/tickets" element={<Tickets />} />
        <Route path="/facturas" element={<Facturas />} />
        <Route path="/inventario" element={<Inventario />} />
        <Route path="/items" element={<Items />} />
        <Route path="/recetas" element={<Recetas />} />
        <Route path="/programacion" element={<Programacion />} />
        <Route path="/proveedores" element={<Proveedores />} />
        <Route path="/pedidos" element={<Pedidos />} />
      </Routes>
    </Layout>
  )
}

export default App
