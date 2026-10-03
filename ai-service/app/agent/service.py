import os
import uuid

from app.agent.context import ContextStore


class AgentService:
    def __init__(self, context_store: ContextStore) -> None:
        self.context_store = context_store
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

    async def chat(self, message: str, session_id: str | None = None) -> dict[str, str]:
        resolved_session_id = session_id or str(uuid.uuid4())
        self.context_store.append_user_message(resolved_session_id, message)

        reply, provider = self._generate_reply(resolved_session_id, message)

        self.context_store.append_agent_message(resolved_session_id, reply)

        return {
            'reply': reply,
            'session_id': resolved_session_id,
            'provider': provider,
        }

    def _generate_reply(self, session_id: str, message: str) -> tuple[str, str]:
        api_key = os.getenv('GEMINI_API_KEY')
        recent_context = self.context_store.get_recent(session_id)

        if api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(self.model_name)
                prompt = self._build_prompt(recent_context, message)
                response = model.generate_content(prompt)

                if response.text:
                    return response.text.strip(), 'gemini'
            except Exception:
                pass

        fallback = (
            f"Received: '{message}'. Gemini API key missing/unavailable, "
            'using local fallback response.'
        )
        return fallback, 'local-fallback'

    @staticmethod
    def _build_prompt(context: list[dict[str, str]], latest_message: str) -> str:
        transcript = '\n'.join(f"{item['role']}: {item['content']}" for item in context)
        return (
            'You are a modular AI agent for a hackathon app. '
            'Provide concise and helpful responses.\n\n'
            f'Conversation context:\n{transcript}\n\n'
            f'Latest user message:\n{latest_message}'
        )
