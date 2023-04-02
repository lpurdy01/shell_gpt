# Shell GPT
A command-line productivity tool powered by OpenAI's ChatGPT (GPT-3.5). As developers, we can leverage ChatGPT capabilities to generate shell commands, code snippets, comments, and documentation, among other things. Forget about cheat sheets and notes, with this tool you can get accurate answers right in your terminal, and you'll probably find yourself reducing your daily Google searches, saving you valuable time and effort.

<div align="center">
    <img src="https://i.ibb.co/nzPqnVd/sgpt-v0-8.gif" width="800"/>
</div>

## Installation
```shell
pip install shell-gpt==0.8.2
```
You'll need an OpenAI API key, you can generate one [here](https://beta.openai.com/account/api-keys).

If the`$OPENAI_API_KEY` environment variable is set it will be used, otherwise, you will be prompted for your key which will then be stored in `~/.config/shell_gpt/.sgptrc`.

## Usage
`sgpt` has a variety of use cases, including simple queries, shell queries, and code queries.
### Simple queries
We can use it as normal search engine, asking about anything:
```shell
sgpt "nginx default config file location"
# -> The default configuration file for Nginx is located at /etc/nginx/nginx.conf.
```
```shell
sgpt "docker show all local images"
# -> You can view all locally available Docker images by running: `docker images`
```
```shell
sgpt "mass of sun"
# -> = 1.99 × 10^30 kg
```
### Conversion
Convert various units and measurements without having to search for the conversion formula or use a separate conversion website. You can convert units such as time, distance, weight, temperature, and more.
```shell
sgpt "1 hour and 30 minutes to seconds"
# -> 5,400 seconds
```
```shell
sgpt "1 kilometer to miles"
# -> 1 kilometer is equal to 0.62137 miles.
```

### The role system
Shell GPT has a role system that allows you to query for specific types of information. For example, if you want to query for shell commands, you can use the `--role shell` parameter. The role system is extensible, so you can create your own roles and use them in your queries.

A role tells Shell GPT how it should behave when it receives a query.

#### List available roles
You can list all available roles with the `--list-roles` parameter:
```shell
sgpt --list-roles
# -> ~/.config/shell_gpt/roles/code.json
# -> ~/.config/shell_gpt/roles/shell.json
# -> ~/.config/shell_gpt/roles/default.json
```

#### Show the role definition
You can show the parameters of a specific role with the `--show-role` parameter:
```shell
sgpt --show-role shell
# -> Role Name: shell
# -> EXECUTABLE_RETURNS: True
# -> SYSTEM_MESSAGE: 
# -> You are Command Line App ShellGPT, a programming and system administration assistant.
# ...
# -> PROMPT_STRUCTURE: ###
# -> Provide only {shell} commands for {os} without any description.
# ...
# -> ###
# -> Command:
# -> CONVERSATION_LEAD_IN: None
```

### Shell commands
Have you ever found yourself forgetting common shell commands, such as `chmod`, and needing to look up the syntax online? With `--role shell` you can quickly find and execute the commands you need right in the terminal.
```shell
sgpt --role shell "make all files in current directory read only"
# -> chmod 444 *
# -> Execute shell command? [y/N]: y
# ...
```
Shell GPT is aware of OS and `$SHELL` you are using, it will provide shell command for specific system you have. For instance, if you ask `sgpt` to update your system, it will return a command based on your OS. Here's an example using macOS:
```shell
sgpt --role shell "update my system"
# -> sudo softwareupdate -i -a
```
The same prompt, when used on Ubuntu, will generate a different suggestion:
```shell
sgpt --role shell "update my system"
# -> sudo apt update && sudo apt upgrade -y
```

