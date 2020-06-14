"""
Manages channels a la google hangouts through a role-based system.
Members can kick/add each other with commands.
"""
import aiofiles
import json
from os import path
from src.message_structs import Call
from discord import Permissions, PermissionOverwrite, Member, Role
from discord.utils import get

CHANNEL_DATA = "channel_data.json"

if path.exists(CHANNEL_DATA):
    with open(CHANNEL_DATA) as f:
        role_ids = {int(key): value for key, value in json.load(f).items()}
else:
    role_ids = {}

ROLE_PERMISSIONS = Permissions.all()
ROLE_PERMISSIONS.update(administrator=False, manage_roles=False, manage_channels=False)

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


async def serialize_role_ids():
    serialized = json.dumps(role_ids)
    async with aiofiles.open(CHANNEL_DATA, "w") as f:
        await f.write(serialized)


def get_role_from_member_id(guild, member_id):
    return get(guild.roles, id=role_ids[member_id])


def get_members_from_str(guild, str_members):
    members = set()
    for member_id in role_ids:
        member = get(guild.members, id=member_id)
        if get_role_from_member_id(guild, member_id).name in str_members:
            members.add(member)
    return members


async def _set_role_id(msg_info, target, name):
    if isinstance(target, Member):
        role = await msg_info.guild.create_role(name=name, permissions=ROLE_PERMISSIONS)
        await target.add_roles(role)
        role_ids[target.id] = role.id
    elif isinstance(target, Role):
        await target.edit(name=name)
    await serialize_role_ids()
    await msg_info.channel.send("set role id to {}".format(name))


def set_role_id(msg_info, name):
    """
    > Changes the name of the unique role assigned to the user.
     """
    author_id = msg_info.author.id
    if author_id in role_ids:
        target = get_role_from_member_id(msg_info.guild, author_id)
    else:
        target = msg_info.author
    return Call(task=_set_role_id, args=(msg_info, target, name))


async def _make_channel(msg_info, name, members=None):
    overwrites = {msg_info.author: ALLOWED, msg_info.guild.roles[0]: BANNED}
    if members is not None:
        overwrites.update({
            get_role_from_member_id(msg_info.guild, member.id): ALLOWED for member in members
        })
    category = msg_info.channel.category
    channel = await msg_info.guild.create_text_channel(name, category=category,
                                                       overwrites=overwrites)
    await channel.send("created channel {0}".format(name))


def make_channel(msg_info, name, members=None):
    """
    > Makes a new channel with supplied users.
        > author of message is added automatically.
    > /make channel_name *users
     """
    args = (msg_info, name)
    if members is not None:
        members = get_members_from_str(msg_info.guild, members.split())
        args += members
    return Call(task=_make_channel, args=args)


async def _add_members(channel, *members):
    for member in members:
        await channel.set_permissions(member, overwrite=ALLOWED)
    await channel.send("added {} to channel".format(", ".join(map(lambda m: m.name, members))))


def add_members(msg_info, members):
    """
    > Adds members to channel
    > /add *users
    """
    members = get_members_from_str(msg_info.guild, members.split())
    return Call(task=_add_members, args=(msg_info.channel, *members))


async def _remove_members(channel, *members):
    members = set(members)
    for member in members:
        await channel.set_permissions(member, overwrite=BANNED)
    await channel.send("removed {} from channel".format(", ".join(map(lambda m: m.name, members))))


def remove_members(msg_info, members):
    """
    > Removes members from channel
    > /remove *users
    """
    members = get_members_from_str(msg_info.guild, members.split())
    return Call(task=_remove_members, args=(msg_info.channel, *members))


async def _rename_channel(channel, name):
    await channel.edit(name=name)


def rename_channel(msg_info, name):
    """
    > Renames channel (follow emoji format please!)
    > /rename channel_name
    """
    return Call(task=_rename_channel, args=(msg_info.channel, name))
