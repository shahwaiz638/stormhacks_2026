import { cn } from '@/lib/utils'

function NativeSelect({ className, children, ...props }) {
  return (
    <select className={cn('h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50', className)} {...props}>
      {children}
    </select>
  )
}

export { NativeSelect }
