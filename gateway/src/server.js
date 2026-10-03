import 'dotenv/config'
import app from './app.js'

const port = process.env.PORT || 4000
process.env.AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000'
process.env.CLIENT_ORIGIN = process.env.CLIENT_ORIGIN || 'http://localhost:5173'

app.listen(port, () => {
  console.log(`Gateway listening on http://localhost:${port}`)
})
