import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { LoaderCircle } from 'lucide-react'
import ReportFeedback from '@/components/ReportFeedback'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { buildLostReportData, sendLostReport } from '@/lib/reports'

function LostReportPage() {
  const [isSending, setIsSending] = useState(false)
  const [status, setStatus] = useState({ message: '', error: false, result: null })
  const sending = useRef(false)

  async function handleSubmit(event) {
    event.preventDefault()
    if (sending.current) return
    const form = event.currentTarget
    sending.current = true
    setIsSending(true)
    setStatus({ message: '', error: false, result: null })
    try {
      const data = await buildLostReportData(form)
      const result = await sendLostReport(data)
      setStatus({ message: result.matches?.length ? `Search complete. ${result.matches.length} possible ${result.matches.length === 1 ? 'match' : 'matches'} found.` : 'No plausible matches found. Try adding more identifying details.', error: false, result })
    } catch (error) {
      setStatus({ message: error.message || 'Unable to submit your report. Please try again.', error: true, result: null })
    } finally {
      sending.current = false
      setIsSending(false)
    }
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-12 sm:px-8 sm:py-16">
      <h1 className="font-hero text-4xl font-bold tracking-tight">Report a lost item</h1>
      <p className="mt-3 text-sm leading-relaxed text-muted-foreground">Tell us what you’re looking for. A few details can help find the right match.</p>

      <form className="mt-8 rounded-xl border border-border bg-card p-5 shadow-sm sm:p-8" onSubmit={handleSubmit}>
        <fieldset disabled={isSending} className="min-w-0 space-y-6">
          <div className="space-y-2">
            <Label required htmlFor="item-name">Item name</Label>
            <Input id="item-name" name="itemName" placeholder="e.g. Black backpack" required maxLength={200} pattern=".*\S.*" />
          </div>
          <div className="space-y-2">
            <Label required htmlFor="description">Description</Label>
            <Textarea id="description" name="description" placeholder="Describe its color, brand, and any noticeable features…" required maxLength={5000} />
          </div>
          <div className="space-y-2">
            <Label required htmlFor="last-seen-location">Where did you last see it?</Label>
            <Input id="last-seen-location" name="lastSeenLocation" placeholder="e.g. Library, second floor" required maxLength={100} pattern=".*\S.*" />
          </div>
          <div className="space-y-2">
            <Label required htmlFor="last-seen-at">Date / approximate time</Label>
            <Input id="last-seen-at" name="lastSeenAt" type="datetime-local" required aria-describedby="time-note" className="[color-scheme:dark]" />
            <p id="time-note" className="text-xs text-muted-foreground">Use your local date and approximate time.</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="photo">Photo (optional)</Label>
            <Input id="photo" name="photo" type="file" accept="image/jpeg,image/png,image/webp" aria-describedby="photo-note" className="h-auto min-h-10 cursor-pointer" />
            <p id="photo-note" className="text-xs text-muted-foreground">JPEG, PNG, or WebP, up to 5 MiB.</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="private-detail">Private identifying detail (optional)</Label>
            <Input id="private-detail" name="privateDetail" placeholder="A detail only you would know" maxLength={1000} pattern=".*\S.*" aria-describedby="private-note" />
            <p id="private-note" className="text-xs text-muted-foreground">This detail stays private and is not stored in this version.</p>
          </div>
          <Button type="submit" disabled={isSending} aria-busy={isSending} className="w-full sm:w-auto">
            {isSending && <LoaderCircle className="animate-spin motion-reduce:animate-none" aria-hidden="true" />}
            {isSending ? 'Processing...' : 'Submit report'}
          </Button>
        </fieldset>
        <ReportFeedback status={status} />
      </form>

      <div className="mt-10 flex flex-wrap items-center gap-3 border-t border-border pt-6">
        <Button variant="ghost" asChild><Link to="/">Return home</Link></Button>
        <Button variant="outline" asChild><Link to="/report/found">Found an item?</Link></Button>
      </div>
    </section>
  )
}

export default LostReportPage

