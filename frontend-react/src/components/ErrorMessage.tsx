import { AlertCircle, X } from 'lucide-react'
import { useState } from 'react'

interface ErrorMessageProps {
  title?: string
  message: string
  onClose?: () => void
}

export function ErrorMessage({ title = 'Error', message, onClose }: ErrorMessageProps) {
  const [isVisible, setIsVisible] = useState(true)

  if (!isVisible) return null

  const handleClose = () => {
    setIsVisible(false)
    onClose?.()
  }

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-4">
      <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
      <div className="flex-1">
        <h3 className="font-semibold text-red-900">{title}</h3>
        <p className="text-red-700 text-sm mt-1">{message}</p>
      </div>
      <button
        onClick={handleClose}
        className="text-red-600 hover:text-red-900 flex-shrink-0"
      >
        <X size={18} />
      </button>
    </div>
  )
}
