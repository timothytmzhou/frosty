import wolframalpha
from message_structs import *

with open("wa_app_id.txt") as waid:
    waClient = wolframalpha.Client(waid.read())

def ask(msg_info, *args):
    query = args[0]
    res = waClient.query(query)
    message = "".join("```md\n{0}```".format(r.text) for r in res.results)
    return Call(CallType.SEND, msg_info.message, message)
