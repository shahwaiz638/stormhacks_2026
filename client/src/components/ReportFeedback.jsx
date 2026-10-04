import { useState } from 'react'
import { CheckCircle2, CircleAlert, ImageOff, MapPin, Sparkles } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

function MatchPhoto({ match }) {
  const [failed, setFailed] = useState(false)
  return (
    <div className="relative flex min-h-32 w-28 shrink-0 items-center justify-center overflow-hidden bg-muted sm:w-36">
      {match.image_url && !failed ? (
        <img src={match.image_url} alt={match.title} onError={() => setFailed(true)} className="absolute inset-0 h-full w-full object-cover" loading="lazy" />
      ) : <ImageOff className="size-7 text-muted-foreground" aria-label="No photo available" />}
    </div>
  )
}

function ReportFeedback({ status }) {
  if (!status.message) return null
  const result = status.result
  const isLost = result?.report_type === 'LOST'
  return (
    <div className="mt-6 space-y-4" aria-live="polite">
      <Alert variant={status.error ? 'destructive' : 'default'}>
        {status.error ? <CircleAlert aria-hidden="true" /> : <CheckCircle2 aria-hidden="true" />}
        <AlertTitle>{status.error ? 'Could not complete request' : isLost ? 'Search complete' : 'Report saved'}</AlertTitle>
        <AlertDescription>{status.message}</AlertDescription>
      </Alert>
      {isLost && !!result.matches?.length && (
        <section aria-label="Possible matches" className="space-y-3">
          <h2 className="flex items-center gap-2 font-hero text-xl font-semibold"><Sparkles className="size-5 text-primary" aria-hidden="true" /> Possible matches</h2>
          {result.matches.map((match, index) => (
            <article key={match.candidate_id} className="flex overflow-hidden rounded-xl border border-border bg-card shadow-sm">
              <MatchPhoto match={match} />
              <div className="min-w-0 flex-1 space-y-2 p-4 sm:p-5">
                <span className="inline-flex rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">Possible match {index + 1}</span>
                <h3 className="break-words font-hero text-lg font-semibold">{match.title}</h3>
                <p className="flex items-start gap-1.5 text-xs text-muted-foreground"><MapPin className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />{match.location_name || 'Location unavailable'}</p>
                <p className="text-sm leading-relaxed">{match.summary_explanation}</p>
                {!!match.matching_reasons?.length && <ul className="space-y-1 text-xs text-muted-foreground">{match.matching_reasons.map((reason, position) => <li key={position} className="flex items-start gap-1.5"><CheckCircle2 className="mt-0.5 size-3 shrink-0 text-primary" aria-hidden="true" />{reason}</li>)}</ul>}
              </div>
            </article>
          ))}
          <p className="text-xs text-muted-foreground">These are plausible matches, not verified ownership.</p>
        </section>
      )}
      {result && (
        <details className="rounded-lg border border-border p-3 text-sm">
          <summary className="cursor-pointer text-muted-foreground">Processing details</summary>
          <div className="mt-3 space-y-3">
            {result.saved ? <p className="break-all">Saved report ID: <span className="font-mono">{result.report_id}</span></p> : <p>Read-only search. Your lost item was not added to TiDB.</p>}
            <p>{isLost ? 'Gemini analysis, query embedding, vector search, and final match evaluation completed.' : 'Gemini analysis, text embedding, and TiDB storage completed.'}</p>
            <div>
              <p className="mb-1 font-medium">Extracted item attributes</p>
              <pre className="overflow-auto whitespace-pre-wrap break-words rounded-md bg-muted p-3 text-xs">{JSON.stringify(result.attributes, null, 2)}</pre>
            </div>
            {isLost && <pre className="overflow-auto whitespace-pre-wrap break-words rounded-md bg-muted p-3 text-xs">{JSON.stringify(result.matches.map((match) => ({ candidate_id: match.candidate_id, vector_score: match.vector_score, ai_match_percentage: match.ai_match_percentage })), null, 2)}</pre>}
            {isLost && <p className="text-xs text-muted-foreground">AI percentages are subjective estimates, not calibrated probabilities.</p>}
            {result.warnings?.map((warning, index) => <p key={index} className="text-muted-foreground">Notice: {warning}</p>)}
          </div>
        </details>
      )}
    </div>
  )
}

export default ReportFeedback
