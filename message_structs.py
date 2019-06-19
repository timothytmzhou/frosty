from enum import Enum


class UserTypes(Enum):
    OWNER = 2
    ADMIN = 1
    USER = 0
    BANNED = -1


class UserData:

    levels = {
        UserTypes.OWNER: ["stackdynamic#4860"],
        UserTypes.ADMIN: ["nog642#5233", "veggietiki#4699", "imyxh#6725", "Creon#3992", "NotDeGhost#6829", "jespiron#3979"],
        UserTypes.USER: [],
        UserTypes.BANNED: []
    }

    @staticmethod
    def get_level(author, discrim):
        for access_level in UserData.levels:
            if [author, discrim] in [user.split("#") for user in UserData.levels[access_level]]:
                return access_level.value
        # If the user's level isn't already defined, add them to the users list
        UserData.levels[UserTypes.USER].append("{0}#{1}".format(author, discrim))
        return 0


class CallType(Enum):
    DELETE = 0
    SEND = 1
    REPLACE = 2
