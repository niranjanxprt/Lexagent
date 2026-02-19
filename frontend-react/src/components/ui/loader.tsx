import * as React from "react"
import { Loader2 } from "lucide-react"

export interface LoaderProps
  extends React.HTMLAttributes<HTMLDivElement> {
  size?: "sm" | "md" | "lg"
  variant?: "default" | "spinner"
}

const Loader = React.forwardRef<HTMLDivElement, LoaderProps>(
  ({ className = "", size = "md", variant = "default", ...props }, ref) => {
    const sizes = {
      sm: 16,
      md: 24,
      lg: 32,
    }

    const sizeValue = sizes[size]

    return (
      <div
        ref={ref}
        className={`flex items-center justify-center ${className}`}
        {...props}
      >
        {variant === "spinner" ? (
          <div className="animate-spin">
            <Loader2 size={sizeValue} className="text-gray-600" />
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <div className="animate-spin">
              <Loader2 size={sizeValue} className="text-gray-600" />
            </div>
            <span className="text-gray-600 text-sm">Loading...</span>
          </div>
        )}
      </div>
    )
  }
)
Loader.displayName = "Loader"

export { Loader }
