import { useEffect, useRef, useState } from 'react'

const GREETING = {
  role: 'assistant',
  content: "Hi! I'm Bookly's assistant. Ask me for a recommendation or anything about the store.",
}

export default function Chatbot() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([GREETING])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, open])

  const send = async (e) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return

    const next = [...messages, { role: 'user', content: text }]
    setMessages(next)
    setInput('')
    setSending(true)
    setError(null)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: next
            .filter((m) => m !== GREETING)
            .map(({ role, content }) => ({ role, content })),
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`)
      setMessages((m) => [...m, { role: 'assistant', content: data.reply }])
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  return (
    <>
      <button
        type="button"
        className="chat-fab"
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? 'Close chat' : 'Open chat'}
      >
        {open ? '×' : '💬'}
      </button>

      {open && (
        <div className="chat-panel" role="dialog" aria-label="Bookly assistant">
          <header className="chat-header">
            <span>Bookly Assistant</span>
            <button
              type="button"
              className="chat-close"
              onClick={() => setOpen(false)}
              aria-label="Close chat"
            >
              ×
            </button>
          </header>
          <div className="chat-messages" ref={scrollRef}>
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg chat-msg--${m.role}`}>
                {m.content}
              </div>
            ))}
            {sending && (
              <div className="chat-msg chat-msg--assistant chat-msg--typing">
                …
              </div>
            )}
            {error && (
              <div className="chat-msg chat-msg--error">
                Sorry, something went wrong: {error}
              </div>
            )}
          </div>
          <form className="chat-input-row" onSubmit={send}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about a book…"
              disabled={sending}
              autoFocus
            />
            <button type="submit" disabled={sending || !input.trim()}>
              Send
            </button>
          </form>
        </div>
      )}
    </>
  )
}
