import * as React from "react"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "outline" | "secondary" | "destructive" | "success"
}

function Badge({ className = "", variant = "default", ...props }: BadgeProps) {
  const variants = {
    default: "inline-flex items-center rounded-full bg-gray-900 px-3 py-1 text-xs font-medium text-white",
    outline: "inline-flex items-center rounded-full border border-gray-300 px-3 py-1 text-xs font-medium text-black",
    secondary: "inline-flex items-center rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-black",
    destructive: "inline-flex items-center rounded-full bg-red-100 px-3 py-1 text-xs font-medium text-red-800",
    success: "inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-800",
  }

  return (
    <div
      className={`${variants[variant]} ${className}`}
      {...props}
    />
  )
}

export { Badge }
