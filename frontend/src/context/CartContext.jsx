import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const CartContext = createContext(null)
const STORAGE_KEY = 'bookly.cart'

export function CartProvider({ children }) {
  const [items, setItems] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      return raw ? JSON.parse(raw) : []
    } catch {
      return []
    }
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
  }, [items])

  const value = useMemo(() => {
    const addItem = (book) => {
      setItems((prev) => {
        const existing = prev.find((i) => i.id === book.id)
        if (existing) {
          return prev.map((i) =>
            i.id === book.id ? { ...i, quantity: i.quantity + 1 } : i,
          )
        }
        return [
          ...prev,
          {
            id: book.id,
            title: book.title,
            price: book.price,
            cover: book.cover,
            quantity: 1,
          },
        ]
      })
    }

    const removeItem = (id) =>
      setItems((prev) => prev.filter((i) => i.id !== id))

    const setQuantity = (id, quantity) =>
      setItems((prev) =>
        prev
          .map((i) => (i.id === id ? { ...i, quantity } : i))
          .filter((i) => i.quantity > 0),
      )

    const clear = () => setItems([])

    const count = items.reduce((n, i) => n + i.quantity, 0)
    const total = items.reduce((n, i) => n + i.price * i.quantity, 0)

    return { items, addItem, removeItem, setQuantity, clear, count, total }
  }, [items])

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be used within CartProvider')
  return ctx
}
