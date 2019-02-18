from enum import Enum


class UserTypes(Enum):
    OWNER = 2
    ADMIN = 1
    USER = 0
    BANNED = -1


class UserData:
    levels = {UserTypes.OWNER: ["Timothy Z."],
              UserTypes.ADMIN: ["nog642", "veggietiki", "imyxh", "VkRob"],
              UserTypes.USER: [],
              UserTypes.BANNED: []
              }

    @staticmethod
    def get_level(author):
        for access_level in UserData.levels:
            if author in UserData.levels[access_level]:
                return access_level.value
        # If the user's level isn't already defined, add them to the users list
        UserData.user.append(author)
        return 0