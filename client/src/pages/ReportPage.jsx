import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

function ReportPage({ kind }) {
  const isLost = kind === 'lost'

  return (
    <section className="mx-auto max-w-7xl px-4 py-16 sm:px-8 lg:px-12">
      <h1 className="font-hero text-3xl font-bold">
        {isLost ? 'Report a lost item' : 'Report a found item'}
      </h1>
      <p className="mt-3 text-muted-foreground">The reporting form will be added here.</p>
      <Button variant="outline" className="mt-6" asChild>
        <Link to="/">Back to home</Link>
      </Button>
    </section>
  )
}

export default ReportPage
