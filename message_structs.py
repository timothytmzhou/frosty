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
    def get_level(author, discrim):
        name = "{0}#{1}".format(author, discrim)
        for access_level in UserData.levels:
            if name in UserData.levels[access_level]:
                return access_level.value
        # If the user's level isn't already defined, add them to the users list
        UserData.levels[UserTypes.USER].append(name)
        return 0


class CallType(Enum):
    DELETE = 0
    SEND = 1
    REPLACE = 2


class Message_Info:
    def __init__(self, message):
        self.message = message
        self.words = self.message.content.split(" ")
        self.lwords = [w.lower() for w in self.words]
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
            if not self.ignore_keywords:
                keywords = {
                    "!auth": self.message.author.name,
                    "!channel": self.message.channel.name
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
        # Sets beginning and ending trigger phrases, .split()ed versions of
        #     them.
        self.begin = begin.lower()
        self.b_words = self.begin.split()

        self.end = end
        if self.end is not None:
            self.end = self.end.lower()
            self.e_words = self.end.split()

        self.access_level = access_level
        self.protected = protected

    def __str__(self):
        string = "< {0}+ > ".format(
            UserTypes(self.access_level).name.lower()
        )
        if self.end is not None:
            string += "{0}...{1}".format(self.begin, self.end)
        else:
            string += "{0}".format(self.begin)
        return string

    def begins(self, lwords):
        """
        Given a list of lowercase words, checks if it begins with this
        trigger's start phrase.
        :param lwords:
        :return:
        """
        return lwords[:len(self.b_words)] == self.b_words

    def ends(self, lwords):
        """
        Given a list of lowercase words, checks if it begins with this
        trigger's end phrase.
        :param lwords:
        :return:
        """
        return self.end is None or lwords[-len(self.e_words):] == self.e_words

    def begin_index(self, lwords):
        """
        Gets index of last element of this trigger's start phrase (guaranteed
        to be in lwords).
        :param lwords:
        :return:
        """
        return lwords.index(self.b_words[0]) + len(self.b_words)

    def end_index(self, lwords):
        """
        Gets index of first element of this trigger's end phrase (guaranteed to
        be in lwords).
        :param lwords:
        :return:
        """
        if self.end is None:
            return len(lwords)
        else:
            return lwords.index(self.e_words[0])

    def slice(self, words, lwords):
        """
        Gets the content of the message between the start and end triggers
            (guaranteed to be in lwords).
        E.g "_START_ my message in between _END_" returns "my message in
            between"
        :param words:
        :param lwords:
        :return: A space-separated string.
        """
        return " ".join(words[
                        self.begin_index(lwords):
                        self.end_index(lwords)
                        ])
