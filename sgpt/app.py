"""
shell-gpt: An interface to OpenAI's ChatGPT (GPT-3.5) API

This module provides a simple interface for OpenAI's ChatGPT API using Typer
as the command line interface. It supports different modes of output including
shell commands and code, and allows users to specify the desired OpenAI model
and length and other options of the output. Additionally, it supports executing
shell commands directly from the interface.

API Key is stored locally for easy use in future runs.
"""

import os

import typer

# Click is part of typer.
from click import MissingParameter
from sgpt import config, OpenAIClient
from sgpt import ChatHandler, DefaultHandler
from sgpt.utils import get_edited_prompt
from sgpt import role_manager


def main(  # pylint: disable=R0913,R0914
    prompt: str = typer.Argument(
        None,
        show_default=False,
        help="The prompt to generate completions for.",
    ),
    temperature: float = typer.Option(
        0.1,
        min=0.0,
        max=1.0,
        help="Randomness of generated output.",
    ),
    top_probability: float = typer.Option(
        1.0,
        min=0.1,
        max=1.0,
        help="Limits highest probable tokens (words).",
    ),
    model: str = typer.Option(
        config.get("DEFAULT_MODEL"),
        help="The model to use for completion.",
    ),
    role: str = typer.Option(
        "default",
        help="Specify what role a prompt should use. Defaults: shell, code, default.",
        rich_help_panel="Role Options",
    ),
    save_role: str = typer.Option(
        None,
        help="Save a role for future use.",
        rich_help_panel="Role Options",
    ),
    list_roles: bool = typer.Option(  # pylint: disable=W0613
        False,
        help="List all saved roles.",
        callback=role_manager.list_roles,
        rich_help_panel="Role Options",
    ),
    show_role: str = typer.Option(  # pylint: disable=W0613
        None,
        help="Show a saved role.",
        callback=role_manager.show_role,
        rich_help_panel="Role Options",
    ),
    chat: str = typer.Option(
        None,
        help="Follow conversation with id (chat mode).",
        rich_help_panel="Chat Options",
    ),
    show_chat: str = typer.Option(  # pylint: disable=W0613
        None,
        help="Show all messages from provided chat id.",
        callback=ChatHandler.show_messages,
        rich_help_panel="Chat Options",
    ),
    list_chat: bool = typer.Option(  # pylint: disable=W0613
        False,
        help="List all existing chat ids.",
        callback=ChatHandler.list_ids,
        rich_help_panel="Chat Options",
    ),
    editor: bool = typer.Option(
        False,
        help="Open $EDITOR to provide a prompt.",
    ),
    cache: bool = typer.Option(
        True,
        help="Cache completion results.",
    ),
) -> None:
    role_manager.check_and_setup_default_roles()
    if save_role:
        role_manager.save_role(save_role, prompt, echo=True)
        return

    if not prompt and not editor:
        raise MissingParameter(param_hint="PROMPT", param_type="string")

    if editor:
        prompt = get_edited_prompt(prompt)

    api_host = config.get("OPENAI_API_HOST")
    api_key = config.get("OPENAI_API_KEY")
    client = OpenAIClient(api_host, api_key)

    if chat:
        # TODO: Why doesn't execution continue after .handle returns?
        full_completion = ChatHandler(client, chat, prompt, role).handle(
            temperature=temperature,
            top_probability=top_probability,
            model=model,
            chat_id=chat,
            caching=cache,
        )
    else:
        full_completion = DefaultHandler(client, prompt, role).handle(
            temperature=temperature,
            top_probability=top_probability,
            model=model,
            caching=cache,
        )

        # if "EXECUTABLE_RETURNS" in role is true then ask
        # if the response should be executed as shell command
        role_data = role_manager.recall_role(role)
        if (
            role_data
            and role_data.get("EXECUTABLE_RETURNS")
            and typer.confirm("Execute shell command?")
        ):
            os.system(full_completion)


def entry_point() -> None:
    # Python package entry point defined in setup.py
    typer.run(main)


if __name__ == "__main__":
    entry_point()
