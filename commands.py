from message_structs import *
from sandbox import execute
from textwrap import dedent, indent
from util import format_table


def frosty_help(msg_info, message_slice):
    """
    > To get a full list of available commands, use the !list command.
    > To reference the Frosty user manual, call !help with no args.
    """
    if message_slice == "":
        with open("help.txt", "r") as f:
            return Call(CallType.SEND, msg_info.message, f.read())
    for key, value in commands.items():
        if message_slice == key.name:
            if value.__doc__ is not None:
                return Call(CallType.SEND, msg_info.message,
                            "```md\n{0}```".format(dedent(value.__doc__)),
                            ignore_keywords=True)
            else:
                return Call(CallType.SEND, msg_info.message,
                            "{0} does not define a docstring (yell at "
                            "Timothy to add one)!")


def new_command(msg_info, message_slice):
    """
    > Allows users to add commands which run python code.
    > These must follow the syntax of "trigger_phrase : code".
    """
    words = message_slice.split(":", 1)
    name = words[0].strip()
    trigger = Trigger(name, protected=False)
    code = words[1]
    
    def call_func(msg_info, message_slice):
        return run_code(msg_info, code)

    call_func.__name__ = name.replace("!", "")
    call_func.__doc__ = "> !add created command running code:\n{}".format(
        indent(code, " " * 4)
    )
    commands[trigger] = call_func
    return Call(
        CallType.SEND,
        msg_info.message,
        "```asciidoc\nadded command {}```".format(trigger.name)
    )


def remove_command(msg_info, message_slice):
    """
    > Removes commands from the command dictionary.
    > Remove functionality for built-ins is disabled.
    """
    for trigger in commands:
        if trigger.name == message_slice and trigger.protected == False:
            commands.pop(trigger)
            return Call(
                CallType.SEND,
                msg_info.message,
                "{0} has been removed".format(trigger.name)
            )


def ban(msg_info, message_slice):
    """
    > Changes the ban status of a user.
    > If already banned, gives them user status, otherwise if they are not
      an owner, ban them.
    """
    recipient_level = UserData.get_level(*message_slice.split("#"))
    if recipient_level == -1:
        UserData.levels[UserTypes.BANNED].remove(message_slice)
        UserData.levels[UserTypes.USER].append(message_slice)
        return Call(CallType.SEND, msg_info.message,
                    "un-banned {0}".format(message_slice))
    elif recipient_level == 2:
        return Call(CallType.SEND, msg_info.message, "owners can't be banned")
    else:
        UserData.levels[UserTypes(recipient_level)].remove(message_slice)
        UserData.levels[UserTypes.BANNED].append(message_slice)
        return Call(CallType.SEND, msg_info.message,
                    "{0} has been banned".format(message_slice))


def give_admin(msg_info, message_slice):
    """
    > Changes admin status of a user.
    > If already an admin, gives them user status, otherwise makes them an
      admin-level user.
    """
    recipient_level = UserData.get_level(*message_slice.split("#"))
    if recipient_level == 1:
        UserData.levels[UserTypes.ADMIN].remove(message_slice)
        UserData.levels[UserTypes.USER].append(message_slice)
        return Call(
            CallType.SEND,
            msg_info.message,
            "{0}'s admin status has been revoked".format(message_slice)
        )
    elif recipient_level == 2:
        return Call(CallType.SEND, msg_info.message,
                    "owners can't be given admin status")
    else:
        UserData.levels[UserTypes(recipient_level)].remove(message_slice)
        UserData.levels[UserTypes.ADMIN].append(message_slice)
        return Call(CallType.SEND, msg_info.message,
                    "{0} is now an admin".format(message_slice))


def snowman(msg_info, message_slice):
    """
    > Giver of snowmen since 2018.
    > Translates "a" to 1, evals arithmetic expressions <= 128 in snowmen.
    """
    if msg_info.user_level == -1:
        return Call(
            CallType.SEND,
            msg_info.message,
            "{0} doesn't deserve ANY snowmen".format(msg_info.message.author.name)
        )
    else:
        if message_slice == "a":
            return Call(CallType.SEND, msg_info.message, "☃")
        else:
            result = execute("print(({}) * '☃')".format(message_slice))
            return Call(
                CallType.SEND,
                msg_info.message,
                result["stdout"].decode()
            )


def frosty_say(msg_info, message_slice):
    """
    > Echo command, replaces message invoking <!say>.
    """
    return Call(
        CallType.REPLACE,
        msg_info.message,
        message_slice
    )


def run_code(msg_info, message_slice):
    """
    > Runs arbitrary python code in docker sandbox.
    > 60 second time limit, 1 mb memory limit.
    """
    # Removes leading/trailing pairs of ` to allow for code formatting
    message_slice = message_slice.strip()
    i = 0
    while True:
        if i < len(message_slice) // 2 and message_slice[i] == message_slice[-i - 1] == "`":
            i += 1
        else:
            break
    message_slice = message_slice[i: len(message_slice) - i]
    if message_slice.startswith("python"):
        message_slice = message_slice[6:]
    result = execute(message_slice)
    msg = result["stdout"].decode()
    if result["timeout"]:
        msg += "TimeoutError: computation timed out"
    if result["oom_killed"]:
        msg += "MemoryError: computation exceeded memory limit"
    if result["stderr"] not in (b"", b"Killed\n"):
        msg += result["stderr"].decode()
    msg = msg.replace("`", "​`")
    if msg != "":
        return Call(
            CallType.SEND,
            msg_info.message,
            "```python\n{}```".format(msg)
        )


def command_list(msg_info, message_slice):
    """
    > Generates a list of all available commands.
    """
    headers = ("pattern", "command", "level", "description")
    data = tuple(
        (
            trigger.pattern,
            trigger.name,
            "< {}+ >".format(trigger.level),
            func.__doc__.strip().partition("\n")[0].lower().replace("> ", "")
        )
        for trigger, func in commands.items()
    )
    message = format_table(data, headers)
    return Call(CallType.SEND, msg_info.message, message)


commands = {
    Trigger(r"!help (.*)|!help", access_level=-1): frosty_help,
    Trigger(r"!run[\s\n](.*)"): run_code,
    Trigger(r"give me (.*) (snowmen|snowman)", name="!snowman"): snowman,
    Trigger(r"!ban (.*)", access_level=1): ban,
    Trigger(r"!admin (.*)", access_level=1): give_admin,
    Trigger(r"!say (.*)"): frosty_say,
    Trigger(r"!add (.*)", access_level=1): new_command,
    Trigger(r"!remove (.*)", access_level=1): remove_command,
    Trigger(r"!list", access_level=-1): command_list,
}
