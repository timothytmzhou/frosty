"""
Manages channels a la google hangouts through a role-based system.
Members can kick/add each other with commands.
"""
import discord.utils


unique_user_nicknames = dict()


def set_nickname(msg_info, name):
    if msg_info.tag in unique_user_nicknames:
        unique_user_nicknames.pop(msg_info.tag)

