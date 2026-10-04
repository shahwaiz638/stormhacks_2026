export function buildLostReportData(form) {
  const data = new FormData(form)
  for (const field of ['itemName', 'description', 'lastSeenLocation', 'privateDetail']) {
    data.set(field, String(data.get(field) || '').trim())
  }
  const photo = data.get('photo')
  if (!photo || photo.size === 0) data.delete('photo')
  // datetime-local represents the user's local time; send the timezone alongside it.
  data.set('timeZone', Intl.DateTimeFormat().resolvedOptions().timeZone)
  return data
}

export async function sendLostReport(data, endpoint = import.meta.env.VITE_LOST_REPORT_API_URL) {
  if (!endpoint) return { configured: false }
  // Let the browser set the multipart boundary, including the optional photo.
  const response = await fetch(endpoint, { method: 'POST', body: data })
  if (!response.ok) throw new Error('Unable to submit your report. Please try again.')
  return { configured: true }
}

export function buildFoundReportData(form, photos) {
  const data = new FormData(form)
  for (const field of ['description', 'foundLocation']) {
    data.set(field, String(data.get(field) || '').trim())
  }
  for (const photo of photos) data.append('photos', photo, photo.name)
  data.set('timeZone', Intl.DateTimeFormat().resolvedOptions().timeZone)
  return data
}

export async function sendFoundReport(data, endpoint = import.meta.env.VITE_FOUND_REPORT_API_URL) {
  if (!endpoint) return { configured: false }
  const response = await fetch(endpoint, { method: 'POST', body: data })
  if (!response.ok) throw new Error('Unable to submit your report. Please try again.')
  return { configured: true }
}