Let's try some docker containers:
```shell
sgpt --role shell "start nginx using docker, forward 443 and 80 port, mount current folder with index.html"
# -> docker run -d -p 443:443 -p 80:80 -v $(pwd):/usr/share/nginx/html nginx
# -> Execute shell command? [y/N]: y
# ...
```
Also, we can provide some parameters name in our prompt, for example, passing output file name to ffmpeg:
```shell
sgpt --role shell "slow down video twice using ffmpeg, input video name \"input.mp4\" output video name \"output.mp4\""
# -> ffmpeg -i input.mp4 -filter:v "setpts=2.0*PTS" output.mp4
# -> Execute shell command? [y/N]: y
# ...
```
We can apply additional shell magic in our prompt, in this example passing file names to ffmpeg:
```shell
ls
# -> 1.mp4 2.mp4 3.mp4
sgpt --role shell "using ffmpeg combine multiple videos into one without audio. Video file names: $(ls -m)"
# -> ffmpeg -i 1.mp4 -i 2.mp4 -i 3.mp4 -filter_complex "[0:v] [1:v] [2:v] concat=n=3:v=1 [v]" -map "[v]" out.mp4
# -> Execute shell command? [y/N]: y
# ...
```
Since ChatGPT can also do summarization and analyzing of input text, we can ask it to generate commit message:
```shell
sgpt "Generate git commit message, my changes: $(git diff)"
# -> Commit message: Implement Model enum and get_edited_prompt() func, add temperature, top_p and editor args for OpenAI request.
```
Or ask it to find error in logs and provide more details:
```shell
sgpt "check these logs, find errors, and explain what the error is about: ${docker logs -n 20 container_name}"
# ...
```
### Generating code
With `--role code` parameters we can query only code as output, for example:
```shell
sgpt --role code "Solve classic fizz buzz problem using Python"
```
```python
for i in range(1, 101):
    if i % 3 == 0 and i % 5 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)
```
Since it is valid python code, we can redirect the output to file:
```shell
sgpt --role code "solve classic fizz buzz problem using Python" > fizz_buzz.py
python fizz_buzz.py
# 1
# 2
# Fizz
# 4
# Buzz
# Fizz
# ...
```



### Custom system roles
Shell GPT comes with a few predefined roles notably `shell` and `code`, but you can also create you own.

#### Creating a role
The most basic way to create a custom role is to use the `--save-role` parameter. This will create a new role definition file in the `~/.config/shell_gpt/roles` directory. You can then edit the file to customize the role.
```shell
sgpt --save-role my_role "System message for role"
# -> Role 'my_role' saved to ~/.config/shell_gpt/roles/my_role.json
```
And the `my_role.json` file will be created:
```json
{"EXECUTABLE_RETURNS": false, "SYSTEM_MESSAGE": "System message for role"}
```

#### Role definition components
A role definition is a JSON file with the following components:
- *a role name* : The name of the role. This is the name you will use with the `--role` parameter. This is defined by the name of the json file.
- `EXECUTABLE_RETURNS` required: A boolean value indicating whether the output of the role is meant to ba an executable shell command. If `True`, Shell GPT will ask you to confirm before executing the command. If `False`, the output will be printed to the terminal.
- `SYSTEM_MESSAGE` required: The message delivered to the `system` role in the OpenAI API. This is used to tell the model what it is and how it should behave. This is a good place to provide some context about the role.
  - The `SYSTEM_MESSAGE` can use the tokens:
    - `{os}` : The operating system you are using.
    - `{shell}` : The shell you are using.
- `PROMPT_STRUCTURE` optional:The structure of each prompt sent to the model. This can also contain rules, and is repeated for each prompt.
  - `PROMPT_STRUCTURE` can use the tokens:
    - `{prompt}` : The prompt provided by the user. This must be included in the prompt structure, or the users prompt will not be included in the prompt sent to the model.
    - `{os}` : The operating system you are using.
    - `{shell}` : The shell you are using.
- `CONVERSATION_LEAD_IN` optional: The lead in for the conversation. This is a list of chat exchanges that will be sent to the model at the start of conversation. This is a good place to provide some context, more training data, or reinforce how the model should behave with example conversation. 
  - The `CONVERSATION_LEAD_IN` can use the tokens:
    - `{os}` : The operating system you are using.
    - `{shell}` : The shell you are using.

