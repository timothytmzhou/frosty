from src.message_structs import Call, Trigger
from src.extensions import sandbox
from src.util import format_table
from textwrap import dedent


def frosty_help(msg_info, command=None):
    """
    > To reference the Frosty user manual, call /help with no args
    > To get a full list of available commands, use the /list command
    > To see details of a specific command, call /help command_name
    """
    if command is None:
        with open("about.txt", "r") as f:
            return Call(task=Call.send, args=(msg_info.channel, f.read()))
    else:
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


def snowman(msg_info, snowmen_request=None):
    """
    > Giver of snowmen since 2018
    > Translates "a" to 1, evals arithmetic expressions <= 128 in snowmen
    > give me quantity snowman
    """
    if snowmen_request is None:
        return Call(task=Call.send, args=(msg_info.channel, "☃"))
    else:
        result = sandbox.LANGUAGES["python"].execute("print(({}) * '☃')".format(snowmen_request))
        out = result["stdout"].decode()
        if not all(c == '☃' for c in out):
            out = "```py\n{0}```".format(out)
        return Call(
            task=Call.send,
            args=(msg_info.channel, out)
        )


def command_list(msg_info):
    """
    > Generates a list of all available commands
    > /list
    """
    headers = ("pattern", "command", "description")
    data = tuple(
        (
            trigger.pattern.replace("`", "​`"),
            trigger.name,
            func.__doc__.strip().partition("\n")[0].lower().replace("> ", "")
        )
        for trigger, func in commands.items()
    )
    message = format_table(data, headers)
    return Call(task=Call.send, args=(msg_info.channel, message))


# \u is space-separated list of users/tags/roles
commands = {
    Trigger(r"^/help (.+)|^/help"): frosty_help,
    Trigger(r"^/run\s```(.+?)[\s\n]([\s\S]*)```", name="/run"): sandbox.run_code,
    Trigger(r"^/list"): command_list,
    Trigger(r"^(?:give me a snowman|give me (.+) snowmen)", name="/snowman"): snowman,
}
