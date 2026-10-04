import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import PhotoUpload from '@/components/PhotoUpload'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { buildFoundReportData, sendFoundReport } from '@/lib/reports'

function FoundReportPage() {
  const [photos, setPhotos] = useState([])
  const [isSending, setIsSending] = useState(false)
  const [status, setStatus] = useState({ message: '', error: false })
  const sending = useRef(false)

  async function handleSubmit(event) {
    event.preventDefault()
    if (sending.current) return
    if (!photos.length) {
      setStatus({ message: 'Please add at least one photo of the item.', error: true })
      return
    }
    const data = buildFoundReportData(event.currentTarget, photos)
    sending.current = true
    setIsSending(true)
    setStatus({ message: '', error: false })
    try {
      const result = await sendFoundReport(data)
      setStatus({ message: result.configured ? 'Your found item report has been submitted.' : 'Your report is ready. Nothing has been sent yet; submission will be available soon.', error: false })
    } catch (error) {
      setStatus({ message: error.message || 'Unable to submit your report. Please try again.', error: true })
    } finally {
      sending.current = false
      setIsSending(false)
    }
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-12 sm:px-8 sm:py-16">
      <h1 className="font-hero text-4xl font-bold tracking-tight">Report a found item</h1>
      <p className="mt-3 text-sm leading-relaxed text-muted-foreground">Found something? Share a few details to help it get back to its owner.</p>
      <form className="mt-8 rounded-xl border border-border bg-card p-5 shadow-sm sm:p-8" onSubmit={handleSubmit}>
        <fieldset disabled={isSending} className="min-w-0 space-y-6">
          <div className="space-y-2">
            <Label required htmlFor="found-photos">Photos</Label>
            <PhotoUpload files={photos} onChange={setPhotos} disabled={isSending} />
          </div>
          <div className="space-y-2">
            <Label required htmlFor="found-description">Description</Label>
            <Textarea id="found-description" name="description" placeholder="Describe its color, brand, and any noticeable features…" required maxLength={5000} />
          </div>
          <div className="space-y-2">
            <Label required htmlFor="found-location">Location found</Label>
            <Input id="found-location" name="foundLocation" placeholder="e.g. Library, second floor" required maxLength={500} pattern=".*\S.*" />
          </div>
          <div className="space-y-2">
            <Label required htmlFor="found-at">Date / approximate time</Label>
            <Input id="found-at" name="foundAt" type="datetime-local" required aria-describedby="found-time-note" className="[color-scheme:dark]" />
            <p id="found-time-note" className="text-xs text-muted-foreground">Use your local date and approximate time.</p>
          </div>
          <Button type="submit" className="w-full sm:w-auto">{isSending ? 'Sending…' : 'Submit report'}</Button>
        </fieldset>
        <p role="status" aria-live="polite" className={`text-sm ${status.message ? 'mt-4' : ''} ${status.error ? 'text-red-400' : 'text-muted-foreground'}`}>{status.message}</p>
      </form>
      <div className="mt-10 flex flex-wrap items-center gap-3 border-t border-border pt-6">
        <Button variant="ghost" asChild><Link to="/">Return home</Link></Button>
        <Button variant="outline" asChild><Link to="/report/lost">Report lost</Link></Button>
      </div>
    </section>
  )
}

export default FoundReportPage

