import wolframalpha
from message_structs import *

with open("wa_app_id.txt") as waid:
    waClient = wolframalpha.Client(waid.read())

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
    return Call(CallType.SEND, msg_info.message, message)
