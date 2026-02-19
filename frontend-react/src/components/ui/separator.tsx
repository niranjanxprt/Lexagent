import * as React from "react"

export interface SeparatorProps
  extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: "horizontal" | "vertical"
}

const Separator = React.forwardRef<HTMLDivElement, SeparatorProps>(
  ({ className = "", orientation = "horizontal", ...props }, ref) => (
    <div
      ref={ref}
      className={`${
        orientation === "horizontal"
          ? "h-[1px] w-full bg-gray-200"
          : "h-full w-[1px] bg-gray-200"
      } shrink-0 ${className}`}
      {...props}
    />
  )
)
Separator.displayName = "Separator"

export { Separator }
