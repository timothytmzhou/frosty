"""
ihscy's over-engineered Discord bot
"""
import sys
from textwrap import dedent
import discord
from bsd import SnowAlertSystem
from message_structs import CallType, UserData, UserTypes
from sheets import get_sheet, format_table

client = discord.Client()
SHEET = get_sheet()


class Call:
    def __init__(self, call_type, message, response=None, ignore_keywords = False):
        self.call_type = call_type
        self.response = response
        self.message = message
        self.ignore_keywords = ignore_keywords


    async def invoke(self):
        # Invokes an action depending on call_type:
        # CallType.DELETE -- deletes message.
        # CallType.SEND -- sends response to the same channel as message.
        # CallType.REPLACE -- performs both of the actions above.
        if self.call_type == CallType.DELETE or self.call_type == CallType.REPLACE:
            await self.delete()
        if self.call_type == CallType.SEND or self.call_type == CallType.REPLACE:
            if self.response is not None:
                await self.send()


    async def send(self):
        if self.response is not None:
            if not self.ignore_keywords:
                keywords =  {
                    "!auth" : self.message.author.name, 
                    "!channel" : self.message.channel.name
                }
                for key in keywords:
                    self.response = self.replace_keyords(key, keywords[key])
            await self.message.channel.send(self.response)


    async def delete(self):
        await self.message.delete()


    def replace_keyords(self, key, var):
        return self.response.replace(key, var)


class Trigger:
    def __init__(self, begin, access_level=0, end=None, protected=False):
        # Sets beggining and ending trigger phrases, .split()ed versions of them.
        self.begin = begin.lower()   
        self.b_words = self.begin.split()

        self.end = end
        if self.end is not None:
            self.end = self.end.lower()
            self.e_words = self.end.split()

        self.access_level = access_level
        self.protected = protected


    def __str__(self):
        if self.end is not None:
            string = "`{0}...{1}`".format(self.begin, self.end)
        else:
            string = "`{0}`".format(self.begin)
        string += " with user status `{0}` or higher".format(
            UserTypes(self.access_level).name.lower()
        )
        return string


    def begins(self, lwords):
        # Given a list of lowercase words, checks if it begins with this trigger's start phrase.
        return lwords[:len(self.b_words)] == self.b_words


    def ends(self, lwords):
        # Given a list of lowercase words, checks if it begins with this trigger's end phrase.
        return self.end is None or lwords[-len(self.e_words):] == self.e_words


    def begin_index(self, lwords):
        # Gets index of last element of this trigger's start phrase (guranteed to be in lwords).
        return lwords.index(self.b_words[0]) + len(self.b_words)


    def end_index(self, lwords):
        # Gets index of first element of this trigger's end phrase (guranteed to be in lwords).
        if self.end is None:
            return len(lwords)
        else:
            return lwords.index(self.e_words[0])


    def slice(self, words, lwords):
        # Gets the content of the message between the start and end triggers (guranteed to be in lwords).
        # Return value is a space-seperated string.
        # E.g "_START_ my message in between _END_" returns "my message in between"
        sliced = " ".join(words[
            self.begin_index(lwords):
            self.end_index(lwords)
        ])
        # Removes leading/trailing pairs of ` to allow for code formatting
        i = 0
        while True:
            if i < len(sliced) // 2 and sliced[i] == sliced[-i - 1] == '`':
                i += 1
            else:
                break
        return sliced[i:len(sliced) - i]


