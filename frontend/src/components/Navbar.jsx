import { NavLink } from 'react-router-dom'
import { useCart } from '../context/CartContext.jsx'

const NAV_ITEMS = [
  { to: '/', label: 'Home', end: true },
  { to: '/search', label: 'Search' },
  { to: '/books', label: 'Books' },
  { to: '/support', label: 'Support' },
]

export default function Navbar() {
  const { count } = useCart()

  return (
    <header className="navbar">
      <div className="brand">
        <span className="brand-mark">📖</span>
        <span className="brand-name">Bookly</span>
      </div>
      <nav className="nav-buttons">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              'nav-button' + (isActive ? ' nav-button--active' : '')
            }
          >
            {item.label}
          </NavLink>
        ))}
        <NavLink
          to="/cart"
          className={({ isActive }) =>
            'nav-button nav-cart' + (isActive ? ' nav-button--active' : '')
          }
        >
          🛒 Cart{count > 0 && <span className="cart-badge">{count}</span>}
        </NavLink>
      </nav>
    </header>
  )
}
