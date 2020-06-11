import re
from src.message_structs import Call, Trigger
from src.extensions.sandbox import execute
from src.util import format_table
from src.extensions import query
from textwrap import dedent, indent


def frosty_help(msg_info, *args):
    """
    > To get a full list of available commands, use the /list command.
    > To reference the Frosty user manual, call /help with no args.
    """
    if len(args) == 0:
        with open("about.txt", "r") as f:
            return Call(task=Call.send, args=(msg_info.channel, f.read()))
    else:
        command = args[0]
        for key, value in commands.items():
            if command == key.name:
                if value.__doc__ is not None:
                    return Call(
                        task=Call.send,
                        args=(
                            msg_info.channel,
                            "```md\n{0}```".format(dedent(value.__doc__))
                        )
                    )
                else:
                    return Call(
                        task=Call.send,
                        args=(
                            msg_info.message,
                            "{0} does not define a docstring (yell at stackdynamic to add one)!"
                        )
                    )


def snowman(msg_info, *args):
    """
    > Giver of snowmen since 2018.
    > Translates "a" to 1, evals arithmetic expressions <= 128 in snowmen.
    """
    snowmen_request = args[0]
    if snowmen_request == "a":
        return Call(task=Call.send, args=(msg_info.channel, "☃"))
    else:
        result = execute("print(({}) * '☃')".format(snowmen_request))
        return Call(
            task=Call.send,
            args=(msg_info.channel, result["stdout"].decode())
        )


def frosty_say(msg_info, *args):
    """
    > Echo command, deletes message invoking /say.
    """
    return Call(task=Call.replace, args=(msg_info, args[0]))


def run_code(msg_info, *args):
    """
    > Runs arbitrary python code in docker sandbox.
    > 60 second time limit, 1 mb memory limit.
    """
    # Removes leading/trailing pairs of ` to allow for code formatting
    code_pattern = "```{0}```|`{0}`".format("(?:py | python | gyp)?(.*)")
    code = re.match(code_pattern, args[0].strip(), re.DOTALL).group(1)
    result = execute(code)
    if result["timeout"]:
        msg = "TimeoutError: computation timed out\n"
    elif result["oom_killed"]:
        msg = "MemoryError: computation exceeded memory limit\n"
    else:
        msg = (result["stdout"] + result["stderr"]).decode().replace("`", "​`")
    msg = "```py\n{0}Execution time: {1}s```".format(msg, result["duration"])
    return Call(task=Call.send, args=(msg_info.channel, "```py\n{}```".format(msg)))


def command_list(msg_info, *args):
    """
    > Generates a list of all available commands.
    """
    headers = ("pattern", "command", "description")
    data = tuple(
        (
            trigger.pattern,
            trigger.name,
            func.__doc__.strip().partition("\n")[0].lower().replace("> ", "")
        )
        for trigger, func in commands.items()
    )
    message = format_table(data, headers)
    return Call(task=Call.send, args=(msg_info.channel, message))


commands = {
    Trigger(r"^/help (.*)|^/help"): frosty_help,
    Trigger(r"^/run[\s\n](.*)"): run_code,
    Trigger(r"^give me (.*) (snowmen|snowman)", name="/snowman"): snowman,
    Trigger(r"^/say (.*)"): frosty_say,
    Trigger(r"^/list"): command_list,
    Trigger(r"^/ask (.*)"): query.ask
}
