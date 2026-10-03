from collections import defaultdict


class ContextStore:
    def __init__(self) -> None:
        self._history = defaultdict(list)

    def append_user_message(self, session_id: str, message: str) -> None:
        self._history[session_id].append({'role': 'user', 'content': message})

    def append_agent_message(self, session_id: str, message: str) -> None:
        self._history[session_id].append({'role': 'assistant', 'content': message})

    def get_recent(self, session_id: str, limit: int = 8) -> list[dict[str, str]]:
        return self._history[session_id][-limit:]
