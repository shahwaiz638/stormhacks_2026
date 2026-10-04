import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

function HomePage() {
  return (
        <section aria-labelledby="hero-heading" className="hero-surface flex min-h-[calc(100svh-65px)] items-center justify-center bg-background px-4 py-16 sm:px-8">
          <div className="mx-auto w-full max-w-6xl text-center">
            <h1 id="hero-heading" className="font-hero text-[clamp(2.25rem,5vw,4.5rem)] font-extrabold leading-none tracking-[-0.025em] text-foreground">
              Lost something?
            </h1>
            <p className="mt-3 text-[clamp(1.125rem,2.5vw,2rem)] font-light leading-tight tracking-[-0.025em] text-muted-foreground">
              Let AI find the match.
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3 sm:mt-10">
              <Button size="lg" asChild><Link to="/report/lost">Lost Item</Link></Button>
              <Button variant="outline" size="lg" className="border-primary bg-transparent" asChild><Link to="/report/found">Report Item</Link></Button>
            </div>
          </div>
        </section>
  )
}

export default HomePage

