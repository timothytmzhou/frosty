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
    await ctx.send("> {}".format(query))
    msg = await ctx.send(content="hol up lemme check...")
    try:
        res = await client.loop.run_in_executor(None, waClient.query, query)
        content = "".join("```md\n{}```".format(r.text) for r in res.results)
        if not content:
            content = "```no text results found```"
    except AttributeError:
        content = "```Wolfram Alpha doesn't understand your query```"
    await msg.edit(content=content)
