import { cn } from '@/lib/utils'

function Input({ className, type, ...props }) {
  return <input type={type} className={cn('flex h-10 w-full min-w-0 max-w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm transition-colors file:mr-3 file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50', type === 'datetime-local' && 'date-time-input', className)} {...props} />
}

export { Input }
