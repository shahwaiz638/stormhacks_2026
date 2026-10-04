import { cn } from '@/lib/utils'

function Label({ className, required = false, children, ...props }) {
  return (
    <label className={cn('text-sm font-medium leading-none', className)} {...props}>
      {children}
      {required && <><span className="ml-1 text-red-400" aria-hidden="true">*</span><span className="sr-only"> (required)</span></>}
    </label>
  )
}

export { Label }
