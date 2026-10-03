import { Router } from 'express'

const agentProxyRouter = Router()

agentProxyRouter.post('/chat', async (req, res, next) => {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 10000)

  try {
    const upstreamResponse = await fetch(`${process.env.AI_SERVICE_URL}/api/v1/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
      signal: controller.signal,
    })

    const payload = await upstreamResponse.json()
    res.status(upstreamResponse.status).json(payload)
  } catch (error) {
    next(error)
  } finally {
    clearTimeout(timeoutId)
  }
})

export default agentProxyRouter
