from message_structs import *
from sandbox import execute
from textwrap import dedent, indent
from util import format_table


def frosty_help(msg_info, *args):
    """
    > To get a full list of available commands, use the !list command.
    > To reference the Frosty user manual, call !help with no args.
    """
    if len(args) == 0:
        with open("src/help.txt", "r") as f:
            return Call(CallType.SEND, msg_info.message, f.read())
    else:
        command = args[0]
        for key, value in commands.items():
            if command == key.name:
                if value.__doc__ is not None:
                    return Call(CallType.SEND, msg_info.message,
                                "```md\n{0}```".format(dedent(value.__doc__)),
                                ignore_keywords=True)
                else:
                    return Call(CallType.SEND, msg_info.message,
                                "{0} does not define a docstring (yell at "
                                "Timothy to add one)!")


def new_command(msg_info, *args):
    """
    > Allows users to add commands which run python code.
    > These must follow the syntax of "regex pattern : code".
    > Note that an implicit ^ anchor is put in front of the pattern, so e.g !test becomes ^!test
    """
    name, code = args[0], args[1]
    trigger = Trigger("^{}".format(name), protected=False)
    
    def call_func(msg_info, *args):
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


def remove_command(msg_info, *args):
    """
    > Removes commands from the command dictionary.
    > Remove functionality for built-ins is disabled.
    """
    command = args[0]
    for trigger in commands:
        if trigger.name == command and trigger.protected == False:
            commands.pop(trigger)
            return Call(
                CallType.SEND,
                msg_info.message,
                "{0} has been removed".format(trigger.name)
            )


def ban(msg_info, *args):
    """
    > Changes the ban status of a user.
    > If already banned, gives them user status, otherwise if they are not
      an owner, ban them.
    """
    id = args[0]
    recipient_level = UserData.get_level(id)
    if recipient_level == -1:
        UserData.levels[UserTypes.BANNED].remove(id)
        UserData.levels[UserTypes.USER].append(id)
        return Call(CallType.SEND, msg_info.message,
                    "un-banned {0}".format(id))
    elif recipient_level == 2:
        return Call(CallType.SEND, msg_info.message, "owners can't be banned")
    else:
        UserData.levels[UserTypes(recipient_level)].remove(id)
        UserData.levels[UserTypes.BANNED].append(id)
        return Call(CallType.SEND, msg_info.message,
                    "{0} has been banned".format(id))


def give_admin(msg_info, *args):
    """
    > Changes admin status of a user.
    > If already an admin, gives them user status, otherwise makes them an
      admin-level user.
    """
    recipient_level = UserData.get_level(id)
    if recipient_level == 1:
        UserData.levels[UserTypes.ADMIN].remove(id)
        UserData.levels[UserTypes.USER].append(id)
        return Call(
            CallType.SEND,
            msg_info.message,
            "{0}'s admin status has been revoked".format(id)
        )
    elif recipient_level == 2:
        return Call(CallType.SEND, msg_info.message,
                    "owners can't be given admin status")
    else:
        UserData.levels[UserTypes(recipient_level)].remove(id)
        UserData.levels[UserTypes.ADMIN].append(id)
        return Call(CallType.SEND, msg_info.message,
                    "{0} is now an admin".format(id))


def snowman(msg_info, *args):
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
        snowmen_request = args[0]
        if snowmen_request == "a":
            return Call(CallType.SEND, msg_info.message, "☃")
        else:
            result = execute("print(({}) * '☃')".format(snowmen_request))
            return Call(
                CallType.SEND,
                msg_info.message,
                result["stdout"].decode()
            )


def frosty_say(msg_info, *args):
    """
    > Echo command, deletes message invoking !say.
    """
    return Call(
        CallType.REPLACE,
        msg_info.message,
        args[0]
    )


def run_code(msg_info, *args):
    """
    > Runs arbitrary python code in docker sandbox.
    > 60 second time limit, 1 mb memory limit.
    """
    # Removes leading/trailing pairs of ` to allow for code formatting
    code = args[0]
    i = 0
    while True:
        if i < len(code) // 2 and code[i] == code[-i - 1] == "`":
            i += 1
        else:
            break
    code = code[i: len(code) - i]
    for prefix in ("python", "py"):
        if code.startswith(prefix):
            code = code[len(prefix):]
    result = execute(code)
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


def command_list(msg_info, *args):
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
    Trigger(r"^!help (.*)|^!help", access_level=-1): frosty_help,
    Trigger(r"^!run[\s\n](.*)"): run_code,
    Trigger(r"^give me (.*) (snowmen|snowman)", name="!snowman"): snowman,
    Trigger(r"^!ban (.*)", access_level=1): ban,
    Trigger(r"^!admin (.*)", access_level=1): give_admin,
    Trigger(r"^!say (.*)"): frosty_say,
    Trigger(r"^!add (.*):(.*)", access_level=1): new_command,
    Trigger(r"^!remove (.*)", access_level=1): remove_command,
    Trigger(r"^!list", access_level=-1): command_list,
}
