import { Button } from '@/components/ui/button'

function Navbar() {
  return (
      <header className="border-b border-border/60">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-2 px-4 sm:px-8 lg:px-12">
          <div className="flex items-center gap-0 sm:gap-1">
          {/* <a href="/" aria-label="LostLens home" className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-secondary text-foreground transition-colors hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
            <Scan className="size-6" strokeWidth={3} aria-hidden="true" />
          </a> */}
            <Button variant="ghost" size="sm" className="px-2 text-xs font-normal text-muted-foreground sm:px-3 sm:text-sm">How to</Button>
            <Button variant="ghost" size="sm" className="px-2 text-xs font-normal text-muted-foreground sm:px-3 sm:text-sm">Contact</Button>
            <Button variant="ghost" size="sm" className="px-2 text-xs font-normal text-muted-foreground sm:px-3 sm:text-sm">FAQs</Button>
          </div>
          <nav aria-label="Account and reporting" className="flex items-center gap-1 sm:gap-2">
            {/* <Button size="sm" className="px-2 text-xs sm:px-3 sm:text-sm">Report Item</Button> */}
            <Button size="sm" className="px-2 text-xs sm:px-3 sm:text-sm">Sign In</Button>
          </nav>
        </div>
      </header>
  )
}

export default Navbar

