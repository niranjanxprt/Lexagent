/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'libra-black': '#000',
        'libra-white': '#fff',
        'libra-light-gray': '#f5f5f5',
        'libra-dark-gray': '#1a1a1a',
        'libra-border': '#e0e0e0',
        // Aliases for index.css and legacy components
        'brand-black': '#000',
        'brand-white': '#fff',
        'brand-gray': '#1a1a1a',
        'light-bg': '#f5f5f5',
        'border': '#e0e0e0',
      },
      fontFamily: {
        'manrope': ['Manrope', 'sans-serif'],
        'inter': ['Inter', 'sans-serif'],
        'mono': ['Geist Mono', 'Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
}
