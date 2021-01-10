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


def parse_emote(emote):
    """
    Parses a emote name from a string.
    """
    return re.search(':.*:', emote).group()


async def make(ctx, emote, name, members):
    """
    Updates a channel with the supplied members (roles or users).

    :param emote: emote for the channel
    :param name: name of the channel
    :param members: members to add to channel
    """
    overwrites = {ctx.author: ALLOWED, ctx.guild.roles[0]: BANNED}
    overwrites.update({member: ALLOWED for member in members})
    category = get(ctx.guild.categories, id=PROFILE["text"])
    await ctx.guild.create_text_channel("{0}│{1}".format(parse_emote(emote), name),
                                        category=category,
                                        overwrites=overwrites)


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


async def update_members(channel, members, permissions):
    """
    Updates the permissions of members (roles or users) in a channel.

    :param channel: channel to add members to
    :param members: members to add to channel
    :param permissions: permissions object
    """
    for member in members:
        await channel.set_permissions(member, overwrite=permissions)


@subcommand()
async def add_role(ctx, *roles):
    """
    Adds roles to channel.

    :param role roles: roles to add
    """
    await update_members(ctx.channel, roles, ALLOWED)


def get_members(guild, tags):
    tags = re.findall("<@[!&]?\d+>|\S.+?#\d{4}|@here|@everyone", tags)
    for tag in tags:
        if (m := re.match(r"<@[!]?(\d+)>", tag)):
            uid = int(m.group(1))
            yield get(guild.members, id=uid)
        elif (m := re.match("(\S.+?#\d{4})", tag)):
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


@subcommand()
async def add_user(ctx, *users):
    """
    Adds users to channel.

    :param string users: users to add
    """
    await update_members(ctx.channel, get_members(ctx.guild, users), ALLOWED)


@subcommand()
async def kick_role(ctx, *roles):
    """
    Kicks roles from channel.

    :param role roles: roles to kick
    """
    await update_members(ctx.channel, roles, BANNED)


@subcommand()
async def kick_user(ctx, *users):
    """
    Kicks users from channel.

    :param user users: users to kick
    """
    await update_members(ctx.channel, users, BANNED)


@command()
async def rename(ctx, emote, name):
    """
    Renames a channel.

    :param string emote: new emote of the channel
    :param string name: new name of the channel
    """
    await ctx.channel.edit(name=("{0}│{1}".format(parse_emote(emote), name)))


@command()
async def archive(ctx):
    """
    Archives this channel.
    """
    channel = ctx.channel
    if channel.category_id == PROFILE["archive"]:
        await channel.edit(category=get(ctx.guild.categories, id=PROFILE["text"]))
    else:
        await channel.edit(category=get(ctx.guild.categories, id=PROFILE["archive"]))


@command()
async def pin(ctx, id):
    """
    Pins or unpins a message.

    :param integer id: message id
    """
    msg = await ctx.channel.fetch_message(id)
    if msg.pinned():
        await msg.unpin()
    else:
        await msg.pin()
