import epicboxie
import json
from src.commands import *


class Language:
    def __init__(self, name, file, command):
        self.name = name
        self.file = file
        self.command = command

    def execute(self, code, cputime=60, memory=512):
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
                epicboxie.Profile(language_name, "frosty/{}".format(language_name))
                for language_name in language_data
            ]
        )
    return languages


LANGUAGES = parse_language_data("languages/languages.json")

users_running_code = set()

@trigger("^/run\s```(.+?)[\s\n]([\s\S]*)```")
async def run_code(msg, lang, code):
    print(code)
    if msg.author in users_running_code:
        language = LANGUAGES[lang]
        result = await client.loop.run_in_executor(None, language.execute, code)
        if result["timeout"]:
            out = "TimeoutError: computation timed out\n"
        elif result["oom_killed"]:
            out = "MemoryError: computation exceeded memory limit\n"
        else:
            out = (result["stdout"] + result["stderr"]).decode().replace("`", "​`")
        out = "```py\n{0}\nExecution time: {1}s```".format(out.strip(), result["duration"])
        users_running_code.remove(msg.author)
        await msg.channel.send(out)
