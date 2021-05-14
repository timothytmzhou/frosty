from src.commands import *


@command("help")
async def frosty_help(ctx):
    """
    Shows the Frosty user manual.
    """
    with open("about.txt", "r") as f:
        await ctx.send(content=f.read(), hidden=True)

@command("langs")
async def langs(ctx):
    """
    Gets a list of supported languages.
    """
    with open("languages.txt", "r") as f:
        await ctx.send(f.read(), hidden=True)

@trigger("give me a snowman|give me (.+) snowmen")
async def snowman(msg, snowmen_request=1):
    """
    Giver of snowmen since 2018.

    :param snowmen_request: translates "a" to 1, evals arithmetic expressions <= 128
    """
    try:
        n = int(snowmen_request)
        if n > 128:
            await msg.channel.send("that's too many snowmen")
        elif n > 0:
            await msg.channel.send(n * "☃")
        else:
            await msg.channel.send("that's not a valid number of snowmen")
    except ValueError:
        await msg.channel.send("I don't know how many snowmen that is")


@command()
async def echo(ctx, string):
    """
    Make frosty say something.

    :param string string: a string of text
    """
    await ctx.channel.send(string)
    await ctx.send(content="​", hidden=True)
