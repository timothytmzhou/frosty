To add a language, add an entry to `languages.json`:
```
language_name: the name of the language you are adding {
    prefixes: list of highlight.js prefixes see github.com/highlightjs/highlight.js/blob/master/SUPPORTED_LANGUAGES.md,
    file: the name of the file source is sent to,
    command: command to run the code,
}
```
For example:
```
  "python:3.8": {
    "prefixes": [
      "py",
      "python",
      "gyp"
    ],
    "file": "main.py",
    "command": "python main.py"
  }
```
Then, add a docker file to `dockerfiles/` which can run the command you entered. The name of the file must be equal to language_name (for example: `python:3.8.dockerfile`). If you want to add packages, just write the corresponding commands in the dockerfile. The `packages/` directory is reserved for package lists. 