import epicbox
import json
from src.message_structs import Call


class Language:
    def __init__(self, name, file, command):
        self.name = name
        self.file = file
        self.command = "{{{0}}} 2>&1".format(command)

    def execute(self, code, cputime=60, memory=512):
        files = [{'name': self.file, 'content': code.strip().encode()}]
        limits = {'cputime': cputime, 'memory': memory}
        return epicbox.run(self.name, self.command + " 2>&1", files=files, limits=limits)


def parse_language_data(path):
    languages = {}
    with open(path) as f:
        language_data = json.load(f)
        for language_name, params in language_data.items():
            prefixes, file, command = params["prefixes"], params["file"], params["command"]
            language = Language(language_name, file, command)
            languages.update({prefix: language for prefix in prefixes})
        epicbox.configure(
            profiles=[
                epicbox.Profile(language_name, "frosty/{}".format(language_name))
                for language_name in language_data
            ]
        )
    return languages


LANGUAGES = parse_language_data("languages/languages.json")


def run_code(msg_info, extension, code):
    """
    > Runs arbitrary python code in docker sandbox
    > 60 second time limit, 1 mb memory limit
    > Supports code formatting
    > /run code
    """
    # Removes leading/trailing pairs of ` to allow for code formatting
    language = LANGUAGES[extension]
    result = language.execute(code)
    if result["timeout"]:
        msg = "TimeoutError: computation timed out\n"
    elif result["oom_killed"]:
        msg = "MemoryError: computation exceeded memory limit\n"
    else:
        msg = (result["stdout"]).decode().replace("`", "`​")
    msg = "{0}\nExecution time: {1}s".format(msg.strip(), result["duration"])
    return Call(task=Call.send, args=(msg_info.channel, msg, "bash"))
