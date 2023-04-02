from typing import List, Generator, Mapping

import typer

from sgpt import OpenAIClient


class Handler:
    def __init__(self, client: OpenAIClient):
        self.client = client

    def get_messages(self) -> List[Mapping[dict, dict]]:
        # This should never be called because it is overridden in the child class.
        raise NotImplementedError

    def get_completion(  # pylint: disable=too-many-arguments
        self,
        messages: List[Mapping[dict, dict]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 1,
        top_probability: float = 1,
        caching: bool = True,
    ) -> Generator:
        yield from self.client.get_completion(
            messages,
            model,
            temperature,
            top_probability,
            caching=caching,
        )

    def handle(self, **kwargs) -> str:
        messages = self.get_messages()
        full_completion = ""
        for word in self.get_completion(messages=messages, **kwargs):
            typer.secho(word, fg="magenta", bold=True, nl=False)
            full_completion += word
        typer.echo()
        return full_completion
