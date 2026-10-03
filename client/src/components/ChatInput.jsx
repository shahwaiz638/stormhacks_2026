import { useState } from 'react'

function ChatInput({ onSend }) {
  const [message, setMessage] = useState('')
  const [responseText, setResponseText] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()

    const trimmedMessage = message.trim()
    if (!trimmedMessage || isLoading) {
      return
    }

    setIsLoading(true)
    try {
      const payload = await onSend({ message: trimmedMessage })
      setResponseText(payload.reply || 'No response yet')
      setMessage('')
    } catch {
      setResponseText('Unable to reach AI service.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-3">
      <form className="flex flex-col gap-2 sm:flex-row" onSubmit={handleSubmit}>
        <input
          className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 outline-none focus:ring-2 focus:ring-sky-500"
          placeholder="Ask the AI agent..."
          value={message}
          onChange={(event) => setMessage(event.target.value)}
        />
        <button
          className="rounded-md bg-sky-600 px-4 py-2 font-medium text-white hover:bg-sky-500 disabled:cursor-not-allowed disabled:opacity-70"
          type="submit"
          disabled={isLoading}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>

      <div className="rounded-md border border-slate-800 bg-slate-950 p-3 text-sm text-slate-300">
        <p className="mb-1 text-xs uppercase tracking-wide text-slate-500">Agent response</p>
        <p>{responseText || 'Responses will appear here.'}</p>
      </div>
    </div>
  )
}

export default ChatInput
