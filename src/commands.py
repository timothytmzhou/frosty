import traceback
import re
import discord
from src.config import PARAMS
from inspect import getfullargspec
from docstring_parser import parse
from discord_slash import SlashCommand
from discord_slash import SlashCommandOptionType
from discord_slash.utils import manage_commands

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, auto_register=True)


class CommandDocstringParser:
    """
    Parses a docstring for a command.
    """

    def __init__(self, command):
        """
        :param command: the function to parse the info of
        """
        self.argspec = getfullargspec(command)
        self.docstring = command.__doc__
        self.name = command.__name__

        parsed = parse(self.docstring)
        self.description = parsed.short_description
        self.params = self.parse_params(parsed.params)

    def parse_params(self, params):
        """
        Parses the params of the docstring.

        :param params: output of docstring_parser.parse.params
        """
        parsed = []
        num_args = len(self.argspec.args)
        num_defaults = len(self.argspec.defaults) if self.argspec.defaults is not None else 0
        for param in params:
            if not param.arg_name in self.argspec.args:
                raise ValueError(
                    "Found unknown param {0} in docstring for {1}".format(param.arg_name,
                                                                          self.name))
            elif self.argspec.kwonlyargs:
                raise ValueError("Commands should not have keyword only arguments")

            arg_index = self.argspec.args.index(param.arg_name)
            if arg_index == 0:
                continue
            param_name = param.arg_name
            description = param.description
            option_type = SlashCommandOptionType[param.type_name.upper()]
            required = num_args - arg_index > num_defaults
            parsed.append((param_name, description, option_type, required))
        return parsed


def handle(func):
    """
    Wraps an async function with a typing context, a check to make sure the bot does not reply
    to itself, and a try/except block which handles errors.
    """

    async def wrapper(ctx, *args, **kwargs):
        if not ctx.author.bot:
            try:
                async with ctx.channel.typing():
                    await func(ctx, *args, **kwargs)
            except Exception:
                traceback.print_exc()

    return wrapper


def command(name=None):
    """
    The command decorator. Returns a decorator which fills out discord_slash options automatically
    based on parsed docstrings.

    :param name: the name of the command (function name if None)
    """

    def wrapper(func):
        parsed = CommandDocstringParser(func)
        command_name = parsed.name if name is None else name
        slash_command = slash.slash(name=command_name, guild_ids=[PARAMS["guild_id"]],
                                    description=parsed.description,
                                    options=[manage_commands.create_option(*args) for args in
                                             parsed.params])
        return slash_command(handle(func))

    return wrapper


def subcommand(base=None, name=None):
    """
    The subcommand decorator. Returns a decorator which fills out discord_slash options
    automatically based on parsed docstrings. Subcommands should be named like base_name.

    :param base: the name of the base command (first part of function name if None)
    :param name: the name of the subcommand (second part of function name if None)
    """

    def wrapper(func):
        parsed = CommandDocstringParser(func)
        base_name = base
        sub_name = name
        if "_" in parsed.name:
            a, b = parsed.name.split("_", limit=1)
            if base is None:
                base_name = a
            if name is None:
                sub_name = b

        slash_command = slash.subcommand(base=base_name, name=sub_name,
                                         guild_ids=[PARAMS["guild_id"]],
                                         description=parsed.description,
                                         options=[manage_commands.create_option(*args) for args in
                                                  parsed.params])
        return slash_command(handle(func))

    return wrapper


class Trigger:
    """
    Simple wrapper for a pattern and whether or not it should be searched for or matched against.
    """

    def __init__(self, pattern, search=False):
        """
        :param pattern: regex pattern
        :param search: whether or not the string should be searched for, rather than matched
                       against, the pattern
        """
        self.pattern = pattern
        self.search = search

    def match(self, string):
        """
        Returns either a re.match or a re.search object.

        :param string: the string to match against
        """
        if self.search:
            return re.search(self.pattern, string)
        else:
            return re.match(self.pattern, string)


# map of Trigger objects to async functions
triggers = {}


def trigger(pattern, search=False):
    """
    The trigger decorator. Returns a decorator which sets a trigger on which the input command
    is executed.

    :param pattern: regex pattern
    :param search: whether or not the string should be searched for, rather than matched
                   against, the pattern
    """

    def wrapper(func):
        triggers[Trigger(pattern, search)] = func
        return func

    return wrapper


@client.event
@handle
async def on_message(ctx):
    """
    Handles message triggers.
    """
    for trigger, func in triggers.items():
        if (m := trigger.match(ctx.content)):
            await func(ctx, *m.groups())
