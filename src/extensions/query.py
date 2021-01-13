import wolframalpha
from src.commands import *
from src.config import PROFILE

waClient = wolframalpha.Client(PROFILE["wa_app_id"])

@command()
async def ask(ctx, query):
    """
    Queries Wolfram Alpha.

    :param string query: input to Wolfram Alpha
    """
    await ctx.send(content="hol up lemme check...")
    try:
        res = await client.loop.run_in_executor(None, waClient.query, query)
        msg = "".join("```md\n{0}```".format(r.text) for r in res.results)
        if not msg:
            msg = "```no text results found```"
    except AttributeError:
        msg = "```Wolfram Alpha doesn't understand your query```"
    await ctx.edit(content=msg)
