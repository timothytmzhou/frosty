import re
from enum import Enum


class UserTypes(Enum):
    OWNER = 2
    ADMIN = 1
    USER = 0
    BANNED = -1


class UserData:
    levels = {
        UserTypes.OWNER: ["stackdynamic#4860"],
        UserTypes.ADMIN: ["nog642#5233", "veggietiki#4699", "imyxh#6725", "Creon#3992",
                          "NotDeGhost#6829", "jespiron#3979"],
        UserTypes.USER: [],
        UserTypes.BANNED: []
    }

    @staticmethod
    def get_level(id):
        for access_level in UserData.levels:
            if id in UserData.levels[access_level]:
                return access_level.value
        # If the user's level isn't already defined, add them to the users list
        UserData.levels[UserTypes.USER].append(id)
        return 0


class CallType(Enum):
    DELETE = 0
    SEND = 1
    REPLACE = 2


class Message_Info:
    def __init__(self, message):
        self.message = message
        self.content = self.message.content
        self.author = self.message.author.name
        self.discriminator = self.message.author.discriminator
        self.user_level = UserData.get_level(self.author, self.discriminator)


class Call:
    def __init__(self, call_type, message, response=None,
                 ignore_keywords=False):
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
            self.response = self.response.replace("@", "")
            if not self.ignore_keywords:
                keywords = {
                    "!auth": self.message.author.name,
                    "!channel": self.message.channel.name
                }
                for key in keywords:
                    self.response = self.replace_keyords(key, keywords[key])
            await self.message.channel.send(self.response[:2000])

    async def delete(self):
        await self.message.delete()

    def replace_keyords(self, key, var):
        return self.response.replace(key, var)


class Trigger:
    def __init__(self, pattern, name=None, access_level=0, protected=True):
        # Sets beginning and ending trigger phrases, .split()ed versions of
        #     them.
        self.pattern = pattern
        if name is None:
            self.name = re.match(r"[a-zA-Z\d!]*", self.pattern).group(0).strip()
        else:
            self.name = name
        self.access_level = access_level
        self.level = UserTypes(self.access_level).name.lower()
        self.protected = protected

    def match(self, text):
        return re.match(self.pattern, text, re.DOTALL)

    def slice(self, text):
        return tuple(g.strip() for g in self.match(text).groups())
