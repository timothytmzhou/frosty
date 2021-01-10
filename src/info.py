from src.commands import *
from src.extensions import sandbox


@command("help")
async def frosty_help(ctx):
    """
    Shows the Frosty user manual.
    """
    with open("about.txt", "r") as f:
        await ctx.send(f.read())


@trigger("give me (.+) snowmen")
async def snowman(ctx, snowmen_request):
    """
    Giver of snowmen since 2018.

    :param snowmen_request: translates "a" to 1, evals arithmetic expressions <= 128
    """
    if snowmen_request.strip() == "a":
        await ctx.send("☃")
    else:
        result = sandbox.LANGUAGES["python"].execute("print(({}) * '☃')".format(snowmen_request))
        await ctx.send(result["stdout"].decode())


@command
async def echo(ctx, string):
    """
    Make frosty say something.

    :param string string: a string of text
    """
    ctx.send(string)
