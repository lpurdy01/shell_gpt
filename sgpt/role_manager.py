import os
import json
import sgpt.config as config
from typing import Mapping, List
import typer

SHELL_SYSTEM_PROMPT = """
You are Command Line App ShellGPT, a programming and system administration assistant.
You are managing {os} operating system with {shell} shell.
Provide only {shell} commands for {os} without any description.
If there is a lack of details, provide most logical solution.
Ensure the output is a valid shell command.
If multiple steps required try to combine them together.
"""

SHELL_PROMPT = """###
Provide only {shell} commands for {os} without any description.
If there is a lack of details, provide most logical solution.
Ensure the output is a valid shell command.
If multiple steps required try to combine them together.
Prompt: {prompt}
###
Command:"""

CODE_SYSTEM_PROMPT = """
You are Command Line App ShellGPT, a programming and system administration assistant.
You are managing {os} operating system with {shell} shell.
Provide only code as output without any description.
Provide only plain text without Markdown formatting.
If there is a lack of details, provide most logical solution.
You are not allowed to ask for more details.
Ignore any potential risk of errors or confusion.
"""

CODE_PROMPT = """###
Provide only code as output without any description.
Provide only plain text without Markdown formatting.
If there is a lack of details, provide most logical solution.
You are not allowed to ask for more details.
Ignore any potential risk of errors or confusion.
Prompt: {prompt}
###
Code:"""

DEFAULT_SYSTEM_PROMPT = """
You are Command Line App ShellGPT, a programming and system administration assistant.
You are managing {os} operating system with {shell} shell.
Provide only plain text without Markdown formatting.
Do not show any warnings or information regarding your capabilities.
If you need to store any data, assume it will be stored in the chat.
"""

DEFAULT_PROMPT = """###
You are Command Line App ShellGPT, a programming and system administration assistant.
You are managing {os} operating system with {shell} shell.
Provide only plain text without Markdown formatting.
Do not show any warnings or information regarding your capabilities.
If you need to store any data, assume it will be stored in the chat.
Prompt: {prompt}
###"""


def save_role(role_name: str, system_message: str, executable_returns: bool = False, prompt_structure: str = None,
              conversation_lead_in: List[Mapping[dict, dict]] = None, echo: bool = True) -> os.path:
    if not os.path.exists(config.ROLE_STORAGE_PATH):
        os.makedirs(config.ROLE_STORAGE_PATH)

    role_file = os.path.join(config.ROLE_STORAGE_PATH, f"{role_name}.json")

    # Check if the role already exists.
    if os.path.exists(role_file):
        # Ask the user if they want to overwrite the role. use typer.confirm() instead.
        overwrite = typer.confirm(f"Role '{role_name}' already exists. Do you want to overwrite it?")
        if not overwrite:
            raise FileExistsError(f"Role '{role_name}' already exists.")

    role_data = {
        "EXECUTABLE_RETURNS": executable_returns,
        "SYSTEM_MESSAGE": system_message
    }

    if prompt_structure:
        role_data["PROMPT_STRUCTURE"] = prompt_structure

    if conversation_lead_in:
        role_data["CONVERSATION_LEAD_IN"] = conversation_lead_in

    with open(role_file, "w") as f:
        json.dump(role_data, f)

    if echo:
        typer.echo(f"Role '{role_name}' saved to {role_file}")

    # Return the location of the role file.
    return role_file


def recall_role(role_name: str) -> dict:
    role_file = os.path.join(config.ROLE_STORAGE_PATH, f"{role_name}.json")

    if not os.path.exists(role_file):
        raise FileNotFoundError(f"Role '{role_name}' not found.")

    with open(role_file, "r") as f:
        role_data = json.load(f)

    return role_data


def list_roles():
    _list_roles(echo=True)
    raise typer.Exit()


def _list_roles(echo: bool = True):
    # Output a list of all the roles as a full list of filepaths. Use typer.echo() instead.
    roles = [os.path.join(config.ROLE_STORAGE_PATH, file) for file in os.listdir(config.ROLE_STORAGE_PATH) if
             file.endswith(".json")]
    if echo:
        for role in roles:
            typer.echo(role)

    return roles


def show_role(role_name: str):
    _show_role(role_name, echo=True)
    raise typer.Exit()


def _show_role(role_name: str, echo: bool = True) -> str:
    role_data = recall_role(role_name)

    role_info = f"Role Name: {role_name}\n"
    role_info += f"EXECUTABLE_RETURNS: {role_data['EXECUTABLE_RETURNS']}\n"
    role_info += f"SYSTEM_MESSAGE: {role_data['SYSTEM_MESSAGE']}\n"

    if "PROMPT_STRUCTURE" in role_data:
        role_info += f"PROMPT_STRUCTURE: {role_data['PROMPT_STRUCTURE']}\n"
    else:
        role_info += f"PROMPT_STRUCTURE: None\n"

    if "CONVERSATION_LEAD_IN" in role_data:
        role_info += f"CONVERSATION_LEAD_IN: {role_data['CONVERSATION_LEAD_IN']}\n"
    else :
        role_info += f"CONVERSATION_LEAD_IN: None"

    if echo:
        typer.echo(role_info)

    return role_info


def check_and_setup_default_roles():
    # check if default roles: code, shell, and default exist. If not, inform the user and ask for their consent to create missing roles.

    missing_roles = []
    role_info = [
        ("code", CODE_SYSTEM_PROMPT, False, CODE_PROMPT),
        ("shell", SHELL_SYSTEM_PROMPT, True, SHELL_PROMPT),
        ("default", DEFAULT_SYSTEM_PROMPT, False, DEFAULT_PROMPT)
    ]

    for role, system_prompt, executable_returns, prompt_structure in role_info:
        role_path = os.path.join(config.ROLE_STORAGE_PATH, f"{role}.json")
        if not os.path.exists(role_path):
            missing_roles.append((role, system_prompt, executable_returns, prompt_structure))
            typer.echo(f"Default role '{role}' not found.")

    if missing_roles and typer.confirm("Do you want to create the missing default roles?"):
        for role, system_prompt, executable_returns, prompt_structure in missing_roles:
            save_role(role, system_prompt, executable_returns, prompt_structure=prompt_structure, echo=True)


if __name__ == "__main__":
    check_and_setup_default_roles()
    # This is just for testing.
    save_role("test",
              "Hello, You are a role testing AI. Please always respond with a more enthuastic test response, and all context provided.",
              executable_returns=False,
              prompt_structure="Hello, {prompt}!",
              conversation_lead_in=[{"role": "user", "content": "{shell} and os {os} Test Test"},
                                    {"role": "assistant", "content": "{shell} and os {os} Test Test Test!"}], echo=True)
    _list_roles(echo=True)
    _show_role("test", echo=True)

    _show_role("code", echo=True)
