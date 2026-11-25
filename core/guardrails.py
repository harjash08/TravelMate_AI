
from typing import Any

from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    hook_config
)
from langchain.messages import AIMessage
from langgraph.runtime import Runtime


class TravelInputGuardrail(AgentMiddleware):

    MAX_INPUT_LENGTH = 100000

    @hook_config(can_jump_to=["end"])
    def before_agent(
        self,
        state: AgentState,
        runtime: Runtime
    ) -> dict[str, Any] | None:

        messages = state.get("messages", [])

        # 1. Empty message validation
        if not messages:
            return self.reject("Please provide a message.")

        # Find the latest user message
        user_messages = [
            msg for msg in reversed(messages)
            if msg.type == "human"
        ]

        if not user_messages:
            return self.reject("No user message found.")

        user_message = user_messages[0].content

        # 2. Input type validation
        if not isinstance(user_message, str):
            return self.reject("Invalid input format.")

        # 3. Empty or whitespace validation
        user_message = user_message.strip()

        if not user_message:
            return self.reject("Your message cannot be empty.")

        # 4. Maximum input length validation
        if len(user_message) > self.MAX_INPUT_LENGTH:
            return self.reject(
                f"Your message exceeds the maximum "
                f"limit of {self.MAX_INPUT_LENGTH} characters."
            )

        # All validations passed
        return None

    def reject(self, message: str) -> dict[str, Any]:

        return {
            "messages": [
                AIMessage(content=message)
            ],
            "jump_to": "end"
        }
