import * as React from "react"
import { ChevronDown } from "lucide-react"

export interface CollapsibleProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'title'> {
  title: React.ReactNode
  defaultOpen?: boolean
  onOpenChange?: (open: boolean) => void
}

const Collapsible = React.forwardRef<HTMLDivElement, CollapsibleProps>(
  ({ className = "", title, defaultOpen = false, onOpenChange, children, ...props }, ref) => {
    const [isOpen, setIsOpen] = React.useState(defaultOpen)

    const toggleOpen = () => {
      const newState = !isOpen
      setIsOpen(newState)
      onOpenChange?.(newState)
    }

    return (
      <div
        ref={ref}
        className={`border border-gray-200 rounded-lg overflow-hidden ${className}`}
        {...props}
      >
        <button
          onClick={toggleOpen}
          className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors"
          type="button"
          aria-expanded={isOpen}
        >
          <span className="font-medium text-black">{title}</span>
          <ChevronDown
            className={`h-4 w-4 text-gray-600 transition-transform duration-200 ${
              isOpen ? "transform rotate-180" : ""
            }`}
          />
        </button>
        {isOpen && (
          <div className="px-4 py-3 border-t border-gray-200 bg-white">
            {children}
          </div>
        )}
      </div>
    )
  }
)
Collapsible.displayName = "Collapsible"

export { Collapsible }
