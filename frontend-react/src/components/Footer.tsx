export default function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-brand-gray text-brand-white border-t border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="font-bold text-lg mb-4">LexAgent</h3>
            <p className="text-gray-400">Your AI-powered legal assistant</p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-brand-white transition">Features</a></li>
              <li><a href="#" className="hover:text-brand-white transition">Pricing</a></li>
              <li><a href="#" className="hover:text-brand-white transition">Documentation</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-brand-white transition">Privacy</a></li>
              <li><a href="#" className="hover:text-brand-white transition">Terms</a></li>
              <li><a href="#" className="hover:text-brand-white transition">Disclaimer</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-gray-400">
              <li><a href="#" className="hover:text-brand-white transition">Contact</a></li>
              <li><a href="#" className="hover:text-brand-white transition">Help Center</a></li>
              <li><a href="#" className="hover:text-brand-white transition">Community</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-700 pt-8">
          <p className="text-gray-400 text-center">
            &copy; {currentYear} LexAgent. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}
