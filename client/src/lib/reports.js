const hostname = typeof window === 'undefined' ? 'localhost' : window.location.hostname
const API_URL = (import.meta.env?.VITE_API_URL || `http://${hostname}:8000`).replace(/\/$/, '')
const MAX_IMAGE_BYTES = 5 * 1024 * 1024
const IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']

// Basic guard only. The backend owns instructions, validates output, and uses fixed SQL.
const instructionPattern = /ignore\s+(?:(?:all|the|any)\s+)?(?:previous|prior|above|system)\s+(?:instructions?|prompts?|rules?)|(?:reveal|show|print|return)\s+(?:(?:the|your)\s+)?(?:system\s+prompt|api\s+key|password|credentials)|(?:override|bypass)\s+(?:(?:the|your|all)\s+)?(?:instructions?|rules?|safety|security)|(?:you\s+are\s+now|act\s+as)\s+(?:an?\s+)?(?:assistant|system|developer|chatgpt)|<\/?(?:system|developer|assistant)>|\[INST\]/i

export function validateReportText(...values) {
  if (values.some((value) => instructionPattern.test(String(value || '')))) {
    throw new Error('Describe the item only; remove instructions aimed at the AI.')
  }
}

export function photoToBase64(photo) {
  if (!IMAGE_TYPES.includes(photo.type)) throw new Error('Photos must be JPEG, PNG, or WebP.')
  if (!photo.size || photo.size > MAX_IMAGE_BYTES) throw new Error('Each photo must be nonempty and at most 5 MiB.')
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = () => reject(new Error('Could not read the selected photo.'))
    reader.onabort = () => reject(new Error('Photo reading was cancelled.'))
    reader.readAsDataURL(photo)
  })
}

function text(data, field) {
  return String(data.get(field) || '').trim()
}

function checkFields(payload) {
  if (!payload.description || !payload.location_name || !payload.event_timestamp) {
    throw new Error('Please complete the description, location, and date/time.')
  }
  validateReportText(payload.title, payload.description, payload.location_name, payload.private_detail)
}

export async function buildLostReportData(form) {
  const data = new FormData(form)
  const payload = {
    title: text(data, 'itemName'),
    description: text(data, 'description'),
    location_name: text(data, 'lastSeenLocation'),
    event_timestamp: text(data, 'lastSeenAt'),
    time_zone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    private_detail: text(data, 'privateDetail'),
    images: [],
  }
  checkFields(payload)
  const photo = data.get('photo')
  if (photo && photo.size) payload.images = [await photoToBase64(photo)]
  return payload
}

export async function buildFoundReportData(form, photos) {
  const data = new FormData(form)
  const payload = {
    description: text(data, 'description'),
    location_name: text(data, 'foundLocation'),
    event_timestamp: text(data, 'foundAt'),
    time_zone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    images: [],
  }
  checkFields(payload)
  if (!photos.length) throw new Error('Please add at least one photo of the item.')
  if (photos.length > 5) throw new Error('Choose at most five photos.')
  payload.images = await Promise.all(photos.map(photoToBase64))
  return payload
}

async function sendReport(data, endpoint) {
  let response
  try {
    response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
  } catch {
    throw new Error('Could not reach the backend. Check it is running on port 8000 and reachable from this device. If a found submission was interrupted, check saved reports before retrying.')
  }
  const result = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = result?.detail
    const message = Array.isArray(detail)
      ? detail.map((error) => `${error.loc?.slice(1).join('.') || 'Report'}: ${error.msg}`).join('; ')
      : typeof detail === 'string' ? detail : 'Unable to submit your report. Please try again.'
    throw new Error(message)
  }
  if (!result?.success || !['LOST', 'FOUND'].includes(result.report_type) || (result.report_type === 'FOUND' && !result.report_id)) throw new Error('Unexpected backend response. Check saved reports before retrying.')
  return result
}

export function sendLostReport(data, endpoint = `${API_URL}/reports/lost`) {
  return sendReport(data, endpoint)
}

export function sendFoundReport(data, endpoint = `${API_URL}/reports/found`) {
  return sendReport(data, endpoint)
}
