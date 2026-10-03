import cors from 'cors'
import express from 'express'
import healthRouter from './routes/health.js'
import agentProxyRouter from './routes/agentProxy.js'
import errorHandler from './middleware/errorHandler.js'

const app = express()

app.use(
  cors({
    origin: process.env.CLIENT_ORIGIN || 'http://localhost:5173',
  }),
)
app.use(express.json())

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', service: 'gateway-api' })
})

app.use('/health', healthRouter)
app.use('/api/agent', agentProxyRouter)

app.use(errorHandler)

export default app
