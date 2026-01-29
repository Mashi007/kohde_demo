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
import Pedidos from './pages/Pedidos'
import Charolas from './pages/Charolas'
import Mermas from './pages/Mermas'
import Chat from './pages/Chat'

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
        <Route path="/pedidos" element={<Pedidos />} />
        <Route path="/charolas" element={<Charolas />} />
        <Route path="/mermas" element={<Mermas />} />
        <Route path="/chat" element={<Chat />} />
        </Routes>
      </Layout>
    </>
  )
}

export default App
