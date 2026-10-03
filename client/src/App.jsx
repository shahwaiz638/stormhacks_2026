import { Link, Navigate, Route, Routes } from 'react-router-dom'
import ChatInput from './components/ChatInput.jsx'

function HomePage() {
  return (
    <section className="rounded-lg border border-slate-800 bg-slate-900/60 p-6">
      <h1 className="text-2xl font-semibold text-slate-50">Hackathon App Starter</h1>
      <p className="mt-3 text-slate-300">
        Theme-agnostic foundation with a React client, Express gateway, and FastAPI AI service.
      </p>
    </section>
  )
}

function AgentPlaygroundPage() {
  const handleSend = async ({ message }) => {
    const response = await fetch('/api/agent/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    })

    return response.json()
  }

  return (
    <section className="rounded-lg border border-slate-800 bg-slate-900/60 p-6">
      <h2 className="text-xl font-semibold text-slate-50">AI Agent Playground</h2>
      <p className="mt-2 text-slate-300">Use this reusable chat input to interact with the AI agent service.</p>
      <div className="mt-4">
        <ChatInput onSend={handleSend} />
      </div>
    </section>
  )
}

function App() {
  return (
    <div className="mx-auto flex min-h-screen w-full max-w-5xl flex-col px-4 py-6 sm:px-6">
      <header className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm uppercase tracking-wide text-slate-400">stormhacks_2026</p>
        <nav className="flex gap-2 text-sm">
          <Link className="rounded-md border border-slate-700 px-3 py-2 text-slate-200 hover:bg-slate-800" to="/">
            Home
          </Link>
          <Link
            className="rounded-md border border-slate-700 px-3 py-2 text-slate-200 hover:bg-slate-800"
            to="/agent"
          >
            Agent
          </Link>
        </nav>
      </header>

      <main className="flex-1">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/agent" element={<AgentPlaygroundPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
