from pathlib import Path

from sgpt import OpenAIClient, config, make_prompt
from typing import List, Mapping
from sgpt.utils import CompletionModes
from .handler import Handler

CHAT_CACHE_LENGTH = int(config.get("CHAT_CACHE_LENGTH"))
CHAT_CACHE_PATH = Path(config.get("CHAT_CACHE_PATH"))


class DefaultHandler(Handler):
    def __init__(
        self,
        client: OpenAIClient,
        prompt: str,
        role: str,
        model: str = "gpt-3.5-turbo",
    ) -> None:
        super().__init__(client)
        self.client = client
        self.prompt = prompt
        self.role = role
        self.model = model

    def get_messages(self) -> List[Mapping[dict, dict]]:
        messages = make_prompt.prompt_constructor(
            self.prompt, role=self.role, chat_init=True
        )
        return messages
