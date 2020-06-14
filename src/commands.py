import re
from src.message_structs import Call, Trigger
from src.extensions import sandbox
from src.extensions import channel_management
from src.extensions import query
from src.util import format_table
from textwrap import dedent


def frosty_help(msg_info, *args):
    """
    > To reference the Frosty user manual, call /help with no args.
    > To get a full list of available commands, use the /list command.
    > To see details of a specific command, call /help command_name.
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
    > give me quantity snowman
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
    > /say message
    """
    return Call(task=Call.replace, args=(msg_info, args[0]))


def command_list(msg_info, *args):
    """
    > Generates a list of all available commands.
    > /list
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
    Trigger(r"^/help (.+)|^/help"): frosty_help,
    Trigger(r"^/run[\s\n](.+)", name="/run"): sandbox.run_code,
    Trigger(r"^give me (.+) (snowmen|snowman)", name="/snowman"): snowman,
    Trigger(r"^/say (.+)"): frosty_say,
    Trigger(r"^/list"): command_list,
    Trigger(r"^/ask (.+)"): query.ask,
    Trigger(r"^/rename (.+)"): channel_management.rename_channel,
    Trigger(r"^/id (.+)"): channel_management.set_role_id,
    Trigger(r"^/make (\S+)(?: (.+))?"): channel_management.make_channel,
    Trigger(r"^/add (.+)"): channel_management.add_members,
    Trigger(r"^/kick (.+)"): channel_management.remove_members

}
