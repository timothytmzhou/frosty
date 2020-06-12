import re
from io import StringIO
from discord import File


class Message_Info:
    def __init__(self, message):
        self.message = message
        self.content = message.content
        self.channel = message.channel
        self.guild = message.guild
        self.author = message.author
        self.name = self.author.name
        self.discriminator = self.author.discriminator
        self.tag = "{0}#{1}".format(self.name, self.discriminator)


class Call:
    def __init__(self, task, args):
        self.task = task
        self.args = args

    async def invoke(self):
        if self.task:
            await self.task(self.args)

    async def send(self, channel, text):
        if len(text > 2000):
            await channel.send("message is longer than 2000 characters, writing to file")
            await channel.send(file=File(StringIO(text), "output.txt"))
        else:
            await channel.send(text)

    async def delete(self, msg):
        await msg.delete()

    async def replace(self, msg, text):
        channel = msg.channel
        await self.delete(msg)
        await self.send(text, channel)


class Trigger:
    def __init__(self, pattern, name=None, protected=True):
        # Sets beginning and ending trigger phrases, .split()ed versions of
        #     them.
        self.pattern = pattern
        if name is None:
            # assume pattern in the form ^/name args if name is not specified
            assert re.match(r"\^\/\w+( .*)?", self.pattern)
            self.name = self.pattern.split()[0][1:]
        else:
            self.name = name
        self.protected = protected

    def match(self, text):
        return re.match(self.pattern, text, re.DOTALL)

    def slice(self, text):
        return tuple(
            g.strip() for g in self.match(text).groups() if g is not None
        )
