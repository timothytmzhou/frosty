from message_structs import *
from sandbox import execute
from textwrap import dedent


def frosty_help(msg_info, message_slice):
    """
    > To get a full list of available commands, use the !list command.
    > To reference the Frosty user manual, call !help with no args.
    :param message_slice:
    :return:
    """
    if message_slice == "":
        with open("help.txt", "r") as f:
            return Call(CallType.SEND, msg_info.message, f.read())
    for key, value in commands.items():
        if message_slice == key.begin or message_slice == value.__name__:
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
    > Allows users to add simple echo commands.
    > These must follow the syntax of "trigger_phrase : msg_info".
    < optional params > {
        <!del> : makes Frosty delete the triggering message.
        <!auth> : placeholder for the name of the author of the triggering
                  message.
        <!channel> : placeholder for the name of the channel the triggering
                     message was sent in.
    }
    :param message_slice:
    :return:
    """
    words = message_slice.split()
    i = words.index(":")
    args = words[0:i]
    if len(args) > 1:
        args[1] = int(args[1])
    trigger = Trigger(*args)
    reply = " ".join(words[i + 1:]).strip()
    if "!del" in reply:
        reply = reply.replace("!del", "")
        call_type = CallType.REPLACE
    else:
        call_type = CallType.SEND

    def call_func(msg_info, message_slice):
        return Call(call_type, msg_info.message, reply)

    call_func.__name__ = args[0].replace("!", "")
    call_func.__doc__ = "!add created echo-like command returning {0}".format(reply)
    commands[trigger] = call_func
    return Call(
        CallType.SEND,
        msg_info.message,
        "New command: on {0} I'll say `{1}`".format(str(trigger), reply),
        ignore_keywords=True
    )


def remove_command(msg_info, message_slice):
    """
    > Removes commands from the command dictionary.
    > Remove functionality for built-ins is disabled.
    :param message_slice:
    :return:
    """
    for trigger in commands:
        if trigger.begin == message_slice and trigger.protected == False:
            return Call(
                CallType.SEND,
                msg_info.message,
                "{0} with msg_info `{1}` has been removed".format(
                    str(trigger),
                    commands.pop(trigger).__name__)
            )


def ban(msg_info, message_slice):
    """
    > Changes the ban status of a user:
    > If already banned, gives them user status, otherwise if they are not
      an owner, ban them.
    :param message_slice:
    :return:
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
    > Changes admin status of a user:
    > If already an admin, gives them user status, otherwise makes them an
      admin-level user.
    :param message_slice:
    :return:
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
    > Translates "a" to 1, evals arithmetic expressions <= 128 in snowmen
    :param message_slice:
    :return:
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
            return run_code(msg_info, f"print(({message_slice}) * ☃)")


def frosty_say(msg_info, message_slice):
    """
    > Echo command, replaces message invoking <!say>
    :param message_slice:
    :return:
    """
    return Call(
        CallType.REPLACE,
        msg_info.message,
        message_slice.replace("@", "")
    )


def run_code(msg_info, message_slice):
    # Removes leading/trailing pairs of ` to allow for code formatting
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
    return Call(
        CallType.SEND,
        msg_info.message,
        f"```python\n{result['stdout'].decode()}```"
    )


def command_list(msg_info, message_slice):
    """
    Generates a list of all available commands.
    :param message_slice:
    :return:
    """
    message = "**Commands:**\n"
    message += "\n".join(
        "{0} :: `{1}`\n".format(str(trigger), func.__name__)
        for trigger, func in commands.items()
    )
    return Call(CallType.SEND, msg_info.message, f"```md{message}```")

commands = {
    Trigger("!run", protected=True): run_code,
    Trigger("give me", end="snowman", protected=True): snowman,
    Trigger("give me", end="snowmen", protected=True): snowman,
    Trigger("!ban", access_level=1, protected=True): ban,
    Trigger("!admin", access_level=1, protected=True): give_admin,
    Trigger("!say", protected=True): frosty_say,
    Trigger("!add", access_level=1, protected=True): new_command,
    Trigger("!remove", access_level=1, protected=True): remove_command,
    Trigger("!list", access_level=-1, protected=True): command_list,
    Trigger("!help", access_level=-1, protected=True): frosty_help
}
