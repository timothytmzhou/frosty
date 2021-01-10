from src.commands import *
# from src.extensions import sandbox


@command("help")
async def frosty_help(ctx):
    """
    Shows the Frosty user manual.
    """
    with open("about.txt", "r") as f:
        await ctx.send(content=f.read())


@trigger("give me (.+) (?:snowman|snowmen)")
async def snowman(msg, snowmen_request):
    """
    Giver of snowmen since 2018.

    :param snowmen_request: translates "a" to 1, evals arithmetic expressions <= 128
    """
    if snowmen_request.strip() == "a":
        await msg.channel.send("☃")
    # else:
    #     result = sandbox.LANGUAGES["python"].execute("print(({}) * '☃')".format(snowmen_request))
    #     await ctx.send(result["stdout"].decode())


@command("echo")
async def echo(ctx, string):
    """
    Make frosty say something.

    :param string string: a string of text
    """
    await ctx.send(content=string)