class Response:

    safe_characters = "0123456789*/+-%^()"

    def __init__(self, message):
        self.message = message
        self.words = self.message.content.split()
        self.lwords = [w.lower() for w in self.words]
        self.author = self.message.author.name
        user_level = UserData.get_level(self.author)

        # Iterates through the commands dict of the form {Trigger: func -> Call}:
        for trigger, func in Response.commands.copy().items():
            #  Uses the begins() and ends() helper methods to check if activation conditions for any trigger are met.
            if trigger.begins(self.lwords) and trigger.ends(self.lwords):
                if user_level >= trigger.access_level:
                    message_slice = trigger.slice(self.words, self.lwords)
                    # If so, passes the slice into the corresponding function, and adds the returned Call object's invoke() method to the client loop.
                    task = func(self, message_slice)
                    if isinstance(task, Call):
                        client.loop.create_task(task.invoke())


    def help(self, message_slice):
        """
        > To get a full list of available commands, use the !list command.
        > To reference the Frosty user manual, call !help with no args.
        :param message_slice:
        :return:
        """
        if message_slice == "":
            with open("help.txt", "r") as f:
                return Call(CallType.SEND, self.message, f.read())
        for key, value in Response.commands.items():
            if message_slice == key.begin or message_slice == value.__name__:
                if value.__doc__ is not None:
                    return Call(CallType.SEND, self.message, "```md\n{0}```".format(dedent(value.__doc__)), ignore_keywords=True)
                else:
                    return Call(CallType.SEND, self.message, "{0} does not define a docstring (yell at Timothy to add one)!")


    def new_command(self, message_slice):
        """
        > Allows users to add simple echo commands.
        > These must follow the syntax of "trigger_phrase : response".
        < optional params > {
            <!del> : makes Frosty delete the triggering message.
            <!auth> : placeholder for the name of the author of the triggering message.
            <!channel> : placeholder for the name of the channel the triggering message was sent in.
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

        def call_func(response, message_slice):
            return Call(call_type, response.message, reply)

        call_func.__name__ = args[0].replace("!", "")
        call_func.__doc__ = "!add created echo-like command returning {0}".format(reply)
        Response.commands[trigger] = call_func
        return Call(
            CallType.SEND,
            self.message,
            "New command: on {0} I'll say `{1}`".format(str(trigger), reply),
            ignore_keywords = True

        )


    def remove_command(self, message_slice):
        """
        > Removes commands from the command dictionary.
        > Remove functionality for built-ins is disabled.
        :param message_slice:
        :return:
        """
        for trigger in Response.commands:
            if trigger.begin == message_slice and trigger.protected == False:
                return Call(
                    CallType.SEND,
                    self.message,
                    "{0} with response `{1}` has been removed".format(
                        str(trigger),
                        Response.commands.pop(trigger).__name__)
                )


    def get_finances(self, message_slice):
        """
        :param message_slice:
        :return:
        """
        values = SHEET.get_all_values()
        data = [[x for x in row[:4] if x != ""] for row in values[3:]]
        data = [i for i in data if i != []]
        return Call(CallType.SEND, self.message, format_table(data))


    def ban(self, message_slice):
        """
        > Changes the ban status of a user:
        > If already banned, gives them user status, otherwise if they are not an owner, ban them.
        :param message_slice:
        :return:
        """
        recipient_level = UserData.get_level(message_slice)
        if recipient_level == -1:
            UserData.levels[UserTypes.BANNED].remove(message_slice)
            UserData.levels[UserTypes.USER].append(message_slice)
            return Call(CallType.SEND, self.message, "un-banned {0}".format(message_slice))
        elif recipient_level == 2:
            return Call(CallType.SEND, self.message, "owners can't be banned")
        else:
            UserData.levels[UserTypes(recipient_level)].remove(message_slice)
            UserData.levels[UserTypes.BANNED].append(message_slice)
            return Call(CallType.SEND, self.message, "{0} has been banned".format(message_slice))


    def give_admin(self, message_slice):
        """
        > Changes admin status of a user:
        > If already an admin, gives them user status, otherwise makes them an admin-level user.
        :param message_slice:
        :return:
        """
        recipient_level = UserData.get_level(message_slice)
        if recipient_level == 1:
            UserData.levels[UserTypes.ADMIN].remove(message_slice)
            UserData.levels[UserTypes.USER].append(message_slice)
            return Call(
                CallType.SEND,
                self.message,
                "{0}'s admin status has been revoked".format(message_slice)
            )
        elif recipient_level == 2:
            return Call(CallType.SEND, self.message, "owners can't be given admin status")
        else:
            UserData.levels[UserTypes(recipient_level)].remove(message_slice)
            UserData.levels[UserTypes.ADMIN].append(message_slice)
            return Call(CallType.SEND, self.message, "{0} is now an admin".format(message_slice))


    def snowman(self, message_slice):
        """
        > Giver of snowmen since 2018.
        > Translates "a" to 1, evals arithmetic expressions <= 128 in snowmen (limited to safe characters).
        :param message_slice:
        :return:
        """
        if UserData.get_level(self.author) == -1:
            return Call(
                CallType.SEND, 
                self.message, 
                "{0} doesn't deserve ANY snowmen".format(self.message.author.name)
            )
        else:
            if message_slice == "a":
                snowman_count = 1
            else:
                if all(char in Response.safe_characters for char in message_slice):
                    snowman_count = int(eval(message_slice))
                else:
                    snowman_count = 0
            if snowman_count > 0:
                return Call(CallType.SEND, self.message, "☃" * min(snowman_count, 128))


    def frosty_say(self, message_slice):
        """
        > Echo command, replaces message invoking <!say>
        :param message_slice:
        :return:
        """
        if UserData.get_level(self.author) < 1 and "@everyone" in message_slice:
            return Call(CallType.REPLACE, self.message, "I can't ping everyone unless you have admin status")
        return Call(CallType.REPLACE, self.message, message_slice)


    def command_list(self, message_slice):
        """
        Generates a list of all available commands.
        :param message_slice:
        :return:
        """
        message = "**Commands:**\n" 
        message += "\n".join(
            "{0} will run `{1}`\n".format(str(trigger), func.__name__)
            for trigger, func in Response.commands.items()
        )
        return Call(CallType.SEND, self.message, message)


    commands = {
        Trigger("give me", end="snowman", protected=True): snowman,
        Trigger("give me", end="snowmen", protected=True): snowman,
        Trigger("!ban", access_level=1, protected=True): ban,
        Trigger("!admin", access_level=1, protected=True): give_admin,
        Trigger("!say", protected=True): frosty_say,
        Trigger("!add", access_level=1, protected=True): new_command,
        Trigger("!remove", access_level=1, protected=True): remove_command,
        Trigger("!budget", access_level=-1, protected=True) : get_finances,
        Trigger("!list", access_level=-1, protected=True): command_list,
        Trigger("!help", access_level=-1, protected=True) : help
    }


@client.event
async def on_message(message):
    if not message.author.bot:
        try:
            Response(message)
        except Exception as e:
            raise e


def main():
    snow_alert = SnowAlertSystem(client)
    client.loop.create_task(snow_alert.check_bsd())

    client.run(sys.argv[1])


if __name__ == "__main__":
    main()
