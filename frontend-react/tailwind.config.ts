import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        'brand-black': '#000',
        'brand-white': '#fff',
        'brand-gray': '#1a1a1a',
        'border': '#e0e0e0',
        'light-bg': '#f5f5f5'
      },
      fontFamily: {
        manrope: ['Manrope', 'sans-serif'],
        inter: ['Inter', 'sans-serif']
      }
    }
  },
  plugins: []
}

export default config
