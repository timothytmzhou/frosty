import wolframalpha
from src.message_structs import *
from src.config import PROFILE

waClient = wolframalpha.Client(PROFILE["wa_app_id"])


def ask(msg_info, *args):
    """
    > Queries Wolfram Alpha.
    > Shows all text from pods with the results tag.
    """
    query = args[0]
    try:
        res = waClient.query(query)
        message = "".join("```md\n{0}```".format(r.text) for r in res.results)
    except AttributeError:
        message = "```Wolfram Alpha doesn't understand your query```"
    return Call(task=Call.send, args=(msg_info.channel, message))
