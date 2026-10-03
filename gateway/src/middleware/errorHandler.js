export default function errorHandler(err, _req, res, _next) {
  const statusCode = err.name === 'AbortError' ? 504 : 500
  const message = err.name === 'AbortError' ? 'AI service request timed out' : 'Internal server error'

  res.status(statusCode).json({
    error: message,
    details: process.env.NODE_ENV === 'development' ? err.message : undefined,
  })
}
