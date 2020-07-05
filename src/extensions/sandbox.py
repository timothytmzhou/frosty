import epicboxie
import re
import json
from src.message_structs import Call


class Language:
    def __init__(self, name, file, command):
        self.name = name
        self.file = file
        self.command = command

    def execute(self, code, cputime=60, memory=64):
        files = [{'name': self.file, 'content': code.strip().encode()}]
        limits = {'cputime': cputime, 'memory': memory}
        ports = {443: 443, 80: 80}
        return epicboxie.run(self.name, self.command, files=files, limits=limits, ports=ports)


def parse_language_data(path):
    languages = {}
    with open(path) as f:
        language_data = json.load(f)
        for language_name, params in language_data.items():
            prefixes, file, command = params["prefixes"], params["file"], params["command"]
            language = Language(language_name, file, command)
            languages.update({prefix: language for prefix in prefixes})
        epicboxie.configure(
            profiles=[
                epicboxie.Profile(language_name, "ohm/{}".format(language_name))
                for language_name in language_data
            ]
        )
    return languages


LANGUAGES = parse_language_data("languages/languages.json")


def run_code(msg_info, *args):
    """
    > Runs arbitrary python code in docker sandbox
    > 60 second time limit, 1 mb memory limit
    > Supports code formatting
    > /run code
    """
    # Removes leading/trailing pairs of ` to allow for code formatting
    code_pattern = r"```(.+?)[\s\n](.+?)```"
    extension, code = re.match(code_pattern, args[0].strip(), re.DOTALL).groups()
    language = LANGUAGES[extension]
    result = language.execute(code)
    if result["timeout"]:
        msg = "TimeoutError: computation timed out\n"
    elif result["oom_killed"]:
        msg = "MemoryError: computation exceeded memory limit\n"
    else:
        msg = (result["stdout"] + result["stderr"]).decode().replace("`", "​`")
    msg = "```py\n{0}\nExecution time: {1}s```".format(msg.strip(), result["duration"])
    return Call(task=Call.send, args=(msg_info.channel, msg))
