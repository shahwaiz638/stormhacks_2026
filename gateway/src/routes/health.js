import { Router } from 'express'

const healthRouter = Router()

healthRouter.get('/', (_req, res) => {
  res.json({ status: 'ok', service: 'gateway' })
})

export default healthRouter
