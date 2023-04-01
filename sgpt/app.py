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
from typing import Mapping, List
import sgpt.role_manager as role_manager

import typer

# Click is part of typer.
from click import MissingParameter, BadParameter
from sgpt import config, make_prompt, OpenAIClient
from sgpt.utils import (
    echo_chat_ids,
    echo_chat_messages,
    get_edited_prompt,
)


def get_completion(
        messages: List[Mapping[dict, dict]],
        temperature: float,
        top_p: float,
        model: str,
        caching: bool,
        chat: str,
):
    api_host = config.get("OPENAI_API_HOST")
    api_key = config.get("OPENAI_API_KEY")
    client = OpenAIClient(api_host, api_key)
    return client.get_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        top_probability=top_p,
        caching=caching,
        chat_id=chat,
    )


def main(
        prompt: str = typer.Argument(None, show_default=False, help="The prompt to generate completions for."),
        temperature: float = typer.Option(1.0, min=0.0, max=1.0, help="Randomness of generated output."),
        top_probability: float = typer.Option(1.0, min=0.1, max=1.0, help="Limits highest probable tokens (words)."),
        model: str = typer.Option(config.get("DEFAULT_MODEL"), help="Specify what model to use."),
        role: str = typer.Option("default", help="Specify what role a prompt should use. Defaults: shell, code, default."),
        save_role: str = typer.Option(None, help="Save a role for future use."),
        list_roles: bool = typer.Option(False, help="List all saved roles."),
        show_role: str = typer.Option(None, help="Show a saved role."),
        chat: str = typer.Option(None, help="Follow conversation with id (chat mode)."),
        show_chat: str = typer.Option(None, help="Show all messages from provided chat id."),
        list_chat: bool = typer.Option(False, help="List all existing chat ids."),
        editor: bool = typer.Option(False, help="Open $EDITOR to provide a prompt."),
        cache: bool = typer.Option(True, help="Cache completion results."),
) -> None:
    role_manager.check_and_setup_default_roles()
    if list_chat:
        echo_chat_ids()
        return
    if show_chat:
        echo_chat_messages(show_chat)
        return
    if list_roles:
        role_manager.list_roles(echo=True)
        return
    if show_role:
        role_manager.show_role(show_role, echo=True)
        return
    if save_role:
        role_manager.save_role(save_role, prompt, echo=True)
        return

    if not prompt and not editor:
        raise MissingParameter(param_hint="PROMPT", param_type="string")

    if editor:
        prompt = get_edited_prompt(prompt)

    # is an existing chat that should be continued
    if chat and OpenAIClient.chat_cache.exists(chat):
        chat_history = OpenAIClient.chat_cache.get_messages(chat)
        existing_system_prompt = chat_history[0]["content"]
        hypothetical_messages = make_prompt.prompt_constructor(prompt, role=role)

        if hypothetical_messages[0]["content"] == existing_system_prompt:
            # return everything except the first message
            # because the system message is already in the chat history, and chat_cache will add it again
            messages = hypothetical_messages[1:]
        else:
            # Error message about how the user is asking for a different system chat than the one that already exists
            raise BadParameter(
                f"Chat id:'{chat}' was initiated with system role as \n'{existing_system_prompt}'\n\n Can't be continued with new system prompt \n'{hypothetical_messages[0]['content']}'")
    else:
        # not chat or is a new chat case
        messages = make_prompt.prompt_constructor(prompt, role=role, chat_init=True)

    completion = get_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        top_p=top_probability,
        caching=cache,
        chat=chat,
    )

    full_completion = ""
    for word in completion:
        typer.secho(word, fg="magenta", bold=True, nl=False)
        full_completion += word
    typer.secho()
    # if "EXECUTABLE_RETURNS" in role is true then ask if the response should be executed as shell command
    role_data = role_manager.recall_role(role)
    if role_data and role_data.get("EXECUTABLE_RETURNS") and typer.confirm("Execute shell command?"):
        os.system(full_completion)


def entry_point() -> None:
    # Python package entry point defined in setup.py
    typer.run(main)


if __name__ == "__main__":
    entry_point()
