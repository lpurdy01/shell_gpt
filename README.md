# Shell GPT
A command-line productivity tool powered by OpenAI's GPT-3.5 model.\
You can find original version from the fork information.

## Download and Install
You can get updated version on this site, and install locally.\
[Download](https://github.com/MartletH/shell_gpt/raw/main/dist/shell_gpt-0.8.8.2.tar.gz)

### Install
- Go to your local download folder
- pip install shell_gpt-x.tar.gz

## Updates
1. Simplify --chat to -c, --show-chat to -sc, --list-chat to -lc, DONE.
2. Automatic identify problem domain and become the expert the answer questions. DONE.
3. Concise Read Me. DONE.

### Possible future updates,
- Handle token limits nicely, defining nicely, already good with current update.

### Full list of arguments
```text
╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────────╮
│   prompt      [PROMPT]  The prompt to generate completions for.                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --model            [gpt-3.5-turbo|gpt-4|gpt-4-32k]  OpenAI GPT model to use. [default: gpt-3.5-turbo]      │
│ --temperature      FLOAT RANGE [0.0<=x<=1.0]        Randomness of generated output. [default: 0.1]         │
│ --top-probability  FLOAT RANGE [0.1<=x<=1.0]        Limits highest probable tokens (words). [default: 1.0] │
│ --editor                                            Open $EDITOR to provide a prompt. [default: no-editor] │
│ --cache                                             Cache completion results. [default: cache]             │
│ --help                                              Show this message and exit.                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Assistance Options ───────────────────────────────────────────────────────────────────────────────────────╮
│ --shell      -s                 Generate and execute shell commands.                                       │
│ --code       --no-code      Generate only code. [default: no-code]                                         │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Chat Options ─────────────────────────────────────────────────────────────────────────────────────────────╮
│ --chat       -c    TEXT  Follow conversation with id, use "temp" for quick session. [default: None]        │
│ --repl             TEXT  Start a REPL (Read–eval–print loop) session. [default: None]                      │
│ --show-chat  -sc   TEXT  Show all messages from provided chat id. [default: None]                          │
│ --list-chat  -lc        List all existing chat ids. [default: no-list-chat]                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Usage Examples
### Simple queries

```shell
sgpt "mass of sun"
# -> = 1.99 × 10^30 kg
```

### Summarization and analyzing
ShellGPT accepts prompt from both stdin and command line argument
```shell
git diff | sgpt "Generate git commit message, for my changes"
# -> Commit message: Implement Model enum and get_edited_prompt()
```

### Shell commands
```shell
sgpt --shell "make all files in current directory read only"
# -> chmod 444 *
# -> Execute shell command? [y/N]: y
# ...
```
```shell
sgpt -s "update my system"
# -> sudo softwareupdate -i -a
```
```shell
sgpt -s "update my system"
# -> sudo apt update && sudo apt upgrade -y
```

### Generating code
```shell
sgpt --code "solve classic fizz buzz problem using Python" > fizz_buzz.py
python fizz_buzz.py
# 1
# 2
# Fizz
# 4
# Buzz
# Fizz
# ...
```
```shell
cat fizz_buzz.py | python -m sgpt --code "Generate comments for each line of my code"
```
```python
# Loop through numbers 1 to 100
for i in range(1, 101):
    # Check if number is divisible by both 3 and 5
    if i % 3 == 0 and i % 5 == 0:
        # Print "FizzBuzz" if number is divisible by both 3 and 5
        print("FizzBuzz")
    # Check if number is divisible by 3
    elif i % 3 == 0:
        # Print "Fizz" if number is divisible by 3
        print("Fizz")
    # Check if number is divisible by 5
    elif i % 5 == 0:
        # Print "Buzz" if number is divisible by 5
        print("Buzz")
    # If number is not divisible by 3 or 5, print the number itself
    else:
        print(i)
```

### Chat

We can use `--code` or `--shell` options to initiate `--chat`, so you can keep refining the results:

```shell
sgpt --chat sh --shell "What are the files in this directory?"
# -> ls
sgpt --chat sh "Sort them by name"
# -> ls | sort
sgpt --chat sh "Concatenate them using FFMPEG"
# -> ffmpeg -i "concat:$(ls | sort | tr '\n' '|')" -codec copy output.mp4
sgpt --chat sh "Convert the resulting file into an MP3"
# -> ffmpeg -i output.mp4 -vn -acodec libmp3lame -ac 2 -ab 160k -ar 48000 final_output.mp3
```

### REPL
REPL (read–eval–print loop) mode. It reuse chat id.

```text
sgpt --repl temp
Entering REPL mode, press Ctrl+C to exit.
>>> What is REPL?
REPL stands for Read-Eval-Print Loop. It is a programming environment ...
>>> How can I use Python with REPL?
To use Python with REPL, you can simply open a terminal or command prompt ...
```
REPL mode can work with `--shell` and `--code` options, which makes it very handy for interactive shell commands and code generation:
```text
sgpt --repl temp --shell
Entering shell REPL mode, type [e] to execute commands or press Ctrl+C to exit.
>>> What is in current folder?
ls
>>> Show file sizes
ls -lh
>>> Sort them by file sizes
ls -lhS
>>> e (enter just e to execute commands)
...
```
Example of using REPL mode to generate code:
```text
sgpt --repl temp --code
Entering REPL mode, press Ctrl+C to exit.
>>> Using Python request localhost:80
import requests
response = requests.get('http://localhost:80')
print(response.text)
>>> Change port to 443
import requests
response = requests.get('https://localhost:443')
print(response.text)
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

This is just some examples of what we can do using OpenAI GPT models, I'm sure you will find it useful for your specific use cases.

### Config file
Config file location `~/.config/shell_gpt/.sgptrc`
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
# Default OpenAI model to use.
DEFAULT_MODEL=gpt-3.5-turbo
# Default color for OpenAI completions.
DEFAULT_COLOR=magenta
```
Possible options for `DEFAULT_COLOR`: black, red, green, yellow, blue, magenta, cyan, white, bright_black, bright_red, bright_green, bright_yellow, bright_blue, bright_magenta, bright_cyan, bright_white.

