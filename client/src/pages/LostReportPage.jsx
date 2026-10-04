import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Textarea } from '@/components/ui/textarea'
import { buildLostReportData, sendLostReport } from '@/lib/reports'

// Replace with category records from the API once its endpoint is available.
const categories = []

function LostReportPage() {
  const [isSending, setIsSending] = useState(false)
  const [status, setStatus] = useState({ message: '', error: false })
  const sending = useRef(false)

  async function handleSubmit(event) {
    event.preventDefault()
    if (sending.current) return
    const data = buildLostReportData(event.currentTarget)
    sending.current = true
    setIsSending(true)
    setStatus({ message: '', error: false })
    try {
      const result = await sendLostReport(data)
      setStatus({ message: result.configured ? 'Your lost item report has been submitted.' : 'Your report is ready. Nothing has been sent yet; submission will be available soon.', error: false })
    } catch (error) {
      setStatus({ message: error.message || 'Unable to submit your report. Please try again.', error: true })
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
            <Label required htmlFor="category">Category</Label>
            <NativeSelect id="category" name="category" defaultValue="" disabled={!categories.length} required aria-describedby="category-note">
              <option value="" disabled>{categories.length ? 'Select a category' : 'Categories coming soon'}</option>
              {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
            </NativeSelect>
            <p id="category-note" className="text-xs text-muted-foreground">Categories will be available soon.</p>
          </div>
          <div className="space-y-2">
            <Label required htmlFor="last-seen-location">Where did you last see it?</Label>
            <Input id="last-seen-location" name="lastSeenLocation" placeholder="e.g. Library, second floor" required maxLength={500} pattern=".*\S.*" />
          </div>
          <div className="space-y-2">
            <Label required htmlFor="last-seen-at">Date / approximate time</Label>
            <Input id="last-seen-at" name="lastSeenAt" type="datetime-local" required aria-describedby="time-note" className="[color-scheme:dark]" />
            <p id="time-note" className="text-xs text-muted-foreground">Use your local date and approximate time.</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="photo">Photo (optional)</Label>
            <Input id="photo" name="photo" type="file" accept="image/*" aria-describedby="photo-note" className="h-auto min-h-10 cursor-pointer" />
            <p id="photo-note" className="text-xs text-muted-foreground">Choose a photo of your item.</p>
          </div>
          <div className="space-y-2">
            <Label required htmlFor="private-detail">Private identifying detail</Label>
            <Input id="private-detail" name="privateDetail" placeholder="A detail only you would know" required maxLength={1000} pattern=".*\S.*" aria-describedby="private-note" />
            <p id="private-note" className="text-xs text-muted-foreground">This will NOT be shown publicly.</p>
          </div>
          <Button type="submit" className="w-full sm:w-auto">{isSending ? 'Sending…' : 'Submit report'}</Button>
        </fieldset>
        <p role="status" aria-live="polite" className={`text-sm ${status.message ? 'mt-4' : ''} ${status.error ? 'text-red-400' : 'text-muted-foreground'}`}>{status.message}</p>
      </form>

      <div className="mt-10 flex flex-wrap items-center gap-3 border-t border-border pt-6">
        <Button variant="ghost" asChild><Link to="/">Return home</Link></Button>
        <Button variant="outline" asChild><Link to="/report/found">Find My Item</Link></Button>
      </div>
    </section>
  )
}

export default LostReportPage

