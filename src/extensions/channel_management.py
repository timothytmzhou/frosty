"""
Manages channels a la google hangouts through a role-based system.
Members can kick/add each other with commands.
"""
import re
from src.message_structs import Call
from discord import PermissionOverwrite, Status
from discord.utils import get

ALLOWED = PermissionOverwrite(
    read_messages=True,
    send_messages=True,
    manage_messages=False,
    read_message_history=True,
    mention_everyone=True,
    external_emojis=True,
    embed_links=True,
    attach_files=True
)

BANNED = PermissionOverwrite(
    read_messages=False,
    send_messages=False,
    manage_messages=False,
    read_message_history=False,
    mention_everyone=False,
    external_emojis=False,
    embed_links=False,
    attach_files=False
)


# TODO: clean this up
# @here and @everyone are not channel-specific--is this behavior correct?
def _get_members(guild, tags):
    tags = tags.split()
    for tag in tags:
        if (m := re.match(r"<@[!]?(\d+)>", tag)):
            uid = int(m.group(1))
            yield get(guild.members, id=uid)
        elif (m := re.match("(\w+#\d{4})", tag)):
            username, discriminator = m.group(1).split("#")
            yield get(guild.members, name=username, discriminator=discriminator)
        elif (m := re.match("<@\&(\d+)>", tag)):
            role_id = m.group(1)
            role = get(guild.roles, id=int(role_id))
            yield from role.members
        elif tag == "@here":
            yield from (member for member in guild.members if member.status == Status.online)
        elif tag == "@everyone":
            yield from guild.members


def get_members(guild, members):
    return set(_get_members(guild, members))


async def _make_channel(msg_info, name, members=None):
    overwrites = {msg_info.author: ALLOWED, msg_info.guild.roles[0]: BANNED}
    if members is not None:
        overwrites.update({
            member: ALLOWED for member in members
        })
    category = msg_info.channel.category
    channel = await msg_info.guild.create_text_channel(name, category=category,
                                                       overwrites=overwrites)
    await channel.send("created channel {0}".format(name))


def make_channel(msg_info, name, members=None):
    """
    > Makes a new channel with supplied users
    > author of message is added automatically
    > /make channel_name *users
    """
    args = [msg_info, name]
    if members is not None:
        members = get_members(msg_info.guild, members)
        args.append(members)
    return Call(task=_make_channel, args=args)


async def _add_members(channel, members):
    added = []
    for member in members:
        await channel.set_permissions(member, overwrite=ALLOWED)
        added.append(member.name)
    await channel.send("added {} to channel".format(", ".join(added)))


def add_members(msg_info, members):
    """
    > Adds members to channel
    > /add *users
    """
    members = get_members(msg_info.guild, members)
    return Call(task=_add_members, args=(msg_info.channel, members))


async def _remove_members(channel, members):
    added = []
    for member in members:
        await channel.set_permissions(member, overwrite=BANNED)
        added.append(member.name)
    await channel.send("removed {} from channel".format(", ".join(added)))


def remove_members(msg_info, members):
    """
    > Removes members from channel
    > /remove *users
    """
    members = get_members(msg_info.guild, members)
    return Call(task=_remove_members, args=(msg_info.channel, members))


async def _rename_channel(channel, name):
    await channel.edit(name=name)


def rename_channel(msg_info, name):
    """
    > Renames channel (follow emoji format please!)
    > /rename channel_name
    """
    return Call(task=_rename_channel, args=(msg_info.channel, name))


async def _pin_message(channel, msg_id):
    msg = await channel.fetch_message(int(msg_id))
    await msg.pin()


def pin_message(msg_info, msg_id):
    """
    > Pins a message via id
    > /pin msg_id
    """
    return Call(task=_pin_message, args=(msg_info.channel, msg_id))
