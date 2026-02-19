import { Menu, X } from 'lucide-react'
import { useState } from 'react'

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="bg-brand-white border-b border-border sticky top-0 z-50">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-brand-black rounded-lg flex items-center justify-center">
              <span className="text-brand-white font-bold text-sm">LA</span>
            </div>
            <h1 className="text-xl font-bold text-brand-black">LexAgent</h1>
          </div>

          <div className="hidden md:flex gap-8">
            <a href="/" className="text-gray-700 hover:text-brand-black transition">Home</a>
            <a href="/documents" className="text-gray-700 hover:text-brand-black transition">Documents</a>
            <a href="/query" className="text-gray-700 hover:text-brand-black transition">Query</a>
            <a href="/about" className="text-gray-700 hover:text-brand-black transition">About</a>
          </div>

          <button
            className="md:hidden p-2"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {isMenuOpen && (
          <div className="md:hidden pb-4 space-y-2">
            <a href="/" className="block py-2 text-gray-700 hover:text-brand-black">Home</a>
            <a href="/documents" className="block py-2 text-gray-700 hover:text-brand-black">Documents</a>
            <a href="/query" className="block py-2 text-gray-700 hover:text-brand-black">Query</a>
            <a href="/about" className="block py-2 text-gray-700 hover:text-brand-black">About</a>
          </div>
        )}
      </nav>
    </header>
  )
}
