import epicbox
import re
from src.message_structs import Call

epicbox.configure(
    profiles=[
        epicbox.Profile('python', 'python:3.8-alpine')
    ]
)


def execute(code):
    files = [{'name': 'main.py', 'content': code.strip().encode()}]
    limits = {'cputime': 60, 'memory': 64}
    result = epicbox.run('python', 'python3 main.py', files=files, limits=limits)
    return result


def run_code(msg_info, *args):
    """
    > Runs arbitrary python code in docker sandbox.
    > 60 second time limit, 1 mb memory limit.
    > Supports code formatting.
    > /run code
    """
    # Removes leading/trailing pairs of ` to allow for code formatting
    code_pattern = r"```(?:py | python | gyp)?(.+)```|`(.+)`|(.+)"
    groups = re.match(code_pattern, args[0].strip(), re.DOTALL).groups()
    code = next(group for group in groups if group is not None)
    result = execute(code)
    if result["timeout"]:
        msg = "TimeoutError: computation timed out\n"
    elif result["oom_killed"]:
        msg = "MemoryError: computation exceeded memory limit\n"
    else:
        msg = (result["stdout"] + result["stderr"]).decode().replace("`", "​`")
    msg = "```py\n{0}Execution time: {1}s```".format(msg, result["duration"])
    return Call(task=Call.send, args=(msg_info.channel, msg))
