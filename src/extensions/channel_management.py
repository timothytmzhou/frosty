"""
Manages channels a la google hangouts through a role-based system.
Members can kick/add each other with commands.
"""
from src.message_structs import Call
from discord import Permissions, PermissionOverwrite

# Member : Role
role_ids = {}
role_permissions = Permissions.all()
role_permissions.update({"administrator": False, "manage_roles": False, "manage_channels": False})


def get_permission_overwrite(allowed):
    return PermissionOverwrite(
        read_messages=allowed,
        send_messages=allowed,
        read_message_history=allowed,
        mention_everyone=allowed,
        external_emojis=allowed,
        embed_links=allowed,
        attach_files=allowed
    )


allowed = get_permission_overwrite(True)
banned = get_permission_overwrite(False)


def get_members_from_str(str_members):
    return set(member for member in role_ids if role_ids[member].name in str_members)


async def _set_role_id(guild, member, role):
    role = await guild.create_role(name=role, permissions=role_permissions)
    await member.add_roles(role)
    role_ids[member] = role


def set_role_id(msg_info, name):
    """
    > Changes the name of the unique role assigned to the user.
     """
    if msg_info.author in role_ids:
        role = role_ids[msg_info.author]
        role.edit(name=name)
        return Call(
            task=Call.send,
            args=(msg_info.channel, "set {0}'s role id to {1}".format(msg_info.name, name))
        )
    else:
        return Call(task=_set_role_id, args=(msg_info.guild, msg_info.author, name))


async def _make_channel(msg_info, name, members=None):
    overwrites = {msg_info.author: allowed}
    if members is not None:
        overwrites.update({
            role_ids[member]: allowed for member in members
        })
    channel = await msg_info.guild.create_text_channel(name, overwrites=overwrites)
    await channel.send("created channel {0}".format(name))


def make_channel(msg_info, name, members=None):
    """
    > Makes a new channel with supplied users.
        > author of message is added automatically.
    > /make channel_name *users
     """
    args = (msg_info, name)
    if members is not None:
        members = get_members_from_str(members.split())
        args += members
    return Call(task=_make_channel, args=args)


async def _add_members(channel, *members):
    for member in members:
        await channel.set_permissions(member, allowed)
    await channel.send("added {} to channel".format(", ".join(map(lambda m: m.name, members))))


def add_members(msg_info, members):
    """
    > Adds members to channel
    > /add *users
    """
    members = get_members_from_str(members.split())
    return Call(task=_add_members, args=(msg_info.channel, *members))


async def _remove_members(channel, *members):
    members = set(members)
    for member in members:
        await channel.set_permissions(member, banned)
    await channel.send("removed {} from channel".format(", ".join(map(lambda m: m.name, members))))


def remove_members(msg_info, members):
    """
    > Removes members from channel
    > /remove *users
    """
    members = get_members_from_str(members.split())
    return Call(task=_remove_members, args=(msg_info.channel, *members))


async def _rename_channel(channel, name):
    await channel.edit(name=name)


def rename_channel(msg_info, name):
    """
    > Renames channel (follow emoji format please!)
    > /rename channel_name
    """
    return Call(task=_rename_channel, args=(msg_info.channel, name))
