import json
from pathlib import Path
from typing import List, Dict, Optional, Callable, Generator, Mapping

import typer
from click import BadArgumentUsage

from sgpt import OpenAIClient, config, make_prompt
from sgpt.utils import CompletionModes
from sgpt.handlers.handler import Handler

CHAT_CACHE_LENGTH = int(config.get("CHAT_CACHE_LENGTH"))
CHAT_CACHE_PATH = Path(config.get("CHAT_CACHE_PATH"))


class ChatSession:
    """
    This class is used as a decorator for OpenAI chat API requests.
    The ChatCache class caches chat messages and keeps track of the
    conversation history. It is designed to store cached messages
    in a specified directory and in JSON format.
    """

    def __init__(self, length: int, storage_path: Path):
        """
        Initialize the ChatCache decorator.

        :param length: Integer, maximum number of cached messages to keep.
        """
        self.length = length
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def __call__(self, func: Callable) -> Callable:
        """
        The Cache decorator.

        :param func: The chat function to cache.
        :return: Wrapped function with chat caching.
        """

        def wrapper(*args, **kwargs):
            chat_id = kwargs.pop("chat_id", None)
            messages = kwargs["messages"]
            if not chat_id:
                yield from func(*args, **kwargs)
                return
            old_messages = self._read(chat_id)
            for message in messages:
                old_messages.append(message)
            kwargs["messages"] = old_messages
            response_text = ""
            for word in func(*args, **kwargs):
                response_text += word
                yield word
            old_messages.append({"role": "assistant", "content": response_text})
            self._write(kwargs["messages"], chat_id)

        return wrapper

    def _read(self, chat_id: str) -> List[Dict]:
        file_path = self.storage_path / chat_id
        if not file_path.exists():
            return []
        parsed_cache = json.loads(file_path.read_text())
        return parsed_cache if isinstance(parsed_cache, list) else []

    def _write(self, messages: List[Dict], chat_id: str):
        file_path = self.storage_path / chat_id
        json.dump(messages[-self.length:], file_path.open("w"))

    def invalidate(self, chat_id: str):
        file_path = self.storage_path / chat_id
        file_path.unlink()

    def get_messages(self, chat_id):
        messages = self._read(chat_id)
        return messages

    def exists(self, chat_id: Optional[str]) -> bool:
        return chat_id and bool(self._read(chat_id))

    def list(self):
        # Get all files in the folder.
        files = self.storage_path.glob("*")
        # Sort files by last modification time in ascending order.
        return sorted(files, key=lambda f: f.stat().st_mtime)


class ChatHandler(Handler):
    chat_session = ChatSession(CHAT_CACHE_LENGTH, CHAT_CACHE_PATH)

    def __init__(  # pylint: disable=too-many-arguments
            self,
            client: OpenAIClient,
            chat_id: str,
            prompt: str,
            role: str,
            model: str = "gpt-3.5-turbo",
    ) -> None:
        super().__init__(client)
        self.chat_id = chat_id
        self.client = client
        self.role = role
        self.model = model
        self.prompt = prompt

        self.chat_history = self.chat_session.get_messages(self.chat_id)
        self.messages = self.validate()

    @classmethod
    def list_ids(cls, value) -> None:
        if not value:
            return
        # Prints all existing chat IDs to the console.
        for chat_id in cls.chat_session.list():
            typer.echo(chat_id)
        raise typer.Exit()

    @classmethod
    def show_messages(cls, chat_id: str) -> None:
        if not chat_id:
            return
        # Prints all messages from a specified chat ID to the console.
        for index, message in enumerate(cls.chat_session.get_messages(chat_id)):
            color = "cyan" if index % 2 == 0 else "green"
            typer.secho(message, fg=color)
        raise typer.Exit()

    def validate(self) -> List[Mapping[dict, dict]]:
        if self.initiated:
            # TODO: Make this system able to tell what role a chat was started with, validate, and continue if the user didn't specify a role
            existing_system_prompt = self.chat_history[0]["content"]
            hypothetical_messages = make_prompt.prompt_constructor(self.prompt, role=self.role, chat_init=False)
            if hypothetical_messages[0]["content"] == existing_system_prompt:
                # return everything except the first message
                # because the system message is already in the chat history, and chat_cache will add it again
                messages = hypothetical_messages[1:]
            else:
                # Error message about how the user is asking for a different system chat than the one that already exists
                raise BadArgumentUsage(
                    f"Chat id:'{self.chat_id}' was initiated with system role as \n'{existing_system_prompt}'\n\n Can't be continued with new system prompt \n'{hypothetical_messages[0]['content']}'")
        else:
            messages = make_prompt.prompt_constructor(self.prompt, role=self.role, chat_init=True)

        return messages

    @property
    def initiated(self) -> bool:
        return self.chat_session.exists(self.chat_id)

    def get_messages(self) -> List[Mapping[dict, dict]]:
        return self.messages

    @chat_session
    def get_completion(  # pylint: disable=arguments-differ
            self,
            **kwargs,
    ) -> Generator:
        yield from super().get_completion(**kwargs)