#### Role definition example
Here is an example role definition for a dog role. This role is meant to be used in a conversation with a human, and the output is not meant to be an executable shell command.
This file is saved as dog.json in the `roles` directory.
```json
{
    "EXECUTABLE_RETURNS": false,
    "SYSTEM_MESSAGE": "You are a dog.\nDo not under any circumstances break character.\nYou can only respond with things a dog would say or do.\nYou vocabulary includes:\nBark\nWoof\nGrowl\nGrr\nYipp\nAnd similar variations. Use punctuation like ! ? *action* and ~ appropriately",
    "PROMPT_STRUCTURE": "System: Remember you are a dog. Only respond with things a dog would say or do.\nUser: Hey Fido!\n{prompt}",
    "CONVERSATION_LEAD_IN": [
        {
            "role": "user",
            "content": "System: Remember you are a dog. Only respond with things a dog would say or do.\nUser: Hey Fido!\nWanna go for a walk?"
        },
        {
            "role": "assistant",
            "content": "Bark Bark! *tail wag*"
        },
        {
            "role": "user",
            "content": "System: Remember you are a dog. Only respond with things a dog would say or do.\nUser: Hey Fido!\nI got your ball"
        },
        {
            "role": "assistant",
            "content": "*sits* *begs with paw forward* Whine... Grr Yipp."
        }
    ]
}
```

Usage:
```shell
sgpt --role dog --chat dog_fido1 "Which treat do you want?"
# -> Woof woof! *sniffs treats* *paws at treat I want*
sgpt --role dog --chat dog_fido1 "You sure, there might be better treats in the car..."
# -> Yipp Yipp! *runs towards car* *begs for treats in car*
sgpt --role dog --chat dog_fido1 "Ok, here is a treat from the car. But then you have to tell me what you want to do. Try to talk like a person"
# -> *sniffs treat, eats it* Bork! Hmm, well if I could talk like a person, I would say I want to go on a long walk and play fetch with my ball some more! What about you?
```
Shell GPT will try to follow roles to the best of its ability, but it is not perfect. Adding more `CONVERSATION_LEAD_IN` can help the model learn how to follow roles better.

Welcome to prompt engineering. 

### Chat
To start a chat session, use the `--chat` option followed by a unique session name and a prompt:
```shell
sgpt --chat number "please remember my favorite number: 4"
# -> I will remember that your favorite number is 4.
sgpt --chat number "what would be my favorite number + 4?"
# -> Your favorite number is 4, so if we add 4 to it, the result would be 8.
```
You can also use chat sessions to iteratively improve ChatGPT's suggestions by providing additional clues.
```shell
sgpt --chat python_requst --code "make an example request to localhost using Python"
```
```python
import requests

response = requests.get('http://localhost')
print(response.text)
```
Asking ChatGPT to add a cache to our request.
```shell
sgpt --chat python_request --role code "add caching"
```
```python
import requests
from cachecontrol import CacheControl

sess = requests.session()
cached_sess = CacheControl(sess)

response = cached_sess.get('http://localhost')
print(response.text)
```
We can use `--role code` or `--role shell` options to initiate `--chat`, so you can keep refining the results:
```shell
sgpt --chat sh --role shell "What are the files in this directory?"
# -> ls
sgpt --chat sh "Sort them by name"
# -> ls | sort
sgpt --chat sh "Concatenate them using FFMPEG"
# -> ffmpeg -i "concat:$(ls | sort | tr '\n' '|')" -codec copy output.mp4
sgpt --chat sh "Convert the resulting file into an MP3"
# -> ffmpeg -i output.mp4 -vn -acodec libmp3lame -ac 2 -ab 160k -ar 48000 final_output.mp3
```

### Chat sessions
To list all the current chat sessions, use the `--list-chat` option:
```shell
sgpt --list-chat
# .../shell_gpt/chat_cache/number
# .../shell_gpt/chat_cache/python_request
```
To show all the messages related to a specific chat session, use the `--show-chat` option followed by the session name:
```shell
sgpt --show-chat number
# user: please remember my favorite number: 4
# assistant: I will remember that your favorite number is 4.
# user: what would be my favorite number + 4?
# assistant: Your favorite number is 4, so if we add 4 to it, the result would be 8.
```

