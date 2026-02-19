/**
 * Utility function to combine class names conditionally
 * Useful for Tailwind CSS class management
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes
    .filter((c): c is string => typeof c === 'string')
    .join(' ')
}
