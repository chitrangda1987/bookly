import { Routes, Route } from 'react-router-dom'
import { CartProvider } from './context/CartContext.jsx'
import Navbar from './components/Navbar.jsx'
import Chatbot from './components/Chatbot.jsx'
import Home from './pages/Home.jsx'
import Search from './pages/Search.jsx'
import Books from './pages/Books.jsx'
import Support from './pages/Support.jsx'
import Cart from './pages/Cart.jsx'

export default function App() {
  return (
    <CartProvider>
      <div className="app">
        <Navbar />
        <main className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/search" element={<Search />} />
            <Route path="/books" element={<Books />} />
            <Route path="/support" element={<Support />} />
            <Route path="/cart" element={<Cart />} />
          </Routes>
        </main>
        <Chatbot />
      </div>
    </CartProvider>
  )
}
