import * as React from "react"

export interface ScrollAreaProps
  extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: "vertical" | "horizontal" | "both"
}

const ScrollArea = React.forwardRef<HTMLDivElement, ScrollAreaProps>(
  ({ className = "", orientation = "vertical", children, ...props }, ref) => {
    const scrollClasses = {
      vertical: "overflow-y-auto overflow-x-hidden",
      horizontal: "overflow-x-auto overflow-y-hidden",
      both: "overflow-auto",
    }

    return (
      <div
        ref={ref}
        className={`relative w-full h-full ${scrollClasses[orientation]} ${className}`}
        {...props}
      >
        <div className="w-full h-full">
          {children}
        </div>
      </div>
    )
  }
)
ScrollArea.displayName = "ScrollArea"

export { ScrollArea }
