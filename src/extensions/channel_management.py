"""
Manages channels a la google hangouts through a role-based system.
Members can kick/add each other with commands.
"""
from src.commands import *
from src.config import PROFILE
from discord import PermissionOverwrite
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


async def show_log(ctx, content):
    """
    Does something with the context so the slash command log is shown.
    """
    await ctx.send(content="`{}`".format(content))


async def make(ctx, emote, name, members):
    """
    Updates a channel with the supplied members (roles or users).

    :param emote: emote for the channel
    :param name: name of the channel
    :param members: members to add to channel
    """
    channel_name = "{0}│{1}".format(emote, name)
    overwrites = {ctx.author: ALLOWED, ctx.guild.roles[0]: BANNED}
    overwrites.update({member: ALLOWED for member in members})
    category = get(ctx.guild.categories, id=PROFILE["text"])
    await ctx.guild.create_text_channel(channel_name,
                                        category=category,
                                        overwrites=overwrites)
    await show_log(ctx, "Made channel {}".format(channel_name))


@subcommand()
async def make_role(ctx, emote, name, *roles):
    """
    Makes a new channel and adds supplied roles to it.

    :param string emote: emote for the channel
    :param string name: name of the channel
    :param role roles: roles to add to channel
    """
    await make(ctx, emote, name, roles)


@subcommand()
async def make_user(ctx, emote, name, *users):
    """
    Makes a new channel and adds supplied users to it.

    :param string emote: emote for the channel
    :param string name: name of the channel
    :param user users: users to add to channel
    """
    await make(ctx, emote, name, users)


async def update_members(ctx, members, permissions):
    """
    Updates the permissions of members (roles or users) in a channel.

    :param ctx: message context
    :param members: members to add to channel
    :param permissions: permissions object
    """
    for member in members:
        if isinstance(member, Exception):
            await show_log(ctx, str(member))
            return False
        else:
            await ctx.channel.set_permissions(member, overwrite=permissions)
    return True


async def update_roles(channel, roles, permissions):
    """
    Updates the permissions of members (roles or users) in a channel.

    :param channel: channel to add members to
    :param roles: roles to update
    :param permissions: permissions object
    """
    for role in roles:
        await channel.set_permissions(role, overwrite=permissions)


def get_display_name(user):
    """
    Helper method to get display name for a user.
    """
    return user.nick if user.nick is not None else user.name


@subcommand()
async def add_role(ctx, **roles):
    """
    Gives default permissions for the given roles. User-level permissions overwrite role-level ones.

    :param role roles: roles to add
    """
    await update_roles(ctx.channel, roles.values(), ALLOWED)
    await show_log(ctx, "Added {}".format(", ".join(role.name for role in roles.values())))


def get_members(guild, tags):
    """
    Gets members from either pings or names + discriminators.
    """
    for tag in tags:
        if (m := re.match(r"<@[!]?(\d+)>", tag)):
            uid = int(m.group(1))
            yield get(guild.members, id=uid)
        elif (m := re.match("(\S.+?#\d{4})", tag)):
            username, discriminator = m.group(1).split("#")
            yield get(guild.members, name=username, discriminator=discriminator)
        else:
            # Assume user nicknames
            matches = [member for member in guild.members if get_display_name(member).lower() == tag.lower()]
            if len(matches) > 1:
                yield ValueError("Nickname is not unique, use username and discriminator")
            elif matches:
                yield matches[0]
            else:
                yield ValueError("Not found.")


@subcommand()
async def add_user(ctx, **users):
    """
    Adds users to channel.

    :param string users: name and discriminator (e.g frosty#1234) or nickname (must be unique in server, case-insensitive)
    """
    success = await update_members(ctx, get_members(ctx.guild, users.values()), ALLOWED)
    if success:
        await show_log(ctx, "Added {}".format(", ".join(user.nick for user in get_members(ctx.guild, users.values()))))


@subcommand()
async def kick_role(ctx, **roles):
    """
    Removes default permissions for the given roles. User-level permissions overwrite role-level ones.

    :param role roles: roles to kick
    """
    await update_roles(ctx.channel, roles.values(), BANNED)
    await show_log(ctx, "Kicked {}".format(", ".join(role.name for role in roles.values())))


@subcommand()
async def kick_user(ctx, **users):
    """
    Kicks users from channel.

    :param user users: users to kick
    """
    await update_members(ctx, users.values(), BANNED)
    await show_log(ctx, "Kicked {}".format(", ".join(user.nick for user in users.values())))


@command()
async def rename(ctx, emote, name):
    """
    Renames a channel.

    :param string emote: new emote of the channel
    :param string name: new name of the channel
    """
    await ctx.channel.edit(name=("{0}│{1}".format(emote, name)))
    await show_log(ctx, "Renamed channel to {}".format(name))


@command()
async def archive(ctx):
    """
    Archives this channel.
    """
    channel = ctx.channel
    if channel.category_id == PROFILE["archive"]:
        await channel.edit(category=get(ctx.guild.categories, id=PROFILE["text"]))
        await show_log(ctx, "Unarchived channel")
    else:
        await channel.edit(category=get(ctx.guild.categories, id=PROFILE["archive"]))
        await show_log(ctx, "Archived channel")


@command()
async def pin(ctx, id):
    """
    Pins or unpins a message.

    :param string id: message id
    """
    msg = await ctx.channel.fetch_message(int(id))
    if msg.pinned:
        await msg.unpin()
    else:
        await msg.pin()
    await show_log(ctx, "Pinned message")
