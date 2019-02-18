# ihscy's over-engineered Discord bot
# This code is probably borken rn (IDK, haven't unit tested any of it) so neil plz fix thx
import discord
import asyncio
import math
import xkcd
import numpy as np
from bsd import SnowAlertSystem
from message_structs import CallType, UserData, UserTypes
from timeout import timeout


client = discord.Client()


class Call:
    def __init__(self, call_type, message, response=None):
        self.call_type = call_type
        self.response = response
        self.message = message

    def invoke(self):
        if self.call_type == CallType.DELETE or self.call_type == CallType.REPLACE:
            self.delete(self.message)
        if self.call_type == CallType.SEND or self.call_type == CallType.REPLACE:
            if self.response is not None:
                self.send(self.message.channel, self.response)
        else:
            return

    async def send(self):
        if self.response is not None:
            self.response = self.response.replace("!auth", self.message.author.name)
            await client.send_message(self.message.channel, self.response)

    async def delete(self):
        await client.delete_message(self.message)


class Trigger:
    def __init__(self, begin, access_level=0, end=None):
        self.begin = begin.lower()
        self.end = end
        if self.end is not None:
            self.end = self.end.lower()
        self.access_level = access_level

    def __str__(self):
        string = ""
        if self.end is not None:
            string += "`{0}...{1}`".format(self.begin, self.end)
        else:
            string += "`{0}`".format(self.begin)
        string += " with user status `{0}` or higher".format(
            UserTypes(self.access_level).name.lower()
        )
        return string

    def begins(self, lwords):
        return self.begin in lwords

    def ends(self, lwords):
        return self.end is None or self.end in lwords

    def begin_index(self, lwords):
            return lwords.index(self.begin)

    def end_index(self, lwords):
        if self.end is None:
            return len(lwords)
        else:
            return lwords.index(self.end) + 1

    def slice(self, words):
        sliced = " ".join(words[
            self.begin_index(w.lower() for w in words):
            self.end_index(w.lower() for w in words)
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
    safe_characters = (
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "/", "+", "-", "%", "^", "(", ")"
    )

    def __init__(self, message):
        # Get data from message
        self.message = message
        self.words = self.message.content.split(" ")
        self.lwords = [s.lower() for s in self.words]
        self.author = self.message.author.name
        for trigger, func in Response.commands.items():
            if trigger.begins(self.lwords) and trigger.ends(self.lwords):
                user_level = UserData.get_level(self.author)
                if user_level >= trigger.access_level:
                    message_slice = trigger.slice(self.words)
                    if message_slice is not None:
                        func(message_slice).invoke()
                else:
                    func.send("Command unauthorized for status `{0}`").format(
                        UserTypes(trigger.access_level).name.lower()
                    )

    def new_command(self, message_slice):
        i = message_slice.index(":")
        trigger = Trigger(*message_slice[:i])
        reply = ' '.join(message_slice[i + 1:])
        if "!del" in reply:
            call = Call(CallType.REPLACE, self.message, reply.replace("!del", "").strip())
        else:
            call = Call(CallType.SEND, self.message, reply.strip())
        Response.commands[trigger] = call
        return Call(
            CallType.SEND,
            self.message,
            "New command: on `{0}` I'll say `{1}`".format(', '.join(trigger), reply)
        )

    def remove_command(self, message_slice):
        for trigger in Response.commands:
            if trigger.begin == message_slice:
                return Call(
                    CallType.SEND,
                    self.message,
                    "Trigger `{0}` with response `{1}` removed".format(
                        ', '.join(trigger.begin),
                        Response.commands.pop(trigger)
                    )
                )

    def ban(self, message_slice):
        recipient_level = UserData.get_level(message_slice)
        if recipient_level == -1:
            UserData.levels[UserTypes.BAN].remove(message_slice)
            return Call(CallType.SEND, self.message, "Un-banned {0}".format(message_slice))
        elif recipient_level == 2:
            return Call(CallType.SEND, self.message, "Owners can't be banned")
        else:
            UserData.levels[UserData(recipient_level)].remove(message_slice)
            UserData.levels[UserTypes.BANNED].append(message_slice)
            return Call(CallType.SEND, self.message, "{0} has been banned")

    def give_admin(self, message_slice):
        recipient_level = UserData.get_level(message_slice)
        if recipient_level == 1:
            UserData.levels[UserTypes.ADMIN].remove(message_slice)
            return Call(
                CallType.SEND,
                self.message,
                "{0}'s admin status has been revoked".format(message_slice)
            )
        elif recipient_level == 2:
            return Call(CallType.SEND, self.message, "Owners can't be given admin status")
        else:
            UserData.levels[UserData(recipient_level)].remove(message_slice)
            UserData.levels[UserTypes.ADMIN].append(message_slice)
            return Call(CallType.SEND, self.message, "{0} is now an admin")

    def snowman(self, message_slice):
        if UserData.get_level(self.author) == -1:
            return "{0} doesn't deserve ANY snowmen".format(
                self.message.author.name
            )
        else:
            if message_slice == "a":
                snowman_count = 1
            else:
                if all(char in Response.safe_characters for char in message_slice):
                    @timeout
                    def evaluate():
                        return int(eval(message_slice))
                    snowman_count = evaluate()
            if snowman_count > 0:
                return Call(CallType.SEND, self.message, "☃" * min(snowman_count, 128))

    def frosty_say(self, message_slice):
        return Call(CallType.REPLACE, self.message, message_slice)

    def command_list(self, message_slice):
        message = "**Commands:**\n"
        message += "\n".join(
            "`{0}` will run `{1}`\n".format(trigger.begin, func.__name__)
            for trigger, func in Response.commands
        )
        return Call(CallType.SEND, self.message, message)

    commands = {
        Trigger("give me", end="snowman"): snowman,
        Trigger("give me", end="snowmen"): snowman,
        Trigger("!ban", access_level=1): ban,
        Trigger("!admin", access_level=1): give_admin,
        Trigger("!say"): frosty_say,
        Trigger("!add", access_level=1): new_command,
        Trigger("!remove", access_level=1): remove_command,
        Trigger("!list"): command_list
    }


@client.event
async def on_message(message):
    if not message.author.bot:
        Response(message)


async def check_bsd():
    await client.wait_until_ready()
    while not client.is_closed:
        if SnowAlertSystem.get_warning() != SnowAlertSystem.last:
            last = SnowAlertSystem.get_warning()
            await client.send_message(
                ANNOUNCEMENTS,
                "`{0}`".format(last.strip())
            )
        await asyncio.sleep(5)

ANNOUNCEMENTS = discord.Object(id=500749047364321344)
snow_alert = SnowAlertSystem()
client.loop.create_task(check_bsd())

client.run(input("Token: "))
