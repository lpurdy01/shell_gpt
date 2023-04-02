import platform
from os import getenv
from os.path import basename, splitext
from distro import name as distro_name
from typing import Mapping, List
import json
import sgpt.role_manager as role_manager


def message_completer(message: str, prompt:str = None) -> str:
    operating_systems = {
        "Linux": "Linux/" + distro_name(pretty=True),
        "Windows": "Windows " + platform.release(),
        "Darwin": "Darwin/MacOS " + platform.mac_ver()[0],
    }
    current_platform = platform.system()
    os_name = operating_systems.get(current_platform, current_platform)
    shell_name = basename(getenv("SHELL", "PowerShell"))
    if os_name == "nt":
        shell_name = splitext(basename(getenv("COMSPEC", "Powershell")))[0]
    if prompt:
        return message.format(prompt=prompt, shell=shell_name, os=os_name)
    return message.format(shell=shell_name, os=os_name)


def conversation_lead_in_context_completer(lead_in: List[Mapping[dict, dict]]) -> List[Mapping[dict, dict]]:
    for message in lead_in:
        message["content"] = message_completer(message["content"])
    return lead_in


def prompt_constructor(prompt: str, role: str = "default", chat_init: bool = True) -> List[Mapping[dict, dict]]:
    prompt = prompt.strip()

    if not role:
        role = "default"

    role_data = role_manager.recall_role(role)
    system_message = message_completer(role_data["SYSTEM_MESSAGE"])

    messages = [message_constructor(system_message, system=True)]
    if chat_init and "CONVERSATION_LEAD_IN" in role_data:
        # Add the conversation lead in messages with context.
        messages.extend(conversation_lead_in_context_completer(role_data["CONVERSATION_LEAD_IN"]))
    messages.append(following_prompt_constructor(prompt, role_data))
    return messages


def following_prompt_constructor(prompt: str, role_data: dict) -> dict:
    prompt = prompt.strip()
    if "PROMPT_STRUCTURE" not in role_data:
        return message_constructor(prompt, user=True)
    prompt_structure = role_data["PROMPT_STRUCTURE"]
    prompt_structure = message_completer(prompt_structure, prompt=prompt)
    message = message_constructor(prompt_structure, user=True)

    return message


def message_constructor(message: str, system: bool = False, user: bool = False, assistant: bool = False) -> dict:
    if not (system or user or assistant):
        raise ValueError("At least one of system, user, assistant must be True")

    if system:
        return json.loads(f'{{"role": "system", "content": "{message}"}}', strict=False)
    elif user:
        return json.loads(f'{{"role": "user", "content": "{message}"}}', strict=False)
    elif assistant:
        return json.loads(f'{{"role": "assistant", "content": "{message}"}}', strict=False)