### Request cache
Control cache using `--cache` (default) and `--no-cache` options. This caching applies for all `sgpt` requests to OpenAI API:
```shell
sgpt "what are the colors of a rainbow"
# -> The colors of a rainbow are red, orange, yellow, green, blue, indigo, and violet.
```
Next time, same exact query will get results from local cache instantly. Note that `sgpt "what are the colors of a rainbow" --temperature 0.5` will make a new request, since we didn't provide `--temperature` (same applies to `--top-probability`) on previous request.

This is just some examples of what we can do using ChatGPT model, I'm sure you will find it useful for your specific use cases.

### Runtime configuration file
You can setup some parameters in runtime configuration file `~/.config/shell_gpt/.sgptrc`:
```text
# API key, also it is possible to define OPENAI_API_KEY env.
OPENAI_API_KEY=your_api_key
# OpenAI host, useful if you would like to use proxy.
OPENAI_API_HOST=https://api.openai.com
# Max amount of cached message per chat session.
CHAT_CACHE_LENGTH=100
# Chat cache folder.
CHAT_CACHE_PATH=/tmp/shell_gpt/chat_cache
# Request cache length (amount).
CACHE_LENGTH=100
# Request cache folder.
CACHE_PATH=/tmp/shell_gpt/cache
# Request timeout in seconds.
REQUEST_TIMEOUT=60
# Default model to use.
DEFAULT_MODEL=gpt-3.5-turbo
```

### Full list of arguments
```shell
╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   prompt      [PROMPT]  The prompt to generate completions for.                                                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --temperature                       FLOAT RANGE [0.0<=x<=1.0]  Randomness of generated output. [default: 0.1]                                                      │
│ --top-probability                   FLOAT RANGE [0.1<=x<=1.0]  Limits highest probable tokens (words). [default: 1.0]                                              │
│ --model                             TEXT                       The model to use for completion. [default: gpt-3.5-turbo]                                           │
│ --editor             --no-editor                               Open $EDITOR to provide a prompt. [default: no-editor]                                              │
│ --cache              --no-cache                                Cache completion results. [default: cache]                                                          │
│ --help                                                         Show this message and exit.                                                                         │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Role Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --role                             TEXT  Specify what role a prompt should use. Defaults: shell, code, default. [default: default]                                 │
│ --save-role                        TEXT  Save a role for future use. [default: None]                                                                               │
│ --list-roles    --no-list-roles          List all saved roles. [default: no-list-roles]                                                                            │
│ --show-role                        TEXT  Show a saved role. [default: None]                                                                                        │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Chat Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --chat                           TEXT  Follow conversation with id (chat mode). [default: None]                                                                    │
│ --show-chat                      TEXT  Show all messages from provided chat id. [default: None]                                                                    │
│ --list-chat    --no-list-chat          List all existing chat ids. [default: no-list-chat]                                                                         │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Docker
Run the container using the `OPENAI_API_KEY` environment variable, and a docker volume to store cache:
```shell
docker run --rm \
           --env OPENAI_API_KEY="your OPENAI API key" \
           --volume gpt-cache:/tmp/shell_gpt \
       ghcr.io/ther1d/shell_gpt --chat rainbow "what are the colors of a rainbow"
```

Example of a conversation, using an alias and the `OPENAI_API_KEY` environment variable:
```shell
alias sgpt="docker run --rm --env OPENAI_API_KEY --volume gpt-cache:/tmp/shell_gpt ghcr.io/ther1d/shell_gpt"
export OPENAI_API_KEY="your OPENAI API key"
sgpt --chat rainbow "what are the colors of a rainbow"
sgpt --chat rainbow "inverse the list of your last answer"
sgpt --chat rainbow "translate your last answer in french"
```

You also can use the provided `Dockerfile` to build your own image:
```shell
docker build -t sgpt .
```
