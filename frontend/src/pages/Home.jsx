import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <section className="panel hero">
      <h1>Welcome to Bookly</h1>
      <p className="tagline">
        A cozy, rustic corner of the internet for readers who love stories worth
        slowing down for.
      </p>
      <div className="hero-actions">
        <Link className="cta" to="/books">Browse the Shelves</Link>
        <Link className="cta cta--ghost" to="/search">Find a Book</Link>
      </div>
    </section>
  )
}
